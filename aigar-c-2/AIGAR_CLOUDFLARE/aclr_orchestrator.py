"""ACLR Layer B orchestration: bounded concurrent execution of planned paths."""
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Mapping

from aclr_contracts import validate_retrieval_plan, validate_evidence_envelope

async def execute_retrieval_plan(
    plan: Mapping[str, Any],
    retrieve_path: Callable[[Mapping[str, Any]], Awaitable[Mapping[str, Any]]],
    *,
    max_concurrency: int = 4,
) -> dict:
    """Execute paths independently; one failure never discards other path results.

    The callback is the storage/retriever adapter boundary. No R2 key layout,
    D1 catalogue shape or production timeout is assumed by this orchestrator.
    """
    normalized = validate_retrieval_plan(plan)
    semaphore = asyncio.Semaphore(max(1, int(max_concurrency)))

    async def run(path: Mapping[str, Any]) -> dict:
        async with semaphore:
            try:
                raw = await retrieve_path(path)
                envelope = validate_evidence_envelope(raw)
                if envelope["query_id"] != normalized["query_id"]:
                    raise ValueError("retriever returned a different query_id")
                return {"path_id": path["path_id"], "status": envelope["status"], "envelope": envelope}
            except Exception:
                return {
                    "path_id": path["path_id"],
                    "status": "error",
                    "envelope": {
                        "query_id": normalized["query_id"],
                        "retriever_id": "aclr_path:" + path["path_id"],
                        "status": "error",
                        "latency_ms": None,
                        "evidence": [],
                        "warnings": ["retrieval_path_failed"],
                        "error": {
                            "code": "retrieval_path_error",
                            "message": "A retrieval path failed; other paths were retained.",
                            "retryable": True,
                            "component": "aclr_orchestrator",
                        },
                    },
                }

    results = await asyncio.gather(*(run(path) for path in normalized["paths"]))
    statuses = [item["status"] for item in results]
    usable = any(item["status"] in {"success", "partial"} for item in results)
    if usable and any(status in {"error", "partial"} for status in statuses):
        aggregate = "partial"
    elif usable or (statuses and all(status == "empty" for status in statuses)):
        aggregate = "complete"
    else:
        aggregate = "failed"
    return {
        "query_id": normalized["query_id"],
        "retrieval_status": aggregate,
        "path_results": results,
        "envelopes": [item["envelope"] for item in results],
    }
