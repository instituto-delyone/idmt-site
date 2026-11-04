"""Passively report runtime state without triggering boot or network I/O."""
from __future__ import annotations

import time
from typing import Any


def _age(timestamp: Any, now: float) -> float | None:
    try:
        value = float(timestamp or 0)
    except (TypeError, ValueError):
        return None
    return round(max(0.0, now - value), 3) if value > 0 else None


def _component(state: str, **detail: Any) -> dict:
    return {"state": state, "ready": state == "READY", **({"detail": detail} if detail else {})}


def build_runtime_health(env: Any, library_module: Any, memory_lab: Any = None) -> dict:
    """Snapshot in-isolate counters and configuration; never performs I/O."""
    now = time.time()
    index_cache = getattr(library_module, "INDEX_CACHE", None)
    boot_cache = getattr(library_module, "LIBRARY_BOOT_CACHE", None)
    boot_status = getattr(library_module, "LIBRARY_BOOT_STATUS", None)
    matrix_cache = getattr(library_module, "TEXT_MATRIX_CACHE", None)
    chunk_cache = getattr(library_module, "CHUNK_CACHE", None)

    index_count = len(index_cache) if isinstance(index_cache, (list, tuple, dict)) else 0
    boot_chunks = len(boot_cache) if isinstance(boot_cache, dict) else 0
    matrix_loaded = len(matrix_cache) if isinstance(matrix_cache, (list, tuple, dict)) else 0
    matrix_expected = len(getattr(library_module, "TEXT_MATRIX_FILES", []) or [])
    chunk_count = len(chunk_cache) if isinstance(chunk_cache, dict) else 0

    statuses = boot_status if isinstance(boot_status, list) else []
    boot_all_ready = bool(statuses) and all(
        isinstance(item, dict) and item.get("status") == "ready" for item in statuses
    )
    boot_ready = boot_all_ready and boot_chunks > 0
    matrix_ready = matrix_expected > 0 and matrix_loaded == matrix_expected

    # MemoryLab's actual public contract is status["ready"], not an invented
    # .initialized attribute. This remains a passive read of current state.
    memory_status = getattr(memory_lab, "status", None) if memory_lab is not None else None
    memory_ready = isinstance(memory_status, dict) and memory_status.get("ready") is True

    try:
        from cloudflare_bindings import binding
        r2_present = binding(env, "AIGAR_LIBRARY_BUCKET") is not None
        d1_present = binding(env, "AIGAR_DB") is not None
    except Exception:
        r2_present = d1_present = False

    components = {
        "worker": _component("READY", request_state="REQUEST_HANDLED"),
        "library_indexes": _component(
            "READY" if index_count else "NOT_INITIALIZED",
            cached_indexes=index_count,
            cache_age_seconds=_age(getattr(library_module, "INDEX_CACHE_AT", 0), now),
        ),
        "library_boot": _component(
            "READY" if boot_ready else "PARTIAL" if boot_chunks else "NOT_INITIALIZED",
            cached_chunks=boot_chunks,
            libraries_reported=len(statuses),
            libraries_ready=sum(1 for x in statuses if isinstance(x, dict) and x.get("status") == "ready"),
            cache_age_seconds=_age(getattr(library_module, "LIBRARY_BOOT_AT", 0), now),
        ),
        "text_matrix": _component(
            "READY" if matrix_ready else "PARTIAL" if matrix_loaded else "NOT_INITIALIZED",
            loaded_documents=matrix_loaded,
            expected_documents=matrix_expected,
            cache_age_seconds=_age(getattr(library_module, "TEXT_MATRIX_AT", 0), now),
        ),
        "chunk_cache": _component("READY" if chunk_count else "EMPTY", cached_chunks=chunk_count),
        # Binding presence proves configuration only. It is not an R2/D1 I/O test.
        "storage": _component(
            "CONFIGURED" if r2_present and d1_present else "PARTIAL" if r2_present or d1_present else "NOT_CONFIGURED",
            r2_binding_present=r2_present,
            d1_binding_present=d1_present,
            io_verified=False,
        ),
        "memory_lab": _component("READY" if memory_ready else "NOT_INITIALIZED"),
    }

    required = ("worker", "library_indexes", "library_boot", "text_matrix", "memory_lab")
    if all(components[name]["ready"] for name in required):
        overall = "READY"
    elif any(components[name]["ready"] for name in required):
        overall = "DEGRADED"
    else:
        overall = "INITIALIZING"

    return {
        "schema_version": "1.1",
        "status": overall,
        "observed_at_epoch": round(now, 3),
        "components": components,
        "resources": {
            "isolate_memory": {
                "value": None,
                "unit": "bytes",
                "status": "not_exposed",
                "note": "O runtime Python Workers não expõe RSS confiável por esta aplicação.",
            },
            "cache_counts_are_not_memory_bytes": True,
        },
    }
