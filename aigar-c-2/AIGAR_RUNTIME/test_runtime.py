from AIGAR_RUNTIME.main import run_runtime
from AIGAR_RUNTIME.models import RuntimeRequest


def test_phatic():
    result = run_runtime(RuntimeRequest(input="Oi", session_id="test"))
    assert result.state.reading.intent == "phatic"
    assert result.text


def test_concept_routes_to_library_boundary():
    result = run_runtime(RuntimeRequest(
        input="O que é insuficiência adrenal?",
        session_id="test-concept",
    ))
    assert result.state.reading.needs_library is True
    assert any(s.kind == "library" for s in result.sources)


def test_executable_language_is_connected_to_runtime():
    result = run_runtime(RuntimeRequest(
        input="O que foi a Revolução Agrícola",
        session_id="test-executable-language",
    ))
    assert result.state.reading.intent == "concept_basic"
    assert result.state.reading.needs_library is True
    assert result.state.reading.scope == "a revolução agrícola"
    assert result.state.reading.linguistic_analysis["question"]["type"] == "definition"
    assert result.plan["question_type"] == "definition"
    assert "answer_mode" in result.plan


def test_continuity_uses_session_memory():
    run_runtime(RuntimeRequest(input="Meu nome é X", session_id="continuity"))
    result = run_runtime(RuntimeRequest(input="continue", session_id="continuity"))
    assert result.state.reading.intent == "continuity"
    assert any(s.kind == "memory" for s in result.sources)
