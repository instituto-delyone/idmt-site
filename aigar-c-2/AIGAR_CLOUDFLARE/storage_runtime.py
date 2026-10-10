"""Cloudflare authentication, storage, document ingestion and library workflow services."""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
import uuid
from datetime import datetime, timezone
from workers import WorkflowEntrypoint, fetch
from cloudflare_bindings import binding

MEDUNITY_AUTH_URL = "https://medunity-api.dr-delyone.workers.dev"

async def medunity_admin_login(body):
    response = await fetch(
        MEDUNITY_AUTH_URL + "/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({
            "nome_usuario": body.get("nome_usuario"),
            "senha": body.get("senha"),
        }),
    )
    data = await response.json()
    return response.status, data

async def medunity_me(request):
    authorization = request.headers.get("Authorization") or ""
    if not authorization.startswith("Bearer "):
        return 401, {"detail": "Autenticação necessária."}
    response = await fetch(
        MEDUNITY_AUTH_URL + "/me",
        method="GET",
        headers={"Authorization": authorization},
    )
    data = await response.json()
    if response.status >= 400:
        return response.status, data
    usuario = data.get("usuario") or {}
    if usuario.get("perfil") != "admin":
        return 403, {"detail": "Esta conta não possui acesso administrativo."}
    return 200, data

async def require_admin(request):
    status, data = await medunity_me(request)
    if status != 200:
        return None, status, data
    return data.get("usuario") or {}, 200, data

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
ALLOWED_UPLOAD_TYPES = {"application/pdf"}
R2_BINDING = "AIGAR_LIBRARY_BUCKET"
D1_BINDING = "AIGAR_DB"

def sanitize_filename(name):
    name = (name or "document.pdf").strip().replace("\\", "/").split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9À-ÿ._ -]+", "_", name)
    name = re.sub(r"\\s+", " ", name).strip()
    if not name:
        name = "document.pdf"
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name[:180]

async def storage_status(env):
    bucket = binding(env, R2_BINDING)
    db = binding(env, D1_BINDING)
    return {
        "r2": bool(bucket),
        "d1": bool(db),
        "ready": bool(bucket and db),
        "bucket_binding": R2_BINDING,
        "database_binding": D1_BINDING,
    }

