"""Context-sensitive dispatch for the AIGAR-C runtime.

The router converts the language layer’s structured reading into an explicit
resource-selection contract. Execution and error handling remain the runtime
orchestrator’s responsibility.
"""
from __future__ import annotations

from .models import ConversationReading, RoutingDecision


def route_reading(reading: ConversationReading) -> RoutingDecision:
    """Select optional subsystems without executing them.

    The continuity intent explicitly requests memory even if a language adapter
    omitted the flag. Reasoning remains enabled by default to preserve the current
    runtime pipeline; the field is still represented explicitly for future policy.
    """
    return RoutingDecision(
        use_memory=reading.needs_memory or reading.intent == "continuity",
        use_library=reading.needs_library,
        use_diagnosis=reading.needs_diagnosis,
        use_reasoning=reading.needs_reasoning,
    )
