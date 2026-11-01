"""Controlled ACLR-to-CORTEX transition with safe legacy fallback."""
from __future__ import annotations
from typing import Any, Mapping
from aclr_r2_runtime import run_aclr_r2_shadow

ALLOWED_MODES = {"shadow", "candidate"}
TRUSTED_SOURCE_STATUSES = {"verified", "reviewed"}

def configured_aclr_mode(env: Any) -> str:
    raw = getattr(env, "ACLR_MODE", None) if env is not None else None
    value = str(raw or "shadow").strip().lower()
    return value if value in ALLOWED_MODES else "shadow"

def _adapt_evidence(items: list[Mapping[str, Any]]) -> list[dict]:
    adapted = []
    for item in items:
        provenance = dict(item.get("provenance") or {})
        status = str(provenance.get("source_status") or "").strip().lower()
        text = str(item.get("text") or "").strip()
        if not text or status not in TRUSTED_SOURCE_STATUSES:
            continue
        adapted.append({"text": text[:14000], "source": str(item.get("source_id") or "ACLR verified source"),
            "source_key": "aclr_r2_index_first", "chunk_id": str(item.get("evidence_id") or ""),
            "domain_ids": list(item.get("domain_ids") or []), "provenance": provenance,
            "visibility": "public", "retrieval_method": "aclr_hierarchical_index_first"})
    return adapted

async def execute_aclr_transition(env: Any, question: str, legacy_evidence: list[dict], *, top_k: int = 5, mode_override: str | None = None) -> dict:
    mode = str(mode_override or configured_aclr_mode(env)).strip().lower()
    if mode not in ALLOWED_MODES:
        mode = "shadow"
    diagnostic = {"mode": mode, "status": "skipped", "selected_count": 0, "accepted_count": 0,
        "fallback": False, "fallback_reason": None, "manifest_version": None, "latency_ms": 0, "warnings": []}
    if env is None:
        diagnostic.update(status="unavailable", fallback=True, fallback_reason="environment_missing")
        return {"evidence_items": legacy_evidence, "diagnostic": diagnostic}
    result = await run_aclr_r2_shadow(env, question, top_k=top_k)
    diagnostic.update({"status": result.get("status", "unknown"), "manifest_version": result.get("manifest_version"),
        "planner_version": result.get("planner_version"), "selected_count": int(result.get("selected_chunk_count", 0) or 0),
        "latency_ms": int(result.get("latency_ms", 0) or 0), "warnings": list(result.get("warnings") or []),
        "source_statuses": list(result.get("source_statuses") or [])})
    if mode == "shadow":
        diagnostic["fallback_reason"] = "shadow_mode_legacy_preserved"
        return {"evidence_items": legacy_evidence, "diagnostic": diagnostic}
    candidate = _adapt_evidence(result.get("evidence_items") or [])
    diagnostic["accepted_count"] = len(candidate)
    if result.get("status") not in {"complete", "partial"}:
        diagnostic.update(fallback=True, fallback_reason="aclr_retrieval_not_complete")
        return {"evidence_items": legacy_evidence, "diagnostic": diagnostic}
    if not candidate:
        diagnostic.update(fallback=True, fallback_reason="no_reviewed_or_verified_sources")
        return {"evidence_items": legacy_evidence, "diagnostic": diagnostic}
    diagnostic.update(status="candidate_selected", fallback=False)
    return {"evidence_items": candidate, "diagnostic": diagnostic}
