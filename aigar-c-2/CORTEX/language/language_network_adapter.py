from __future__ import annotations

from typing import Any

from ..thalamus.models import ConversationReading
from .interpreter import AIGARLanguage


class LanguageNetworkAdapter:
    """Ponte entre a rede computacional de linguagem e o Runtime; analogia funcional, não equivalência com áreas cerebrais específicas."""

    def __init__(self) -> None:
        self.engine = AIGARLanguage()


    def interpret(self, text: str) -> ConversationReading:
        result: dict[str, Any] = self.engine.interpret(text)
        ambiguity_map = {
            "clear": 0.0, "too_short": 0.45,
            "context_dependent": 0.35, "empty": 1.0,
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
