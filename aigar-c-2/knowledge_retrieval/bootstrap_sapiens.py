from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "biblioteca" / "Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf"


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Fonte não encontrada: {SOURCE}")
    subprocess.run([
        sys.executable, "-m", "knowledge_consolidation.build",
        str(SOURCE), "--key", "sapiens", "--pages-per-chunk", "25"
    ], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
