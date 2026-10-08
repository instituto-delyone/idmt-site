from __future__ import annotations

from .models import ConversationReading, SourceTrace

class Aurora:
    """Response modulation boundary.

    Aurora owns conversational presentation, not specialized knowledge.
    """

    def respond(
        self,
        input_text: str,
        reading: ConversationReading,
        memory: list,
        library: list,
        diagnosis: dict,
        plan: dict,
    ) -> tuple[str, SourceTrace]:

        if reading.intent == "phatic":
            return "Oi! Aurora aqui. Manda o que você quer construir que a gente organiza.", SourceTrace(
                kind="aurora", id="runtime.aurora", status="proposed"
            )

        if library or diagnosis:
            return (
                "A solicitação foi roteada para os módulos especializados, "
                "mas a integração executável deles ainda precisa ser conectada ao runtime."
            ), SourceTrace(kind="aurora", id="runtime.aurora", status="proposed")

        if reading.intent == "unknown":
            return (
                "Entendi a entrada, mas ainda não tenho uma fonte ou módulo conectado "
                "para responder com segurança. Posso continuar a partir do contexto da conversa."
            ), SourceTrace(kind="aurora", id="runtime.aurora", status="proposed")

        return (
            "Entendi a solicitação e organizei o estado da conversa. "
            "O próximo passo é conectar a fonte documental ou o motor especializado correspondente."
        ), SourceTrace(kind="aurora", id="runtime.aurora", status="proposed")
