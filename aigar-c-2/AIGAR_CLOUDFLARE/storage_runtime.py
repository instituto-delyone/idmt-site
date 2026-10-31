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



CHUNK_PAGES = 25  # Compatibilidade com imports antigos; o chunking agora é orientado por conteúdo.
MAX_CHUNK_CHARS = 20000
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

def make_page_chunks(pages, max_chars=MAX_CHUNK_CHARS):
    """Split by content volume while preserving page boundaries whenever possible.

    Chunk count is determined by the document's actual extracted text, not a fixed
    target count. A single unusually long page is split into smaller pieces.
    """
    if not pages:
        return []
    out = []
    current_texts = []
    current_start = None
    current_end = None
    current_len = 0

    def flush():
        nonlocal current_texts, current_start, current_end, current_len
        if current_texts:
            out.append((current_start, current_end, "\n\n".join(current_texts)))
        current_texts = []
        current_start = None
        current_end = None
        current_len = 0

    for page_number, page_text in pages:
        text = normalize_library_text(page_text)
        if not text:
            continue
        # Pages with no detected page marker are handled identically, but without page metadata.
        pieces = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
        for piece in pieces:
            if current_texts and current_len + len(piece) + 2 > max_chars:
                flush()
            if current_start is None:
                current_start = page_number
            current_end = page_number
            current_texts.append(piece)
            current_len += len(piece) + (2 if len(current_texts) > 1 else 0)
    flush()
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
    from js import Blob, Array, Uint8Array, Object
    view = Uint8Array.new(data)
    parts = Array.new()
    parts.push(view)
    # Let Workers AI infer the document type from the .pdf filename.
    blob_options = Object.new()
    blob_options.type = "application/pdf"
    blob = Blob.new(parts, blob_options)
    if int(getattr(blob, "size", 0) or 0) <= 0:
        raise RuntimeError("PDF recuperado do R2 resultou em Blob vazio.")
    file_item = Object.new()
    file_item.name = filename
    file_item.blob = blob
    files = Array.new()
    files.push(file_item)
    result = await ai.toMarkdown(files)
    def result_field(obj, key, default=None):
        # Workers AI may return a Python mapping or a JavaScript proxy object.
        try:
            value = obj.get(key, default)
            return default if value is None else value
        except Exception:
            pass
        try:
            value = obj[key]
            return default if value is None else value
        except Exception:
            pass
        try:
            value = getattr(obj, key)
            return default if value is None else value
        except Exception:
            return default

    if isinstance(result, list):
        items = result
    else:
        items = []
        # Some Python Workers builds expose a single JS result object, not an array.
        if result_field(result, "format") is not None or result_field(result, "data") is not None:
            items = [result]
        if not items:
            try:
                items = [result[i] for i in range(int(result.length))]
            except Exception:
                try:
                    items = list(result)
                except Exception:
                    items = []
    if not items:
        raise RuntimeError("Workers AI não retornou conteúdo para o PDF.")
    extracted = []
    errors = []
    for item in items:
        fmt = str(result_field(item, "format", "") or "")
        if fmt == "error":
            errors.append(str(result_field(item, "error", "Falha na conversão do PDF.") or "Falha na conversão do PDF."))
            continue
        data = result_field(item, "data", "")
        if data:
            extracted.append(str(data))
    if not extracted:
        detail = "; ".join(errors[:3]) or "Nenhum item continha o campo data."
        raise RuntimeError("Workers AI não retornou texto extraído do PDF. " + detail)
    # toMarkdown may return one item per page; do not silently discard every page after the first.
    return "\n\n".join(extracted)

async def _document_row(env, document_id):
    db = binding(env, D1_BINDING)
    row = await db.prepare(
        "SELECT id, filename, r2_key, sha256, status FROM documents WHERE id = ? LIMIT 1"
    ).bind(document_id).first()
    if not row:
        raise RuntimeError("Documento não encontrado.")
    return row


