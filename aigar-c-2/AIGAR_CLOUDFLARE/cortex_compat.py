"""Compatibility boundary between the Cloudflare Worker and CORTEX contracts.

This module intentionally has no imports from the sibling local CORTEX package.
Cloudflare packages this Worker from its own directory, and local CORTEX modules
have separate runtime/resource dependencies. The adapter keeps the Worker
operational while making shared intent/routing semantics explicit.
"""
from __future__ import annotations

from typing import Any

CONTRACT_NAME = "CORTEX.thalamus.models"
CONTRACT_VERSION = "1"
ALLOWED_INTENTS = {
    "phatic", "concept_basic", "concept_scoped", "clinical_case",
    "action", "correction", "continuity", "doubt", "unknown",
}
ALLOWED_DEPTHS = {"brief", "simple", "normal", "technical", "deep"}

CORTEX_COMPATIBILITY = {
    "contract": CONTRACT_NAME,
    "contract_version": CONTRACT_VERSION,
    "mode": "worker_native_adapter",
    "local_cortex_imported": False,
    "deferred_capabilities": [
        "persistent_memory_cards",
        "diagnosis_engine_execution",
        "additional_workers",
        "audio_visual_input",
        "default_mode_network",
    ],
}


def normalize_reading(reading: Any) -> dict[str, Any]:
    """Normalize a Worker-native reading to the shared CORTEX field vocabulary.

    Unknown enum values degrade to safe defaults; additional Worker fields are
    preserved so this boundary does not discard cognitive-core annotations.
    """
    result = dict(reading) if isinstance(reading, dict) else {}

    intent = str(result.get("intent") or "unknown").strip()
    result["intent"] = intent if intent in ALLOWED_INTENTS else "unknown"

    depth = str(result.get("depth") or "normal").strip()
    result["depth"] = depth if depth in ALLOWED_DEPTHS else "normal"

    result["needs_memory"] = bool(result.get("needs_memory")) or result["intent"] == "continuity"
    result["needs_library"] = bool(result.get("needs_library"))
    result["needs_diagnosis"] = bool(result.get("needs_diagnosis"))
    result["needs_reasoning"] = bool(result.get("needs_reasoning", True))

    analysis = result.get("linguistic_analysis")
    result["linguistic_analysis"] = analysis if isinstance(analysis, dict) else {}

    if "uncertainty" not in result:
        try:
            confidence = float(result.get("confidence", 0.45))
            result["uncertainty"] = max(0.0, min(1.0, 1.0 - confidence))
        except (TypeError, ValueError):
            result["uncertainty"] = 0.55
    else:
        try:
            result["uncertainty"] = max(0.0, min(1.0, float(result["uncertainty"])))
        except (TypeError, ValueError):
            result["uncertainty"] = 0.55

    return result


def build_routing_decision(
    reading: dict[str, Any], profile: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Return the CORTEX-style resource-selection contract.

    Selection is not execution: a true use_diagnosis flag does not mean the
    separate Diagnosis engine is connected to this Worker.
    """
    profile = profile if isinstance(profile, dict) else {}
    use_diagnosis = bool(reading.get("needs_diagnosis"))
    return {
        "use_memory": bool(
            reading.get("needs_memory")
            or reading.get("intent") == "continuity"
            or profile.get("context_required")
        ),
        "use_library": bool(
            reading.get("needs_library") or profile.get("research_required")
        ),
        "use_diagnosis": use_diagnosis,
        "use_reasoning": bool(reading.get("needs_reasoning", True)),
        "diagnosis_execution": "not_connected" if use_diagnosis else "not_requested",
    }

