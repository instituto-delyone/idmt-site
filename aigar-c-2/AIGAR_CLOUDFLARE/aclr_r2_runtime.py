"""ACLR R2 catalogue reader and shadow retrieval runtime.

Reads versioned routing indexes first, resolves selected chunk IDs, and only then
loads the corresponding R2 chunk bodies. Results are diagnostic only in shadow mode.
"""
from __future__ import annotations

import json
import time
from typing import Any

from cloudflare_bindings import binding
R2_BINDING = "AIGAR_LIBRARY_BUCKET"
from aclr_router import build_retrieval_plan, inspect_selected_targets
from aclr_resolver import resolve_evidence

ACLR_ROOT = "aclr/catalog/v1"
ACLR_MANIFEST_KEY = f"{ACLR_ROOT}/manifest.json"
ACLR_ROUTER_KEY = f"{ACLR_ROOT}/router_index.json"


async def _read_json(bucket: Any, key: str) -> dict:
    obj = await bucket.get(key)
    if not obj:
        raise FileNotFoundError(f"ACLR index not found: {key}")
    raw = await obj.text()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"ACLR index must be a JSON object: {key}")
    return value


async def _read_text(bucket: Any, key: str) -> str:
    obj = await bucket.get(key)
    if not obj:
        raise FileNotFoundError(f"ACLR chunk not found: {key}")
    return str(await obj.text())


def _strip_frontmatter(content: str) -> tuple[dict, str]:
    text = str(content or "").strip()
    metadata = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            for line in parts[1].splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
            text = parts[2].strip()
    return metadata, text


async def run_aclr_r2_shadow(env: Any, question: str, *, top_k: int = 5) -> dict:
    """Run index-first ACLR traversal without changing answer evidence or legacy retrieval."""
    started = time.time()
    bucket = binding(env, R2_BINDING)
    if not bucket:
        return {"enabled": True, "status": "unavailable", "reason": "r2_binding_missing"}

    try:
        manifest = await _read_json(bucket, ACLR_MANIFEST_KEY)
        master = await _read_json(bucket, ACLR_ROUTER_KEY)
        domain_indexes = {}
        for domain in master.get("domains", []):
            domain_id = str(domain.get("domain_id") or "")
            relative = str(domain.get("index_path") or "")
            if not domain_id or not relative:
                continue
            key = f"{ACLR_ROOT}/{relative}"
            domain_indexes[domain_id] = await _read_json(bucket, key)

        request = {
            "query_id": f"shadow-{int(time.time() * 1000)}",
            "question": str(question),
            "language": "pt-BR",
            "request_mode": "shadow",
            "top_k": max(1, min(10, int(top_k))),
        }
        plan = build_retrieval_plan(
            request,
            master,
            domain_indexes,
            general_index=manifest.get("general_index"),
        )
        selected = inspect_selected_targets(plan, domain_indexes)
        evidence = []
        loaded_keys = []
        for path in plan.get("paths", []):
            chunk_ids = selected.get(path.get("path_id"), [])
            for chunk_id in chunk_ids[:max(1, min(10, int(top_k)))]:
                key = f"{ACLR_ROOT}/chunks/{chunk_id}.md"
                content = await _read_text(bucket, key)
                metadata, body = _strip_frontmatter(content)
                evidence.append({
                    "evidence_id": str(chunk_id),
                    "source_id": str(metadata.get("domain_id") or path.get("domain_id") or "aclr_prototype"),
                    "content": body,
                    "domain_ids": [str(metadata.get("domain_id") or path.get("domain_id") or "unknown")],
                    "provenance": {
                        "r2_key": key,
                        "subdomain_id": metadata.get("subdomain_id"),
                        "source_status": metadata.get("source_status", "unclassified"),
                        "content_type": metadata.get("content_type", "unknown"),
                        "index_version": manifest.get("manifest_version"),
                    },
                })
                loaded_keys.append(key)

        envelope = {
            "query_id": plan["query_id"],
            "retriever_id": "aclr_r2_index_first_shadow",
            "status": "success" if evidence else "empty",
            "evidence": evidence,
            "warnings": [],
        }
        resolved = resolve_evidence(plan["query_id"], [envelope])
        source_statuses = sorted({
            item.get("provenance", {}).get("source_status", "unclassified")
            for item in resolved.get("evidence", [])
        })
        return {
            "enabled": True,
            "status": "complete" if resolved.get("retrieval_status") == "complete" else resolved.get("retrieval_status"),
            "mode": "shadow",
            "manifest_version": manifest.get("manifest_version"),
            "planner_version": plan.get("planner_version"),
            "planned_paths": len(plan.get("paths", [])),
            "selected_chunk_count": len(loaded_keys),
            "selected_chunk_ids": [item["evidence_id"] for item in resolved.get("evidence", [])],
            "source_statuses": source_statuses,
            "synthetic_only": bool(source_statuses) and all(value == "synthetic_test_content" for value in source_statuses),
            "latency_ms": int((time.time() - started) * 1000),
            "warnings": resolved.get("warnings", []),
        }
    except Exception as exc:
        return {
            "enabled": True,
            "status": "error",
            "mode": "shadow",
            "error_type": type(exc).__name__,
            "reason": str(exc)[:240],
            "latency_ms": int((time.time() - started) * 1000),
        }
