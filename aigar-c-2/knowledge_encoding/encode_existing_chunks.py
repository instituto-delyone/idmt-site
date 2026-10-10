from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Index existing TXT/MD chunks into a private cache")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, default=Path("knowledge_retrieval"))
    parser.add_argument("--key", default=None)
    args = parser.parse_args()

    source_dir = args.directory.resolve()
    key = args.key or re.sub(r"[^a-z0-9]+", "_", source_dir.name.lower()).strip("_")
    cache = args.output / "cache" / key
    cache.mkdir(parents=True, exist_ok=True)
    entries = []

    for sequence, path in enumerate(sorted(source_dir.rglob("*")), start=1):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        checksum = hashlib.sha256(text.encode()).hexdigest()
        cid = f"{key.upper()}-{hashlib.sha256((key+'|'+path.name+'|'+checksum).encode()).hexdigest()[:12].upper()}"
        target = cache / f"{cid}.txt"
        target.write_text(text, encoding="utf-8")
        entries.append({"id":cid,"sequence":sequence,"source":path.name,"source_key":key,
                        "text_length":len(text),"text_checksum":checksum})

    args.output.joinpath("indexes").mkdir(parents=True, exist_ok=True)
    args.output.joinpath("public_indexes").mkdir(parents=True, exist_ok=True)
    index={"schema_version":"1.0","source":{"key":key,"type":"existing_chunks"},
           "chunking":{"cache_policy":"private_local","summarizes":False},"chunks":entries}
    (args.output/"indexes"/f"{key}.index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
    (args.output/"public_indexes"/f"{key}.index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Indexed {len(entries)} chunks into {cache}")


if __name__ == "__main__":
    main()