async def admin_upload(request, env, usuario):
    bucket = binding(env, R2_BINDING)
    db = binding(env, D1_BINDING)
    if not bucket or not db:
        return 503, {
            "ok": False,
            "status": "storage_not_configured",
            "message": "A persistência do AIGAR ainda não está vinculada ao Worker. Configure R2 e D1.",
            "storage": await storage_status(env),
        }

    content_type = (request.headers.get("Content-Type") or "").split(";")[0].lower()
    if content_type not in ALLOWED_UPLOAD_TYPES:
        return 415, {"ok": False, "status": "invalid_file_type", "message": "Apenas arquivos PDF são aceitos nesta primeira fase."}

    raw_length = request.headers.get("Content-Length")
    try:
        content_length = int(raw_length) if raw_length else None
    except Exception:
        content_length = None
    if content_length and content_length > MAX_UPLOAD_BYTES:
        return 413, {"ok": False, "status": "file_too_large", "message": "O limite desta primeira fase é 100 MB."}

    filename = sanitize_filename(request.headers.get("X-Filename"))
    client_sha = (request.headers.get("X-File-SHA256") or "").strip().lower()
    if client_sha and not re.fullmatch(r"[0-9a-f]{64}", client_sha):
        return 400, {"ok": False, "status": "invalid_checksum", "message": "X-File-SHA256 inválido."}

    if client_sha:
        duplicate = await db.prepare(
            "SELECT id, filename, status, r2_key FROM documents WHERE sha256 = ? LIMIT 1"
        ).bind(client_sha).first()
        if duplicate:
            return 200, {
                "ok": True,
                "status": "already_exists",
                "document": plain_document(duplicate),
            }

    seed = f"{client_sha}:{time.time_ns()}:{filename}".encode("utf-8")
    document_id = hashlib.sha256(seed).hexdigest()[:24]
    r2_key = f"documents/{document_id}/original.pdf"

    try:
        uploaded = await bucket.put(r2_key, request.body, {
            "httpMetadata": {"contentType": "application/pdf"},
            "customMetadata": {
                "original_filename": filename,
                "document_id": document_id,
                "uploaded_by": str(usuario.get("nome_usuario") or usuario.get("id") or "admin"),
            },
        })
    except Exception as exc:
        return 500, {"ok": False, "status": "r2_upload_error", "message": str(exc)}

    size_bytes = int(getattr(uploaded, "size", content_length or 0) or 0)
    now = int(time.time())

    try:
        await db.prepare(
            """INSERT INTO documents
               (id, filename, mime_type, size_bytes, sha256, r2_key, status,
                uploaded_at, uploaded_by, chunk_count)
               VALUES (?, ?, ?, ?, ?, ?, 'uploaded', ?, ?, 0)"""
        ).bind(
            document_id, filename, "application/pdf", size_bytes,
            client_sha or None, r2_key, now,
            str(usuario.get("nome_usuario") or usuario.get("id") or "admin"),
        ).run()
    except Exception as exc:
        try:
            await bucket.delete(r2_key)
        except Exception:
            pass
        return 500, {"ok": False, "status": "metadata_error", "message": str(exc)}

    workflow = binding(env, "AIGAR_LIBRARY_BUILDER")
    workflow_status = "not_configured"
    workflow_id = None
    if workflow:
        try:
            instance = await workflow.create(params={"document_id": document_id})
            workflow_status = "started"
            workflow_id = str(instance.id)
        except Exception as exc:
            workflow_status = "error"
            workflow_id = str(exc)[:500]

    return 201, {
        "ok": True,
        "status": "uploaded",
        "document": {
            "id": document_id,
            "filename": filename,
            "mime_type": "application/pdf",
            "size_bytes": size_bytes,
            "sha256": client_sha or None,
            "r2_key": r2_key,
            "status": "uploaded",
            "uploaded_at": now,
            "uploaded_by": str(usuario.get("nome_usuario") or usuario.get("id") or "admin"),
            "chunk_count": 0,
        },
        "next_step": "automatic_processing",
        "processing": {"status": workflow_status, "workflow_id": workflow_id},
    }

def plain_document(row):
    if not row:
        return None
    def scalar(name, default=None):
        try:
            value=getattr(row,name)
        except Exception:
            return default
        if value is None:
            return default
        return value
    return {
        "id": str(scalar("id","")),
        "filename": str(scalar("filename","")),
        "mime_type": str(scalar("mime_type","")),
        "size_bytes": int(scalar("size_bytes",0) or 0),
        "sha256": str(scalar("sha256")) if scalar("sha256") else None,
        "r2_key": str(scalar("r2_key","")),
        "status": str(scalar("status","")),
        "uploaded_at": int(scalar("uploaded_at",0) or 0),
        "uploaded_by": str(scalar("uploaded_by","")),
        "chunk_count": int(scalar("chunk_count",0) or 0),
        "error_message": str(scalar("error_message")) if scalar("error_message") else None,
    }



CHUNK_PAGES = 25
LIBRARY_R2_PREFIX = "libraries"

def normalize_library_text(text):
    text = (text or "").replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def markdown_pages(markdown):
    """Return [(page_number, text)] from Workers AI Markdown output."""
    raw = normalize_library_text(markdown)
    matches = list(re.finditer(r"(?m)^###\s+Page\s+(\d+)\s*$", raw))
    if not matches:
        return [(None, raw)] if raw else []
    pages = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        body = normalize_library_text(raw[start:end])
        if body:
            pages.append((int(m.group(1)), body))
    return pages

def make_page_chunks(pages, pages_per_chunk=CHUNK_PAGES):
    if not pages:
        return []
    if pages[0][0] is None:
        text = pages[0][1]
        # TXT/Markdown-style fallback: preserve the document and split by ~24k chars.
        out = []
        for start in range(0, len(text), 24000):
            out.append((None, None, text[start:start + 24000]))
        return out
    out = []
    for i in range(0, len(pages), pages_per_chunk):
        group = pages[i:i + pages_per_chunk]
        out.append((group[0][0], group[-1][0], "\n\n".join(x[1] for x in group)))
    return out