async def prepare_document_library(env, document_id):
    """Extract a PDF once and persist the full Markdown outside the Workflow step output."""
    db = binding(env, D1_BINDING)
    bucket = binding(env, R2_BINDING)
    if not db or not bucket:
        raise RuntimeError("Persistência do AIGAR não está configurada.")
    row = await _document_row(env, document_id)
    filename = str(row.filename or "document.pdf")
    r2_key = str(row.r2_key or "")
    await db.prepare(
        "UPDATE documents SET status = 'processing', error_message = NULL WHERE id = ?"
    ).bind(document_id).run()
    try:
        extracted_key = f"{LIBRARY_R2_PREFIX}/{document_id}/processing/extracted.md"
        existing_extraction = await bucket.get(extracted_key)
        if existing_extraction:
            markdown = await existing_extraction.text()
        else:
            markdown = await convert_r2_pdf_to_markdown(env, r2_key, filename)
        pages = markdown_pages(markdown)
        chunks = make_page_chunks(pages, MAX_CHUNK_CHARS)
        if not chunks:
            preview = repr(markdown[:500])
            raise RuntimeError(
                "Nenhum texto recuperável foi encontrado no PDF. "
                f"markdown_chars={len(markdown)}; pages_detected={len(pages)}; preview={preview}"
            )
        # Refuse metadata-only conversions; they are not valid memory content.
        meaningful = sum(len(normalize_library_text(text)) for _, _, text in chunks)
        if meaningful < 200 or ("## Metadata" in markdown and not re.search(r"(?m)^###\s+Page\s+\d+", markdown)):
            raise RuntimeError(
                "A conversão retornou metadados do PDF, mas não conteúdo das páginas. "
                "É necessário OCR ou outra rota de extração."
            )
        digest = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        extracted_key = f"{LIBRARY_R2_PREFIX}/{document_id}/processing/extracted.md"
        await bucket.put(
            extracted_key,
            markdown,
            {
                "httpMetadata": {"contentType": "text/markdown; charset=utf-8"},
                "customMetadata": {
                    "document_id": document_id,
                    "source": filename,
                    "source_digest": digest,
                    "page_count": str(len(pages)),
                    "chunk_count": str(len(chunks)),
                },
            },
        )
        return {
            "document_id": document_id,
            "filename": filename,
            "source_digest": digest,
            "extracted_key": extracted_key,
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "text_chars": len(markdown),
        }
    except Exception as exc:
        try:
            await db.prepare(
                "UPDATE documents SET status = 'error', error_message = ? WHERE id = ?"
            ).bind(str(exc)[:2000], document_id).run()
        except Exception:
            pass
        raise


async def cleanup_document_chunks(env, document_id):
    """Remove indexed chunks from prior attempts before rebuilding a document."""
    db = binding(env, D1_BINDING)
    bucket = binding(env, R2_BINDING)
    old = await db.prepare(
        "SELECT r2_key FROM document_chunks WHERE document_id = ?"
    ).bind(document_id).all()
    deleted = 0
    for old_row in old.results:
        key = str(old_row.r2_key or "")
        if key:
            try:
                await bucket.delete(key)
                deleted += 1
            except Exception:
                # The metadata is removed below; a missing stale object must not block rebuilding.
                pass
    await db.prepare("DELETE FROM document_chunks WHERE document_id = ?").bind(document_id).run()
    return {"document_id": document_id, "old_chunk_rows": len(old.results), "objects_deleted": deleted}


