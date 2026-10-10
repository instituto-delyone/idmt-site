from __future__ import annotations

from fastapi import FastAPI

from .models import RuntimeRequest, RuntimeResponse
from .language_network_bridge import LanguageNetworkAdapter
from .conversation import ConversationStore
from .hippocampal_memory import HippocampalMemoryAdapter
from .library import LibraryAdapter
from .diagnosis import DiagnosisAdapter
from .prefrontal_controller import PrefrontalController
from .aurora import Aurora

app = FastAPI(title="AIGAR Neurocognitive Runtime", version="0.3.0")

store = ConversationStore()
language = LanguageNetworkAdapter()
memory = HippocampalMemoryAdapter()
library = LibraryAdapter()
diagnosis = DiagnosisAdapter()
reasoning = PrefrontalController()
aurora = Aurora()


def run_runtime(request: RuntimeRequest) -> RuntimeResponse:
    state = store.get(request.session_id)

    reading = language.interpret(request.input)
    state.reading = reading

    memory_context = []
    sources = []

    if reading.needs_memory or reading.intent == "continuity":
        memory_context, trace = memory.recall(state)
        sources.append(trace)

    library_context = []
    if reading.needs_library:
        library_context, trace = library.search(
            request.input,
            reading=reading.model_dump(),
        )
        sources.append(trace)

    diagnosis_result = {}
    if reading.needs_diagnosis:
        diagnosis_result, trace = diagnosis.evaluate({
            "input": request.input,
            "reading": reading.model_dump(),
            "memory": memory_context,
            "library": library_context,
        })
        sources.append(trace)

    plan, trace = reasoning.plan(
        request.input,
        reading.model_dump(),
        memory_context,
        library_context,
        diagnosis_result,
    )
    sources.append(trace)

    text, trace = aurora.respond(
        request.input,
        reading,
        memory_context,
        library_context,
        diagnosis_result,
        plan,
    )
    sources.append(trace)

    store.update(state, request.input, text)

    confirmed_or_connected = [
        source for source in sources
        if source.status in {"confirmed", "inferred"}
    ]
    confidence = 0.15 if any(
        source.status == "missing" for source in sources
    ) else 0.35
    if confirmed_or_connected:
        confidence = min(0.75, confidence + 0.1 * len(confirmed_or_connected))

    return RuntimeResponse(
        text=text,
        state=state,
        sources=sources,
        confidence=confidence,
        plan=plan,
    )


@app.get("/health")
def health() -> dict:
    return {"ok": True, "runtime": "AIGAR", "version": "0.3.0"}


@app.post("/perguntar", response_model=RuntimeResponse)
def perguntar(request: RuntimeRequest) -> RuntimeResponse:
    return run_runtime(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("AIGAR_RUNTIME.main:app", host="127.0.0.1", port=8000, reload=False)
