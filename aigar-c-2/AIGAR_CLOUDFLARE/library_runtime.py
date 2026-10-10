"""Cloudflare library and retrieval services.

Index loading, Text-Matrix boot, chunk retrieval and ranking extracted from the
Worker entrypoint. The existing embedded index catalogue is injected by main.py
so its bytes remain unchanged and the current runtime behavior is preserved.
"""
from __future__ import annotations

import asyncio
import base64
import json
import re
import time
from urllib.parse import quote
from workers import fetch
from association_core import CognitiveContextCore
from memory_lab import MemoryLab
from language_runtime import CHUNK_CACHE, LIBRARY_INDEX, LANGUAGE, PORTUGUESE, STOPWORDS, find_linguistic_concept, sentences, tokens

EMBEDDED_LIBRARY_INDEXES = []  # Injected by main.py from the existing embedded catalogue.

def chunk_urls(entry):
    # The index stores the relative cache path. Keep both a raw-file route
    # and the GitHub Contents API as a fallback for Worker egress.
    name=entry["cache_file"].replace("\\","/").lstrip("/")
    path="aigar-c-2/knowledge_retrieval/cache/"+name
    return [
        "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/"+path,
        "https://api.github.com/repos/instituto-delyone/idmt-site/contents/"+path+"?ref=main",
    ]

async def load_chunk_text(entry):
    for url in chunk_urls(entry):
        try:
            r=await fetch(
                url,
                method="GET",
                headers={"Accept":"application/vnd.github+json"},
            )
            if r.status>=400:
                continue
            if "api.github.com" in url:
                data=await r.json()
                encoded=(data.get("content") or "").replace("\n","")
                if not encoded:
                    continue
                return base64.b64decode(encoded).decode("utf-8")
            return await r.text()
        except Exception:
            continue
    return None

# Catálogo explícito dos índices públicos/versionados. Evita depender do
# endpoint Contents API do GitHub no boot do Worker, que pode falhar e acionar
# silenciosamente o fallback de uma única biblioteca (Português).
INDEX_URLS = [
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/knowledge_retrieval/indexes/arquitetura_organizacao_computadores.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/knowledge_retrieval/indexes/etica.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/knowledge_retrieval/indexes/interacoes_aigar.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/knowledge_retrieval/indexes/matematica_computacional.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/knowledge_retrieval/indexes/portuguese_language_knowledge.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/knowledge_retrieval/indexes/raciocinio_logico_matematica.index.json",
    "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/knowledge_retrieval/indexes/sapiens.index.json",
]
INDEX_DIRECTORY_URL = "https://api.github.com/repos/instituto-delyone/idmt-site/contents/aigar-c-2/knowledge_retrieval/indexes?ref=main"
INDEX_CACHE = None
INDEX_CACHE_AT = 0
LIBRARY_BOOT_CACHE = None
LIBRARY_BOOT_STATUS = None
LIBRARY_BOOT_AT = 0
LIBRARY_CACHE_TTL_SECONDS = 300
COGNITIVE_CORE = CognitiveContextCore()

async def memory_lab_fetch(url, options=None):
    # Cloudflare Workers Python fetch aceita um único argumento Request/URL;
    # o Memory Lab usa a convenção fetch(url, options) de fetchers HTTP comuns.
    # Para estes endpoints públicos do GitHub, a URL já define o método GET.
    return await fetch(url)

MEMORY_LAB = MemoryLab(memory_lab_fetch)

# Índices incorporados como catálogo de segurança: o boot não depende da descoberta remota
# de arquivos de índice. O texto dos chunks continua sendo carregado sob demanda do GitHub.

async def load_library_indexes():
    """Retorna o catálogo completo mesmo quando a descoberta remota do GitHub falha."""
    global INDEX_CACHE, INDEX_CACHE_AT
    if INDEX_CACHE is not None and time.time() - INDEX_CACHE_AT < LIBRARY_CACHE_TTL_SECONDS:
        return INDEX_CACHE

    # Catálogo local embarcado contém todas as fontes e todos os metadados de chunks.
    # Isso impede que uma falha de fetch silenciosamente reduza a biblioteca a Português.
    indexes = list(EMBEDDED_LIBRARY_INDEXES)

    # Atualiza os índices por URL quando disponíveis, sem perder fontes se alguma URL falhar.
    by_key = {((idx.get("source") or {}).get("key")): idx for idx in indexes}
    for url in INDEX_URLS:
        try:
            response = await fetch(url, method="GET")
            if response.status >= 400:
                continue
            remote = json.loads(await response.text())
            key = (remote.get("source") or {}).get("key")
            if key and remote.get("chunks"):
                by_key[key] = remote
        except Exception:
            continue

    INDEX_CACHE = list(by_key.values())
    INDEX_CACHE_AT = time.time()
    return INDEX_CACHE

