"""ACLR v1 contract validation helpers. Pure stdlib; safe for Workers Python."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

class ContractError(ValueError):
    def __init__(self, code: str, message: str, component: str = "contracts"):
        super().__init__(message)
        self.code, self.message, self.component = code, message, component

def _obj(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError("invalid_object", f"{name} must be an object")
    return value

def _required(obj: Mapping[str, Any], fields: tuple[str, ...], name: str) -> None:
    missing = [key for key in fields if key not in obj]
    if missing:
        raise ContractError("missing_required", f"{name} missing required fields: {', '.join(missing)}")

def _str(value: Any, name: str, nonempty: bool = True) -> None:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        raise ContractError("invalid_string", f"{name} must be a non-empty string")

def _array(value: Any, name: str) -> None:
    if not isinstance(value, list):
        raise ContractError("invalid_array", f"{name} must be an array")

def _datetime(value: Any, name: str) -> None:
    _str(value, name)
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        raise ContractError("invalid_datetime", f"{name} must be an ISO-8601 date-time")

def validate_query_request(data: Any) -> dict:
    obj = _obj(data, "query_request")
    _required(obj, ("query_id", "question", "language", "request_mode"), "query_request")
    for key in ("query_id", "question", "language", "request_mode"):
        _str(obj[key], key)
    if "conversation_context" in obj: _array(obj["conversation_context"], "conversation_context")
    if "requested_domains" in obj:
        _array(obj["requested_domains"], "requested_domains")
        for item in obj["requested_domains"]: _str(item, "requested_domains[]")
    if "top_k" in obj and (not isinstance(obj["top_k"], int) or isinstance(obj["top_k"], bool) or not 1 <= obj["top_k"] <= 100):
        raise ContractError("invalid_top_k", "top_k must be an integer from 1 to 100")
    if "trace" in obj and not isinstance(obj["trace"], bool):
        raise ContractError("invalid_trace", "trace must be boolean")
    return dict(obj)

def validate_context_pointer(data: Any) -> dict:
    obj = _obj(data, "context_pointer")
    _required(obj, ("pointer_id", "schema_version", "target_type", "target_id", "domain_ids", "concept_ids", "provenance", "status"), "context_pointer")
    for key in ("pointer_id", "schema_version", "target_id"): _str(obj[key], key)
    if obj["target_type"] not in {"domain","subdomain","concept","entity","document","chunk","index","collection","claim"}:
        raise ContractError("invalid_target_type", "unsupported context pointer target_type")
    for key in ("domain_ids", "concept_ids", "relation_refs", "index_refs"):
        if key in obj:
            _array(obj[key], key)
            for item in obj[key]: _str(item, key + "[]")
    if not isinstance(obj["provenance"], Mapping): raise ContractError("invalid_provenance", "provenance must be an object")
    if obj["status"] not in {"unreviewed","active","deprecated","rejected"}:
        raise ContractError("invalid_status", "unsupported context pointer status")
    for key in ("created_at", "updated_at"):
        if key in obj: _datetime(obj[key], key)
    return dict(obj)

def validate_library_manifest(data: Any) -> dict:
    obj = _obj(data, "library_manifest")
    _required(obj, ("manifest_version", "library_id", "created_at", "domains", "general_index"), "library_manifest")
    for key in ("manifest_version", "library_id"): _str(obj[key], key)
    _datetime(obj["created_at"], "created_at")
    _array(obj["domains"], "domains")
    for domain in obj["domains"]:
        _obj(domain, "domains[]")
        _required(domain, ("domain_id", "domain_manifest_key", "status"), "domains[]")
        for key in ("domain_id", "domain_manifest_key"): _str(domain[key], key)
        if domain["status"] not in {"active","staged","deprecated"}: raise ContractError("invalid_domain_status", "unsupported domain status")
    general = _obj(obj["general_index"], "general_index")
    _required(general, ("index_key", "version"), "general_index")
    _str(general["index_key"], "general_index.index_key"); _str(general["version"], "general_index.version")
    return dict(obj)

def validate_retrieval_plan(data: Any) -> dict:
    obj = _obj(data, "retrieval_plan")
    _required(obj, ("plan_id", "query_id", "planner_version", "general_index_required", "paths"), "retrieval_plan")
    for key in ("plan_id", "query_id", "planner_version"): _str(obj[key], key)
    if obj["general_index_required"] is not True: raise ContractError("general_index_required", "general index must be required")
    _array(obj["paths"], "paths")
    for path in obj["paths"]:
        _obj(path, "paths[]")
        _required(path, ("path_id", "target_index", "query_text", "rationale"), "paths[]")
        for key in ("path_id", "target_index", "query_text", "rationale"): _str(path[key], key)
        if "max_results" in path and (not isinstance(path["max_results"], int) or path["max_results"] < 1):
            raise ContractError("invalid_max_results", "max_results must be a positive integer")
        if "traversed_edges" in path: _array(path["traversed_edges"], "traversed_edges")
    if not any(p.get("domain_id") is None for p in obj["paths"]):
        raise ContractError("missing_general_path", "retrieval plan must include a general-index path")
    return dict(obj)

def validate_evidence_envelope(data: Any) -> dict:
    obj = _obj(data, "evidence_envelope")
    _required(obj, ("query_id", "retriever_id", "status", "evidence", "warnings"), "evidence_envelope")
    for key in ("query_id", "retriever_id"): _str(obj[key], key)
    if obj["status"] not in {"success","empty","partial","error"}: raise ContractError("invalid_status", "unsupported evidence status")
    _array(obj["evidence"], "evidence"); _array(obj["warnings"], "warnings")
    for item in obj["evidence"]:
        _obj(item, "evidence[]")
        _required(item, ("evidence_id", "source_id", "content", "domain_ids", "provenance"), "evidence[]")
        for key in ("evidence_id", "source_id", "content"): _str(item[key], key, nonempty=False)
        _array(item["domain_ids"], "domain_ids")
        if not isinstance(item["provenance"], Mapping): raise ContractError("invalid_provenance", "evidence provenance must be an object")
        score = item.get("relevance_score")
        if score is not None and (not isinstance(score, (int,float)) or isinstance(score,bool)): raise ContractError("invalid_score", "relevance_score must be numeric or null")
        confidence = item.get("confidence")
        if confidence is not None and (not isinstance(confidence,(int,float)) or isinstance(confidence,bool) or not 0 <= confidence <= 1):
            raise ContractError("invalid_confidence", "confidence must be between 0 and 1")
    return dict(obj)
