from __future__ import annotations

from pathlib import Path

from AIGAR_LIBRARY.retriever import LibraryRetriever
from .models import SourceTrace


class KnowledgeRetrievalAdapter:
    """Runtime boundary for knowledge retrieval from the local AIGAR library cache."""

    def __init__(self, root: str | Path | None = None):
        self.retriever = LibraryRetriever(root)

    def search(
        self,
        query: str,
        limit: int = 3,
        reading: dict | None = None,
    ) -> tuple[list[dict], SourceTrace]:
        hits = self.retriever.search(query, limit=limit, reading=reading)
        if not hits:
            return [], SourceTrace(
                kind="library",
                id="local.library",
                status="missing",
                detail="Nenhum chunk disponível no cache local para esta consulta."
            )

        context = [{
            "id": h["id"],
            "source": h.get("source"),
            "source_key": h.get("source_key"),
            "sequence": h.get("sequence"),
            "start_page": h.get("start_page"),
            "end_page": h.get("end_page"),
            "score": h.get("score"),
            "lexical_score": h.get("lexical_score"),
            "semantic_score": h.get("semantic_score"),
            "source_relevance": h.get("source_relevance"),
            "text": h["text"],
        } for h in hits]

        return context, SourceTrace(
            kind="library",
            id="local.library",
            status="confirmed",
            detail=f"{len(hits)} chunk(s) recuperado(s) por busca híbrida."
        )

    def load(self, chunk_id: str) -> tuple[dict | None, SourceTrace]:
        hit = self.retriever.load(chunk_id)
        if hit is None:
            return None, SourceTrace(
                kind="library",
                id=chunk_id,
                status="missing",
                detail="Chunk não encontrado no cache local."
            )
        return hit, SourceTrace(
            kind="library",
            id=chunk_id,
            status="confirmed",
            detail="Chunk carregado sob demanda do cache local."
        )
