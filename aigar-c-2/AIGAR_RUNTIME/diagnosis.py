from __future__ import annotations

from .models import SourceTrace

class DiagnosisAdapter:
    """Boundary for the specialized Diagnosis Engine.

    Diagnosis remains a specialized clinical engine. AIGAR orchestrates it;
    it does not absorb its internal logic.
    """

    def evaluate(self, payload: dict) -> tuple[dict, SourceTrace]:
        return {}, SourceTrace(
            kind="diagnosis",
            id="runtime.diagnosis_adapter",
            status="missing",
            detail="Diagnosis Engine exists separately; adapter connection is pending."
        )
