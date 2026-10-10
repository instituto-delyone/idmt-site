from __future__ import annotations

from typing import Any

from ..thalamus.models import (
    ConversationState,
    MemoryRecallRequest,
    MemoryRecallResult,
    SourceTrace,
)


class HippocampalMemoryAdapter:
    """Functional hippocampal-memory analogy for the historical memory layer.

    This adapter provides session-local context only and leaves persistent recall
    to the real Memory Card / recall implementation. It is not a literal hippocampus model.
    """

    def recent_context(self, state: ConversationState, limit: int = 8) -> list[dict[str, Any]]:
        if limit <= 0:
            return []
        return state.turns[-limit:]

    def recall(self, request: MemoryRecallRequest) -> MemoryRecallResult:
        state = request.state
        items = self.recent_context(state, request.limit)
        return MemoryRecallResult(
            items=items,
            source=SourceTrace(
                kind="memory",
                id="runtime.recent_context",
                status="inferred",
                detail="Session-local continuity; persistent Memory Card recall not yet wired.",
            ),
        )
