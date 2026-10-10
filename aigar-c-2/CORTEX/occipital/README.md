# Occipital — Placeholder da interface visual

**Estado:** estrutura reservada; arquivos ainda não migrados.

**Conteúdo previsto:** ponto de entrada visual (por exemplo, index), assets, components e outros recursos de apresentação que forem confirmados no inventário.

A analogia com o córtex occipital é organizacional: esta pasta representa a camada visual do software, não uma equivalência literal com a função biológica do cérebro.

**Próxima etapa:** inventariar os arquivos de interface existentes e planejar a migração sem duplicar nem apagar arquivos.


## Interface migrada — MIG-015
Os arquivos `index.html`, `app.js` e `style.css` foram movidos da subpasta `aigar_ui_chat_mvp/web/` para esta pasta em um lote estrutural. O backend e os dados de memória da aplicação independente foram preservados no caminho original. Os caminhos de assets e integrações ainda aguardam auditoria; não assumir que a interface já está funcional após a mudança.


## Integração estática com o backend MVP
A interface desta pasta é servida pelo backend em `aigar_ui_chat_mvp/server/main.py`, que aponta `WEB` para `CORTEX/occipital/`. Os caminhos `/static/style.css` e `/static/app.js` são servidos pelo mount estático do FastAPI; as rotas `/health` e `/api/*` continuam pertencendo ao backend. Esta ligação foi atualizada estaticamente no lote MIG-016; não foi executada nem validada em runtime.
