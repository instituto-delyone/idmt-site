from __future__ import annotations

from .models import SourceTrace

class ReasoningEngine:
    """Small deterministic planning layer.

    This is not intended to replace the existing raciocínio_rapido_hibrido;
    it establishes the runtime boundary around reasoning.
    """

    def plan(self, input_text: str, reading: dict, memory: list, library: list, diagnosis: dict) -> tuple[dict, SourceTrace]:
        plan = {
            "understand_before_answer": True,
            "intent": reading.get("intent"),
            "depth": reading.get("depth"),
            "use_memory": reading.get("needs_memory", False),
            "use_library": bool(library) or reading.get("needs_library", False),
            "use_diagnosis": bool(diagnosis) or reading.get("needs_diagnosis", False),
            "steps": [
                "interpret",
                "gather_available_context",
                "reason",
                "plan_response",
            ],
        }
        return plan, SourceTrace(
            kind="reasoning",
            id="runtime.reasoning",
            status="inferred",
            detail="Runtime boundary around the historical hybrid reasoning principles."
        )