async def write_document_chunk_batch(env, document_id, start_index, batch_size=20):
    """Write a bounded, idempotent batch so each Workflow step stays below Worker API limits."""
    db = binding(env, D1_BINDING)
    bucket = binding(env, R2_BINDING)
    row = await _document_row(env, document_id)
    filename = str(row.filename or "document.pdf")
    extracted_key = f"{LIBRARY_R2_PREFIX}/{document_id}/processing/extracted.md"
    obj = await bucket.get(extracted_key)
    if not obj:
        raise RuntimeError("Texto extraído não encontrado no R2; a etapa de extração precisa ser repetida.")
    markdown = await obj.text()
    pages = markdown_pages(markdown)
    chunks = make_page_chunks(pages, MAX_CHUNK_CHARS)
    source_digest = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    selected = chunks[start_index:start_index + batch_size]
    created = []
    for offset, (start_page, end_page, text) in enumerate(selected, start=start_index + 1):
        chunk_text = normalize_library_text(text)
        if not chunk_text:
            continue
        chunk_id = f"{document_id}_chunk_{offset:04d}"
        r2_chunk_key = f"{LIBRARY_R2_PREFIX}/{document_id}/chunks/chunk_{offset:04d}.md"
        header = (
            f"# {chunk_id}\n\n"
            f"**Biblioteca:** {filename}\n"
            f"**Fonte:** {filename}\n"
            + (f"**Páginas:** {start_page}-{end_page}\n" if start_page is not None else "")
            + f"**Checksum fonte:** {source_digest[:16]}\n\n---\n\n"
        )
        payload = header + chunk_text + "\n"
        await bucket.put(
            r2_chunk_key,
            payload,
            {
                "httpMetadata": {"contentType": "text/markdown; charset=utf-8"},
                "customMetadata": {
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "sequence": str(offset),
                    "source": filename,
                    "start_page": str(start_page or ""),
                    "end_page": str(end_page or ""),
                },
            },
        )
        await db.prepare(
            """INSERT OR REPLACE INTO document_chunks
               (id, document_id, sequence, source, start_page, end_page,
                r2_key, text_length, checksum, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        ).bind(
            chunk_id, document_id, offset, filename, start_page, end_page,
            r2_chunk_key, len(chunk_text), source_digest, int(time.time())
        ).run()
        created.append({"id": chunk_id, "sequence": offset, "start_page": start_page,
                        "end_page": end_page, "r2_key": r2_chunk_key, "text_length": len(chunk_text)})
    return {"document_id": document_id, "start": start_index + 1, "written": len(created),
            "total_chunks": len(chunks)}


async def finalize_document_library(env, document_id, chunk_count):
    db = binding(env, D1_BINDING)
    await db.prepare(
        "UPDATE documents SET status = 'ready', chunk_count = ?, error_message = NULL WHERE id = ?"
    ).bind(chunk_count, document_id).run()
    return {"document_id": document_id, "chunk_count": chunk_count, "status": "ready"}


async def build_document_library(env, document_id):
    """Compatibility helper for small documents; large work is coordinated by Workflow steps."""
    prepared = await prepare_document_library(env, document_id)
    await cleanup_document_chunks(env, document_id)
    written = 0
    for start_index in range(0, prepared["chunk_count"], 20):
        batch = await write_document_chunk_batch(env, document_id, start_index, 20)
        written += batch["written"]
    return await finalize_document_library(env, document_id, written)


class LibraryBuilderWorkflow(WorkflowEntrypoint):
    async def run(self, event, step):
        payload = event
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

        @step.do("prepare-extraction", config={"retries": {"limit": 2, "delay": "10 seconds", "backoff": "exponential"}})
        async def prepare():
            return await prepare_document_library(self.env, document_id)
        prepared = await prepare()

        @step.do("cleanup-old-chunks", config={"retries": {"limit": 2, "delay": "10 seconds", "backoff": "exponential"}})
        async def cleanup():
            return await cleanup_document_chunks(self.env, document_id)
        await cleanup()

        batch_size = 20
        total_chunks = int(prepared["chunk_count"])
        for start_index in range(0, total_chunks, batch_size):
            batch_number = start_index // batch_size + 1
            batch_start = start_index
            async def write_batch():
                return await write_document_chunk_batch(self.env, document_id, batch_start, batch_size)
            step_name = f"write-chunks-{batch_number:03d}"
            do_step = step.do(step_name, config={"retries": {"limit": 3, "delay": "10 seconds", "backoff": "exponential"}})
            wrapped_step = do_step(write_batch)
            result = await wrapped_step()

        @step.do("finalize-library", config={"retries": {"limit": 3, "delay": "10 seconds", "backoff": "exponential"}})
        async def finalize():
            return await finalize_document_library(self.env, document_id, total_chunks)
        await finalize()
        # The durable document status/counts are stored in D1; return no SDK proxy.
        return None
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


async def search_r2_document_chunks(env, query, topic=None, limit=5):
    """Busca os corpos dos chunks indexados em D1 e armazenados no R2."""
    db = binding(env, D1_BINDING)
    bucket = binding(env, R2_BINDING)
    if not db or not bucket: return []
    qtext = (str(query or "") + " " + str(topic or "")).casefold()
    stop = {"para","com","uma","uns","das","dos","que","qual","quais","como","sobre","pela","pelo","este","esta","isso","esse","essa","the","and","for","from","into","with"}
    def terms(s): return {x for x in re.findall(r"[a-z0-9À-ÿ]{3,}", str(s or "").casefold()) if x not in stop}
    qt = terms(qtext)
    if not qt: return []
    result = await db.prepare("SELECT id, document_id, sequence, source, start_page, end_page, r2_key, text_length, checksum FROM document_chunks ORDER BY document_id, sequence LIMIT 1000").all()
    rows = list(getattr(result, "results", []) or [])
    def val(row,k,d=None):
        try:
            v=getattr(row,k); return d if v is None else v
        except Exception:
            try: v=row.get(k,d); return d if v is None else v
            except Exception: return d
    source_scores={}
    for row in rows:
        ov=len(qt & terms(val(row,"source","")))
        if ov:
            did=str(val(row,"document_id","") or ""); source_scores[did]=max(source_scores.get(did,0),ov/max(1,len(qt)))
    candidates=[r for r in rows if str(val(r,"document_id","") or "") in source_scores] if source_scores else rows[:40]
    if len(candidates)>160: candidates=sorted(candidates,key=lambda r:(-source_scores.get(str(val(r,"document_id","") or ""),0),int(val(r,"sequence",0) or 0)))[:160]
    import asyncio as _asyncio
    sem=_asyncio.Semaphore(8)
    async def one(row):
        key=str(val(row,"r2_key","") or "")
        if not key:return None
        async with sem:
            try:
                obj=await bucket.get(key)
                if not obj:return None
                content=(await obj.text()).strip()
            except Exception:return None
        body=re.sub(r"(?s)^#.*?---\s*","",content,count=1).strip()
        bt=terms(body); overlap=len(qt & bt); coverage=overlap/max(1,len(qt)); density=overlap/max(1,min(len(bt),250))
        did=str(val(row,"document_id","") or ""); src=str(val(row,"source","") or "")
        bonus=source_scores.get(did,0)*0.18; phrase=0.12 if qtext.strip() and qtext.strip() in body.casefold() else 0.0
        score=coverage*0.72+density*0.10+bonus+phrase
        if overlap<2 and not phrase and bonus<0.10:return None
        return {"chunk_id":str(val(row,"id","") or ""),"document_id":did,"sequence":int(val(row,"sequence",0) or 0),"source":src,"source_key":"r2_document_chunks","start_page":val(row,"start_page"),"end_page":val(row,"end_page"),"checksum":val(row,"checksum"),"r2_key":key,"text":body[:14000],"score":round(score,5),"retrieval_method":"d1_metadata_r2_body_lexical_v1"}
    loaded=await _asyncio.gather(*(one(row) for row in candidates),return_exceptions=True)
    found=[x for x in loaded if isinstance(x,dict)]; found.sort(key=lambda x:(x["score"],-x["sequence"]),reverse=True)
    return found[:max(1,min(10,int(limit or 5)))]
