from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

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
            "AIGAR_LIBRARY_ROOT",
            Path(__file__).resolve().parent
        ))
        self.index_dir = self.root / "indexes"

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

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        q = tokens(query)
        if not q:
            return []
        hits = []
        for path in self._indexes():
            index = self._load(path)
            for entry in index.get("chunks", []):
                cache = self._cache_path(entry)
                if not cache.exists():
                    continue
                text = cache.read_text(encoding="utf-8", errors="replace")
                overlap = q & tokens(text)
                if not overlap:
                    continue
                score = len(overlap) / max(1, len(q))
                hits.append({**entry, "score": round(score, 6), "text": text})
        hits.sort(key=lambda x: (-x["score"], x.get("source_key",""), x.get("sequence",0)))
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
