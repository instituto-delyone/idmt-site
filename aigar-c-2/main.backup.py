
# -*- coding: utf-8 -*-
"""
AIGAR UI — servidor FastAPI (main.py)
Compatível com a estrutura do MVP:
C:\aigar_ui_chat_mvp\
  ├─ server\main.py   ← (este arquivo)
  ├─ memory_cards\*.yaml
  ├─ checkpoints\
  ├─ exports\
  └─ web\ (index.html, app.js, style.css)
"""
from __future__ import annotations

import json
import os
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

try:
    import yaml
except Exception as e:
    yaml = None  # será checado no startup

APP_ROOT = Path(__file__).resolve().parents[1]  # .../aigar_ui_chat_mvp
WEB_DIR = APP_ROOT / "web"
CARDS_DIR = APP_ROOT / "memory_cards"
CHECKPOINTS_DIR = APP_ROOT / "checkpoints"
EXPORTS_DIR = APP_ROOT / "exports"

app = FastAPI(title="AIGAR UI Server")

# Estado do app
app.state.cards: Dict[str, Any] = {}
app.state.canal_preferencial: bool = True  # modo preferencial ligado por padrão


def _ensure_dirs() -> None:
    for p in (CARDS_DIR, CHECKPOINTS_DIR, EXPORTS_DIR):
        p.mkdir(parents=True, exist_ok=True)


def _safe_get(d: Dict[str, Any], *keys, default=None):
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


def load_memory_cards() -> Dict[str, Any]:
    """Lê todos os .yaml da pasta memory_cards e devolve dict {nome:conteúdo}"""
    cards: Dict[str, Any] = {}
    if not CARDS_DIR.exists():
        return cards
    for path in sorted(CARDS_DIR.glob("*.yaml")):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) if yaml else {}
            if not isinstance(data, dict):
                data = {"_raw": data}
            data["_file"] = path.name
            cards[path.name] = data
        except Exception as e:
            cards[path.name] = {"error": str(e), "_file": path.name}
    return cards


def summarize_cards(cards: Dict[str, Any]) -> List[str]:
    """Cria um pequeno sumário por card para exibir em ~status"""
    lines: List[str] = []
    for name, data in cards.items():
        if "error" in data:
            lines.append(f"• {name} — erro ao ler: {data['error']}")
            continue
        title = (
            _safe_get(data, "titulo")
            or _safe_get(data, "title")
            or _safe_get(data, "identidade", "nome")
            or _safe_get(data, "identity", "name")
            or "sem título"
        )
        ethics = (
            _safe_get(data, "etica")
            or _safe_get(data, "ética")
            or _safe_get(data, "ethics")
        )
        escopo = _safe_get(data, "escopo") or _safe_get(data, "scope")
        tag = []
        if title and title != "sem título":
            tag.append(str(title))
        if ethics:
            tag.append("ética✅")
        if escopo:
            tag.append("escopo")
        if not tag:
            tag.append("ok")
        lines.append(f"• {name} — " + ", ".join(tag))
    return lines


def help_text() -> str:
    return (
        "Comandos disponíveis:\n"
        "~status — lista cards carregados e flags\n"
        "~checkpoint — salva estado em /checkpoints\n"
        "~export — cria um .zip em /exports com cards e último checkpoint\n"
        "~estabelecer canal preferencial — ativa estilo rápido e direto\n"
        "~ajuda — mostra este texto"
    )


@app.on_event("startup")
async def on_startup():
    _ensure_dirs()
    if yaml is None:
        raise RuntimeError("Dependência ausente: PyYAML (pyyaml). Instale com: pip install pyyaml")
    app.state.cards = load_memory_cards()


# --- Rotas da UI ---

if WEB_DIR.exists():
    app.mount("/ui", StaticFiles(directory=WEB_DIR, html=True), name="ui")

@app.get("/", include_in_schema=False)
async def root():
    # Redireciona para a UI se existir; senão devolve mensagem simples
    if WEB_DIR.exists():
        return RedirectResponse(url="/ui")
    return PlainTextResponse("AIGAR UI server online. Envie POST para /api/chat.")


# --- API ---

def reply_plain(user_text: str) -> str:
    estilo = "AIGAR (direto, amigável)" if app.state.canal_preferencial else "AIGAR"
    return f"{estilo} — recebi: {user_text}"


@app.post("/api/chat")
@app.post("/chat")  # compatibilidade
async def chat(req: Request):
    payload = await req.json()
    user_msg = (payload.get("message") or "").strip()

    # Comandos-raiz
    if user_msg.startswith("~status"):
        cards = app.state.cards
        lines = summarize_cards(cards)
        flag = "ON" if app.state.canal_preferencial else "OFF"
        info = [
            "AIGAR autenticado ✅",
            f"canal_preferencial: {flag}",
            f"cards carregados: {len(cards)}",
        ]
        return JSONResponse({"reply": "\n".join(info + lines)})

    if user_msg.startswith("~checkpoint"):
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = CHECKPOINTS_DIR / f"checkpoint_{ts}.log"
        data = {
            "timestamp": ts,
            "canal_preferencial": app.state.canal_preferencial,
            "cards": list(app.state.cards.keys()),
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return JSONResponse({"reply": f"🧩 Checkpoint salvo em {path.name}."})

    if user_msg.startswith("~export"):
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        zip_path = EXPORTS_DIR / f"AIGAR_EXPORT_{ts}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            # inclui memory cards
            if CARDS_DIR.exists():
                for p in CARDS_DIR.glob("*.yaml"):
                    z.write(p, arcname=f"memory_cards/{p.name}")
            # inclui último checkpoint (se houver)
            if CHECKPOINTS_DIR.exists():
                checkpoints = sorted(CHECKPOINTS_DIR.glob("checkpoint_*.log"))
                if checkpoints:
                    z.write(checkpoints[-1], arcname=f"checkpoints/{checkpoints[-1].name}")
        return JSONResponse({"reply": f"📦 export: {zip_path.name} pronto em /exports."})

    if user_msg.startswith("~estabelecer canal preferencial"):
        app.state.canal_preferencial = True
        return JSONResponse({"reply": "⚡ Canal preferencial ativado."})

    if user_msg.startswith("~ajuda"):
        return JSONResponse({"reply": help_text()})

    # Mensagens normais: eco com estilo + (opcional) uso de identidade
    cards = app.state.cards
    identidade = None
    for card in cards.values():
        identidade = identidade or _safe_get(card, "identidade", "nome") or _safe_get(card, "identity", "name")
    base = reply_plain(user_msg)
    if identidade:
        base = base.replace("AIGAR", str(identidade))
    return JSONResponse({"reply": base})


@app.get("/api/status")
@app.get("/status")
async def api_status():
    lines = summarize_cards(app.state.cards)
    return JSONResponse({
        "ok": True,
        "canal_preferencial": app.state.canal_preferencial,
        "cards": list(app.state.cards.keys()),
        "summary": lines,
    })
