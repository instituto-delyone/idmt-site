from __future__ import annotations

from ..thalamus.models import AuroraRequest, AuroraResult, ConversationReading, SourceTrace


class Aurora:
    def respond(self, request: AuroraRequest) -> AuroraResult:
        """Typed boundary; legacy presentation branches remain behavior-preserving."""
        text, source = self._respond_legacy(
            request.input_text,
            request.reading,
            request.memory,
            request.library,
            request.diagnosis,
            request.plan.model_dump(),
        )
        return AuroraResult(text=text, source=source)

    """Modula a apresentação final a partir de conteúdo já fundamentado."""

    @staticmethod
    def _topic(plan: dict) -> str:
        return (plan.get("topic") or "").strip(" ?") or "esse assunto"

    def _respond_legacy(
        self,
        input_text: str,
        reading: ConversationReading,
        memory: list,
        library: list,
        diagnosis: dict,
        plan: dict,
    ) -> tuple[str, SourceTrace]:

        if reading.intent == "phatic":
            return (
                "Oi! Aurora aqui. Manda o que você quer construir que a gente organiza."
            ), SourceTrace(kind="aurora", id="runtime.aurora", status="confirmed")

        mode = plan.get("answer_mode")
        topic = self._topic(plan)
        evidence = plan.get("evidence", [])

        if mode == "source_grounded":
            if plan.get("question_type") == "definition":
                prefix = f"{topic.capitalize()} — pelo material recuperado na biblioteca:"
            elif plan.get("question_type") == "function":
                prefix = f"A função de {topic} — pelo material recuperado na biblioteca:"
            elif plan.get("question_type") == "cause":
                prefix = f"Sobre a causa de {topic} — pelo material recuperado na biblioteca:"
            else:
                prefix = f"Encontrei este conteúdo relevante sobre {topic}:"

            body = " ".join(evidence)
            return (
                f"{prefix}\n\n{body}\n\n"
                "A resposta acima foi construída a partir do conteúdo recuperado; "
                "a próxima camada pode fazer a paráfrase e a síntese semântica."
            ), SourceTrace(
                kind="aurora",
                id="runtime.aurora",
                status="confirmed",
                detail="Resposta apresentada a partir de evidência selecionada pelo Reasoning.",
            )

        if mode == "source_unavailable":
            return (
                f"Entendi a pergunta sobre {topic} e determinei que preciso consultar "
                "a biblioteca para responder com segurança. A biblioteca está conectada, "
                "mas não há conteúdo local recuperável suficiente para esta pergunta ainda."
            ), SourceTrace(
                kind="aurora",
                id="runtime.aurora",
                status="confirmed",
                detail="Não houve evidência documental suficiente para gerar resposta factual.",
            )

        if mode == "context_grounded":
            last = memory[-1].get("content") if memory else None
            return (
                "Vou continuar a partir do contexto recente."
                + (f" O ponto anterior foi: {last}" if last else "")
            ), SourceTrace(kind="aurora", id="runtime.aurora", status="confirmed")

        if mode == "reasoned_without_library":
            return (
                "Entendi a solicitação e já estruturei a intenção e o contexto, "
                "mas não vou inventar conteúdo que não foi fundamentado em uma fonte "
                "ou em contexto suficiente."
            ), SourceTrace(kind="aurora", id="runtime.aurora", status="confirmed")

        return (
            "Entendi a solicitação e organizei o estado da conversa."
        ), SourceTrace(kind="aurora", id="runtime.aurora", status="confirmed")
