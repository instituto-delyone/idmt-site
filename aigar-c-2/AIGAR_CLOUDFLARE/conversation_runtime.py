"""Conversation orchestration, adaptive interaction, context use and feedback contracts."""
from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from datetime import datetime, timezone
from cloudflare_bindings import binding
from language_runtime import LANGUAGE, LANGUAGE_ENGINE, SESSIONS, compose_book_grounded_answer
from library_runtime import COGNITIVE_CORE, MEMORY_LAB, boot_library, boot_text_matrix, library_search, source_relevance
from context_runtime import AsymmetricContextManager, build_adaptive_plan, revise_adaptive_plan
from answer_runtime import render_adaptive_answer
from storage_runtime import D1_BINDING

INTERACTION_TYPES = {
    "social", "factual", "exploratory_reasoning", "continuity_recall",
    "correction_feedback", "co_creation_engineering", "execution_problem_solving",
    "emotional_support", "research_audit", "decision_prioritization",
    "artifact_creation", "meta_interaction",
}
FEEDBACK_CATEGORIES = {"intent", "context", "reasoning", "evidence", "format", "other"}
FEEDBACK_RATINGS = {"minor", "incomplete", "wrong", "wrong_mode"}
FEEDBACK_ROOT_CAUSES = {
    "missing_recent_turn", "missing_long_term_memory", "reference_resolution_failure",
    "stale_decision", "context_overflow", "wrong_context_selection",
    "insufficient_information", "other",
}
FEEDBACK_DECISIONS = {"confirmed", "partially_confirmed", "not_confirmed", "inconclusive"}
MODEL_VERSION = "aigar-adaptive-0.1-cloudflare"


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clip(value, limit=4000):
    if value is None:
        return None
    return str(value).strip()[:limit]


def _has_any_phrase(text, phrases):
    """Busca frases sem confundir palavras curtas com substrings (ex.: oi dentro de foi)."""
    for phrase in phrases:
        phrase = str(phrase).casefold().strip()
        if not phrase:
            continue
        if " " in phrase:
            if phrase in text:
                return True
        elif re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, flags=re.UNICODE):
            return True
    return False


