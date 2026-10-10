from __future__ import annotations

from ..thalamus.models import ConversationState

class WorkingStateStore:
    """In-memory working state for the first runtime.

    This is a working-state analogue, not persistent long-term memory. Persistence
    belongs to the memory adapter; this class defines the runtime contract.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationState] = {}

    def get(self, session_id: str) -> ConversationState:
        return self._sessions.setdefault(
            session_id, ConversationState(session_id=session_id)
        )

    def update(self, state: ConversationState, user_input: str, response: str) -> None:
        state.last_user_input = user_input
        state.last_response = response
        state.turns.append({"role": "user", "content": user_input})
        state.turns.append({"role": "assistant", "content": response})
        if len(state.turns) > 40:
            del state.turns[:-40]
