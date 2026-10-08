from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

LANGUAGE_PATH = Path(__file__).with_name("language.json")


class AIGARLanguage:
    """Interpretador determinístico da Linguagem Materna compilada."""

    def __init__(self, path: Path = LANGUAGE_PATH):
        self.language = json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    @staticmethod
    def _has_any(text: str, values: list[str]) -> bool:
        return any(value in text for value in values)

    def interpret(self, raw: str) -> dict[str, Any]:
        text = self._normalize(raw)

        if not text:
            return {
                "intent": "unknown",
                "scope": None,
                "depth": "normal",
                "ambiguity": "empty",
                "needs_memory": False,
                "needs_library": False,
                "needs_diagnosis": False,
                "needs_reasoning": False,
                "confidence": 0.0,
            }

        phatic = self.language["intent"]["phatic"]["examples"]
        clinical = self.language["intent"]["clinical_case"]["examples"]
        continuity = self.language["intent"]["continuity"]["examples"]
        correction = self.language["intent"]["correction"]["examples"]
        doubt = self.language["intent"]["doubt"]["examples"]
        action = self.language["intent"]["action"]["examples"]
        concept_basic = self.language["intent"]["concept_basic"]["examples"]
        concept_scoped = self.language["intent"]["concept_scoped"]["examples"]

        if self._has_any(text, phatic):
            intent, confidence = "phatic", 0.98
        elif self._has_any(text, clinical):
            intent, confidence = "clinical_case", 0.92
        elif self._has_any(text, continuity):
            intent, confidence = "continuity", 0.90
        elif self._has_any(text, correction):
            intent, confidence = "correction", 0.90
        elif self._has_any(text, doubt):
            intent, confidence = "doubt", 0.88
        elif self._has_any(text, action):
            intent, confidence = "action", 0.80
        elif self._has_any(text, concept_basic) or self._has_any(
            text,
            ["o que foi", "o que são", "o que sao", "qual foi", "quem", "quando", "onde"],
        ):
            intent, confidence = "concept_basic", 0.90
        elif self._has_any(text, concept_scoped) or text.endswith("?"):
            intent, confidence = "concept_scoped", 0.82
        else:
            intent, confidence = "unknown", 0.45

        depth = "normal"
        for level, markers in self.language["depth"].items():
            if self._has_any(text, markers):
                depth = level
                break

        if len(text.split()) <= 2:
            ambiguity = "too_short"
        elif intent == "continuity":
            ambiguity = "context_dependent"
        else:
            ambiguity = "clear"

        needs_memory = intent in {"continuity", "unknown", "doubt"}
        needs_library = intent in {
            "concept_basic", "concept_scoped", "clinical_case"
        }
        needs_diagnosis = intent == "clinical_case"
        needs_reasoning = intent not in {"phatic"}

        return {
            "intent": intent,
            "scope": text,
            "depth": depth,
            "ambiguity": ambiguity,
            "needs_memory": needs_memory,
            "needs_library": needs_library,
            "needs_diagnosis": needs_diagnosis,
            "needs_reasoning": needs_reasoning,
            "confidence": confidence,
        }


if __name__ == "__main__":
    import sys

    print(
        json.dumps(
            AIGARLanguage().interpret(" ".join(sys.argv[1:])),
            ensure_ascii=False,
            indent=2,
        )
    )
