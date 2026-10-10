"""Shared data contracts for the AIGAR-C neurocognitive runtime.

This module is the canonical home for request/response, conversation-state,
linguistic-reading and source-trace models. Other CORTEX modules should import
these contracts from CORTEX.thalamus.models rather than defining parallel versions.

The schemas intentionally preserve the field names and defaults of the migrated
runtime contract. Structural migration is not the place to silently change semantics.
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


class RuntimeResponse(BaseModel):
    """External response contract, including state, provenance and plan."""

    text: str
    state: ConversationState
    sources: list[SourceTrace] = Field(default_factory=list)
    confidence: float = 0.0
    plan: dict[str, Any] = Field(default_factory=dict)