TEXT_MATRIX_FILES = [
    ("AIGAR-TM-01", "01_conhecimento.md"),
    ("AIGAR-TM-02", "02_linguagem.md"),
    ("AIGAR-TM-03", "03_linguagem_computador_humanos.md"),
    ("AIGAR-TM-04", "04_existencia_seres.md"),
    ("AIGAR-TM-05", "05_surgimento _evolucao_raciocínio.md"),
    ("AIGAR-TM-06", "06_raciocinio_funcionamento.md"),
    ("AIGAR-TM-07", "07_analogias_raciocinio_sistemas.md"),
    ("AIGAR-TM-08", "08_linguagem_eu_maquina.md"),
]
TEXT_MATRIX_CACHE = None
TEXT_MATRIX_AT = 0
TEXT_MATRIX_TTL_SECONDS = 300
TEXT_MATRIX_ROOT = "https://raw.githubusercontent.com/instituto-delyone/idmt-site/main/aigar-c-2/AIGAR_CLOUDFLARE/texto_matriz/"

async def boot_text_matrix():
    """Segunda leva do boot: carrega os capítulos Markdown antes da interação."""
    global TEXT_MATRIX_CACHE, TEXT_MATRIX_AT
    if TEXT_MATRIX_CACHE is not None and time.time() - TEXT_MATRIX_AT < TEXT_MATRIX_TTL_SECONDS:
        return {
            "ready": len(TEXT_MATRIX_CACHE) == len(TEXT_MATRIX_FILES),
            "loaded": len(TEXT_MATRIX_CACHE),
            "total": len(TEXT_MATRIX_FILES),
            "chunks": list(TEXT_MATRIX_CACHE),
            "mode": "warm_runtime_cache",
        }

    semaphore = asyncio.Semaphore(4)
    async def load_document(doc):
        doc_id, filename = doc
        url = TEXT_MATRIX_ROOT + quote(filename, safe="._-")
        try:
            response = await fetch(url, method="GET")
            if response.status >= 400:
                return {"id": doc_id, "source_key": "texto_matriz_aigar", "source": filename,
                        "status": "error", "error": "HTTP " + str(response.status), "text": ""}
            text = (await response.text()).strip()
            if not text or len(text) < 20:
                return {"id": doc_id, "source_key": "texto_matriz_aigar", "source": filename,
                        "status": "error", "error": "Documento vazio ou incompleto", "text": ""}
            return {"id": doc_id, "source_key": "texto_matriz_aigar", "source": filename,
                    "sequence": int(doc_id[-2:]), "status": "ready", "text": text}
        except Exception as exc:
            return {"id": doc_id, "source_key": "texto_matriz_aigar", "source": filename,
                    "status": "error", "error": str(exc)[:200], "text": ""}

    async def limited(doc):
        async with semaphore:
            return await load_document(doc)
    results = await asyncio.gather(*(limited(doc) for doc in TEXT_MATRIX_FILES))
    loaded = [item for item in results if item.get("status") == "ready" and item.get("text")]
    # Não declarar pronto se algum capítulo obrigatório falhou.
    TEXT_MATRIX_CACHE = loaded if len(loaded) == len(TEXT_MATRIX_FILES) else None
    TEXT_MATRIX_AT = time.time()
    return {
        "ready": len(loaded) == len(TEXT_MATRIX_FILES),
        "loaded": len(loaded),
        "total": len(TEXT_MATRIX_FILES),
        "chunks": loaded,
        "documents": [{"id": x["id"], "source": x["source"], "chars": len(x["text"])} for x in loaded],
        "errors": [{"id": x["id"], "source": x["source"], "error": x.get("error")} for x in results if x.get("status") != "ready"],
        "mode": "cold_boot",
    }


