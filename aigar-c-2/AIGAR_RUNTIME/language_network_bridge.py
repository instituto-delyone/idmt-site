from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from .models import ConversationReading

ROOT = Path(__file__).resolve().parents[2]
INTERPRETER_PATH = ROOT / "aigar-c-2" / "AIGAR_LANGUAGE" / "interpreter.py"


def _load_language_class():
    spec = importlib.util.spec_from_file_location(
        "aigar_language_interpreter",
        INTERPRETER_PATH,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load AIGAR language interpreter: {INTERPRETER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.AIGARLanguage


class LanguageNetworkAdapter:
    """Ponte entre a rede computacional de linguagem e o Runtime; analogia funcional, não equivalência com áreas cerebrais específicas."""

    def __init__(self):
        self.engine = _load_language_class()()

    def interpret(self, text: str) -> ConversationReading:
        result: dict[str, Any] = self.engine.interpret(text)
        ambiguity_map = {
            "clear": 0.0,
            "too_short": 0.45,
            "context_dependent": 0.35,
            "empty": 1.0,
        }
        return ConversationReading(
            intent=result["intent"],
            scope=result.get("scope"),
            depth=result.get("depth", "normal"),
            ambiguity=ambiguity_map.get(result.get("ambiguity"), 0.25),
            uncertainty=max(0.0, 1.0 - float(result.get("confidence", 0.0))),
            needs_memory=bool(result.get("needs_memory", False)),
            needs_library=bool(result.get("needs_library", False)),
            needs_diagnosis=bool(result.get("needs_diagnosis", False)),
            needs_reasoning=bool(result.get("needs_reasoning", True)),
            linguistic_analysis=result.get("linguistic_analysis", {}),
        )
