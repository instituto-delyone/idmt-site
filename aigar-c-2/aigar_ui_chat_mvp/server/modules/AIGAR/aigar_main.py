
from pathlib import Path
import json

try:
    import yaml
except Exception:
    yaml = None

MC_STATE = {
    "authenticated": False,
    "files": [],
    "details": []
}

def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]

def _scan_memory_cards():
    root = _project_root()
    mdir = root / "memory_cards"
    if not mdir.exists():
        return
    candidates = []
    for ext in ["*.yaml", "*.yml"]:
        candidates.extend(mdir.glob(ext))
    if not candidates:
        return
    for f in sorted(candidates):
        entry = {"file": f.name}
        if yaml:
            try:
                data = yaml.safe_load(f.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    entry["id"] = data.get("id") or data.get("name") or data.get("module", {}).get("name")
                    entry["version"] = data.get("version") or data.get("module", {}).get("version")
                    entry["escopo"] = data.get("escopo")
                    entry["data"] = data.get("data") or data.get("date")
            except Exception as e:
                entry["parse_error"] = str(e)
        MC_STATE["files"].append(f.name)
        MC_STATE["details"].append(entry)
    MC_STATE["authenticated"] = True

try:
    _scan_memory_cards()
except Exception:
    pass

def run(task: str, payload: dict) -> dict:
    msg = (payload.get("message") or "").strip()

    if task == "ack_pause":
        return {"ok": True, "reply": "ok"}
    if task == "install_rule":
        return {"ok": True, "reply": "Regra (~) registrada (MVP)."}    
    if task == "explain_no_suggest":
        return {"ok": True, "reply": "Explicação fornecida (sem sugestões). (MVP)"}    
    if task == "command":
        return {"ok": True, "reply": f"AIGAR: executando '{msg}' (MVP)."}

    if MC_STATE.get("authenticated") and MC_STATE["files"]:
        files_list = ", ".join(MC_STATE["files"])
        return {
            "ok": True,
            "reply": f"AIGAR autenticado ✅ — Memory Cards carregados: {files_list}"
        }
    else:
        return {"ok": True, "reply": "AIGAR online. (Nenhum memory card encontrado em /memory_cards)"}
