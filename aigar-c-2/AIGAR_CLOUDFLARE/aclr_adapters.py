"""Compatibility adapters from existing AIGAR retrieval functions to ACLR envelopes.

The adapters preserve the old retrievers as evidence providers. They do not claim
that either legacy search is a domain-index-specific Layer B implementation.
"""
from __future__ import annotations

import asyncio
import hashlib
from typing import Any, Mapping

from aclr_contracts import validate_evidence_envelope

def _envelope(query_id: str, retriever_id: str, results: list[Mapping[str, Any]], *, status: str = "success", warnings: list[str] | None = None, latency_ms: int | None = None) -> dict:
    evidence = []
    for position, item in enumerate(results):
        content = str(item.get("text") or item.get("content") or "")
        source_key = str(item.get("source_key") or item.get("source") or retriever_id)
        chunk_id = item.get("chunk_id") or item.get("id")
        document_id = item.get("document_id")
        evidence_id = str(chunk_id or hashlib.sha256((source_key + content).encode("utf-8")).hexdigest()[:24])
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        evidence.append({
            "evidence_id": evidence_id,
            "source_id": source_key,
            "document_id": str(document_id) if document_id is not None else None,
            "chunk_id": str(chunk_id) if chunk_id is not None else None,
            "domain_ids": list(item.get("domain_ids") or []),
            "content": content,
            "relevance_score": item.get("score"),
            "score_semantics": item.get("retrieval_method") or "legacy_retriever_score_unified_calibration_not_established",
            "confidence": None,
            "provenance": {
                "source": item.get("source"),
                "source_key": source_key,
                "retriever_id": retriever_id,
                "legacy_position": position,
                "start_page": item.get("start_page"),
                "end_page": item.get("end_page"),
                "checksum": item.get("checksum"),
            },
            "location": {"start_page": item.get("start_page"), "end_page": item.get("end_page")},
            "content_hash": digest,
            "index_version": item.get("index_version"),
            "pointer_refs": [],
        })
    envelope = {
        "query_id": query_id,
        "retriever_id": retriever_id,
        "status": status if evidence or status != "success" else "empty",
        "latency_ms": latency_ms,
        "evidence": evidence,
        "warnings": list(warnings or []),
        "error": None,
    }
    return validate_evidence_envelope(envelope)

def library_results_to_envelope(query_id: str, results: list[Mapping[str, Any]], *, latency_ms: int | None = None) -> dict:
    return _envelope(query_id, "legacy_library_search", results, latency_ms=latency_ms)

def r2_results_to_envelope(query_id: str, results: list[Mapping[str, Any]], *, latency_ms: int | None = None) -> dict:
    return _envelope(query_id, "legacy_r2_document_chunks", results, latency_ms=latency_ms)

async def execute_legacy_retrievers(query: str, reading: Mapping[str, Any], env: Any, *, query_id: str, topic: str | None = None, limit: int = 5) -> list[dict]:
    """Run the two existing retrievers independently and return partial envelopes safely."""
    from library_runtime import library_search
    from storage_runtime import search_r2_document_chunks

    async def run_library():
        try:
            rows = await library_search(query, dict(reading), limit=limit)
            return library_results_to_envelope(query_id, rows)
        except Exception as exc:
            return _envelope(query_id, "legacy_library_search", [], status="error",
                             warnings=["legacy_library_search_failed"],
                             latency_ms=None) | {"error": {"code": "legacy_retriever_error", "message": "Library retrieval failed.", "retryable": True, "component": "legacy_library_search"}}

    async def run_r2():
        try:
            rows = await search_r2_document_chunks(env, query, topic=topic, limit=limit)
            return r2_results_to_envelope(query_id, rows)
        except Exception:
            return _envelope(query_id, "legacy_r2_document_chunks", [], status="error",
                             warnings=["legacy_r2_retrieval_failed"],
                             latency_ms=None) | {"error": {"code": "legacy_retriever_error", "message": "R2 retrieval failed.", "retryable": True, "component": "legacy_r2_document_chunks"}}

    return await asyncio.gather(run_library(), run_r2())
