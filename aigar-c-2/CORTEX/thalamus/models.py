"""Shared data contracts for the AIGAR-C neurocognitive runtime.

This module is the canonical home for request/response, conversation-state,
linguistic-reading, routing and source-trace models. Other CORTEX modules should
import these contracts from CORTEX.thalamus.models rather than defining parallel versions.

Existing field names and defaults are preserved; new contracts are additive.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Intent = Literal[
    "phatic", "concept_basic", "concept_scoped", "clinical_case",
    "action", "correction", "continuity", "doubt", "unknown"
]

Depth = Literal["brief", "simple", "normal", "technical", "deep"]
SourceStatus = Literal["confirmed", "inferred", "proposed", "missing"]


class ConversationReading(BaseModel):
    """Structured interpretation of one user input and routing requirements."""

    intent: Intent = "unknown"
    scope: str | None = None
    depth: Depth = "normal"
    ambiguity: float = 0.0
    uncertainty: float = 0.0
    needs_memory: bool = False
    needs_library: bool = False
    needs_diagnosis: bool = False
    needs_reasoning: bool = True
    linguistic_analysis: dict[str, Any] = Field(default_factory=dict)


class RoutingDecision(BaseModel):
    """Normalized dispatch decision derived from a ConversationReading.

    This contract describes which optional resources should be called. It does not
    claim that a selected subsystem is available or that its operation succeeded.
    """

    use_memory: bool = False
    use_library: bool = False
    use_diagnosis: bool = False
    use_reasoning: bool = True


class ReasoningPlan(BaseModel):
    """Structured plan produced before response presentation."""

    understand_before_answer: bool = True
    intent: Intent | None = None
    depth: Depth | None = None
    use_memory: bool = False
    use_library: bool = False
    use_diagnosis: bool = False
    answer_mode: Literal[
        "social", "source_grounded", "source_unavailable",
        "context_grounded", "reasoned_without_library"
    ] = "reasoned_without_library"
    question_type: str | None = None
    semantic_goal: str | None = None
    topic: str | None = None
    evidence: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)


class ConversationState(BaseModel):
    """Session-local state shared by runtime modules."""

    session_id: str = "default"
    turns: list[dict[str, Any]] = Field(default_factory=list)
    last_user_input: str | None = None
    last_response: str | None = None
    reading: ConversationReading = Field(default_factory=ConversationReading)


class SourceTrace(BaseModel):
    """Provenance/status record returned by a runtime component."""

    kind: str
    id: str
    status: SourceStatus = "proposed"
    detail: str | None = None


class RuntimeRequest(BaseModel):
    """External request contract for the conversational runtime."""

    input: str
    session_id: str = "default"


class SensoryInput(BaseModel):
    """Canonical envelope passed from external ingress to sensory processing.

    The raw text is preserved exactly; normalization belongs to later layers.
    """

    raw_text: str
    session_id: str = "default"
    modality: Literal["text"] = "text"
    source: str = "api"




class DiagnosisRequest(BaseModel):
    """Typed input envelope for the separate clinical Diagnosis subsystem."""

    input_text: str
    reading: ConversationReading
    memory_context: list[dict[str, Any]] = Field(default_factory=list)
    library_context: list[dict[str, Any]] = Field(default_factory=list)


class DiagnosisResult(BaseModel):
    """Typed result envelope; empty findings do not imply a completed diagnosis."""

    findings: dict[str, Any] = Field(default_factory=dict)
    source: SourceTrace


class RuntimeResponse(BaseModel):
    """External response contract, including state, provenance and plan."""

    text: str
    state: ConversationState
    sources: list[SourceTrace] = Field(default_factory=list)
    confidence: float = 0.0
    plan: dict[str, Any] = Field(default_factory=dict)
