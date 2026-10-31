# 📖 README — AIGAR_UI_CHAT_MVP

## 1) Entrar na pasta do projeto

No PowerShell, a partir do local em que o repositório foi clonado:

```powershell
cd "<caminho-do-repositorio>\aigar-c-2\aigar_ui_chat_mvp"
```

A pasta atual deve conter `server\main.py`, `memory_cards\` e `requirements.txt`.

## 2) Criar e ativar o ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, use a orientação oficial de política de execução do Python/PowerShell para o seu ambiente. Não é necessário alterar a política global da máquina.

## 3) Instalar dependências

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4) Rodar o servidor

Na raiz de `aigar_ui_chat_mvp`:

```powershell
python -m uvicorn server.main:app --reload
```

O servidor local ficará disponível em `http://127.0.0.1:8000`.

## 5) Abrir a interface

Abra no navegador:

```text
http://127.0.0.1:8000
```

Healthcheck:

```text
http://127.0.0.1:8000/health
```

## 6) Atalhos de comando na UI

- `!comando` → ordem direta
- `/explica` → modo sem sugestões
- `~regra` → instalar instrução
- `——` → pausa (responde “ok”)

## 7) Retomar o trabalho

Depois de fechar o terminal:

```powershell
cd "<caminho-do-repositorio>\aigar-c-2\aigar_ui_chat_mvp"
.\.venv\Scripts\Activate.ps1
python -m uvicorn server.main:app --reload
```

O ambiente virtual é local e não deve ser enviado ao Git. As dependências são reconstruídas pelo arquivo `requirements.txt`.
