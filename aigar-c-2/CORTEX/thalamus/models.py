from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field

Intent = Literal[
    "phatic", "concept_basic", "concept_scoped", "clinical_case",
    "action", "correction", "continuity", "doubt", "unknown"
]

Depth = Literal["brief", "simple", "normal", "technical", "deep"]

class ConversationReading(BaseModel):
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
    session_id: str = "default"
    turns: list[dict[str, Any]] = Field(default_factory=list)
    last_user_input: str | None = None
    last_response: str | None = None
    reading: ConversationReading = Field(default_factory=ConversationReading)

class SourceTrace(BaseModel):
    kind: str
    id: str
    status: Literal["confirmed", "inferred", "proposed", "missing"] = "proposed"
    detail: str | None = None

class RuntimeRequest(BaseModel):
    input: str
    session_id: str = "default"

class RuntimeResponse(BaseModel):
    text: str
    state: ConversationState
    sources: list[SourceTrace] = Field(default_factory=list)
    confidence: float = 0.0
    plan: dict[str, Any] = Field(default_factory=dict)
