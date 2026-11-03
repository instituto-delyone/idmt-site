"""Runtime telemetry for the AIGAR Cloudflare Worker.

This module reports observable component/cache state. It deliberately does not
claim to measure isolate RSS: the Python Workers runtime does not expose a
portable, authoritative process-memory metric through this application code.
"""
from __future__ import annotations

import time
from typing import Any


def _cache_age_seconds(timestamp: Any, now: float) -> float | None:
    try:
        value = float(timestamp or 0)
    except (TypeError, ValueError):
        return None
    if value <= 0:
        return None
    return round(max(0.0, now - value), 3)


def _component_state(ready: bool, *, detail: dict | None = None) -> dict:
    return {
        "state": "READY" if ready else "NOT_INITIALIZED",
        "ready": bool(ready),
        **({"detail": detail} if detail is not None else {}),
    }


def build_runtime_health(env: Any, library_module: Any, memory_lab: Any = None) -> dict:
    """Build a truthful, low-cost snapshot without triggering boot or network I/O."""
    now = time.time()

    index_cache = getattr(library_module, "INDEX_CACHE", None)
    library_cache = getattr(library_module, "LIBRARY_BOOT_CACHE", None)
    library_status = getattr(library_module, "LIBRARY_BOOT_STATUS", None)
    text_cache = getattr(library_module, "TEXT_MATRIX_CACHE", None)
    chunk_cache = getattr(library_module, "CHUNK_CACHE", None)

    index_count = len(index_cache) if isinstance(index_cache, (list, tuple, dict)) else 0
    library_chunk_count = len(library_cache) if isinstance(library_cache, dict) else 0
    text_loaded = len(text_cache) if isinstance(text_cache, (list, tuple, dict)) else 0
    chunk_count = len(chunk_cache) if isinstance(chunk_cache, dict) else 0

    library_ready = bool(library_status) and library_chunk_count > 0
    text_total = len(getattr(library_module, "TEXT_MATRIX_FILES", []) or [])
    text_ready = text_total > 0 and text_loaded == text_total

    try:
        from cloudflare_bindings import binding
        # Keep binding names aligned with storage_runtime.py without importing
        # its heavier Worker-specific dependency graph into this observer.
        r2_ready = binding(env, "AIGAR_LIBRARY_BUCKET") is not None
        d1_ready = binding(env, "AIGAR_DB") is not None
    except Exception:
        r2_ready = d1_ready = False

    components = {
        "worker": _component_state(True, detail={"state": "REQUEST_HANDLED"}),
        "library_indexes": _component_state(index_count > 0, detail={
            "cached_indexes": index_count,
            "cache_age_seconds": _cache_age_seconds(
                getattr(library_module, "INDEX_CACHE_AT", 0), now
            ),
        }),
        "library_boot": _component_state(library_ready, detail={
            "cached_chunks": library_chunk_count,
            "libraries_reported": len(library_status or []),
            "cache_age_seconds": _cache_age_seconds(
                getattr(library_module, "LIBRARY_BOOT_AT", 0), now
            ),
        }),
        "text_matrix": _component_state(text_ready, detail={
            "loaded_documents": text_loaded,
            "expected_documents": text_total,
            "cache_age_seconds": _cache_age_seconds(
                getattr(library_module, "TEXT_MATRIX_AT", 0), now
            ),
        }),
        "chunk_cache": _component_state(chunk_count > 0, detail={
            "cached_chunks": chunk_count,
        }),
        "storage": _component_state(r2_ready and d1_ready, detail={
            "r2_binding": r2_ready,
            "d1_binding": d1_ready,
        }),
        "memory_lab": _component_state(
            bool(getattr(memory_lab, "initialized", False))
            if memory_lab is not None else False
        ),
    }

    states = [item["state"] for item in components.values()]
    if all(state == "READY" for state in states):
        overall = "READY"
    elif any(state == "READY" for state in states):
        overall = "DEGRADED"
    else:
        overall = "INITIALIZING"

    return {
        "schema_version": "1.0",
        "status": overall,
        "observed_at_epoch": round(now, 3),
        "components": components,
        "resources": {
            "isolate_memory": {
                "value": None,
                "unit": "bytes",
                "status": "not_exposed",
                "note": "O runtime/app não fornece uma métrica confiável de RSS do isolate.",
            },
            "cache_counts_are_not_memory_bytes": True,
        },
    }
