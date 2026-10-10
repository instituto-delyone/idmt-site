from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

BUILDER_VERSION = "1.0.0"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_text(text: str) -> str:
    text = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_id(source_key: str, source_sha: str, sequence: int,
             start_page: int | None, end_page: int | None,
             text_sha: str) -> str:
    material = "|".join([
        source_key, source_sha, str(sequence),
        str(start_page or ""), str(end_page or ""), text_sha
    ])
    return f"{source_key.upper()}-{hashlib.sha256(material.encode()).hexdigest()[:12].upper()}"


def split_text(text: str, target_chars: int) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for paragraph in paragraphs:
        extra = len(paragraph) + (2 if current else 0)
        if current and size + extra > target_chars:
            chunks.append("\n\n".join(current).strip())
            current, size = [], 0
        current.append(paragraph)
        size += extra
    if current:
        chunks.append("\n\n".join(current).strip())
    return chunks


def pdf_pages(path: Path) -> Iterable[tuple[int, str]]:
    from PyPDF2 import PdfReader
    reader = PdfReader(str(path))
    for number, page in enumerate(reader.pages, start=1):
        yield number, normalize_text(page.extract_text() or "")


def build_pdf(source: Path, cache_dir: Path, source_key: str,
              pages_per_chunk: int):
    source_sha = sha256_bytes(source.read_bytes())
    pages = list(pdf_pages(source))
    entries = []
    for start in range(0, len(pages), pages_per_chunk):
        selected = pages[start:start + pages_per_chunk]
        text = "\n\n".join(t for _, t in selected if t).strip()
        if not text:
            continue
        start_page, end_page = selected[0][0], selected[-1][0]
        text_sha = sha256_bytes(text.encode("utf-8"))
        sequence = len(entries) + 1
        cid = chunk_id(source_key, source_sha, sequence, start_page, end_page, text_sha)
        cache_file = cache_dir / f"{cid}.txt"
        cache_file.write_text(text, encoding="utf-8")
        entries.append({
            "id": cid, "sequence": sequence, "source": source.name,
            "source_key": source_key, "start_page": start_page,
            "end_page": end_page, "text_length": len(text),
            "text_checksum": text_sha,
            "cache_file": str(cache_file.relative_to(cache_dir.parent))
        })
    return entries, source_sha, len(pages)


def build_text(source: Path, cache_dir: Path, source_key: str,
                target_chars: int):
    raw = source.read_bytes()
    source_sha = sha256_bytes(raw)
    pieces = split_text(normalize_text(raw.decode("utf-8", errors="replace")), target_chars)
    entries = []
    for sequence, text in enumerate(pieces, start=1):
        text_sha = sha256_bytes(text.encode("utf-8"))
        cid = chunk_id(source_key, source_sha, sequence, None, None, text_sha)
        cache_file = cache_dir / f"{cid}.txt"
        cache_file.write_text(text, encoding="utf-8")
        entries.append({
            "id": cid, "sequence": sequence, "source": source.name,
            "source_key": source_key, "start_page": None, "end_page": None,
            "text_length": len(text), "text_checksum": text_sha,
            "cache_file": str(cache_file.relative_to(cache_dir.parent))
        })
    return entries, source_sha, len(pieces)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build AIGAR private library cache")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("AIGAR_LIBRARY"))
    parser.add_argument("--key", default=None)
    parser.add_argument("--pages-per-chunk", type=int, default=25)
    parser.add_argument("--chars-per-chunk", type=int, default=24000)
    args = parser.parse_args()

    source = args.source.resolve()
    key = args.key or re.sub(r"[^a-z0-9]+", "_", source.stem.lower()).strip("_")
    cache_root = args.output / "cache" / key
    cache_root.mkdir(parents=True, exist_ok=True)

    if source.suffix.lower() == ".pdf":
        entries, source_sha, units = build_pdf(source, cache_root, key, args.pages_per_chunk)
        unit, size = "pages", args.pages_per_chunk
    elif source.suffix.lower() in {".txt", ".md"}:
        entries, source_sha, units = build_text(source, cache_root, key, args.chars_per_chunk)
        unit, size = "characters", args.chars_per_chunk
    else:
        raise SystemExit(f"Unsupported source type: {source.suffix}")

    index = {
        "schema_version": "1.0", "builder_version": BUILDER_VERSION,
        "source": {"name": source.name, "key": key, "sha256": source_sha,
                   "type": source.suffix.lower().lstrip(".")},
        "chunking": {"unit": unit, "size": size, "preserves_source_text": True,
                     "summarizes": False, "cache_policy": "private_local"},
        "chunks": entries
    }
    args.output.joinpath("indexes").mkdir(parents=True, exist_ok=True)
    args.output.joinpath("public_indexes").mkdir(parents=True, exist_ok=True)
    (args.output / "indexes" / f"{key}.index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    public = {**index, "chunks": [
        {k: v for k, v in e.items() if k != "cache_file"} for e in entries]}
    (args.output / "public_indexes" / f"{key}.index.json").write_text(
        json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8")
    (cache_root / "manifest.json").write_text(json.dumps({
        "schema_version": "1.0", "source_key": key, "source_name": source.name,
        "source_sha256": source_sha, "chunk_count": len(entries),
        "source_units": units, "generated_by": BUILDER_VERSION
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "source": source.name, "source_key": key,
                      "chunks": len(entries), "source_units": units,
                      "cache": str(cache_root)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
