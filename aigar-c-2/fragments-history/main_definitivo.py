from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import yaml, json, datetime, subprocess, sys, hashlib, zipfile

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = BASE_DIR / "memory_cards"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"
PACK_DIR = BASE_DIR / "AIGAR_FINISH_PACK"
BIB_DIR = BASE_DIR / "biblioteca"
CACHE_DIR = BASE_DIR / ".cache_biblioteca"

for d in (LOGS_DIR, EXPORTS_DIR, CACHE_DIR):
    d.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AIGAR + Aurora", version="3.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------- Memory Cards ----------
loaded_cards = {}
active_cards = []

def list_yaml():
    return sorted([p.name for p in MEMORY_DIR.glob("*.y?ml")])

def load_card_file(name: str):
    p = MEMORY_DIR / name
    return yaml.safe_load(p.read_text(encoding="utf-8-sig"))

def reload_all():
    loaded_cards.clear()
    for n in list_yaml():
        try:
            loaded_cards[n] = load_card_file(n)
        except Exception as e:
            loaded_cards[n] = {"error": str(e)}
reload_all()

# ---------- Manifest / Autoload ----------
def read_manifest():
    f1 = PACK_DIR / "aigar_manifest.yaml"
    f2 = MEMORY_DIR / "aigar_manifest.yaml"
    for p in (f1, f2):
        if p.exists():
            try:
                return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            except Exception:
                return {}
    return {}

def autoload_from_manifest():
    global active_cards
    manifest = read_manifest()
    autoload = (manifest.get("aigar_manifest", {}) or {}).get("autoload_cards", [])
    active_cards = []
    names = list_yaml()
    for name in autoload:
        if name in names:
            try:
                loaded_cards[name] = load_card_file(name)
                active_cards.append(name)
            except Exception:
                pass
    return active_cards

# ---------- Export / Checkpoint ----------
def run_release_script():
    ps1 = PACK_DIR / "release.ps1"
    if ps1.exists() and sys.platform.startswith("win"):
        try:
            out = subprocess.check_output(
                ["powershell","-ExecutionPolicy","Bypass","-File",str(ps1)],
                cwd=str(PACK_DIR), text=True).strip()
            return {"ok": True, "artifact": out}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zipname = EXPORTS_DIR / f"AIGAR_release_{ts}.zip"
    with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as z:
        for y in MEMORY_DIR.glob("*.y?ml"):
            z.write(y, arcname=y.name)
    return {"ok": True, "artifact": str(zipname)}

