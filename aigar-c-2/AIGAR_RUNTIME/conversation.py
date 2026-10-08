from __future__ import annotations

from .models import ConversationState

class ConversationStore:
    """In-memory state for the first runtime.

    Persistence belongs to the future memory adapter; this class only defines
    the runtime contract and makes session continuity explicit.
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
