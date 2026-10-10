# Occipital — interface visual do AIGAR-C

**Estado atual:** interface estática presente nesta pasta; estrutura congelada. Não mover nem renomear arquivos durante a revisão de indexações.

**Arquivos atuais:** `index.html`, `app.js` e `style.css`. O backend permanece separado em `aigar_ui_chat_mvp/server/main.py` e serve esta pasta como conteúdo estático.

A analogia com o córtex occipital é organizacional: esta pasta representa a camada visual do software, não uma equivalência literal com a função biológica do cérebro.


## Interface migrada — MIG-015
Os arquivos `index.html`, `app.js` e `style.css` foram movidos da subpasta `aigar_ui_chat_mvp/web/` para esta pasta em um lote estrutural. O backend e os dados de memória da aplicação independente foram preservados no caminho original. Os caminhos de assets e integrações ainda aguardam auditoria; não assumir que a interface já está funcional após a mudança.


## Integração estática com o backend MVP
A interface desta pasta é servida pelo backend em `aigar_ui_chat_mvp/server/main.py`, que aponta `WEB` para `CORTEX/occipital/`. Os caminhos `/static/style.css` e `/static/app.js` são servidos pelo mount estático do FastAPI; as rotas `/health` e `/api/*` continuam pertencendo ao backend. Esta ligação foi atualizada estaticamente no lote MIG-016; não foi executada nem validada em runtime.
