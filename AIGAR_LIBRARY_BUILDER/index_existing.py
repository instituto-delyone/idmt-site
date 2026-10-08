from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Index existing AIGAR chunks")
    parser.add_argument("--library", required=True)
    parser.add_argument("--output", default="index.json")
    args = parser.parse_args()
    root = Path(args.library)
    files = sorted(p for p in root.rglob("*") if p.suffix.lower() in {".md",".txt"})
    entries = []
    for path in files:
        data = path.read_bytes()
        entries.append({
            "id": path.stem,
            "file": str(path.relative_to(root)).replace("\\\\","/"),
            "text_length": len(data.decode("utf-8", errors="replace")),
            "checksum": hashlib.sha256(data).hexdigest()
        })
    Path(args.output).write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Indexed {len(entries)} existing chunks.")

if __name__ == "__main__":
    main()