def append_checkpoint(note: str):
    entry = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "note": note}
    with open(LOGS_DIR / "checkpoints.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

# ---------- Biblioteca ----------
def list_pdfs():
    return sorted(BIB_DIR.rglob("*.pdf")) if BIB_DIR.exists() else []

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

MAN_BIB = CACHE_DIR / "manifest.json"

def load_json(path: Path, default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return default

def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

def read_pdf_chunk(pdf: Path, start_page: int, max_pages: int):
    try:
        from PyPDF2 import PdfReader
    except Exception:
        return "", 0, 0, "PyPDF2 not installed"
    try:
        r = PdfReader(str(pdf))
        total = len(r.pages)
        if start_page >= total: return "", total, 0, None
        end = min(start_page + max_pages, total)
        chunks = []
        for i in range(start_page, end):
            try: txt = r.pages[i].extract_text() or ""
            except Exception: txt = ""
            if txt.strip(): chunks.append(txt.strip())
        text = " ".join("\n".join(chunks).split())
        return text, total, (end - start_page), None
    except Exception as e:
        return "", 0, 0, str(e)

def cache_path(pdf: Path):
    return CACHE_DIR / f"{pdf.name}__{sha256_file(pdf)}.txt"

# ---------- API ----------
@app.get("/api/ping")
def api_ping():
    return {"status":"ok","time":now(),"cards":len(loaded_cards),"active":active_cards}

@app.get("/api/list_cards")
def api_list_cards():
    items = []
    for n in list_yaml():
        try:
            d = load_card_file(n)
            ok = isinstance(d, dict) and (("memory_card" in d) or ("mc_base" in d))
        except Exception:
            ok = False
        items.append({"name": n, "validation": {"ok": ok}, "active": (n in active_cards)})
    return {"cards": items, "active": active_cards}

@app.post("/api/auto_load")
def api_auto_load():
    return {"ok": True, "active": autoload_from_manifest()}

@app.post("/api/export_release")
def api_export():
    return run_release_script()

@app.post("/api/checkpoint_note")
async def api_checkpoint(req: Request):
    try: data = await req.json()
    except Exception: data = {}
    note = (data.get("note") or "manual").strip()
    return append_checkpoint(note)

@app.get("/api/bib_status")
def api_bib_status():
    files = list_pdfs()
    man = load_json(MAN_BIB, {})
    out = []
    for i, p in enumerate(files):
        key = f"{p.name}::{sha256_file(p)}"
        rec = man.get(key, {"cached_pages":0,"total_pages":None})
        cp = rec.get("cached_pages") or 0
        tp = rec.get("total_pages")
        percent = float(cp)/tp*100 if tp else None
        out.append({"idx":i,"file":p.name,"cached":cp,"total":tp,"percent":percent})
    rot = load_json(LOGS_DIR / "bib_rotation.json", {"files_per_cycle":5,"pages_per_file":50,"next_start":0})
    return {"files": out, "rotation": rot}

@app.post("/api/bib_cycle")
def api_bib_cycle():
    files = list_pdfs()
    if not files: return {"ok":True,"processed":0}
    pol_path = LOGS_DIR / "bib_rotation.json"
    rot = load_json(pol_path, {"files_per_cycle":5,"pages_per_file":50,"next_start":0})
    s = rot.get("next_start",0); n = int(rot.get("files_per_cycle",5)); pages = int(rot.get("pages_per_file",50))
    man = load_json(MAN_BIB, {}); processed = []
    for i in range(n):
        idx = (s+i) % len(files)
        pdf = files[idx]
        key = f"{pdf.name}::{sha256_file(pdf)}"
        rec = man.get(key, {"cached_pages":0,"total_pages":None})
        start = int(rec.get("cached_pages",0))
        txt, total, got, err = read_pdf_chunk(pdf, start, pages)
        if err: processed.append({"file":pdf.name,"error":err}); continue
        if total: rec["total_pages"] = total
        if got>0:
            rec["cached_pages"] = start + got
            cp = cache_path(pdf)
            with open(cp, "a", encoding="utf-8") as w:
                if cp.exists() and cp.stat().st_size>0: w.write("\n\n")
                w.write(txt)
            processed.append({"file":pdf.name,"added_pages":got,"total_pages":total})
        else:
            processed.append({"file":pdf.name,"added_pages":0,"total_pages":total,"done":True})
        man[key] = rec
    rot["next_start"] = (s+n) % len(files)
    save_json(pol_path, rot); save_json(MAN_BIB, man)
    return {"ok":True,"processed":processed,"next_rotation":rot["next_start"]}

@app.post("/api/bib_policy")
async def api_bib_policy(req: Request):
    data = await req.json()
    pol_path = LOGS_DIR / "bib_rotation.json"
    rot = load_json(pol_path, {"files_per_cycle":5,"pages_per_file":50,"next_start":0})
    if "files_per_cycle" in data: rot["files_per_cycle"] = int(data["files_per_cycle"])
    if "pages_per_file" in data: rot["pages_per_file"] = int(data["pages_per_file"])
    save_json(pol_path, rot)
    return {"ok":True,"policy":rot}

@app.get("/api/notes")
def api_notes():
    path = LOGS_DIR / "user_notes.jsonl"
    out = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try: out.append(json.loads(line))
            except: pass
    return {"notes": out[-200:]}

@app.post("/api/note_save")
async def api_note_save(req: Request):
    data = await req.json()
    note = (data.get("note") or "").strip()
    tag = (data.get("tag") or "").strip()
    if not note:
        return JSONResponse({"ok": False, "error": "empty note"}, status_code=400)
    entry = {"ts": now(), "tag": tag, "note": note}
    with open(LOGS_DIR / "user_notes.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False)+"\n")
    return {"ok": True, "entry": entry}

@app.get("/ui/", response_class=HTMLResponse)
def ui():
    f = TEMPLATES_DIR / "index.html"
    return f.read_text(encoding="utf-8") if f.exists() else "<h1>AIGAR UI</h1>"
