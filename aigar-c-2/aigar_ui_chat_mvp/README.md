# AIGAR UI — Chat MVP

Interface minimalista estilo ChatGPT + backend FastAPI local com endpoint /api/chat.
Módulos plugáveis (AIGAR/Jarvis) e pasta separada para memory cards.

## Instalação
1) Python 3.10+
2) (Opcional) venv
3) pip install fastapi uvicorn pyyaml

## Execução
uvicorn server.main:app --reload
Abra http://127.0.0.1:8000

## Estrutura
aigar_ui_chat_mvp/
├─ server/
│  ├─ main.py
│  └─ modules/
│     ├─ AIGAR/
│     │  ├─ manifest.yaml
│     │  └─ aigar_main.py
│     └─ Jarvis/
│        ├─ manifest.yaml
│        └─ jarvis_main.py
├─ web/
│  ├─ index.html
│  ├─ style.css
│  └─ app.js
└─ memory_cards/   # coloque seus memory_card_*.yaml aqui

## Atalhos de mensagem
!comando  -> ordem direta
/explica  -> modo sem sugestões
~regra    -> instalar instrução
——        -> pausa/ack

