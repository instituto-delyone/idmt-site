"""ACLR evidence normalization and resolution before CORTEX."""
from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping

from aclr_contracts import validate_evidence_envelope

def _canonical_content(value: str) -> str:
    return re.sub(r"\\s+", " ", value.casefold()).strip()

def resolve_evidence(query_id: str, envelopes: list[Mapping[str, Any]]) -> dict:
    """Merge evidence, preserve provenance/status and expose claim disagreement."""
    accepted, warnings, path_status = [], [], []
    seen: dict[str, dict] = {}
    groups: dict[str, list[str]] = {}
    claims: dict[str, list[dict]] = {}
    for raw in envelopes:
        envelope = validate_evidence_envelope(raw)
        if envelope["query_id"] != query_id:
            warnings.append("envelope_query_id_mismatch")
            continue
        path_status.append({"retriever_id": envelope["retriever_id"], "status": envelope["status"], "latency_ms": envelope.get("latency_ms")})
        warnings.extend(envelope.get("warnings") or [])
        for item in envelope["evidence"]:
            content_key = _canonical_content(item.get("content", ""))
            digest = item.get("content_hash") or hashlib.sha256(content_key.encode("utf-8")).hexdigest()
            stable_key = item.get("evidence_id") or digest
            existing = seen.get(stable_key) or seen.get(digest)
            if existing:
                existing.setdefault("duplicate_evidence_refs", []).append(item["evidence_id"])
                if envelope["retriever_id"] not in existing["retrieved_by"]:
                    existing["retrieved_by"].append(envelope["retriever_id"])
                continue
            normalized = dict(item)
            normalized["retrieved_by"] = [envelope["retriever_id"]]
            normalized["duplicate_evidence_refs"] = []
            seen[stable_key] = normalized
            seen[digest] = normalized
            accepted.append(normalized)
            for domain in item.get("domain_ids") or []:
                groups.setdefault(domain, []).append(item["evidence_id"])
            claim_id = (item.get("provenance") or {}).get("claim_id")
            if claim_id:
                claims.setdefault(str(claim_id), []).append(normalized)
    conflicts = []
    for claim_id, items in claims.items():
        distinct = {}
        for item in items:
            fingerprint = _canonical_content(item.get("content", ""))
            distinct.setdefault(fingerprint, []).append(item["evidence_id"])
        if len(distinct) > 1:
            conflicts.append({
                "conflict_id": "claim-" + hashlib.sha256(claim_id.encode()).hexdigest()[:12],
                "claim_id": claim_id,
                "conflict_type": "divergent_evidence_content",
                "evidence_refs": [item["evidence_id"] for item in items],
                "resolution": "unresolved_preserve_all",
            })
    statuses = [p["status"] for p in path_status]
    if accepted and any(s in {"error", "partial"} for s in statuses): status = "partial"
    elif accepted: status = "complete"
    elif statuses and all(s == "empty" for s in statuses): status = "complete"
    else: status = "failed"
    return {
        "query_id": query_id,
        "retrieval_status": status,
        "path_status": path_status,
        "evidence": accepted,
        "groups": [{"group_id": key, "group_type": "domain", "evidence_refs": value} for key, value in sorted(groups.items())],
        "conflicts": conflicts,
        "uncovered_concepts": [],
        "warnings": sorted(set(warnings)),
        "coverage": {"evidence_count": len(accepted), "domain_count": len(groups)},
        "trace_id": f"aclr-resolve-{hashlib.sha256(query_id.encode()).hexdigest()[:16]}",
    }
