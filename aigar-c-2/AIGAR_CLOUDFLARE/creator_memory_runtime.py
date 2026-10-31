"""Private creator-memory import and retrieval for the AIGAR Worker."""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from cloudflare_bindings import binding
from storage_runtime import D1_BINDING, R2_BINDING
from conversation_runtime import _audit_admin_action, _utc_now

MAX_CREATOR_MEMORY_BYTES = 256 * 1024
CREATOR_MEMORY_PREFIX = "creator-memory/originals"


def _json_size(value):
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _source_fields(payload):
    interaction_id = payload.get("interaction_id")
    turn_id = payload.get("turn_id")
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    if not turn_id:
        turn_id = state.get("turn_id")
    return (
        str(interaction_id)[:100] if interaction_id is not None else None,
        str(turn_id)[:100] if turn_id is not None else None,
    )


async def creator_memory_schema_ready(db):
    try:
        row = await db.prepare(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='creator_memory_records' LIMIT 1"
        ).first()
        return bool(row)
    except Exception:
        return False


async def import_creator_memory(payload, env, usuario):
    if not isinstance(payload, dict) or not payload:
        return 400, {"ok": False, "status": "invalid_json_object", "message": "Envie um objeto JSON não vazio."}
    try:
        size_bytes = _json_size(payload)
    except Exception:
        return 400, {"ok": False, "status": "invalid_json", "message": "O JSON não pôde ser serializado com segurança."}
    if size_bytes > MAX_CREATOR_MEMORY_BYTES:
        return 413, {"ok": False, "status": "payload_too_large", "message": "Limite de importação: 256 KiB por interação."}

    db = binding(env, D1_BINDING)
    bucket = binding(env, R2_BINDING)
    if not db or not bucket:
        return 503, {"ok": False, "status": "storage_not_configured", "message": "D1 ou R2 não está vinculado ao Worker."}
    if not await creator_memory_schema_ready(db):
        return 503, {"ok": False, "status": "creator_memory_schema_not_ready", "message": "A tabela creator_memory_records ainda não existe no D1. Aplique a migração antes de importar."}

    canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    raw = canonical.encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    duplicate = await db.prepare(
        "SELECT id, imported_at, size_bytes FROM creator_memory_records WHERE sha256 = ? LIMIT 1"
    ).bind(digest).first()
    if duplicate:
        return 200, {
            "ok": True, "status": "already_exists",
            "record": {"id": str(duplicate.id), "imported_at": str(duplicate.imported_at), "size_bytes": int(duplicate.size_bytes or 0), "sha256": digest},
        }

    record_id = str(uuid.uuid4())
    r2_key = f"{CREATOR_MEMORY_PREFIX}/{record_id}.json"
    imported_by = str(usuario.get("id") or usuario.get("usuario_id") or usuario.get("nome_usuario") or "admin")[:200]
    interaction_id, turn_id = _source_fields(payload)
    now = _utc_now()
    metadata = {
        "top_level_keys": sorted([str(key)[:80] for key in payload.keys()])[:40],
        "source_interaction_id": interaction_id,
        "source_turn_id": turn_id,
    }

    try:
        await bucket.put(r2_key, raw, {
            "httpMetadata": {"contentType": "application/json; charset=utf-8"},
            "customMetadata": {"record_id": record_id, "sha256": digest, "visibility": "private"},
        })
    except Exception as exc:
        return 500, {"ok": False, "status": "r2_write_failed", "message": str(exc)[:300]}

    try:
        await db.prepare(
            """INSERT INTO creator_memory_records
               (id, source_interaction_id, source_turn_id, schema_version, r2_key,
                sha256, size_bytes, imported_by, imported_at, status, metadata_json)
               VALUES (?, ?, ?, 'aigar-runtime-json-v1', ?, ?, ?, ?, ?, 'stored', ?)"""
        ).bind(
            record_id, interaction_id, turn_id, r2_key, digest, size_bytes,
            imported_by, now, json.dumps(metadata, ensure_ascii=False),
        ).run()
    except Exception as exc:
        try:
            await bucket.delete(r2_key)
        except Exception:
            pass
        return 500, {"ok": False, "status": "d1_write_failed", "message": str(exc)[:300]}

    try:
        await _audit_admin_action(db, imported_by, "import_creator_memory", "creator_memory_record", record_id, {"sha256": digest, "size_bytes": size_bytes})
    except Exception:
        # The durable imported_by/imported_at fields remain the minimum provenance record.
        # Audit-log availability must not turn a successfully persisted import into a false failure.
        pass

    return 201, {
        "ok": True, "status": "stored",
        "record": {
            "id": record_id, "source_interaction_id": interaction_id,
            "source_turn_id": turn_id, "sha256": digest,
            "size_bytes": size_bytes, "imported_at": now, "status": "stored",
        },
    }


async def list_creator_memory(env, limit=50):
    db = binding(env, D1_BINDING)
    if not db:
        return 503, {"ok": False, "status": "storage_not_configured"}
    if not await creator_memory_schema_ready(db):
        return 503, {"ok": False, "status": "creator_memory_schema_not_ready"}
    rows = (await db.prepare(
        """SELECT id, source_interaction_id, source_turn_id, sha256, size_bytes,
                  imported_at, status
           FROM creator_memory_records ORDER BY imported_at DESC LIMIT ?"""
    ).bind(max(1, min(int(limit), 100))).all()).results
    return 200, {"ok": True, "items": [dict(row) for row in rows]}


async def get_creator_memory(env, record_id):
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", str(record_id or "")):
        return 400, {"ok": False, "status": "invalid_record_id"}
    db = binding(env, D1_BINDING)
    bucket = binding(env, R2_BINDING)
    if not db or not bucket:
        return 503, {"ok": False, "status": "storage_not_configured"}
    if not await creator_memory_schema_ready(db):
        return 503, {"ok": False, "status": "creator_memory_schema_not_ready"}
    row = await db.prepare(
        "SELECT id, r2_key, sha256, size_bytes, status FROM creator_memory_records WHERE id = ? LIMIT 1"
    ).bind(record_id).first()
    if not row:
        return 404, {"ok": False, "status": "record_not_found"}
    obj = await bucket.get(str(row.r2_key))
    if not obj:
        return 500, {"ok": False, "status": "r2_object_missing"}
    raw = await obj.text()
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if digest != str(row.sha256):
        return 409, {"ok": False, "status": "integrity_check_failed", "message": "O hash do objeto não corresponde ao registro D1."}
    try:
        payload = json.loads(raw)
    except Exception:
        return 500, {"ok": False, "status": "stored_json_invalid"}
    return 200, {
        "ok": True,
        "record": {"id": str(row.id), "sha256": digest, "size_bytes": int(row.size_bytes or 0), "status": str(row.status)},
        "payload": payload,
    }
