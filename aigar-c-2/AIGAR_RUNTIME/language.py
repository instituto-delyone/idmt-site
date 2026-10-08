from __future__ import annotations

import re
from .models import ConversationReading

PHATIC = {"oi", "olá", "ola", "hey", "bom dia", "boa tarde", "boa noite", "e aí", "e ai"}
DEPTH_WORDS = {
    "breve": "brief", "curto": "brief", "simples": "simple",
    "normal": "normal", "técnico": "technical", "tecnico": "technical",
    "profundo": "deep", "profunda": "deep", "detalhado": "deep"
}

CONCEPT_STARTERS = (
    "o que é", "o que e", "o que foi", "o que são", "o que sao",
    "como", "por que", "porque", "qual", "quais",
    "qual é", "qual e", "qual foi", "quais são", "quais sao",
    "quem", "quando", "onde",
    "explique", "defina", "me fale", "me explica",
    "para que serve", "pra que serve",
)

def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def interpret(text: str) -> ConversationReading:
    t = _normalize(text)
    words = set(re.findall(r"[\wÀ-ÿ]+", t))
    depth = "normal"
    for key, value in DEPTH_WORDS.items():
        if key in t:
            depth = value
            break

    if t in PHATIC or any(t.startswith(x) for x in PHATIC):
        return ConversationReading(
            intent="phatic", depth=depth, needs_reasoning=False
        )

    clinical_markers = {
        "paciente", "pa", "pressão", "pressao", "fc", "saturação", "saturacao",
        "sintomas", "exame", "diagnóstico", "diagnostico", "potássio", "potassio",
        "sódio", "sodio", "gasometria", "choque", "sepse"
    }
    if words & clinical_markers:
        return ConversationReading(
            intent="clinical_case",
            depth=depth,
            needs_library=True,
            needs_diagnosis=True,
            needs_reasoning=True,
        )

    if t.endswith("?") or any(t.startswith(q) for q in CONCEPT_STARTERS):
        scoped = len(words) > 8
        return ConversationReading(
            intent="concept_scoped" if scoped else "concept_basic",
            scope=t,
            depth=depth,
            needs_library=True,
            needs_reasoning=True,
        )

    if any(x in t for x in ("corrija", "corrigir", "arrume", "melhore")):
        return ConversationReading(
            intent="correction", depth=depth, needs_reasoning=True
        )

    if any(x in t for x in ("continue", "continuando", "e depois", "então")):
        return ConversationReading(
            intent="continuity", depth=depth, needs_memory=True, needs_reasoning=True
        )

    return ConversationReading(
        intent="unknown", scope=t, depth=depth, needs_memory=True, needs_reasoning=True
    )
