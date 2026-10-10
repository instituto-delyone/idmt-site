from __future__ import annotations

import re
import unicodedata
from typing import Any


STOPWORDS = {
    "a", "o", "e", "de", "do", "da", "dos", "das", "um", "uma", "uns", "umas",
    "em", "no", "na", "nos", "nas", "por", "para", "com", "que", "como",
    "qual", "quais", "é", "foi", "ser", "se", "ao", "à", "às", "os", "as",
    "mais", "sobre", "isso", "esse", "essa", "este", "esta", "ou", "um",
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def semantic_tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9_]{2,}", normalize(text))
    return {w for w in words if w not in STOPWORDS}


_EXPANSION_SOURCE = {
    "função": {"papel", "finalidade", "serve", "servir", "funcionamento"},
    "funciona": {"funcionamento", "mecanismo", "processo", "operação"},
    "explicar": {"explicação", "conceito", "definição", "entendimento"},
    "definição": {"conceito", "significado", "definição"},
    "causa": {"motivo", "razão", "porque", "origem"},
    "efeito": {"consequência", "resultado", "impacto"},
    "processo": {"etapas", "mecanismo", "procedimento", "processo"},
    "comparar": {"diferença", "semelhança", "comparação"},
    "diferença": {"contraste", "distinção", "diferença"},
    "limite": {"limites", "continuidade", "aproximação"},
    "derivada": {"derivação", "taxa", "variação"},
    "integral": {"integração", "área", "antiderivada"},
    "computador": {"computação", "processador", "hardware", "arquitetura"},
    "arquitetura": {"organização", "computador", "processador", "memória"},
    "ética": {"moral", "princípio", "conduta", "responsabilidade"},
    "lógica": {"raciocínio", "proposição", "inferência", "dedução"},
    "matemática": {"cálculo", "número", "equação"},
    "português": {"língua", "linguagem", "gramática", "sintaxe", "semântica"},
}

EXPANSIONS = {
    normalize(key): {normalize(value) for value in values}
    for key, values in _EXPANSION_SOURCE.items()
}


SOURCE_PROFILES = {
    "portuguese_language_knowledge": {
        "terms": {"português", "gramática", "língua", "linguagem", "sintaxe", "semântica",
                  "oração", "frase", "período", "verbo", "sujeito", "pronomes"},
    },
    "matematica_computacional": {
        "terms": {"matemática", "cálculo", "limite", "derivada", "integral", "função",
                  "equação", "número", "álgebra", "geometria"},
    },
    "arquitetura_organizacao_computadores": {
        "terms": {"arquitetura", "computador", "processador", "memória", "hardware",
                  "cpu", "sistema", "organização", "barramento"},
    },
    "etica": {
        "terms": {"ética", "moral", "princípio", "conduta", "responsabilidade",
                  "dever", "valor", "justiça"},
    },
    "raciocinio_logico_matematica": {
        "terms": {"lógica", "raciocínio", "proposição", "inferência", "dedução",
                  "concurso", "matemática", "problema"},
    },
    "interacoes_aigar": {
        "terms": {"aigar", "aurora", "conversa", "memória", "interação", "diálogo"},
    },
    "sapiens": {
        "terms": {"humanidade", "história", "evolução", "civilização", "sociedade",
                  "agricultura", "revolução", "harari"},
    },
}


class SemanticRouter:
    """Interpretable semantic expansion and source relevance scoring."""

    def expand(self, query: str, reading: dict[str, Any] | None = None) -> set[str]:
        base = semantic_tokens(query)
        expanded = set(base)
        for term in list(base):
            expanded.update(EXPANSIONS.get(term, set()))

        reading = reading or {}
        linguistic = reading.get("linguistic_analysis") or {}
        for value in (
            linguistic.get("question_type"),
            linguistic.get("semantic_goal"),
            reading.get("scope"),
        ):
            if isinstance(value, str):
                expanded.update(semantic_tokens(value))
        return expanded

    def source_scores(self, query: str, reading: dict[str, Any] | None = None) -> dict[str, float]:
        q = self.expand(query, reading)
        scores: dict[str, float] = {}
        for source, profile in SOURCE_PROFILES.items():
            overlap = q & {normalize(x) for x in profile["terms"]}
            if overlap:
                scores[source] = min(1.0, len(overlap) / max(2, len(profile["terms"]) * 0.35))
        return scores

    def score(
        self,
        query: str,
        text: str,
        source_key: str,
        reading: dict[str, Any] | None = None,
    ) -> float:
        q = self.expand(query, reading)
        body = semantic_tokens(text)
        if not q or not body:
            return 0.0
        overlap = q & body
        lexical = len(overlap) / max(1, len(q))
        source = self.source_scores(query, reading).get(source_key, 0.0)
        return round(min(1.0, 0.75 * lexical + 0.25 * source), 6)