async def boot_library():
    """Pré-carrega até três chunks por biblioteca para aquecer o cache do Worker e do navegador."""
    global LIBRARY_BOOT_CACHE, LIBRARY_BOOT_STATUS, LIBRARY_BOOT_AT

    def make_payload(cache):
        return [
            {
                "id": cid,
                "source_key": item.get("source_key"),
                "source": item.get("source"),
                "sequence": item.get("sequence"),
                "start_page": item.get("start_page"),
                "end_page": item.get("end_page"),
                "text": item.get("text", ""),
            }
            for cid, item in cache.items()
            if item.get("text")
        ]

    if (LIBRARY_BOOT_CACHE is not None and LIBRARY_BOOT_STATUS is not None
            and time.time() - LIBRARY_BOOT_AT < LIBRARY_CACHE_TTL_SECONDS):
        COGNITIVE_CORE.prime(make_payload(LIBRARY_BOOT_CACHE))
        loaded_libraries = sum(1 for item in LIBRARY_BOOT_STATUS if item.get("chunks_loaded", 0) > 0)
        loaded_chunks = sum(int(item.get("chunks_loaded", 0) or 0) for item in LIBRARY_BOOT_STATUS)
        target_chunks = sum(int(item.get("chunks_target", 0) or 0) for item in LIBRARY_BOOT_STATUS)
        ready = bool(LIBRARY_BOOT_STATUS) and all(item.get("status") == "ready" for item in LIBRARY_BOOT_STATUS)
        return {
            "ready": ready,
            "libraries": LIBRARY_BOOT_STATUS,
            "loaded": loaded_libraries,
            "total": len(LIBRARY_BOOT_STATUS),
            "loaded_chunks": loaded_chunks,
            "total_chunks": target_chunks,
            "chunks": make_payload(LIBRARY_BOOT_CACHE),
            "mode": "warm_runtime_cache",
        }

    indexes = await load_library_indexes()
    statuses = []
    targets = []
    loaded = {}

    # Até três chunks por biblioteca. Bibliotecas com menos de três chunks
    # carregam todos os que existem, sem duplicar nem inventar conteúdo.
    for index in indexes:
        source = index.get("source", {}) or {}
        source_key = source.get("key") or "unknown"
        chunks = sorted(
            index.get("chunks", []) or [],
            key=lambda c: int(c.get("sequence", 0) or 0)
        )
        candidates = [chunk for chunk in chunks if chunk.get("id")][:3]
        targets.append({
            "source_key": source_key,
            "source": source.get("name"),
            "available": len([chunk for chunk in chunks if chunk.get("id")]),
            "candidates": candidates,
        })

    semaphore = asyncio.Semaphore(2)

    async def load_one(library, chunk):
        cid = chunk.get("id")
        if not cid:
            return None
        text = CHUNK_CACHE.get(cid)
        cache_origin = "runtime_cache" if text else "remote_loaded"
        if not text:
            async with semaphore:
                text = await load_chunk_text(chunk)
            if text:
                CHUNK_CACHE[cid] = text
        if not text:
            return None
        return {
            **chunk,
            "id": cid,
            "source_key": library["source_key"],
            "source": chunk.get("source") or library.get("source"),
            "text": text,
            "cache_origin": cache_origin,
        }

    jobs = [
        load_one(library, chunk)
        for library in targets
        for chunk in library["candidates"]
    ]
    results = await asyncio.gather(*jobs, return_exceptions=True) if jobs else []
    for result in results:
        if isinstance(result, dict) and result.get("id") and result.get("text"):
            loaded[result["id"]] = result

    for library in targets:
        key = library["source_key"]
        library_chunks = [
            item for item in loaded.values()
            if item.get("source_key") == key
        ]
        target_count = len(library["candidates"])
        loaded_count = len(library_chunks)
        if loaded_count == target_count and target_count > 0:
            status = "ready"
        elif loaded_count > 0:
            status = "partial"
        else:
            status = "error"
        statuses.append({
            "source_key": key,
            "source": library.get("source"),
            "status": status,
            "chunks_loaded": loaded_count,
            "chunks_target": target_count,
            "chunks_available": library["available"],
            "chunk_sequences": [item.get("sequence") for item in sorted(
                library_chunks, key=lambda item: int(item.get("sequence", 0) or 0)
            )],
            "detail": (
                "Cache aquecido."
                if status == "ready"
                else ("Alguns chunks não puderam ser carregados." if status == "partial"
                      else "Nenhum chunk desta biblioteca pôde ser carregado.")
            ),
        })

    LIBRARY_BOOT_CACHE = loaded
    COGNITIVE_CORE.prime(make_payload(loaded))
    LIBRARY_BOOT_STATUS = statuses
    LIBRARY_BOOT_AT = time.time()
    loaded_libraries = sum(1 for item in statuses if item.get("chunks_loaded", 0) > 0)
    loaded_chunks = len(loaded)
    target_chunks = sum(int(item.get("chunks_target", 0) or 0) for item in statuses)
    ready = bool(statuses) and all(item.get("status") == "ready" for item in statuses)
    return {
        "ready": ready,
        "libraries": statuses,
        "loaded": loaded_libraries,
        "total": len(statuses),
        "loaded_chunks": loaded_chunks,
        "total_chunks": target_chunks,
        "chunks": make_payload(loaded),
        "mode": "cold_boot",
    }


