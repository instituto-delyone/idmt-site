"""Translate external runtime requests into canonical sensory input envelopes.

This boundary preserves the exact submitted text and session identifier. It does
not tokenize, normalize, classify, or invoke any downstream cognitive subsystem.
"""
from __future__ import annotations

from CORTEX.thalamus.models import RuntimeRequest, SensoryInput


def capture_request(request: RuntimeRequest) -> SensoryInput:
    """Wrap an API request as a text signal without changing its content."""
    return SensoryInput(
        raw_text=request.input,
        session_id=request.session_id,
        modality="text",
        source="api",
    )
