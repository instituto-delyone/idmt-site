from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

LANGUAGE_PATH = Path(__file__).with_name("language.json")

class AIGARLanguage:
    """Interpretador determinístico inicial da Linguagem Materna."""

    def __init__(self, path: Path = LANGUAGE_PATH):
        self.language = json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\\s+", " ", text.strip().lower())

    @staticmethod
    def _has_any(text: str, values: list[str]) -> bool:
        return any(v in text for v in values)

    def interpret(self, raw: str) -> dict[str, Any]:
        text = self._normalize(raw)
        if not text:
            return {"intent":"unknown","scope":None,"depth":"normal","ambiguity":"empty","needs_memory":False,"needs_library":False,"confidence":0.0}

        intent, confidence = "concept_scoped", 0.55
        needs_memory, needs_library = False, True

        if self._has_any(text, self.language["intent"]["phatic"]["examples"]):
            intent, confidence, needs_library = "phatic", 0.98, False
        elif self._has_any(text, ["paciente com","qual a conduta","hipóteses diagnósticas","quais dados faltam","diagnóstico diferencial"]):
            intent, confidence = "clinical_case", 0.92
        elif self._has_any(text, ["continua","fala disso","explica melhor","e depois","como você disse","isso que você falou"]):
            intent, confidence, needs_memory = "continuity", 0.90, True
        elif self._has_any(text, ["não entendi","estou confuso","tenho dúvida"]):
            intent, confidence = "doubt", 0.88
        elif self._has_any(text, ["está errado","ta errado","não é isso","quis dizer","corrigindo"]):
            intent, confidence = "correction", 0.90
        elif self._has_any(text, ["faça","crie","monte","calcule","gere"]):
            intent, confidence = "action", 0.80
        elif self._has_any(text, ["o que é","defina","explique o que é"]):
            intent, confidence = "concept_basic", 0.90

        depth = "normal"
        for level, markers in self.language["depth"].items():
            if self._has_any(text, markers):
                depth = level
                break

        ambiguity = "clear"
        if len(text.split()) <= 2:
            ambiguity = "too_short"
        elif intent == "continuity":
            ambiguity = "context_dependent"

        return {"intent":intent,"scope":text,"depth":depth,"ambiguity":ambiguity,"needs_memory":needs_memory,"needs_library":needs_library,"confidence":confidence}

if __name__ == "__main__":
    import sys
    print(json.dumps(AIGARLanguage().interpret(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2))
