from __future__ import annotations

from .models import SourceTrace

class LibraryAdapter:
    """Document retrieval boundary.

    No fake retrieval is performed. The adapter is intentionally empty until
    the existing Biblioteca/Library Router is wired into the runtime.
    """

    def search(self, query: str, limit: int = 3) -> tuple[list[dict], SourceTrace]:
        return [], SourceTrace(
            kind="library",
            id="runtime.library_adapter",
            status="missing",
            detail="Historical library exists; runtime adapter is not connected yet."
        )