async def convert_r2_pdf_to_markdown(env, r2_key, filename):
    bucket = binding(env, R2_BINDING)
    ai = binding(env, "AI")
    if not bucket:
        raise RuntimeError("R2 binding ausente.")
    if not ai:
        raise RuntimeError("Workers AI binding ausente.")
    obj = await bucket.get(r2_key)
    if not obj:
        raise RuntimeError("PDF não encontrado no R2.")
    data = await obj.arrayBuffer()
    # Workers AI's toMarkdown accepts a JS Blob. Python Workers expose JS objects
    # through the FFI, so we create the Blob without copying the PDF through D1.
    from js import Blob, Array, Uint8Array
    view = Uint8Array.new(data)
    parts = Array.new()
    parts.push(view)
    # Let Workers AI infer the document type from the .pdf filename.
    blob = Blob.new(parts)
    if int(getattr(blob, "size", 0) or 0) <= 0:
        raise RuntimeError("PDF recuperado do R2 resultou em Blob vazio.")
    from pyodide.ffi import create_proxy
    file_item = create_proxy({"name": filename, "blob": blob})
    files = Array.new()
    files.push(file_item)
    result = await ai.toMarkdown(files)
    items = result if isinstance(result, list) else list(result)
    if not items:
        raise RuntimeError("Workers AI não retornou conteúdo para o PDF.")
    item = items[0]
    fmt = str(item.get("format") or "")
    if fmt == "error":
        raise RuntimeError(str(item.get("error") or "Falha na conversão do PDF."))
    return str(item.get("data") or "")

