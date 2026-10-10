"""Runtime lifecycle/status reporting for the SARA layer.

This module reports process-level initialization only. It does not probe external
services, claim subsystem readiness, or replace operational health checks.
"""
from __future__ import annotations

from typing import Literal

from ..thalamus.models import BaseModel, Field


RuntimeLifecycle = Literal["initialized", "degraded", "unavailable"]


class RuntimeStatus(BaseModel):
    """Explicit status payload for the runtime lifecycle boundary."""

    ok: bool = True
    runtime: str = "AIGAR"
    version: str = "0.3.0"
    lifecycle: RuntimeLifecycle = "initialized"
    entrypoint: str = "AIGAR_RUNTIME.main:app"
    notes: list[str] = Field(default_factory=list)


def current_runtime_status() -> RuntimeStatus:
    """Return known process metadata without claiming dependency readiness."""
    return RuntimeStatus(
        lifecycle="initialized",
        notes=[
            "Process-level status only; subsystem connectivity has not been validated.",
        ],
    )
