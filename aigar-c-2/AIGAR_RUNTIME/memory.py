from __future__ import annotations

from typing import Any
from .models import ConversationState, SourceTrace

class MemoryAdapter:
    """Safe placeholder for the historical memory layer.

    It provides recent conversational context now and leaves persistent recall
    to the real Memory Card / recall implementation.
    """

    def recent_context(self, state: ConversationState, limit: int = 8) -> list[dict[str, Any]]:
        return state.turns[-limit:]

    def recall(self, state: ConversationState) -> tuple[list[dict[str, Any]], SourceTrace]:
        return self.recent_context(state), SourceTrace(
            kind="memory",
            id="runtime.recent_context",
            status="inferred",
            detail="Session-local continuity; persistent Memory Card recall not yet wired."
        )
