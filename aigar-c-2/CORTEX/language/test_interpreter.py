import json
from pathlib import Path

from CORTEX.language.interpreter import AIGARLanguage


def test_definition_question_is_structured():
    result = AIGARLanguage().interpret("O que foi a Revolução Agrícola?")
    analysis = result["linguistic_analysis"]

    assert result["intent"] == "concept_basic"
    assert result["needs_library"] is True
    assert analysis["question"]["type"] == "definition"
    assert analysis["question"]["topic_candidate"] == "a revolução agrícola"
    assert "foi" in analysis["verbs"]


def test_pronoun_marks_possible_context_dependency():
    result = AIGARLanguage().interpret("Ele chegou.")
    analysis = result["linguistic_analysis"]

    assert "ele" in analysis["possible_subject"]
    assert result["needs_memory"] is True


def test_function_question_is_scoped():
    result = AIGARLanguage().interpret("Qual a função do coração?")
    analysis = result["linguistic_analysis"]

    assert result["intent"] == "concept_scoped"
    assert analysis["question"]["type"] == "function"
    assert analysis["question"]["semantic_goal"] == "explicar_funcao_ou_finalidade"
