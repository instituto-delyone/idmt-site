import os, json, hashlib
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

try:
    import yaml
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT.parent / "CORTEX" / "occipital"
MODULES = Path(__file__).resolve().parent / "modules"
MCARDS = ROOT / "memory_cards"

app = FastAPI(title="AIGAR UI — Chat MVP")

# static / front
app.mount("/static", StaticFiles(directory=str(WEB)), name="static")

@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(WEB / "index.html")

@app.get("/health")
def health():
    return {"ok": True}

def load_manifest(p: Path):
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return json.loads(text)
    if yaml:
        return yaml.safe_load(text)
    return json.loads(text)

def import_entry(module_dir: Path, entry_point: str):
    ep = module_dir / entry_point
    if not ep.exists():
        raise FileNotFoundError(f"entry_point não existe: {ep}")
    spec = spec_from_file_location(module_dir.name, str(ep))
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def call_module(name: str, task: str, payload: dict):
    for child in MODULES.iterdir():
        if not child.is_dir(): 
            continue
        mf = child / "manifest.yaml"
        if not mf.exists():
            mf = child / "manifest.json"
        if not mf.exists():
            continue
        manifest = load_manifest(mf)
        if manifest.get("module", {}).get("name") != name:
            continue
        entry = manifest["module"]["entry_point"]
        integ = manifest["module"].get("integrity", {})
        if "sha256" in integ:
            code = (child / entry).read_bytes()
            sha = hashlib.sha256(code).hexdigest()
            if sha != integ["sha256"]:
                raise ValueError(f"Falha de integridade para {name}")
        mod = import_entry(child, entry)
        if not hasattr(mod, "run"):
            raise AttributeError(f"{name} sem função run(task, payload)")
        return mod.run(task, payload)
    raise ValueError(f"Módulo '{name}' não encontrado")

@app.get("/api/modules")
def list_modules():
    names = []
    for child in MODULES.iterdir():
        mf = child / "manifest.yaml"
        if mf.exists():
            try:
                m = load_manifest(mf)
                names.append(m["module"]["name"])
            except Exception:
                pass
    return {"modules": sorted(names)}

@app.get("/api/memory-cards")
def list_mcards():
    items = []
    if MCARDS.exists():
        for p in sorted(MCARDS.glob("*.yaml")):
            items.append(p.name)
    return {"files": items}

@app.post("/api/chat")
async def chat(req: Request):
    body = await req.json()
    msg = (body.get("message") or "").strip()
    target = (body.get("module") or "Jarvis").strip()

    # mapear tarefa
    task = "chat"
    if msg.startswith("!"):
        task = "command"
    elif msg.startswith("/"):
        task = "explain_no_suggest"
    elif msg.startswith("~"):
        task = "install_rule"
    elif set(msg) in ({"—"}, {"-"}):
        task = "ack_pause"

    payload = {"message": msg}
    try:
        result = call_module(target, task, payload)
        reply = result.get("reply") or result.get("msg") or json.dumps(result, ensure_ascii=False)
    except Exception as e:
        reply = f"[erro] {type(e).__name__}: {e}"

    return JSONResponse({"reply": reply})