def classify_interaction(text, reading):
    """Classifica a interação por dimensões combináveis, usando a leitura real do AIGAR."""
    t = (text or "").casefold().strip()
    intent = (reading or {}).get("intent", "unknown")
    detected = []

    def add(kind):
        if kind not in detected:
            detected.append(kind)

    if intent == "phatic" or _has_any_phrase(t, ("bom dia", "boa tarde", "boa noite", "oi", "olá", "ola", "tudo bem", "você está aí")):
        add("social")
    if intent in {"continuity", "doubt"} or bool((reading or {}).get("needs_memory")) or _has_any_phrase(t, ("lembra", "como combinamos", "na conversa anterior", "continua", "continue", "e depois", "isso que você falou")):
        add("continuity_recall")
    if intent == "correction" or _has_any_phrase(t, ("está errado", "esta errado", "não era isso", "nao era isso", "corrigindo", "quis dizer", "melhore a resposta", "ficou errado")):
        add("correction_feedback")
    if intent == "clinical_case" or _has_any_phrase(t, ("paciente com", "conduta clínica", "conduta clinica", "diagnóstico diferencial", "diagnostico diferencial")):
        add("research_audit")
    if _has_any_phrase(t, ("código", "codigo", "api", "arquitetura", "implemente", "integrar", "integração", "integracao", "debug", "endpoint", "main.py", "javascript", "python")):
        add("co_creation_engineering")
    if _has_any_phrase(t, ("pesquise", "fontes", "audite", "evidência", "evidencia", "artigos", "literatura", "pubmed", "referências", "referencias", "cite")) or bool((reading or {}).get("needs_library")):
        add("research_audit")
    if _has_any_phrase(t, ("decida", "priorize", "qual é melhor", "qual e melhor", "recomenda", "vale a pena", "compare opções", "compare opcoes")):
        add("decision_prioritization")
    if _has_any_phrase(t, ("estou mal", "estou com medo", "estou preocupado", "preciso conversar", "estou triste", "estou assustado")):
        add("emotional_support")
    if _has_any_phrase(t, ("crie um arquivo", "gere um documento", "monte um código", "monte um codigo", "escreva", "redija", "faça um pdf", "faca um pdf", "crie um relatório", "crie um relatorio")):
        add("artifact_creation")
    if _has_any_phrase(t, ("como você funciona", "como voce funciona", "sua arquitetura", "sua memória", "sua memoria", "metainteração", "metainteracao", "modo de interação", "modo de interacao")):
        add("meta_interaction")
    if _has_any_phrase(t, ("passo a passo", "como resolver", "corrija o erro", "conserte", "configure", "instale", "execute")):
        add("execution_problem_solving")
    if _has_any_phrase(t, ("por que", "como funciona", "explique", "e se", "qual mecanismo", "qual o mecanismo")):
        add("exploratory_reasoning")

    # Não permitir uma classificação vazia. A intenção do motor determina fallback.
    if not detected:
        add("factual" if intent != "unknown" else "exploratory_reasoning")

    # Prioridade: correção/continuidade explícitas precedem categorias genéricas.
    priority = [
        "correction_feedback", "continuity_recall", "co_creation_engineering",
        "artifact_creation", "execution_problem_solving", "emotional_support",
        "research_audit", "decision_prioritization", "meta_interaction",
        "exploratory_reasoning", "social", "factual",
    ]
    primary = next((kind for kind in priority if kind in detected), detected[0])
    secondaries = [kind for kind in detected if kind != primary]
    return {
        "primary_type": primary,
        "secondary_types": secondaries,
        "intent": intent,
        "context_required": bool((reading or {}).get("needs_memory")) or "continuity_recall" in detected,
        "research_required": bool((reading or {}).get("needs_library")) or "research_audit" in detected,
        "artifact_required": "artifact_creation" in detected,
        "confidence": min(0.95, 0.45 + 0.12 * max(0, len(detected) - 1)),
        "signals": {
            "language_engine_intent": intent,
            "needs_memory": bool((reading or {}).get("needs_memory")),
            "needs_library": bool((reading or {}).get("needs_library")),
            "classifier_version": "composable-heuristic-v1",
        },
    }


