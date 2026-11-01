"""ACLR Layer A: deterministic prototype planner over contextual catalogue records."""
from __future__ import annotations

import re
import unicodedata
import uuid
from typing import Any, Mapping

from aclr_contracts import validate_query_request, validate_retrieval_plan

PLANNER_VERSION = "aclr-planner-0.1.0"

def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value).casefold())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", value)).strip()

def _matches(text: str, signals: list[str]) -> list[str]:
    normalized = _norm(text)
    padded = f" {normalized} "
    return [signal for signal in signals if _norm(signal) and f" {_norm(signal)} " in padded]

def build_retrieval_plan(
    request: Mapping[str, Any],
    master_index: Mapping[str, Any],
    domain_indexes: Mapping[str, Mapping[str, Any]],
    *,
    general_index: Mapping[str, str] | None = None,
    context_pointers: list[Mapping[str, Any]] | None = None,
    max_paths: int = 12,
    default_top_k: int = 5,
) -> dict:
    """Build specialized paths plus mandatory general-index safety-net path.

    This is a fixture-driven planner, not yet an R2/D1 adapter. It never reads
    chunk bodies; it only emits index targets and stable chunk/pointer references.
    """
    query = validate_query_request(request)
    text = query["question"]
    requested = set(query.get("requested_domains") or [])
    active_domains = [d for d in master_index.get("domains", []) if d.get("status", "prototype") not in {"deprecated","rejected"}]
    domain_hits: list[tuple[dict, list[str], float]] = []
    for domain in active_domains:
        did = domain.get("domain_id")
        hits = _matches(text, list(domain.get("signals") or []))
        if did in requested: hits.append("requested_domain")
        if hits: domain_hits.append((domain, hits, float(len(set(hits)))))
    # Unknown or weak classification broadens candidates; it never removes the general path.
    if not domain_hits:
        for domain in active_domains:
            domain_hits.append((domain, ["fallback_broad_candidate"], 0.1))
    paths: list[dict] = []
    pointers = [p for p in (context_pointers or []) if p.get("status", "active") == "active"]
    for domain, domain_hits_signals, domain_score in domain_hits:
        did = domain["domain_id"]
        index = domain_indexes.get(did)
        if not index:
            continue
        for sub in index.get("subdomains", []):
            sub_hits = _matches(text, list(sub.get("signals") or []) + [sub.get("label", "")])
            pointer_hits = [p for p in pointers if did in (p.get("domain_ids") or []) and (
                sub.get("subdomain_id") in (p.get("concept_ids") or []) or
                any(ref in (p.get("relation_refs") or []) for ref in (sub.get("relation_refs") or []))
            )]
            if sub_hits or pointer_hits or "fallback_broad_candidate" in domain_hits_signals:
                paths.append({
                    "path_id": f"path-{uuid.uuid4().hex[:12]}",
                    "start_node": did,
                    "target_index": f"{did}:{sub.get('subdomain_id')}",
                    "domain_id": did,
                    "query_text": text,
                    "traversed_edges": ["hierarchical"],
                    "rationale": ("matched signals: " + ", ".join(sorted(set(sub_hits))) if sub_hits else
                                  "context pointer match" if pointer_hits else "broad fallback candidate"),
                    "priority": domain_score + float(len(sub_hits)),
                    "max_results": int(query.get("top_k", default_top_k)),
                    "status": "planned",
                    "chunk_ids": list(sub.get("chunks") or []),
                    "pointer_refs": [p.get("pointer_id") for p in pointer_hits if p.get("pointer_id")],
                })
    paths.sort(key=lambda p: (-p["priority"], p["domain_id"], p["target_index"]))
    paths = paths[:max(1, max_paths - 1)]
    general = general_index or {"index_key": "library/general/indexes/active/", "version": "active"}
    paths.append({
        "path_id": f"path-{uuid.uuid4().hex[:12]}",
        "start_node": None,
        "target_index": general.get("index_key", "library/general/indexes/active/"),
        "domain_id": None,
        "query_text": text,
        "traversed_edges": [],
        "rationale": "mandatory general-index safety net",
        "priority": 1.0,
        "max_results": int(query.get("top_k", default_top_k)),
        "status": "planned",
    })
    plan = {
        "plan_id": f"plan-{uuid.uuid4().hex}",
        "query_id": query["query_id"],
        "planner_version": PLANNER_VERSION,
        "general_index_required": True,
        "paths": paths,
        "expansion_policy": {"max_paths": max_paths, "max_depth": 4, "cycle_detection": True},
        "coverage_targets": sorted({signal for _, hits, _ in domain_hits for signal in hits if signal != "requested_domain"}),
    }
    # Contract schema allows additionalProperties=false inside path, so remove prototype-only routing hints.
    for path in plan["paths"]:
        path.pop("chunk_ids", None)
        path.pop("pointer_refs", None)
    return validate_retrieval_plan(plan)

def inspect_selected_targets(plan: Mapping[str, Any], domain_indexes: Mapping[str, Mapping[str, Any]]) -> dict[str, list[str]]:
    """Resolve planned subdomain targets to chunk IDs without reading content."""
    targets: dict[str, list[str]] = {}
    for path in plan.get("paths", []):
        did = path.get("domain_id")
        if not did: continue
        index = domain_indexes.get(did, {})
        sub_id = path.get("target_index", "").split(":", 1)[-1]
        sub = next((item for item in index.get("subdomains", []) if item.get("subdomain_id") == sub_id), None)
        if sub:
            targets[path["path_id"]] = list(sub.get("chunks") or [])
    return targets