async def load_chunks():
    """Compatibilidade: retorna somente o conjunto de referência já carregado."""
    boot = await boot_library()
    return list(LIBRARY_BOOT_CACHE.values()) if LIBRARY_BOOT_CACHE is not None else []


SEMANTIC_EXPANSIONS = {
    "função": {"papel","finalidade","serve","servir","funcionamento"},
    "funciona": {"funcionamento","mecanismo","processo","operação"},
    "explicar": {"explicação","conceito","definição","entendimento"},
    "definição": {"conceito","significado","definição"},
    "causa": {"motivo","razão","porque","origem"},
    "efeito": {"consequência","resultado","impacto"},
    "processo": {"etapas","mecanismo","procedimento","processo"},
    "comparar": {"diferença","semelhança","comparação"},
    "diferença": {"contraste","distinção","diferença"},
    "limite": {"limites","continuidade","aproximação"},
    "derivada": {"derivação","taxa","variação"},
    "integral": {"integração","área","antiderivada"},
    "computador": {"computação","processador","hardware","arquitetura"},
    "arquitetura": {"organização","computador","processador","memória"},
    "ética": {"moral","princípio","conduta","responsabilidade"},
    "lógica": {"raciocínio","proposição","inferência","dedução"},
    "matemática": {"cálculo","número","equação"},
    "português": {"língua","linguagem","gramática","sintaxe","semântica"},
}

SOURCE_PROFILES = {
    "portuguese_language_knowledge": {"português","gramática","língua","linguagem","sintaxe","semântica","oração","frase","período","verbo","sujeito","pronomes"},
    "matematica_computacional": {"matemática","cálculo","limite","derivada","integral","função","equação","número","álgebra","geometria"},
    "arquitetura_organizacao_computadores": {"arquitetura","computador","processador","memória","hardware","cpu","sistema","organização","barramento"},
    "etica": {"ética","moral","princípio","conduta","responsabilidade","dever","valor","justiça"},
    "raciocinio_logico_matematica": {"lógica","raciocínio","proposição","inferência","dedução","concurso","matemática","problema"},
    "interacoes_aigar": {"aigar","aurora","conversa","memória","interação","diálogo"},
    "sapiens": {"humanidade","história","evolução","civilização","sociedade","agricultura","revolução","harari"},
}

def semantic_expand(text):
    base=tokens(text)
    expanded=set(base)
    for term in list(base):
        expanded.update(SEMANTIC_EXPANSIONS.get(term,set()))
    return expanded

def source_relevance(query, source_key):
    q=semantic_expand(query)
    profile=SOURCE_PROFILES.get(source_key,set())
    if not q or not profile:
        return 0.0
    return min(1.0, len(q & profile) / max(2, int(len(profile)*0.35)))

