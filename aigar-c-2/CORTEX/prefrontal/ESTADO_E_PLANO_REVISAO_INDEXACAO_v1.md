# AIGAR-C — Estado congelado e fila de revisão de indexações

**Status da etapa 1 — MOVIMENTAÇÃO ESTRUTURAL: CONCLUÍDA.**  
**Status da etapa 2 — REVISÃO ESTÁTICA DAS OITO FASES: CONCLUÍDA; validação de execução pendente.**  
**Regra de congelamento:** a partir deste registro, não mover, renomear, redistribuir nem reorganizar arquivos. A estrutura atual é a referência fixa para todo o trabalho seguinte.

## 1. Snapshot de referência

- Repositório: `instituto-delyone/idmt-site`
- Branch de trabalho: `neurocognitive-migration`
- Pull request: [#13](https://github.com/instituto-delyone/idmt-site/pull/13) — permanece Draft, não mesclado.
- Snapshot estrutural usado como base: `bb0d51d5fd00e20601edf3b3a587fb5004069998`
- Diretório arquitetural: `aigar-c-2/CORTEX/`
- A branch `main` não foi alterada por merge nem houve deploy nesta etapa.
- Não foram executados testes como parte deste registro.

Este SHA identifica a árvore congelada **antes deste documento de planejamento**. Os próximos commits podem acrescentar apenas registros e corrigir referências de código/configuração; não devem alterar a localização dos arquivos.

## 2. Escopo e regras da etapa 2

Objetivo único: manter o comportamento do AIGAR e trocar referências antigas pelos caminhos e nomes atuais quando o código ainda apontar para a estrutura anterior.

- Corrigir imports, caminhos de arquivos, nomes de módulos, manifestos, configurações e indexações.
- Não redesenhar arquitetura, não adicionar capacidades e não reescrever a lógica funcional.
- Não mover nem renomear arquivos.
- Não apagar arquivos por parecerem redundantes.
- Não modificar o Cloudflare Worker, seus bindings, configurações, contratos, nomes de símbolos ou workflow próprio. Se uma referência do Worker aparecer, registrá-la como dependência protegida e não a editar nesta etapa sem autorização específica.
- Não executar testes nem fazer merge/deploy enquanto a tradução está em andamento.
- Trabalhar em lotes pequenos, com commit por lote e descrição objetiva do que foi corrigido.

## 3. Ordem prioritária de revisão

A prioridade é definida pelo impacto no caminho de execução do AIGAR: inicialização primeiro, depois dependências que ela chama, dados carregados em runtime, persistência/recuperação, integração e só então documentação e automação.

### P0 — Entrada do runtime e cadeia de imports

**Arquivos para revisar primeiro**
- `aigar-c-2/AIGAR_RUNTIME/main.py`
- `aigar-c-2/AIGAR_RUNTIME/__init__.py`
- `aigar-c-2/AIGAR_RUNTIME/requirements.txt`
- `aigar-c-2/AIGAR_RUNTIME/README.md`
- `aigar-c-2/CORTEX/thalamus/models.py`
- `aigar-c-2/CORTEX/thalamus/context_router.py`
- `aigar-c-2/CORTEX/thalamus/linguistic_interpreter.py`
- `aigar-c-2/CORTEX/language/language_network_adapter.py`
- `aigar-c-2/CORTEX/prefrontal/prefrontal_controller.py`
- `aigar-c-2/CORTEX/prefrontal/aurora.py`
- `aigar-c-2/CORTEX/memory/working_memory.py`
- `aigar-c-2/CORTEX/memory/hippocampal_memory.py`
- `aigar-c-2/CORTEX/engram/knowledge_retrieval.py`
- `aigar-c-2/CORTEX/reasoning_engine/diagnosis.py`
- `aigar-c-2/CORTEX/sensory/ingress.py`
- `aigar-c-2/CORTEX/sara/runtime_status.py`

**Conferir:** imports absolutos/relativos, nomes de classes importadas, diretórios base calculados com `Path(__file__)`, carregamento dinâmico por string, e se o entrypoint ainda aponta para módulos nos diretórios antigos. Corrigir só referências comprovadamente desatualizadas; manter os contratos e endpoints existentes.

### P1 — Interpretador e arquivos de dados da linguagem

**Arquivos**
- `aigar-c-2/CORTEX/language/interpreter.py`
- `aigar-c-2/CORTEX/language/language.json`
- `aigar-c-2/CORTEX/language/portuguese_language_knowledge.json`
- `aigar-c-2/CORTEX/language/test_interpreter.py`
- `aigar-c-2/CORTEX/language/portuguese_language_knowledge.pdf`
- `aigar-c-2/CORTEX/language/README.md`
- `aigar-c-2/knowledge_retrieval/sources/portuguese_language_knowledge.pdf`

**Conferir:** caminhos relativos usados pelo interpretador para abrir os JSONs, fallbacks para a pasta antiga `language_network/`, caminhos de corpus/PDF e se o PDF em `CORTEX/language/` é referência documental ou fonte ativa. Não alterar conteúdo dos dados nem duplicar/mover fontes.

### P2 — Recuperação de conhecimento: índices, cache e manifests

**Arquivos de código e configuração**
- `aigar-c-2/knowledge_retrieval/retriever.py`
- `aigar-c-2/knowledge_retrieval/semantic_retriever.py`
- `aigar-c-2/knowledge_retrieval/config.json`
- `aigar-c-2/knowledge_retrieval/README.md`
- `aigar-c-2/knowledge_retrieval/BOOTSTRAP_LOCAL.md`
- `aigar-c-2/knowledge_retrieval/bootstrap_sapiens.py`
- `aigar-c-2/knowledge_retrieval/__init__.py`
- `aigar-c-2/knowledge_encoding/encode_knowledge.py`
- `aigar-c-2/knowledge_encoding/encode_existing_chunks.py`
- `aigar-c-2/knowledge_encoding/README.md`
- `aigar-c-2/knowledge_retrieval/public_indexes/README.md`

**Conjunto de indexação a conferir**
- `aigar-c-2/knowledge_retrieval/indexes/*.index.json`
- `aigar-c-2/knowledge_retrieval/public_indexes/*.index.json`
- `aigar-c-2/knowledge_retrieval/cache/*/manifest.json`
- `aigar-c-2/knowledge_retrieval/.gitignore`

**Conferir:** referências antigas a `AIGAR_LIBRARY/`, nomes de diretórios anteriores, caminhos de cache, URL base do repositório, caminhos públicos versus locais, schema dos índices e resolução de IDs para chunks. Não reprocessar documentos nem regenerar índices nesta subetapa; primeiro corrigir somente as referências de localização.

### P3 — Memória, estado de sessão e continuidade

**Arquivos**
- `aigar-c-2/CORTEX/memory/working_memory.py`
- `aigar-c-2/CORTEX/memory/hippocampal_memory.py`
- `aigar-c-2/CORTEX/engram/knowledge_retrieval.py`
- `aigar-c-2/CORTEX/thalamus/models.py`
- `aigar-c-2/aigar_ui_chat_mvp/server/main.py`
- `aigar-c-2/aigar_ui_chat_mvp/memory_cards/*.yaml`
- `aigar-c-2/aigar_ui_chat_mvp/server/modules/AIGAR/manifest.yaml`
- `aigar-c-2/aigar_ui_chat_mvp/server/modules/Jarvis/manifest.yaml`

**Conferir:** imports do armazenamento de sessão, nomes/caminhos das memory cards, diretórios de persistência, manifests de módulos e formatos de estado. Distinguir memória da aplicação de chat da memória do runtime principal; não uni-las por semelhança de nome.

### P4 — Controlador, formulação de resposta e Diagnosis

**Arquivos**
- `aigar-c-2/CORTEX/prefrontal/prefrontal_controller.py`
- `aigar-c-2/CORTEX/prefrontal/aurora.py`
- `aigar-c-2/CORTEX/reasoning_engine/diagnosis.py`
- `aigar-c-2/Diagnosis/` (árvore existente do motor separado)
- `aigar-c-2/CORTEX/worker_bridge/PLACEHOLDER.md`

**Conferir:** imports antigos de Reasoning/Diagnosis, classes e nomes renomeados, rotas/contratos de integração e referências que presumem que Diagnosis já esteja conectado ao runtime. Não implementar integração nova nem tratar placeholders como código executável.

### P5 — Interface e servidor de chat independente

**Arquivos**
- `aigar-c-2/CORTEX/occipital/index.html`
- `aigar-c-2/CORTEX/occipital/app.js`
- `aigar-c-2/CORTEX/occipital/style.css`
- `aigar-c-2/CORTEX/occipital/README.md`
- `aigar-c-2/aigar_ui_chat_mvp/server/main.py`
- `aigar-c-2/aigar_ui_chat_mvp/README.md`
- `aigar-c-2/aigar_ui_chat_mvp/README_AIGAR_UI_CHAT_MVP.md`

**Conferir:** diretório servido pelo FastAPI, rotas `/static`, referências CSS/JS, assets e links de API. A interface está em `CORTEX/occipital/`; o backend permanece em `aigar_ui_chat_mvp/server/` e é uma aplicação independente.

### P6 — Configurações, contratos, manifestos e indexação transversal

**Arquivos**
- `aigar-c-2/association_network/AIGAR_ARCHITECTURE_v1.yaml`
- `aigar-c-2/association_network/AIGAR_RUNTIME_CONTRACT_v1.json`
- `aigar-c-2/association_network/AIGAR_RUNTIME_CONTRACT_RECONCILIATION_v1.md`
- `aigar-c-2/association_network/AIGAR_SOURCE_MANIFEST_v1.json`
- `aigar-c-2/association_network/AIGAR_SOURCE_MANIFEST_AUDIT_v1.md`
- `aigar-c-2/association_network/AIGAR_EVIDENCE_MAP_v1.md`
- `aigar-c-2/AIGAR_PHASES/phases.json`
- `aigar-c-2/AIGAR_NEUROCOGNITIVE_MIGRATION_MAP_v1.md`
- `aigar-c-2/CORTEX/README.md`
- `aigar-c-2/CORTEX/prefrontal/DECISIONS.md`

**Conferir:** caminhos de módulos e fontes nos JSON/YAML, lista de módulos ativos, manifests, caminhos de dados e contratos que ainda descrevem os nomes anteriores. Atualizar documentos de contrato apenas para refletir caminhos/nomes efetivos; não mudar semântica dos contratos neste trabalho.

### P7 — Automação, instruções de execução e testes (revisão estática apenas)

**Arquivos**
- `.github/workflows/aigar-runtime-validation.yml`
- `.github/workflows/aigar-cognitive-core.yml` — leitura protegida; não editar nesta etapa se tocar o Worker
- `aigar-c-2/AIGAR_RUNTIME/test_runtime.py`
- `aigar-c-2/CORTEX/language/test_interpreter.py`
- `aigar-c-2/knowledge_retrieval/tests/test_retriever.py`
- `aigar-c-2/AIGAR_CLOUDFLARE/README.md` — leitura protegida
- `aigar-c-2/AIGAR_CLOUDFLARE/wrangler.jsonc` — leitura protegida
- `aigar-c-2/AIGAR_CLOUDFLARE/wrangler.storage.example.jsonc` — leitura protegida

**Conferir:** paths de execução, diretórios de trabalho, módulos compilados, nomes de testes e filtros de `paths` que ainda referem diretórios antigos. Não disparar testes nem alterar o Worker/workflow do Worker; registrar qualquer mudança protegida como pendência separada.

### P8 — Documentação, histórico e subsistemas fora do caminho crítico

**Áreas**
- `aigar-c-2/AIGAR_RECONSTRUCTION/`
- `aigar-c-2/AIGAR_PHASES/` (após P6)
- `aigar-c-2/association_network/README.md`
- `aigar-c-2/knowledge_encoding/`
- `aigar-c-2/AIGAR_CLOUDFLARE/` (apenas documentação não operacional e leitura protegida)
- `aigar-c-2/aigar-jarvis-sync/`
- `aigar-c-2/drive-do-aigar/`
- `aigar-c-2/fragments-history/`
- `aigar-c-2/conversational-engine/`
- documentação histórica, memory cards e artigos sobre arquitetura

**Conferir:** referências informativas, exemplos de comandos e nomes históricos que possam induzir a erro. Não atualizar arquivos históricos só para eliminar a nomenclatura antiga quando ela descreve corretamente a arquitetura da época. Separar “referência operacional quebrada” de “registro histórico válido”.

## 4. Como executar a revisão

Em cada lote:
1. Procurar referências antigas nos arquivos da prioridade atual.
2. Confirmar se a referência é operacional e realmente aponta para um caminho antigo.
3. Corrigir apenas essa referência, sem mover arquivos nem refatorar comportamento.
4. Registrar arquivos alterados e motivo em um commit pequeno.
5. Avançar para a prioridade seguinte.

## 5. Estado atual resumido

- [x] Etapa 1 — arquivos selecionados movidos para a estrutura aprovada e registrada no GitHub.
- [x] Estrutura congelada: nenhuma movimentação ou renomeação adicional autorizada.
- [ ] Etapa 2 — P0: cadeia de imports e caminhos do entrypoint.
- [ ] P1: dados linguísticos.
- [ ] P2: índices/cache/recuperação.
- [ ] P3: memória e sessão.
- [ ] P4: controlador/Aurora/Diagnosis.
- [ ] P5: interface e backend independente.
- [ ] P6: contratos e manifestos.
- [ ] P7: workflows e testes, revisão estática sem executar.
- [ ] P8: documentação histórica e subsistemas secundários.

**Critério para considerar a etapa 2 concluída:** todas as referências operacionais relevantes foram reconciliadas com a árvore congelada, e as pendências protegidas/históricas estão explicitamente registradas. Testes e validação de execução ficam para uma autorização posterior.

## Execução sequencial da etapa 2 — registro estático

**Autorização do responsável:** executar as oito fases em sequência sem pausas para aprovação entre lotes. A estrutura permanece congelada; nenhuma movimentação, renomeação ou reorganização de arquivos é permitida.

- P0 — Entrada/imports: corrigida a importação de DiagnosisAdapter para o caminho existente CORTEX.reasoning_engine.diagnosis; demais imports do entrypoint apontam para os módulos presentes na árvore atual.
- P1 — Linguagem: interpretador resolve language.json e portuguese_language_knowledge.json relativos ao próprio módulo; o adaptador importa o contrato canônico de CORTEX.thalamus.models. O workflow agora referencia o teste no caminho novo CORTEX/language/test_interpreter.py.
- P2 — Recuperação/indexação: normalizada a resolução de cache_file no retriever para aceitar separadores Windows e caminhos relativos a cache/, preservando fallback por source_key e id; índices existentes não foram regenerados.
- P3 — Memória: os adaptadores importam os contratos canônicos; o backend da UI mantém os cartões em aigar_ui_chat_mvp/memory_cards/, caminho existente.
- P4 — Integração: os módulos de runtime importam os caminhos CORTEX atuais; o adaptador de Diagnosis continua declarando missing até existir conexão com o motor clínico real.
- P5 — Interface: o backend serve CORTEX/occipital/ e mantém os endpoints da API sem alteração.
- P6 — Configurações/manifests: AIGAR_PHASES/phases.json já aponta para os módulos CORTEX existentes; não foram reescritos contratos históricos que não têm equivalência operacional comprovada.
- P7 — Workflows: o workflow de validação foi atualizado para incluir CORTEX/**, compilar o diretório novo e apontar para o teste linguístico em seu caminho atual. Nenhum teste foi executado manualmente nesta tarefa.
- P8 — Documentação/fechamento: README e auditoria do manifesto foram corrigidos para não apontar o adaptador atual para o diretório inexistente Diagnosis/.

### Limites e pendências que permanecem explícitos

1. O motor clínico especializado indicado historicamente por docs/Js/engine.js e a base docs/knowledge_base/ não foram encontrados no snapshot; não foram substituídos por candidatos apenas pelo nome.
2. O workflow de validação continua configurado para executar testes automaticamente em eventos de PR que correspondam aos caminhos; a execução manual de testes não foi solicitada nem realizada aqui.
3. O Cloudflare Worker e seu workflow próprio permaneceram intocados.
4. Não houve movimentação/renomeação de arquivos, merge ou deploy.

**Status das oito fases:** revisão estática concluída para os caminhos operacionais inspecionados; validação de execução continua pendente.