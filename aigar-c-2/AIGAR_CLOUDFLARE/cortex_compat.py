"""Compatibility boundary between the Cloudflare Worker and canonical CORTEX contracts.

The Worker package is deployed independently from the local Python runtime, so it
must not import sibling CORTEX modules at runtime. This bridge mirrors the shared
contract at the boundary and keeps the Worker-native implementation executable.
"""
from __future__ import annotations

from typing import Any

CONTRACT_NAME = "CORTEX.thalamus.models"
CONTRACT_VERSION = "1"
PUBLIC_CONVERSATION_POLICY = {
    "conversation_access": "public",
    "identity_verification_required": False,
    "activation_phrase_required": False,
    "designated_email_required": False,
    "admin_access_granted_by_conversation": False,
}
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
    "access_policy": dict(PUBLIC_CONVERSATION_POLICY),
    "implemented_capabilities": ["public_memory_card_adapter_allowlisted"],
    "deferred_capabilities": [
        "persistent_cross_instance_conversation_memory",
        "diagnosis_engine_execution",
        "additional_workers",
        "audio_visual_input",
        "default_mode_network",
    ],
}


def _bounded_number(value: Any, default: float) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def normalize_reading(reading: Any) -> dict[str, Any]:
    """Normalize Worker interpretation to the shared ConversationReading vocabulary.

    Known fields are validated, while extra annotations are preserved so the
    compatibility boundary does not discard cognitive-core or language details.
    """
    result = dict(reading) if isinstance(reading, dict) else {}

    intent = str(result.get("intent") or "unknown").strip()
    result["intent"] = intent if intent in ALLOWED_INTENTS else "unknown"

    depth = str(result.get("depth") or "normal").strip()
    result["depth"] = depth if depth in ALLOWED_DEPTHS else "normal"

    # These fields exist in the canonical CORTEX contract. Keep them explicit
    # even when an older Worker language rule does not emit them.
    result["scope"] = result.get("scope")
    result["ambiguity"] = _bounded_number(result.get("ambiguity"), 0.0)
    result["needs_memory"] = bool(result.get("needs_memory")) or result["intent"] == "continuity"
    result["needs_library"] = bool(result.get("needs_library"))
    result["needs_diagnosis"] = bool(result.get("needs_diagnosis"))
    result["needs_reasoning"] = bool(result.get("needs_reasoning", True))

    analysis = result.get("linguistic_analysis")
    result["linguistic_analysis"] = analysis if isinstance(analysis, dict) else {}

    confidence = _bounded_number(result.get("confidence"), 0.45)
    result["confidence"] = confidence
    result["uncertainty"] = _bounded_number(
        result.get("uncertainty", 1.0 - confidence), 1.0 - confidence
    )
    return result


def build_routing_decision(
    reading: dict[str, Any], profile: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Select optional resources; selection is not proof of subsystem execution."""
    profile = profile if isinstance(profile, dict) else {}
    use_diagnosis = bool(reading.get("needs_diagnosis"))
    return {
        "use_memory": bool(
            reading.get("needs_memory")
            or reading.get("intent") == "continuity"
            or profile.get("context_required")
            or profile.get("primary_type") == "meta_interaction"
        ),
        "use_library": bool(
            reading.get("needs_library") or profile.get("research_required")
        ),
        "use_diagnosis": use_diagnosis,
        "use_reasoning": bool(reading.get("needs_reasoning", True)),
        "diagnosis_execution": "not_connected" if use_diagnosis else "not_requested",
        "conversation_access": "public",
        "identity_verification_required": False,
        "activation_phrase_required": False,
        "admin_authorization": "separate_authenticated_admin_routes",
    }


class WorkerCortexBridge:
    """Single entry point for Worker -> shared CORTEX reading/routing contracts."""

    def interpret_contract(
        self, worker_reading: Any, profile: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        reading = normalize_reading(worker_reading)
        routing = build_routing_decision(reading, profile)
        return {
            "reading": reading,
            "routing_decision": routing,
            "compatibility": {
                **CORTEX_COMPATIBILITY,
                "routing_decision": dict(routing),
            },
        }


WORKER_CORTEX_BRIDGE = WorkerCortexBridge()
