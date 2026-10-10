from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).parent
LANGUAGE_PATH = BASE_DIR / "language.json"
PORTUGUESE_KNOWLEDGE_PATH = BASE_DIR / "portuguese_language_knowledge.json"


class AIGARLanguage:
    """Interpretador determinístico da Linguagem Materna + conhecimento linguístico."""

    def __init__(
        self,
        path: Path = LANGUAGE_PATH,
        portuguese_knowledge_path: Path = PORTUGUESE_KNOWLEDGE_PATH,
    ):
        self.language = json.loads(path.read_text(encoding="utf-8"))
        self.portuguese = json.loads(
            portuguese_knowledge_path.read_text(encoding="utf-8")
        )

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.strip().lower()
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"[\wÀ-ÿ]+(?:[-'][\wÀ-ÿ]+)?", text.lower(), flags=re.UNICODE)

    @staticmethod
    def _has_any(text: str, values: list[str]) -> bool:
        """Match whole words for single-token cues; avoid 'oi' matching inside 'foi'."""
        for value in values:
            cue = value.strip().lower()
            if not cue:
                continue
            if " " in cue:
                if cue in text:
                    return True
            elif re.search(rf"(?<!\\w){re.escape(cue)}(?!\\w)", text, flags=re.UNICODE):
                return True
        return False

    @staticmethod
    def _has_word(text: str, value: str) -> bool:
        return re.search(rf"\b{re.escape(value)}\b", text) is not None

    def _find_verbs(self, tokens: list[str]) -> list[str]:
        """Heurística leve: identifica verbos frequentes sem fingir ser um parser completo."""
        verb_lexicon = {
            "é", "são", "foi", "foram", "ser", "sendo", "era", "eram",
            "está", "estão", "estava", "estavam", "ficou", "ficaram",
            "tem", "têm", "teve", "tiveram", "ter",
            "faz", "fazem", "fez", "fizeram", "fazer",
            "pode", "podem", "podia", "podiam", "poder",
            "deve", "devem", "deveria", "deveriam", "dever",
            "vai", "vão", "foi", "aconteceu", "acontecer",
            "chegou", "chegaram", "chegar", "explica", "explicar",
            "explique", "defina", "define", "significa", "significar",
            "funciona", "funcionar", "serve", "servir",
            "quer", "querem", "quero", "precisa", "precisam",
            "crie", "criar", "faça", "fazer", "monte", "montar",
            "calcule", "calcular", "gere", "gerar",
            "compare", "comparar", "analise", "analisar",
            "responda", "responder", "continue", "continua",
            "entendi", "entender", "sabe", "saber",
        }
        return [token for token in tokens if token in verb_lexicon]

    def _classify_tokens(self, tokens: list[str]) -> list[dict[str, str]]:
        """Classificação lexical aproximada para dar pistas ao interpretador."""
        articles = {"o", "a", "os", "as", "um", "uma", "uns", "umas"}
        pronouns = {
            "eu", "tu", "ele", "ela", "nós", "nos", "vós", "vocês", "eles",
            "elas", "isso", "isto", "aquilo", "esse", "essa", "este", "esta",
            "aquele", "aquela", "quem", "que", "meu", "minha", "seu", "sua",
            "me", "te", "se", "lhe", "nos",
        }
        prepositions = {"a", "ante", "após", "até", "com", "contra", "de", "desde", "em", "entre", "para", "por", "sem", "sobre", "sob"}
        conjunctions = {"e", "mas", "ou", "porque", "porém", "embora", "portanto", "se", "quando", "como"}
        adverbs = {"aqui", "ali", "lá", "hoje", "ontem", "amanhã", "agora", "sempre", "nunca", "talvez", "muito", "pouco", "bem", "mal", "rapidamente"}
        verbs = set(self._find_verbs(tokens))

        classified = []
        for token in tokens:
            if token in articles:
                kind = "artigo"
            elif token in pronouns:
                kind = "pronome"
            elif token in prepositions:
                kind = "preposicao"
            elif token in conjunctions:
                kind = "conjuncao"
            elif token in adverbs:
                kind = "adverbio"
            elif token in verbs:
                kind = "verbo"
            else:
                kind = "lexical"
            classified.append({"token": token, "class": kind})
        return classified

    def _extract_question(self, text: str) -> dict[str, Any]:
        patterns = self.portuguese["question_patterns"]

        # Tipos mais específicos vêm antes dos genéricos para preservar a intenção.
        ordered = [
            ("definition", patterns["definition"]["forms"]),
            ("function", patterns["function"]["forms"]),
            ("cause", patterns["cause"]["forms"]),
            ("process", patterns["process"]["forms"]),
            ("comparison", patterns["comparison"]["forms"]),
            ("time", patterns["time"]["forms"]),
            ("place", patterns["place"]["forms"]),
            ("identity", patterns["identity"]["forms"]),
        ]

        for question_type, forms in ordered:
            candidates = []
            for form in forms:
                form = form.lower().strip()
                if "X" in form:
                    prefix, suffix = form.split("X", 1)
                    candidates.append((prefix.strip(), suffix.strip(), form))
                    # Português contrai frequentemente "de + o/a" em "do/da".
                    if prefix.endswith(" de "):
                        for contraction in ("do ", "da ", "dos ", "das "):
                            candidates.append((prefix[:-4].rstrip() + " " + contraction, suffix.strip(), form))
                else:
                    candidates.append((form, "", form))

            for prefix, suffix, original_form in sorted(candidates, key=lambda item: len(item[0]), reverse=True):
                if not text.startswith(prefix):
                    continue
                remainder = text[len(prefix):].strip()
                if suffix:
                    if not remainder.endswith(suffix):
                        continue
                    remainder = remainder[:-len(suffix)].strip()
                remainder = remainder.strip(" ?.!,:;")
                if not remainder:
                    continue
                return {
                    "type": question_type,
                    "matched_form": original_form,
                    "semantic_goal": patterns[question_type]["semantic_goal"],
                    "topic_candidate": remainder,
                }

        return {
            "type": None,
            "matched_form": None,
            "semantic_goal": None,
            "topic_candidate": None,
        }

    def _analyze_structure(self, text: str) -> dict[str, Any]:
        tokens = self._tokens(text)
        classified = self._classify_tokens(tokens)
        verbs = [item["token"] for item in classified if item["class"] == "verbo"]
        pronouns = [item["token"] for item in classified if item["class"] == "pronome"]
        articles = [item["token"] for item in classified if item["class"] == "artigo"]
        question = self._extract_question(text)

        # Esta é uma representação de pistas, não uma análise sintática completa.
        subject_candidate = None
        if pronouns:
            subject_candidate = pronouns[0]
        elif articles:
            first_article = articles[0]
            try:
                index = tokens.index(first_article)
                if index + 1 < len(tokens):
                    subject_candidate = " ".join(tokens[index:index + 2])
            except ValueError:
                pass

        return {
            "tokens": tokens,
            "lexical_classes": classified,
            "verbs": verbs,
            "possible_subject": subject_candidate,
            "question": question,
            "has_question_mark": text.endswith("?"),
            "sentence_count": max(1, len(re.findall(r"[.!?]+", text))),
            "analysis_status": "heuristic_structural_reading",
        }

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
                "linguistic_analysis": {
                    "analysis_status": "empty_input",
                },
            }

        linguistic_analysis = self._analyze_structure(text)
        question = linguistic_analysis["question"]

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
        elif (
            self._has_any(text, concept_basic)
            or question["type"] in {"definition", "identity", "time", "place"}
            or self._has_any(
                text,
                ["o que foi", "o que são", "o que sao", "qual foi", "quem", "quando", "onde"],
            )
        ):
            intent, confidence = "concept_basic", 0.93
        elif (
            self._has_any(text, concept_scoped)
            or question["type"] in {"cause", "function", "process", "comparison"}
            or text.endswith("?")
        ):
            intent, confidence = "concept_scoped", 0.84
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
        elif linguistic_analysis["question"]["type"] and not linguistic_analysis["question"]["topic_candidate"]:
            ambiguity = "context_dependent"
        else:
            ambiguity = "clear"

        needs_memory = intent in {"continuity", "unknown", "doubt"} or any(
            token in {"ele", "ela", "isso", "isto", "aquilo", "esse", "essa", "este", "esta", "aquele", "aquela"}
            for token in linguistic_analysis["tokens"]
        )
        needs_library = intent in {
            "concept_basic", "concept_scoped", "clinical_case"
        }
        needs_diagnosis = intent == "clinical_case"
        needs_reasoning = intent not in {"phatic"}

        return {
            "intent": intent,
            "scope": question["topic_candidate"] or text,
            "depth": depth,
            "ambiguity": ambiguity,
            "needs_memory": needs_memory,
            "needs_library": needs_library,
            "needs_diagnosis": needs_diagnosis,
            "needs_reasoning": needs_reasoning,
            "confidence": confidence,
            "linguistic_analysis": linguistic_analysis,
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
