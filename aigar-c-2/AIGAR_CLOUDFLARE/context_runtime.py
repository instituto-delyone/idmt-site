"""Context selection and adaptive planning for the existing Cloudflare Worker."""
from __future__ import annotations

import re
import uuid
from language_runtime import STOPWORDS

def _context_token_set(text):
    return {word for word in re.findall(r"[a-zA-ZÀ-ÿ0-9_]{3,}", (text or "").casefold()) if word not in STOPWORDS}


class AsymmetricContextManager:
    """Seleciona contexto curto por dependência, recência e pertinência; exclui itens revogados."""
    def __init__(self, max_items=12, max_chars=12000):
        self.max_items = max(1, min(24, int(max_items)))
        self.max_chars = max(1000, min(24000, int(max_chars)))

    def resolve(self, query, turns, needs_context=False):
        q_tokens = _context_token_set(query)
        eligible = []
        excluded = []
        total = len(turns)
        for index, turn in enumerate(turns):
            content = str(turn.get("content") or "")
            status = str(turn.get("context_status") or "active")
            if not content:
                continue
            turn_id = str(turn.get("turn_id") or "")
            if status in {"revoked", "superseded"}:
                excluded.append({"turn_id": turn_id, "reason": status})
                continue
            turn_tokens = _context_token_set(content)
            overlap = len(q_tokens & turn_tokens) / max(1, len(q_tokens))
            recency = (index + 1) / max(1, total)
            dependency = 1.0 if (turn.get("metadata") or {}).get("pinned_context") else 0.0
            reference_signal = 1.0 if needs_context and index >= max(0, total - 4) else 0.0
            score = 0.42 * overlap + 0.25 * recency + 0.23 * reference_signal + 0.10 * dependency
            eligible.append((score, index, turn))

        # Dependências explícitas de referência e turnos recentes ganham preferência.
        eligible.sort(key=lambda item: (item[0], item[1]), reverse=True)
        chosen = []
        chars = 0
        for score, index, turn in eligible:
            content = str(turn.get("content") or "")
            if len(chosen) >= self.max_items:
                break
            if chars + len(content) > self.max_chars:
                continue
            chosen.append({
                "role": turn.get("role", "user"),
                "speaker": turn.get("speaker", "human" if turn.get("role") == "user" else "aigar"),
                "addressee": turn.get("addressee", "AIGAR" if turn.get("role") == "user" else "human"),
                "content": content,
                "turn_id": turn.get("turn_id"),
                "score": round(score, 4),
                "_context_index": index,
            })
            chars += len(content)
        chosen.sort(key=lambda item: item.get("_context_index", 0))
        for item in chosen:
            item.pop("_context_index", None)
        chosen_ids = [str(item.get("turn_id")) for item in chosen if item.get("turn_id")]
        unresolved = []
        if needs_context and not chosen:
            unresolved.append("recent_context_unavailable")
        return {
            "selected_context": chosen,
            "active_decisions": [],  # decisões devem ser explicitamente marcadas; não inferir decisão só pela repetição.
            "unresolved_references": unresolved,
            "excluded_items": excluded,
            "context_budget_used": chars,
            "context_dependencies": chosen_ids,
        }


def build_adaptive_plan(reading, profile, context_resolution):
    strategy_map = {
        "social": "conversational",
        "factual": "direct_answer",
        "exploratory_reasoning": "reasoned_explanation",
        "continuity_recall": "context_grounded",
        "correction_feedback": "inspect_and_correct",
        "co_creation_engineering": "engineering_and_tests",
        "execution_problem_solving": "stepwise_execution",
        "emotional_support": "supportive_and_grounded",
        "research_audit": "evidence_audit",
        "decision_prioritization": "compare_and_recommend",
        "artifact_creation": "produce_artifact",
        "meta_interaction": "explain_system_behavior",
    }
    primary = profile.get("primary_type", "factual")
    unresolved = list(context_resolution.get("unresolved_references") or [])
    return {
        "plan_id": str(uuid.uuid4()),
        "interaction_profile": profile,
        "intent": (reading or {}).get("intent", "unknown"),
        "answer_strategy": strategy_map.get(primary, "direct_answer"),
        "use_memory": bool(profile.get("context_required")),
        "use_library": bool(profile.get("research_required")),
        "use_diagnosis": bool((reading or {}).get("needs_diagnosis")),
        "evidence_required": bool(profile.get("research_required")),
        "context_budget": int(context_resolution.get("context_budget_used", 0)),
        "context_dependencies": list(context_resolution.get("context_dependencies") or []),
        "revision": 0,
        "revision_reasons": [],
        "unresolved_questions": unresolved,
    }


def revise_adaptive_plan(plan, *, evidence_items=None, context_resolution=None, corrected_intent=False):
    """Revisa o plano sem apagar o histórico de razões da revisão."""
    evidence_items = evidence_items or []
    context_resolution = context_resolution or {}
    reasons = []
    evidence_ids = [str(item.get("chunk_id")) for item in evidence_items if item.get("chunk_id")]
    if evidence_ids:
        reasons.append("new_library_evidence")
    if context_resolution.get("unresolved_references"):
        reasons.append("context_reference_unresolved")
    if corrected_intent:
        reasons.append("user_correction_or_reclassification")
    if not reasons:
        return plan
    plan["revision"] = int(plan.get("revision", 0)) + 1
    plan["revision_reasons"] = list(plan.get("revision_reasons", [])) + reasons
    plan["evidence_ids"] = list(dict.fromkeys(list(plan.get("evidence_ids", [])) + evidence_ids))
    plan["unresolved_questions"] = list(context_resolution.get("unresolved_references") or [])
    if evidence_ids:
        plan["answer_strategy"] = "synthesize_with_source_evidence"
        plan["evidence_required"] = True
        plan["use_library"] = True
    if corrected_intent:
        plan["answer_strategy"] = "reclassify_intent_before_answering"
    return plan
