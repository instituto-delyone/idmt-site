"""Public Memory Card retrieval for the Cloudflare Worker.

Cards are opt-in by manifest entry and explicit visibility. Historical/private
cards are never made public by directory discovery. YAML is treated as inert
text: no object constructors, tags, or arbitrary deserialization are executed.
"""
from __future__ import annotations

import hashlib
import json
import re

REPOSITORY = "instituto-delyone/idmt-site"
MANIFEST_PATH = "aigar-c-2/CORTEX/memory/public_memory_manifest.json"
MANIFEST_URL = (
    "https://raw.githubusercontent.com/" + REPOSITORY + "/main/" + MANIFEST_PATH
)
MAX_CARD_BYTES = 60000
MAX_RESULTS = 4
TOKEN_RE = re.compile(r"[a-zA-ZÀ-ÿ0-9_]{3,}", re.UNICODE)


def _tokens(value):
    return {item.casefold() for item in TOKEN_RE.findall(str(value or ""))}


def _safe_card_path(path):
    value = str(path or "").replace("\\", "/").strip("/")
    if not value or value.startswith("/") or ".." in value.split("/"):
        return None
    # Public cards must be copied/reviewed into a dedicated export folder.
    # The adapter must never read historical project or user-memory directories.
    if not value.startswith("aigar-c-2/public_memory_cards/"):
        return None
    if not value.lower().endswith((".yaml", ".yml", ".md", ".txt")):
        return None
    return value


def _extract_scalar(content, key):
    match = re.search(
        r"(?m)^\s*" + re.escape(key) + r"\s*:\s*['\"]?([^'\"#\r\n]+)",
        content or "",
    )
    return match.group(1).strip() if match else None


class MemoryCardAdapter:
    """Retrieves only explicitly public cards using stable IDs and versions."""

    def __init__(self, fetcher=None, manifest=None):
        self.fetcher = fetcher or self._worker_fetch
        self.manifest = manifest
        self._manifest_cache = None
        self._card_cache = {}

    async def _worker_fetch(self, url, options=None):
        from workers import fetch
        options = options or {}
        return await fetch(
            url,
            method=options.get("method", "GET"),
            headers=options.get("headers") or {},
        )

    async def _load_manifest(self):
        if isinstance(self.manifest, dict):
            return self.manifest
        if self._manifest_cache is not None:
            return self._manifest_cache
        response = await self.fetcher(MANIFEST_URL, {"method": "GET"})
        if response.status >= 400:
            raise RuntimeError("public_memory_manifest_unavailable")
        payload = json.loads(await response.text())
        if not isinstance(payload, dict) or payload.get("schema_version") != "1.0":
            raise ValueError("public_memory_manifest_invalid")
        self._manifest_cache = payload
        return payload

    async def retrieve(self, query, limit=MAX_RESULTS):
        try:
            manifest = await self._load_manifest()
        except Exception as exc:
            return {
                "ok": False, "status": "unavailable", "documents": [],
                "error": str(exc)[:180], "manifest_id": None,
            }

        entries = manifest.get("cards", [])
        if not isinstance(entries, list):
            return {
                "ok": False, "status": "invalid_manifest", "documents": [],
                "error": "cards_must_be_a_list",
                "manifest_id": manifest.get("manifest_id"),
            }

        query_tokens = _tokens(query)
        candidates = []
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("visibility") != "public":
                continue
            if entry.get("status", "active") != "active":
                continue
            card_id = str(entry.get("id") or "").strip()
            version = str(entry.get("version") or "").strip()
            path = _safe_card_path(entry.get("path"))
            if not card_id or not version or not path:
                continue
            try:
                url = "https://raw.githubusercontent.com/" + REPOSITORY + "/main/" + path
                cache_key = (card_id, version, path)
                content = self._card_cache.get(cache_key)
                if content is None:
                    response = await self.fetcher(url, {"method": "GET"})
                    if response.status >= 400:
                        continue
                    content = await response.text()
                    if content:
                        self._card_cache[cache_key] = content
                if not content or len(content.encode("utf-8")) > MAX_CARD_BYTES:
                    continue
                # If the card declares an ID/version, it must agree with the manifest.
                declared_id = _extract_scalar(content, "id")
                declared_version = _extract_scalar(content, "version") or _extract_scalar(content, "versao")
                if declared_id and declared_id != card_id:
                    continue
                if declared_version and declared_version != version:
                    continue
                expected_hash = str(entry.get("sha256") or "").lower().strip()
                actual_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                if expected_hash and actual_hash != expected_hash:
                    self._card_cache.pop(cache_key, None)
                    continue
                body_tokens = _tokens(content)
                overlap = len(query_tokens & body_tokens)
                score = overlap / max(1, len(query_tokens))
                if score <= 0:
                    continue
                candidates.append({
                    "text": content[:12000],
                    "source": path.rsplit("/", 1)[-1],
                    "source_key": "public_memory_card",
                    "memory_card_id": card_id,
                    "memory_card_version": version,
                    "memory_path": path,
                    "sha256": actual_hash,
                    "score": round(score, 6),
                    "visibility": "public",
                })
            except Exception:
                # One corrupt/unavailable card must not block the conversation.
                continue

        candidates.sort(key=lambda item: (-item["score"], item["memory_card_id"]))
        selected = candidates[:max(1, min(MAX_RESULTS, int(limit or MAX_RESULTS)))]
        return {
            "ok": True,
            "status": "ready" if selected else ("empty" if not entries else "no_match"),
            "documents": selected,
            "manifest_id": manifest.get("manifest_id"),
            "cards_considered": len(entries),
        }


MEMORY_CARD_ADAPTER = MemoryCardAdapter()
