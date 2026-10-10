from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .semantic_retriever import SemanticRouter

STOPWORDS = {
    "a","o","e","de","do","da","dos","das","um","uma","uns","umas","em","no","na",
    "nos","nas","por","para","com","que","como","qual","quais","é","foi","ser","se",
    "ao","à","às","os","as","mais","sobre","isso","esse","essa","este","esta","ou"
}


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-zA-ZÀ-ÿ0-9_]{2,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


class LibraryRetriever:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root or os.getenv(
            "AIGAR_KNOWLEDGE_RETRIEVAL_ROOT",
            Path(__file__).resolve().parent
        ))
        self.index_dir = self.root / "indexes"
        self.semantic = SemanticRouter()

    def _indexes(self) -> list[Path]:
        return sorted(self.index_dir.glob("*.index.json"))

    def _load(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _cache_path(self, entry: dict[str, Any]) -> Path:
        if entry.get("cache_file"):
            candidate = self.root / entry["cache_file"]
            if candidate.exists():
                return candidate
        return self.root / "cache" / entry["source_key"] / f'{entry["id"]}.txt'

    def search(
        self,
        query: str,
        limit: int = 5,
        reading: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        q = tokens(query)
        semantic_q = self.semantic.expand(query, reading)
        if not q and not semantic_q:
            return []

        hits = []
        source_scores = self.semantic.source_scores(query, reading)
        for path in self._indexes():
            index = self._load(path)
            for entry in index.get("chunks", []):
                cache = self._cache_path(entry)
                if not cache.exists():
                    continue
                text = cache.read_text(encoding="utf-8", errors="replace")
                body = tokens(text)
                semantic_body = self.semantic.expand(text)
                lexical_overlap = q & body
                semantic_overlap = semantic_q & semantic_body
                lexical_score = len(lexical_overlap) / max(1, len(q))
                semantic_score = len(semantic_overlap) / max(1, len(semantic_q))
                source_score = source_scores.get(entry.get("source_key", ""), 0.0)
                if not lexical_overlap and not semantic_overlap and source_score == 0:
                    continue

                # Hybrid ranking: literal evidence remains important, while
                # semantic expansion and source relevance break lexical ties.
                score = (
                    0.45 * lexical_score
                    + 0.40 * semantic_score
                    + 0.15 * source_score
                )
                hits.append({
                    **entry,
                    "score": round(min(1.0, score), 6),
                    "lexical_score": round(lexical_score, 6),
                    "semantic_score": round(semantic_score, 6),
                    "source_relevance": round(source_score, 6),
                    "text": text,
                })

        hits.sort(key=lambda x: (
            -x["score"],
            -x.get("semantic_score", 0),
            -x.get("lexical_score", 0),
            x.get("source_key", ""),
            x.get("sequence", 0),
        ))
        return hits[:limit]

    def load(self, chunk_id: str) -> dict[str, Any] | None:
        for path in self._indexes():
            index = self._load(path)
            for entry in index.get("chunks", []):
                if entry.get("id") != chunk_id:
                    continue
                cache = self._cache_path(entry)
                if not cache.exists():
                    return None
                return {
                    **entry,
                    "text": cache.read_text(encoding="utf-8", errors="replace")
                }
        return None

    def reconstruct(self, chunk_ids: list[str]) -> list[dict[str, Any]]:
        items = [self.load(cid) for cid in chunk_ids]
        return sorted(
            [x for x in items if x],
            key=lambda x: (x.get("source_key",""), x.get("sequence",0))
        )