async def build_document_library(env, document_id):
    db = binding(env, D1_BINDING)
    bucket = binding(env, R2_BINDING)
    if not db or not bucket:
        raise RuntimeError("Persistência do AIGAR não está configurada.")

    row = await db.prepare(
        "SELECT id, filename, r2_key, sha256, status FROM documents WHERE id = ? LIMIT 1"
    ).bind(document_id).first()
    if not row:
        raise RuntimeError("Documento não encontrado.")

    filename = str(row.filename or "document.pdf")
    r2_key = str(row.r2_key or "")
    await db.prepare(
        "UPDATE documents SET status = 'processing', error_message = NULL WHERE id = ?"
    ).bind(document_id).run()

    try:
        markdown = await convert_r2_pdf_to_markdown(env, r2_key, filename)
        pages = markdown_pages(markdown)
        chunks = make_page_chunks(pages, CHUNK_PAGES)
        if not chunks:
            raise RuntimeError("Nenhum texto recuperável foi encontrado no PDF.")

        source_digest = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        # Idempotency: remove old chunk metadata/artifacts before rebuilding.
        old = await db.prepare(
            "SELECT r2_key FROM document_chunks WHERE document_id = ?"
        ).bind(document_id).all()
        for old_row in old.results:
            try:
                await bucket.delete(str(old_row.r2_key))
            except Exception:
                pass
        await db.prepare("DELETE FROM document_chunks WHERE document_id = ?").bind(document_id).run()

        created = []
        for seq, (start_page, end_page, text) in enumerate(chunks, start=1):
            chunk_text = normalize_library_text(text)
            if not chunk_text:
                continue
            chunk_id = f"{document_id}_chunk_{seq:04d}"
            r2_chunk_key = f"{LIBRARY_R2_PREFIX}/{document_id}/chunks/chunk_{seq:04d}.md"
            header = (
                f"# {chunk_id}\n\n"
                f"**Biblioteca:** {filename}\n"
                f"**Fonte:** {filename}\n"
                + (f"**Páginas:** {start_page}-{end_page}\n" if start_page is not None else "")
                + f"**Checksum fonte:** {source_digest[:16]}\n\n---\n\n"
            )
            payload = (header + chunk_text + "\n").encode("utf-8")
            await bucket.put(
                r2_chunk_key,
                payload,
                {
                    "httpMetadata": {"contentType": "text/markdown; charset=utf-8"},
                    "customMetadata": {
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "sequence": str(seq),
                        "source": filename,
                        "start_page": str(start_page or ""),
                        "end_page": str(end_page or ""),
                    },
                },
            )
            await db.prepare(
                """INSERT INTO document_chunks
                   (id, document_id, sequence, source, start_page, end_page,
                    r2_key, text_length, checksum, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            ).bind(
                chunk_id, document_id, seq, filename, start_page, end_page,
                r2_chunk_key, len(chunk_text), source_digest, int(time.time())
            ).run()
            created.append({
                "id": chunk_id,
                "sequence": seq,
                "start_page": start_page,
                "end_page": end_page,
                "r2_key": r2_chunk_key,
                "text_length": len(chunk_text),
            })

        await db.prepare(
            "UPDATE documents SET status = 'ready', chunk_count = ?, error_message = NULL WHERE id = ?"
        ).bind(len(created), document_id).run()
        return {"document_id": document_id, "filename": filename, "chunk_count": len(created), "chunks": created}
    except Exception as exc:
        await db.prepare(
            "UPDATE documents SET status = 'error', error_message = ? WHERE id = ?"
        ).bind(str(exc)[:2000], document_id).run()
        raise

class LibraryBuilderWorkflow(WorkflowEntrypoint):
    async def run(self, event, step):
        # Workflow REST/API instances deliver params as the event payload.
        # Depending on the Python Workers version this can arrive as a dict
        # or as a JSON string, so normalize both forms here.
        payload = event
        # Python WorkflowEvent can expose payload through attributes or
        # JS-proxy indexing depending on the Workers runtime.
        candidates = []
        for attr in ("params", "payload"):
            try:
                candidates.append(getattr(event, attr, None))
            except Exception:
                pass
            try:
                candidates.append(event[attr])
            except Exception:
                pass
        for candidate in candidates:
            if candidate is not None:
                payload = candidate
                break
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {}
        if isinstance(payload, dict):
            if isinstance(payload.get("payload"), dict):
                payload = payload["payload"]
            if isinstance(payload.get("params"), str):
                try:
                    payload = json.loads(payload["params"])
                except Exception:
                    pass
        else:
            for key in ("payload", "params"):
                try:
                    nested = payload[key]
                    if isinstance(nested, str):
                        nested = json.loads(nested)
                    payload = nested
                    break
                except Exception:
                    pass
        if not isinstance(payload, dict):
            payload = {}
        document_id = str(payload.get("document_id") or "")
        if not document_id:
            raise RuntimeError("document_id ausente no Workflow.")
        @step.do("build-library", config={"retries": {"limit": 3, "delay": "10 seconds", "backoff": "exponential"}})
        async def build():
            result = await build_document_library(self.env, document_id)
            return {
                "document_id": result["document_id"],
                "filename": result["filename"],
                "chunk_count": result["chunk_count"],
            }
        return await build()

async def admin_documents(env):
    db = binding(env, D1_BINDING)
    if not db:
        return 503, {"ok": False, "status": "storage_not_configured", "storage": await storage_status(env)}
    result = await db.prepare(
        """SELECT id, filename, mime_type, size_bytes, sha256, r2_key,
                  status, uploaded_at, uploaded_by, chunk_count, error_message
           FROM documents ORDER BY uploaded_at DESC LIMIT 100"""
    ).run()
    documents=[]
    try:
        rows=result.results
        for row in rows:
            doc=plain_document(row)
            if doc:
                documents.append(doc)
    except Exception as exc:
        return 500, {
            "ok": False,
            "status": "documents_serialization_error",
            "message": str(exc),
        }
    return 200, {"ok": True, "documents": documents}

# ---------------------------------------------------------------------------
# AIGAR Adaptive Interaction Layer v0.1
# Integrado ao runtime Cloudflare Workers existente (sem FastAPI/SQLite local).
# ---------------------------------------------------------------------------
