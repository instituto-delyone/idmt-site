# 📖 README — AIGAR_UI_CHAT_MVP

## 1) Entrar na pasta do projeto
No PowerShell:
```powershell
cd "$env:USERPROFILE\Desktop\AIGAR_UI_CHAT_MVP"
```
*(troque o caminho se a pasta estiver em outro lugar — o importante é parar na raiz onde existe a pasta `server/`).*

---

## 2) Criar e ativar ambiente virtual (opcional, mas recomendado)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
👉 Se der bloqueio no `Activate.ps1`, rode este comando **uma vez só**:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Depois tente ativar de novo.

---

## 3) Instalar dependências
```powershell
python -m pip install --upgrade pip
python -m pip install "uvicorn[standard]" fastapi pyyaml
```

---

## 4) Rodar o servidor
Na **raiz do projeto** (`…\AIGAR_UI_CHAT_MVP\`):
```powershell
python -m uvicorn server.main:app --reload
```

Se tudo certo, vai aparecer:
```
Uvicorn running on http://127.0.0.1:8000
```

---

## 5) Abrir a interface
No navegador (Chrome/Edge):  
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 6) Atalhos de comando na UI
- `!comando` → ordem direta  
- `/explica` → modo sem sugestões  
- `~regra` → instalar instrução  
- `——` → pausa (responde “ok”)  

---

📌 Dica: sempre que fechar o terminal e voltar depois, é só:
1. Ativar a venv:
```powershell
.\.venv\Scripts\Activate.ps1
```
2. Rodar o servidor:
```powershell
python -m uvicorn server.main:app --reload
```