async def _record_interaction(env, *, interaction_id, session_id, turn_id, profile, plan, answer_mode):
    """Armazena metadados mínimos no D1; não persiste entrada/saída por padrão."""
    db = binding(env, D1_BINDING)
    if not db:
        return False, "d1_not_configured"
    session_hash = hashlib.sha256(str(session_id).encode("utf-8")).hexdigest()[:32]
    snapshot = {
        "primary_type": profile.get("primary_type"),
        "secondary_types": profile.get("secondary_types", []),
        "intent": profile.get("intent"),
        "answer_strategy": plan.get("answer_strategy"),
        "plan_revision": plan.get("revision", 0),
    }
    try:
        await db.prepare(
            """INSERT INTO adaptive_interactions
               (id, session_hash, turn_id, interaction_type, secondary_types_json,
                predicted_mode, model_version, minimal_snapshot_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        ).bind(
            interaction_id, session_hash, turn_id, profile.get("primary_type"),
            json.dumps(profile.get("secondary_types", []), ensure_ascii=False),
            answer_mode, MODEL_VERSION, json.dumps(snapshot, ensure_ascii=False), _utc_now()
        ).run()
        return True, None
    except Exception:
        # Persistência analítica nunca deve derrubar a resposta principal;
        # detalhes internos do banco não são expostos ao cliente público.
        return False, "adaptive_persistence_unavailable"


async def adaptive_schema_ready(db):
    """Confirma que as tabelas desta camada foram migradas no D1."""
    if not db:
        return False
    expected = {
        "adaptive_interactions", "adaptive_feedback", "adaptive_feedback_reviews",
        "adaptive_evaluation_cases", "adaptive_useful_interaction_logs", "adaptive_audit_log",
    }
    try:
        rows = (await db.prepare(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE 'adaptive_%'"
        ).all()).results
        found = {str(row.name) for row in rows}
        return expected.issubset(found)
    except Exception:
        return False


def _safe_useful_snapshot(value):
    """Allowlist para evitar gravar um objeto arbitrário/conversa inteira sem revisão."""
    if not isinstance(value, dict):
        return {}
    result = {}
    if isinstance(value.get("user_input"), str):
        result["user_input"] = value["user_input"][:12000]
    if isinstance(value.get("assistant_response"), str):
        result["assistant_response"] = value["assistant_response"][:16000]
    if isinstance(value.get("interaction_profile"), dict):
        profile = value["interaction_profile"]
        result["interaction_profile"] = {
            "primary_type": _clip(profile.get("primary_type"), 80),
            "secondary_types": [str(x)[:80] for x in (profile.get("secondary_types") or [])[:12]],
            "intent": _clip(profile.get("intent"), 100),
        }
    if isinstance(value.get("adaptive_plan"), dict):
        plan = value["adaptive_plan"]
        result["adaptive_plan"] = {
            "answer_strategy": _clip(plan.get("answer_strategy"), 100),
            "revision": int(plan.get("revision", 0) or 0),
            "revision_reasons": [str(x)[:100] for x in (plan.get("revision_reasons") or [])[:12]],
        }
    if isinstance(value.get("source_ids"), list):
        result["source_ids"] = [str(x)[:200] for x in value["source_ids"][:20]
                                 if isinstance(x, (str, int, float))]
    if isinstance(value.get("confidence"), (int, float)):
        result["confidence"] = max(0.0, min(1.0, float(value["confidence"])))
    # Limite total adicional; snapshot é sempre explícito, não captura automática da sessão.
    encoded = json.dumps(result, ensure_ascii=False)
    if len(encoded) > 30000:
        raise ValueError("O recorte da interação excede 30.000 caracteres.")
    return result


async def _audit_admin_action(db, actor_id, action, target_type, target_id, details=None):
    await db.prepare(
        """INSERT INTO adaptive_audit_log
           (id, actor_id, action, target_type, target_id, details_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)"""
    ).bind(
        str(uuid.uuid4()), str(actor_id), action, target_type, str(target_id or ""),
        json.dumps(details or {}, ensure_ascii=False), _utc_now()
    ).run()


async def handle_ask(body, env=None):
    text = body.get("input")
    session_id = body.get("session_id") or "default"
    if not isinstance(text, str) or not text.strip():
        return 400, {"ok": False, "status": "invalid_input", "message": "O campo 'input' deve conter texto."}
    text = text.strip()
    answer_depth = str(body.get("answer_depth") or "auto").lower()
    if answer_depth not in {"auto", "direct", "explanatory", "deep", "technical"}:
        answer_depth = "auto"
    source_fidelity = str(body.get("source_fidelity") or "faithful").lower()
    if source_fidelity not in {"extractive", "faithful", "synthesis"}:
        source_fidelity = "faithful"
    if len(text) > 20000:
        return 413, {"ok": False, "status": "input_too_large", "message": "A entrada excede o limite de 20.000 caracteres."}
    session_id = str(session_id)[:128]
    session = SESSIONS.setdefault(session_id, {
        "session_id": session_id,
        "turns": [],
        "context_cache": [],
        "last_user_input": None,
        "last_response": None,
        "reading": None,
    })
    # Migração defensiva de sessões antigas em memória.
    session.setdefault("context_cache", [])
    session.setdefault("turns", [])

    turn_id = str(uuid.uuid4())
    interaction_id = str(uuid.uuid4())

    # Preparar o núcleo antes da interpretação. O boot é cacheado no Worker;
    # em um isolate frio, recarrega os chunks iniciais das sete bibliotecas.
    try:
        core_boot = await boot_library()
        text_matrix_boot = await boot_text_matrix()
        core_chunks = list(core_boot.get("chunks", []) or []) + list(text_matrix_boot.get("chunks", []) or [])
        cognitive_context = COGNITIVE_CORE.prepare(text, core_chunks)
        cognitive_context["text_matrix"] = {
            "ready": bool(text_matrix_boot.get("ready")),
            "loaded": int(text_matrix_boot.get("loaded", 0)),
            "total": int(text_matrix_boot.get("total", len(TEXT_MATRIX_FILES))),
            "documents": text_matrix_boot.get("documents", []),
        }
    except Exception:
        cognitive_context = COGNITIVE_CORE.prepare(text, [])

    reading = LANGUAGE_ENGINE.interpret(text, cognitive_context=cognitive_context)
    reading = COGNITIVE_CORE.annotate_reading(reading, cognitive_context)
    profile = classify_interaction(text, reading)
    prior_turns = session.get("turns", [])
    context_resolution = AsymmetricContextManager().resolve(
        text, prior_turns[-40:], needs_context=bool(profile.get("context_required"))
    )
    memory_context = [
        {"role": turn.get("role"), "content": turn.get("content"),
         "speaker": turn.get("speaker"), "addressee": turn.get("addressee"),
         "turn_id": turn.get("turn_id")}
        for turn in context_resolution.get("selected_context", [])
        if turn.get("content")
    ]
    if profile.get("context_required") and memory_context:
        reading.setdefault("linguistic_analysis", {})["recent_context_available"] = True
        reading["linguistic_analysis"]["recent_context_turns"] = len(memory_context)
        reading["linguistic_analysis"]["context_dependencies"] = context_resolution.get("context_dependencies", [])

    plan = build_adaptive_plan(reading, profile, context_resolution)
    plan["cognitive_core"] = {
        "version": cognitive_context.get("version"),
        "ready": bool(cognitive_context.get("ready")),
        "available_chunks": int(cognitive_context.get("available_chunks", 0)),
        "selected_chunks": [item.get("chunk_id") for item in cognitive_context.get("selected_chunks", [])],
        "mode": cognitive_context.get("mode"),
    }
    evidence_items = []
    library_trace = {
        "kind": "library", "id": "aigar.library", "status": "missing",
        "detail": "A biblioteca não foi consultada para esta intenção.",
    }
    if reading.get("needs_library") or profile.get("research_required"):
        try:
            evidence_items = await library_search(text, reading, limit=5)
            library_trace = {
                "kind": "library", "id": "aigar.library.hybrid",
                "status": "confirmed" if evidence_items else "missing",
                "detail": (f"{len(evidence_items)} evidência(s) recuperada(s) no catálogo híbrido."
                           if evidence_items else
                           "Nenhuma evidência suficientemente relevante foi recuperada."),
            }
        except Exception as exc:
            library_trace = {
                "kind": "library", "id": "aigar.library.hybrid", "status": "missing",
                "detail": "Falha na consulta da biblioteca: " + str(exc)[:400],
            }

    # Optional Memory Lab: isolated retrieval. Failures never break the core API.
    memory_lab_result = {"ok": False, "selected_layer": [], "documents": [], "error": None}
    try:
        memory_lab_result = await MEMORY_LAB.retrieve_with_fallback(text)
        if not evidence_items and memory_lab_result.get("documents"):
            for doc in memory_lab_result["documents"][:3]:
                content = str(doc.get("content") or "").strip()
                if content:
                    evidence_items.append({
                        "text": content[:4000],
                        "source": doc.get("name"),
                        "source_key": "memory_lab",
                        "memory_layer": doc.get("layer"),
                        "memory_path": doc.get("path"),
                        "score": doc.get("score"),
                    })
    except Exception as exc:
        memory_lab_result = {"ok": False, "selected_layer": [], "documents": [], "error": str(exc)[:300]}

    plan = revise_adaptive_plan(
        plan,
        evidence_items=evidence_items,
        context_resolution=context_resolution,
        corrected_intent=(reading.get("intent") == "correction"),
    )
    question = (reading.get("linguistic_analysis") or {}).get("question") or {}
    qtype = question.get("type")
    topic = question.get("topic_head") or question.get("topic_candidate") or reading.get("scope") or "esse assunto"
    evidence_texts = []
    for item in evidence_items:
        sentence = str(item.get("text") or "").strip()
        if sentence and sentence not in evidence_texts:
            evidence_texts.append(sentence)
        if len(evidence_texts) >= 3:
            break

    # answer_mode continua por compatibilidade com a interface atual;
    # o novo answer_strategy é multidimensional e pode ter revisões.
    plan["understand_before_answer"] = True
    plan["intent"] = reading.get("intent")
    plan["depth"] = reading.get("depth")
    plan["answer_depth"] = answer_depth
    plan["source_fidelity"] = source_fidelity
    plan["use_memory"] = bool(profile.get("context_required") and memory_context)
    plan["use_library"] = bool(reading.get("needs_library") or profile.get("research_required"))
    plan["use_diagnosis"] = bool(reading.get("needs_diagnosis"))
    plan["question_type"] = qtype
    plan["semantic_goal"] = question.get("semantic_goal")
    plan["topic"] = topic
    plan["evidence"] = evidence_texts
    plan["evidence_details"] = evidence_items
    plan["steps"] = ["initialize_cognitive_core", "interpret_with_cognitive_context", "resolve_asymmetric_context", "gather_evidence", "memory_lab_optional_retrieval", "revise_plan", "select_response_strategy", "render_natural_language"]
    plan["context_resolution"] = {
        "selected_turn_ids": context_resolution.get("context_dependencies", []),
        "unresolved_references": context_resolution.get("unresolved_references", []),
        "excluded_items": context_resolution.get("excluded_items", []),
        "context_budget_used": context_resolution.get("context_budget_used", 0),
    }

    mode = (
        "social" if reading.get("intent") == "phatic"
        else "source_grounded" if evidence_texts
        else "source_unavailable" if (reading.get("needs_library") or profile.get("research_required"))
        else "context_grounded" if memory_context and profile.get("context_required")
        else "reasoned_without_library"
    )
    plan["answer_mode"] = mode

    if mode == "social":
        answer = "Oi! Aurora aqui. Manda o que você quer construir que a gente organiza."
        aurora_detail = "Resposta social breve; consulta temática não necessária."
    elif mode == "source_grounded":
        book_answer = compose_book_grounded_answer(topic, qtype, reading.get("depth", "normal"), evidence_items)
        if book_answer:
            answer = book_answer
        else:
            prefix = {
                "definition": f"{str(topic).capitalize()} — pelo material recuperado na biblioteca:",
                "function": f"A função de {topic} — pelo material recuperado na biblioteca:",
                "cause": f"Sobre a causa de {topic} — pelo material recuperado na biblioteca:",
            }.get(qtype, f"Encontrei conteúdo relevante sobre {topic}:")
            answer = prefix + "\n\n" + " ".join(evidence_texts)
            answer += "\n\nEsta resposta apresenta os trechos mais relevantes recuperados; a síntese pode ser refinada em uma camada posterior."
        aurora_detail = "Resposta apresentada a partir de evidências selecionadas pelo mecanismo de busca."
    elif mode == "context_grounded":
        previous = session.get("last_user_input")
        previous_response = session.get("last_response")
        answer = "Vou continuar a partir do contexto recente."
        if previous:
            answer += f"\n\nSua mensagem anterior foi: {previous}"
        if previous_response:
            answer += f"\n\nMinha resposta anterior foi: {previous_response}"
        aurora_detail = "Resposta contextual baseada no histórico recente selecionado pelo gerenciador de contexto."
    elif mode == "source_unavailable":
        answer = (
            f"Entendi a pergunta sobre {topic} e identifiquei que preciso consultar a biblioteca, "
            "mas não consegui recuperar evidência suficiente para responder com segurança. "
            "Isso não significa que a pergunta não tenha sentido; significa que a busca atual não encontrou suporte adequado."
        )
        aurora_detail = "A busca não encontrou evidência documental suficiente."
    else:
        answer = (
            "Entendi a solicitação e organizei sua intenção, mas não encontrei contexto ou evidência suficiente "
            "para dar uma resposta factual confiável. Se você delimitar o tema ou fornecer uma fonte, continuo a partir daí."
        )
        aurora_detail = "Resposta sem afirmações factuais não sustentadas por fonte ou contexto."

    renderer_status = {
        "used": False,
        "engine": "template_fallback",
        "reason": "Workers AI não foi chamado.",
        "answer_depth": answer_depth,
        "source_fidelity": source_fidelity,
    }
    try:
        generated_answer = await render_adaptive_answer(
            env=env,
            question=text,
            mode=mode,
            evidence_items=evidence_items,
            memory_context=memory_context,
            answer_depth=answer_depth,
            source_fidelity=source_fidelity,
            cognitive_context=cognitive_context,
        )
        if generated_answer:
            answer = generated_answer
            renderer_status = {
                "used": True,
                "engine": "workers_ai_cognitive_core_v1",
                "reason": "Resposta gerada com contexto cognitivo pré-carregado, contexto conversacional e evidências selecionadas.",
                "answer_depth": answer_depth,
                "source_fidelity": source_fidelity,
                "cognitive_core_ready": bool(cognitive_context.get("ready")),
            }
        else:
            renderer_status["reason"] = "Binding AI indisponível ou resposta vazia; mantido o fallback determinístico."
    except Exception as exc:
        renderer_status["reason"] = "Falha no renderizador; mantido o fallback determinístico: " + str(exc)[:300]

    sources = [
        {"kind": "language", "id": "aigar.language.mother", "status": "confirmed",
         "detail": "Entrada interpretada pela camada de Linguagem Materna executável."},
        library_trace,
        {"kind": "cognitive_core", "id": "aigar.cognitive_core.v1",
         "status": "confirmed" if cognitive_context.get("ready") else "missing",
         "detail": f"{cognitive_context.get('selected_count', 0)} chunk(s) cognitivo(s) selecionado(s) de {cognitive_context.get('available_chunks', 0)} disponíveis antes da interpretação."},
        {"kind": "memory", "id": "aigar.session_memory",
         "status": "confirmed" if memory_context and profile.get("context_required") else "missing",
         "detail": f"{len(memory_context)} turno(s) anterior(es) selecionados pelo cache desta sessão."
         if memory_context and profile.get("context_required")
         else "Contexto limitado à sessão em memória do Worker; persistência conversacional entre instâncias não está configurada."},
        {"kind": "reasoning", "id": "aigar.reasoning",
         "status": "confirmed" if evidence_texts else "inferred",
         "detail": f"Plano organizado com {len(evidence_texts)} evidência(s); revisão {plan.get('revision', 0)}."},
        {"kind": "aurora", "id": "aigar.aurora", "status": "confirmed", "detail": aurora_detail},
    ]

    sources.append({
        "kind": "renderer",
        "id": "aigar.context_renderer.v1",
        "status": "confirmed" if renderer_status.get("used") else "inferred",
        "detail": renderer_status.get("reason"),
    })
    confirmed = sum(1 for source in sources if source.get("status") == "confirmed" and source.get("kind") != "renderer")
    confidence = min(0.85, max(0.15, float(reading.get("confidence", 0.45)) * 0.5 + confirmed * 0.07))
    if (reading.get("needs_library") or profile.get("research_required")) and not evidence_items:
        confidence = min(confidence, 0.35)

    now = _utc_now()
    dependencies = list(context_resolution.get("context_dependencies", [])) if profile.get("context_required") else []
    user_turn = {
        "role": "user", "speaker": "human", "addressee": "AIGAR", "content": text,
        "turn_id": turn_id, "created_at": now, "interaction_type": profile.get("primary_type"),
        "references": [], "context_dependencies": dependencies, "context_status": "active", "metadata": {},
    }
    assistant_turn = {
        "role": "assistant", "speaker": "aigar", "addressee": "human", "content": answer,
        "turn_id": str(uuid.uuid4()), "created_at": _utc_now(), "interaction_type": profile.get("primary_type"),
        "references": [interaction_id], "context_dependencies": [turn_id], "context_status": "active", "metadata": {"answer_mode": mode},
    }
    session["turns"].extend([user_turn, assistant_turn])
    session["turns"] = session["turns"][-80:]
    session["context_cache"] = [turn for turn in session["turns"] if turn.get("content")][-80:]
    session["last_user_input"] = text
    session["last_response"] = answer
    session["reading"] = reading
    session["last_interaction_id"] = interaction_id
    session["last_turn_id"] = turn_id

    persistence = {"interaction_recorded": False, "status": "not_attempted"}
    if env is not None:
        persisted, persistence_error = await _record_interaction(
            env, interaction_id=interaction_id, session_id=session_id, turn_id=turn_id,
            profile=profile, plan=plan, answer_mode=mode,
        )
        persistence = {"interaction_recorded": persisted, "status": "recorded" if persisted else "unavailable"}
        if persistence_error:
            persistence["detail"] = persistence_error

    library_payload = {
        "chunks_loaded": len(evidence_items),
        "chunks": [{
            "id": item.get("chunk_id"), "source": item.get("source"), "source_key": item.get("source_key"),
            "start_page": item.get("start_page"), "end_page": item.get("end_page"),
            "score": item.get("score"), "semantic_score": item.get("semantic_score"),
            "lexical_score": item.get("lexical_score"), "source_relevance": item.get("source_relevance"),
        } for item in evidence_items],
    }
    return 200, {
        "ok": True,
        "text": answer,
        "interaction_id": interaction_id,
        "turn_id": turn_id,
        "interaction_profile": profile,
        "adaptive_plan": {key: value for key, value in plan.items() if key != "evidence_details"},
        "feedback": {
            "endpoint": "/feedback", "interaction_id": interaction_id,
            "enabled": bool(persistence.get("interaction_recorded")),
        },
        "telemetry": persistence,
        "state": {
            "session_id": session_id,
            "turns": session["turns"],
            "last_user_input": session["last_user_input"],
            "last_response": session["last_response"],
            "reading": reading,
            "context_cache_size": len(session["context_cache"]),
        },
        "sources": sources,
        "renderer": renderer_status,
        "cognitive_core": {
            "version": cognitive_context.get("version"),
            "ready": bool(cognitive_context.get("ready")),
            "available_chunks": int(cognitive_context.get("available_chunks", 0)),
            "selected_count": int(cognitive_context.get("selected_count", 0)),
            "selected_chunks": [
                {"chunk_id": item.get("chunk_id"), "source_key": item.get("source_key"), "relevance_score": item.get("relevance_score")}
                for item in cognitive_context.get("selected_chunks", [])
            ],
            "mode": cognitive_context.get("mode"),
        },
        "confidence": round(confidence, 4),
        "plan": plan,
        "library": library_payload,
        "memory_lab": {"ok": bool(memory_lab_result.get("ok")), "selected_layer": memory_lab_result.get("selected_layer", []), "documents_used": [{"path": d.get("path"), "layer": d.get("layer"), "score": d.get("score")} for d in memory_lab_result.get("documents", [])], "status": memory_lab_result.get("status"), "error": memory_lab_result.get("error")},
    }


# --- HTTP entry point: keeps the deployed Worker and frontend contract aligned. ---
