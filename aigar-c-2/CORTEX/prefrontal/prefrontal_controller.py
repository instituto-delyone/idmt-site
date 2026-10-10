from __future__ import annotations

import re

from ..thalamus.models import ReasoningPlan, SourceTrace


def _sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]


def _query_terms(text: str) -> set[str]:
    return {
        word for word in re.findall(r"[\wÀ-ÿ]{3,}", text.lower())
        if word not in {"que", "qual", "quais", "como", "onde", "quando", "para", "uma", "uma"}
    }


class PrefrontalController:
    """Controlador pré-frontal funcional: planeja a resposta a partir da leitura e do contexto. Analogia computacional, não equivalência neuroanatômica literal."""

    def _select_evidence(self, input_text: str, library: list[dict]) -> list[str]:
        terms = _query_terms(input_text)
        candidates = []
        for item in library:
            for sentence in _sentences(item.get("text", "")):
                overlap = len(terms & _query_terms(sentence))
                if overlap:
                    candidates.append((overlap, item.get("score", 0), sentence))
        candidates.sort(key=lambda x: (-x[0], -float(x[1]), len(x[2])))
        selected = []
        for _, _, sentence in candidates:
            if sentence not in selected:
                selected.append(sentence)
            if len(selected) >= 3:
                break
        return selected

    def plan(
        self,
        input_text: str,
        reading: dict,
        memory: list,
        library: list,
        diagnosis: dict,
    ) -> tuple[ReasoningPlan, SourceTrace]:
        evidence = self._select_evidence(input_text, library)
        linguistic = reading.get("linguistic_analysis", {})
        question = linguistic.get("question", {})

        if reading.get("intent") == "phatic":
            answer_mode = "social"
        elif evidence:
            answer_mode = "source_grounded"
        elif reading.get("needs_library"):
            answer_mode = "source_unavailable"
        elif reading.get("needs_memory") and memory:
            answer_mode = "context_grounded"
        else:
            answer_mode = "reasoned_without_library"

        plan = ReasoningPlan(
            understand_before_answer=True,
            intent=reading.get("intent"),
            depth=reading.get("depth"),
            use_memory=reading.get("needs_memory", False),
            use_library=bool(library) or reading.get("needs_library", False),
            use_diagnosis=bool(diagnosis) or reading.get("needs_diagnosis", False),
            answer_mode=answer_mode,
            question_type=question.get("type"),
            semantic_goal=question.get("semantic_goal"),
            topic=question.get("topic_candidate") or reading.get("scope"),
            evidence=evidence,
            steps=[
                "interpret",
                "gather_available_context",
                "select_relevant_evidence",
                "reason",
                "plan_response",
            ],
        )

        detail = (
            f"Raciocínio estruturou a resposta com {len(evidence)} evidência(s) "
            f"recuperada(s) da biblioteca."
            if evidence
            else "Raciocínio estruturou a resposta, mas não possui evidência documental suficiente."
        )

        return plan, SourceTrace(
            kind="reasoning",
            id="runtime.reasoning",
            status="confirmed" if evidence else "inferred",
            detail=detail,
        )
