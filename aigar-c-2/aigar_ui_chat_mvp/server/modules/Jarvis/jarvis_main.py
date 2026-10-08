def run(task: str, payload: dict) -> dict:
    msg = (payload.get("message") or "").strip()
    if task == "ack_pause":
        return {"ok": True, "reply": "ok"}
    if task == "explain_no_suggest":
        return {"ok": True, "reply": "Sem sugestões. Explicação objetiva registrada (MVP)."}    
    if task == "install_rule":
        return {"ok": True, "reply": "Instrução (~) instalada (MVP)."}    
    if task == "command":
        return {"ok": True, "reply": f"Jarvis: comando recebido → {msg} (MVP)."} 
    return {"ok": True, "reply": "Jarvis online. Use !, /, ~ ou ——."}