async def library_search(query,reading,limit=5):
    indexes = await load_library_indexes()
    qinfo = reading.get("linguistic_analysis",{}).get("question",{})
    qtype = qinfo.get("type")
    topic = (qinfo.get("topic_head") or reading.get("scope") or "").lower().strip()
    query_terms = semantic_expand(query)
    topic_terms = semantic_expand(topic)
    q = query_terms or topic_terms
    candidates = []
    noise_markers=("isbn","ficha catalogográfica","sumário","referências","bibliografia","universidade federal")
    definition_markers=("é uma","é um","são","significa","consiste em","refere-se","define-se","definido como","definida como","constitui","constituída por")
    concept=find_linguistic_concept(topic)

    # Primeiro escolhemos bibliotecas/chunks pelo índice. Só depois baixamos
    # o texto dos candidatos. Assim o boot não precisa carregar todos os livros.
    indexed_candidates=[]
    for index in indexes:
        source = index.get("source", {}) or {}
        source_key = source.get("key") or ""
        source_score = source_relevance(query, source_key)
        chunks = index.get("chunks", []) or []
        for chunk in chunks:
            cid=chunk.get("id")
            if not cid:
                continue
            chunk_meta = {**chunk, "source_key": source_key}
            # O índice fornece identidade/página; o texto só é necessário
            # quando o chunk entra na lista de candidatos.
            page_hint = 0.0
            if topic and str(chunk.get("source","")).lower().find(topic) >= 0:
                page_hint = 0.05
            indexed_candidates.append((
                source_score + page_hint,
                float(chunk.get("sequence",0) or 0),
                chunk_meta
            ))

    indexed_candidates.sort(key=lambda x:(-x[0],x[1]))
    # Para uma pergunta temática, trazemos alguns chunks por biblioteca
    # potencialmente relevante; não o corpus inteiro.
    selected_meta=[]
    seen_sources=set()
    for score,_,meta in indexed_candidates:
        sk=meta.get("source_key","")
        if sk in seen_sources and len(selected_meta)>=max(limit*4,8):
            continue
        selected_meta.append(meta)
        seen_sources.add(sk)
        if len(selected_meta)>=max(limit*4,8):
            break

    async def ensure_text(entry):
        cid=entry["id"]
        text=CHUNK_CACHE.get(cid)
        if not text:
            text=await load_chunk_text(entry)
            if text:
                CHUNK_CACHE[cid]=text
        return {**entry,"text":text or ""}

    chunks=[]
    for meta in selected_meta:
        item=await ensure_text(meta)
        if item.get("text"):
            chunks.append(item)

    for chunk in chunks:
        source_key=chunk.get("source_key","")
        source_score=source_relevance(query,source_key)
        for sentence in sentences(chunk["text"]):
            lower=sentence.lower()
            st=semantic_expand(sentence)
            literal=tokens(sentence)
            literal_q=tokens(query)
            lexical_overlap=len(literal_q & literal)
            semantic_overlap=len(q & st)
            topic_overlap=len(topic_terms & st) if topic_terms else 0
            topic_hit=1 if topic and re.search(rf"\b{re.escape(topic)}\b",lower) else 0

            if not lexical_overlap and not semantic_overlap and not topic_overlap and not topic_hit and not source_score:
                continue

            lexical_score=lexical_overlap/max(1,len(literal_q))
            semantic_score=semantic_overlap/max(1,len(q))
            topic_score=min(1.0,topic_overlap/max(1,len(topic_terms))) if topic_terms else 0.0
            score=0.30*lexical_score + 0.40*semantic_score + 0.15*topic_score + 0.15*source_score + topic_hit*0.50

            if any(marker in lower for marker in noise_markers):
                score-=0.50

            if qtype=="definition":
                if topic_hit and any(marker in lower for marker in definition_markers):
                    score+=0.80
                elif topic_hit:
                    score+=0.15
                if concept and any(marker in lower for marker in definition_markers):
                    score+=0.10
            elif qtype=="function" and any(x in lower for x in ("função","serve","finalidade")):
                score+=0.35
            elif qtype=="comparison" and any(x in lower for x in ("diferença","compar","semelhan","distin")):
                score+=0.30
            elif qtype=="cause" and any(x in lower for x in ("causa","porque","razão","motivo")):
                score+=0.30

            candidates.append((
                score, semantic_score, lexical_score, source_score,
                float(chunk.get("sequence",0)), sentence, chunk
            ))

    candidates.sort(key=lambda x:(-x[0],-x[1],-x[2],-x[3],x[4],len(x[5])))
    selected=[]
    seen=set()
    for score,semantic_score,lexical_score,source_score,_,sentence,chunk in candidates:
        key=(chunk["id"],sentence)
        if key in seen:
            continue
        seen.add(key)
        selected.append({
            "text":sentence,
            "chunk_id":chunk["id"],
            "source":chunk.get("source"),
            "source_key":chunk.get("source_key"),
            "start_page":chunk.get("start_page"),
            "end_page":chunk.get("end_page"),
            "score":round(max(0.0,score),6),
            "semantic_score":round(semantic_score,6),
            "lexical_score":round(lexical_score,6),
            "source_relevance":round(source_score,6)
        })
        if len(selected)>=limit:
            break
    return selected
