from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from PyPDF2 import PdfReader

def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def clean(text: str) -> str:
    text = text.replace("\\x00", " ")
    text = re.sub(r"[ \\t]+", " ", text)
    text = re.sub(r"\\n{3,}", "\\n\\n", text)
    return text.strip()

def pdf_chunks(path: Path, pages: int):
    reader = PdfReader(str(path))
    total = len(reader.pages)
    for start in range(0, total, pages):
        end = min(start + pages, total)
        parts = [(reader.pages[i].extract_text() or "") for i in range(start, end)]
        yield start + 1, end, clean("\\n\\n".join(parts))

def text_chunks(path: Path, chars: int):
    text = clean(path.read_text(encoding="utf-8", errors="replace"))
    paragraphs = re.split(r"\\n\\s*\\n", text)
    current, size = [], 0
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        if current and size + len(paragraph) > chars:
            yield None, None, clean("\\n\\n".join(current))
            current, size = [], 0
        current.append(paragraph.strip())
        size += len(paragraph)
    if current:
        yield None, None, clean("\\n\\n".join(current))

def main():
    parser = argparse.ArgumentParser(description="AIGAR Library Builder")
    parser.add_argument("--input", required=True)
    parser.add_argument("--library", required=True)
    parser.add_argument("--output", default="AIGAR_LIBRARY")
    parser.add_argument("--pages", type=int, default=25)
    parser.add_argument("--chars", type=int, default=24000)
    args = parser.parse_args()

    source = Path(args.input).expanduser().resolve()
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", args.library).strip("_")
    root = Path(args.output) / safe_name
    chunks_dir, cache_dir = root / "chunks", root / "cache"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    raw = source.read_bytes()
    digest = checksum(raw)
    suffix = source.suffix.lower()

    if suffix == ".pdf":
        iterator = pdf_chunks(source, args.pages)
    elif suffix in {".txt", ".md"}:
        iterator = text_chunks(source, args.chars)
    else:
        raise SystemExit("Formato suportado: PDF, TXT ou MD.")

    index = []
    for number, (start, end, text) in enumerate(iterator, start=1):
        if not text:
            continue
        chunk_id = f"{safe_name}_chunk_{number:04d}"
        out = chunks_dir / f"chunk_{number:04d}.md"
        header = [f"# {chunk_id}", "", f"**Biblioteca:** {args.library}", f"**Fonte:** {source.name}"]
        if start is not None:
            header.append(f"**Páginas:** {start}-{end}")
        header += [f"**Checksum fonte:** {digest[:16]}", "", "---", ""]
        out.write_text("\\n".join(header) + text + "\\n", encoding="utf-8")

        index.append({
            "id": chunk_id,
            "file": str(out.relative_to(root)).replace("\\\\", "/"),
            "source": source.name,
            "start_page": start,
            "end_page": end,
            "text_length": len(text),
            "checksum": digest
        })

    (root / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps({
        "library": args.library,
        "source": source.name,
        "source_checksum": digest,
        "chunk_count": len(index),
        "builder": "AIGAR_LIBRARY_BUILDER",
        "default_pdf_pages": args.pages,
        "default_text_chars": args.chars
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(index)} chunks -> {root}")

if __name__ == "__main__":
    main()
