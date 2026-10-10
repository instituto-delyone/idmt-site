from __future__ import annotations

from fastapi import FastAPI

# AIGAR_RUNTIME/main.py remains the operational entry point during migration.
# CORTEX is the provisional canonical home for runtime components and contracts.
from CORTEX.thalamus.models import RuntimeRequest, RuntimeResponse
from CORTEX.sensory.ingress import capture_request
from CORTEX.thalamus.context_router import route_reading
from CORTEX.sara.runtime_status import current_runtime_status
from CORTEX.language.language_network_adapter import LanguageNetworkAdapter
from CORTEX.memory.working_memory import WorkingStateStore
from CORTEX.memory.hippocampal_memory import HippocampalMemoryAdapter
from CORTEX.engram.knowledge_retrieval import KnowledgeRetrievalAdapter
from Diagnosis.diagnosis import DiagnosisAdapter
from CORTEX.prefrontal.prefrontal_controller import PrefrontalController
from CORTEX.prefrontal.aurora import Aurora

app = FastAPI(title="AIGAR Neurocognitive Runtime", version="0.3.0")

store = WorkingStateStore()
language = LanguageNetworkAdapter()
memory = HippocampalMemoryAdapter()
library = KnowledgeRetrievalAdapter()
diagnosis = DiagnosisAdapter()
reasoning = PrefrontalController()
aurora = Aurora()


def run_runtime(request: RuntimeRequest) -> RuntimeResponse:
    signal = capture_request(request)
    state = store.get(signal.session_id)

    reading = language.interpret(signal.raw_text)
    state.reading = reading
    routing = route_reading(reading)

    memory_context = []
    sources = []

    if routing.use_memory:
        memory_context, trace = memory.recall(state)
        sources.append(trace)

    library_context = []
    if routing.use_library:
        library_context, trace = library.search(signal.raw_text, reading=reading.model_dump())
        sources.append(trace)

    diagnosis_result = {}
    if routing.use_diagnosis:
        diagnosis_result, trace = diagnosis.evaluate({
            "input": signal.raw_text,
            "reading": reading.model_dump(),
            "memory": memory_context,
            "library": library_context,
        })
        sources.append(trace)

    # The reasoning stage remains in the pipeline for now; its policy will be
    # refined after all subsystem contracts and references have been completed.
    plan_contract, trace = reasoning.plan(
        signal.raw_text, reading.model_dump(), memory_context, library_context, diagnosis_result
    )
    plan = plan_contract.model_dump()
    sources.append(trace)

    text, trace = aurora.respond(
        signal.raw_text, reading, memory_context, library_context, diagnosis_result, plan
    )
    sources.append(trace)

    store.update(state, signal.raw_text, text)

    confirmed_or_connected = [
        source for source in sources if source.status in {"confirmed", "inferred"}
    ]
    confidence = 0.15 if any(source.status == "missing" for source in sources) else 0.35
    if confirmed_or_connected:
        confidence = min(0.75, confidence + 0.1 * len(confirmed_or_connected))

    return RuntimeResponse(
        text=text, state=state, sources=sources, confidence=confidence, plan=plan
    )


@app.get("/health")
def health() -> dict:
    return current_runtime_status().model_dump()


@app.post("/perguntar", response_model=RuntimeResponse)
def perguntar(request: RuntimeRequest) -> RuntimeResponse:
    return run_runtime(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("AIGAR_RUNTIME.main:app", host="127.0.0.1", port=8000, reload=False)
