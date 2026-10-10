# AIGAR C-2 — Inventário de Workers, Vias, Bindings e Rotas
Versão: 1.0  
Branch: `neurocognitive-migration`  
Data do inventário: 2026-10-10  
Status: levantamento estático parcial da árvore de código; sem deploy, sem alterações de roteamento.

## 1. Objetivo e limites

Este documento registra a topologia que o código atualmente declara, para comparar a implementação real com o mapa neurocognitivo. Os nomes neuroanatômicos são guias de projeto; não representam equivalência biológica literal.

O inventário foi feito por leitura estática dos arquivos desta branch. Não foi feito teste de carga, inspeção de bindings secretos do painel Cloudflare, nem confirmação de estado em produção. Portanto, “declarado no código” não significa “ativo em produção”.

## 2. Resumo executivo

- O entrypoint Cloudflare observado é `aigar-c-2/AIGAR_CLOUDFLARE/main.py`, configurado como `main.py` no `wrangler.jsonc`, com nome de Worker `aigar-api`.
- Esse arquivo contém a classe `Default(WorkerEntrypoint)` e um roteador manual com endpoints de saúde, linguagem/memória, recuperação da biblioteca, perguntas, feedback, autenticação e administração.
- O mesmo entrypoint também importa `CognitiveContextCore` e `MemoryLab`, mantém caches de biblioteca/texto-matriz, chama o binding de IA, acessa R2/D1 e inicia um Workflow de construção da biblioteca.
- O `wrangler.jsonc` declara o binding `AI` e o Workflow `AIGAR_LIBRARY_BUILDER`; o código também procura `AIGAR_LIBRARY_BUCKET` (R2) e `AIGAR_DB` (D1). Esses dois últimos bindings não aparecem no arquivo `wrangler.jsonc` inspecionado. Podem estar definidos por configuração externa/ambiente, mas isso precisa ser confirmado antes de concluir que persistência está configurada.
- Existe um Workflow `LibraryBuilderWorkflow` dentro do próprio `main.py`; isso não equivale a um Worker de biblioteca separado.
- O runtime Python local `AIGAR_RUNTIME/main.py` é outra arquitetura/entrypoint: FastAPI com `/health` e `/perguntar`. Não há evidência neste inventário de que ele seja o entrypoint Cloudflare atual.
- Não foram encontrados Service Bindings entre Workers cognitivos separados nesta configuração examinada. A comunicação entre componentes no Worker atual é majoritariamente por chamadas de função/imports; chamadas de rede incluem fetches a fontes GitHub e ao serviço externo MedUnity.
- A execução de CI mais recente consultada falhou: compilação passou, mas 4 testes falharam e 4 passaram. A migração, portanto, não deve ser declarada validada.

## 3. Arquivos e responsabilidades observadas

| Arquivo / componente | Responsabilidade observada | Classificação arquitetural |
|---|---|---|
| `AIGAR_CLOUDFLARE/main.py` | Entry point, roteador HTTP, orquestração adaptativa, binding de IA, autenticação, administração, persistência e Workflow | Gateway + orquestração; ainda concentra várias responsabilidades |
| `AIGAR_CLOUDFLARE/language_runtime.py` | Implementação linguística atual do Worker, regras de intenção, profundidade, conceitos e composição de resposta fundamentada | Módulo de linguagem extraído do entrypoint; mantém a lógica anterior |
| `AIGAR_CLOUDFLARE/library_runtime.py` | Boot da biblioteca e Texto-Matriz, catálogo/índices, carregamento de chunks, cache e busca de evidências | Módulo de recuperação extraído; o catálogo embutido permanece em `main.py` e é injetado no módulo |
| `AIGAR_CLOUDFLARE/context_runtime.py` | Seleção assimétrica de contexto e construção/revisão do plano adaptativo | Módulo de contexto e planejamento extraído; sem alterar as regras existentes |
| `AIGAR_CLOUDFLARE/http_runtime.py` | Respostas JSON, CORS, extração da origem e leitura segura do corpo JSON | Utilitários HTTP extraídos; rotas continuam em `main.py` |
| `AIGAR_CLOUDFLARE/answer_runtime.py` | Renderização de resposta por Workers AI usando os chunks e o contexto fornecidos | Renderer extraído; mantém o mesmo prompt e parâmetros de geração |
| `AIGAR_CLOUDFLARE/cloudflare_bindings.py` | Resolução de bindings do ambiente Cloudflare | Helper compartilhado extraído sem alterar nomes de bindings |
| `AIGAR_CLOUDFLARE/storage_runtime.py` | Autenticação MedUnity, acesso R2/D1, upload e processamento de documentos, Workflow da biblioteca e listagem de documentos | Serviços administrativos/armazenamento extraídos; rotas continuam no entrypoint |
| `AIGAR_CLOUDFLARE/association_core.py` | `CognitiveContextCore`: prepara/ranqueia chunks e monta contexto compacto para a pergunta | Núcleo de seleção contextual importado pelo `library_runtime.py` |
| `AIGAR_CLOUDFLARE/memory_lab/engine.py` | `MemoryLab`: recuperação de memória imediata, curto prazo e longo prazo | Subsistema de memória importado pelo `library_runtime.py` |
| `AIGAR_CLOUDFLARE/wrangler.jsonc` | Declara Worker `aigar-api`, entrypoint `main.py`, binding `AI` e Workflow `AIGAR_LIBRARY_BUILDER` | Configuração de deploy |
| `AIGAR_RUNTIME/main.py` | FastAPI local: interpretação, memória, biblioteca, diagnóstico, controle e Aurora | Runtime separado; não confundir com o Worker Cloudflare |
| `AIGAR_RUNTIME/language_network_bridge.py` | Adapta interpretador linguístico para o runtime | Adaptador de linguagem |
| `AIGAR_RUNTIME/working_state.py` | Estado de conversa recente em memória do processo | Estado transitório; não é persistência de longo prazo |
| `AIGAR_RUNTIME/hippocampal_memory.py` | Recupera turnos recentes da sessão | Protótipo/analogia de memória contextual |
| `AIGAR_RUNTIME/knowledge_retrieval.py` | Adapta o retriever da biblioteca e retorna rastreabilidade | Recuperação documental |
| `AIGAR_RUNTIME/prefrontal_controller.py` | Seleção heurística de evidências e plano simples | Controle/plano inicial |
| `AIGAR_RUNTIME/aurora.py` | Produz a resposta do runtime local | Formulação de resposta; verificar separadamente em futura análise |

## 4. Binding e recursos configuracionais

| Binding/recurso | Referência no código | Presença no `wrangler.jsonc` inspecionado | Próxima verificação |
|---|---|---|---|
| Workers AI | `AI`; modelo `@cf/meta/llama-3.1-8b-instruct` | Sim: `ai.binding = AI` | Confirmar modelo habilitado e comportamento/limites reais |
| Workflow da biblioteca | `AIGAR_LIBRARY_BUILDER`; classe `LibraryBuilderWorkflow` | Sim, em `workflows` | Verificar execução, retries, idempotência e tratamento de falha |
| Bucket R2 | `AIGAR_LIBRARY_BUCKET` | Não aparece no arquivo examinado | Verificar configuração de ambiente e nome exato do binding |
| Banco D1 | `AIGAR_DB` | Não aparece no arquivo examinado | Verificar configuração de ambiente, migrations e schema |
| Serviço de autenticação MedUnity | `https://medunity-api.dr-delyone.workers.dev` | Não é binding; é URL externa chamada por `fetch` | Definir timeout, tratamento de indisponibilidade e política de autenticação |
| Índices da biblioteca | URLs GitHub e diretório `AIGAR_LIBRARY/indexes` com `ref=main` | Não é binding | Confirmar versionamento imutável, cache e fallback quando GitHub falhar |
| Texto-Matriz | Lista `TEXT_MATRIX_FILES`, boot e cache no Worker | Não é binding separado | Confirmar os oito arquivos esperados, versão carregada e estratégia de invalidação |

## 5. Rotas encontradas no Worker `aigar-api`

O roteador normaliza o prefixo `/aigar/api` e trata `OPTIONS` para CORS.

| Método | Rota | Papel |
|---|---|---|
| GET | `/health` | Saúde do serviço e disponibilidade declarada de bindings |
| GET | `/memory/status` | Inicializa/consulta status do `MemoryLab` |
| GET | `/texto-matriz/boot` | Carrega/consulta Texto-Matriz |
| GET | `/library/boot` | Carrega/consulta biblioteca |
| POST | `/perguntar` | Fluxo principal de pergunta |
| POST | `/feedback` | Registra feedback no D1 |
| POST | `/auth/login` | Validação via serviço MedUnity |
| GET | `/auth/me` | Consulta identidade via serviço MedUnity |
| GET | `/admin/storage` | Estado de R2/D1; exige autenticação administrativa |
| GET | `/admin/documents` | Lista documentos; exige autenticação administrativa |
| POST | `/admin/upload` | Upload de PDF para R2 e registro no D1; tenta iniciar Workflow |
| GET | `/admin/feedback` | Lista feedback; exige autenticação administrativa |
| GET | `/admin/feedback/metrics` | Métricas de feedback; exige autenticação administrativa |
| POST | `/admin/useful-logs` | Registra snapshot mínimo para avaliação; exige autenticação administrativa |
| GET | `/admin/useful-logs` | Lista registros úteis; exige autenticação administrativa |

As rotas administrativas passam por `require_admin()`. O inventário não substitui testes de autorização nem auditoria de segurança. Não foi feita chamada de rede às rotas; esta tabela descreve o código.

## 6. Caminho de uma pergunta observado estaticamente

1. `Default.fetch` recebe e normaliza a rota.
2. `POST /perguntar` lê o JSON e chama `handle_ask(body, self.env)`.
3. `handle_ask` chama `boot_library()` e `boot_text_matrix()` importados de `library_runtime.py`, prepara contexto com `COGNITIVE_CORE.prepare(...)`, consulta `MEMORY_LAB.retrieve_with_fallback(...)` e usa o binding `AI` para produzir a resposta.
4. A resposta é serializada em JSON por `make_response`.

Esse fluxo ocorre dentro do mesmo Worker; `CognitiveContextCore` e `MemoryLab` são componentes importados, não Workers separados nesta configuração.

## 7. Vias de comunicação e concentração de responsabilidades

### Vias atualmente visíveis
- Chamadas de função/imports dentro de `main.py`: orquestração, seleção contextual, memória, armazenamento, autenticação e administração.
- `fetch` para fontes externas: índices/arquivos no GitHub e serviço de autenticação MedUnity.
- Bindings: `AI`, Workflow, e referências no código a R2/D1.
- Workflow: `LibraryBuilderWorkflow` é iniciado após upload, se o binding estiver disponível.

### Riscos de concentração que merecem medição
- O mesmo arquivo de entrada faz roteamento, lógica cognitiva, recuperação, renderização, persistência, upload, autenticação e administração.
- A busca/boot da biblioteca e Texto-Matriz pode participar do caminho de cada pergunta; medir cache-hit, tempo de boot e latência total para saber quanto trabalho é repetido.
- Dependências externas podem propagar falhas para o fluxo principal se não houver timeout/fallback adequado.
- Estado em memória de um Worker pode não se comportar como memória persistente nem ser compartilhado de forma consistente entre instâncias.
- Ter mais Workers só ajuda se reduzir acoplamento ou isolar carga/falhas; chamadas síncronas em cadeia podem aumentar latência e pontos de falha.

## 8. Topologia-alvo proposta — ainda não implementada

A extração de `language_runtime.py` e `library_runtime.py` apenas separa código existente dentro do mesmo Worker. Não cria novos Workers nem conecta automaticamente os módulos do runtime local em `CORTEX/`. Esses módulos têm contratos e dependências diferentes e exigem um adaptador compatível antes de substituir a implementação Cloudflare.

| Worker proposto | Responsabilidade | Dependências/canais propostos | Critério para extrair |
|---|---|---|---|
| `aigar-api` | Gateway, autenticação de entrada, compatibilidade das rotas e agregação de respostas | Service Bindings versionados para serviços internos | Deve permanecer fino; preservar todos os endpoints públicos |
| `aigar-cognition` | Interpretar intenção, organizar contexto ativo, planejar e coordenar resposta | Contratos JSON para memória e conhecimento | Quando contratos e testes de regressão estiverem definidos |
| `aigar-library` | Boot, indexação leve/recuperação e seleção de evidências | Storage/índices e API interna estável | Após medir custo/latência e isolar operações de biblioteca |
| `aigar-memory` | Memória persistente, recuperação episódica, retenção e esquecimento | D1/R2 após schema, autorização e política de retenção | Só depois de definir modelo de dados e separar memória de sessão |
| `aigar-observability` (opcional) | Agregar métricas e rastros de vias | Eventos mínimos, IDs de correlação e métricas sem dados sensíveis | Criar apenas se a observabilidade atual for insuficiente |

Nenhum Worker auxiliar desta tabela foi criado, ligado por Service Binding ou publicado como resultado deste inventário.

## 9. Contrato mínimo recomendado para cada via

Cada chamada entre componentes deve registrar, conforme aplicável:
- `request_id` e `session_id` não sensíveis ou pseudonimizados;
- nome/versionamento do contrato;
- etapa de origem e destino;
- timeout, resultado, duração e classe de erro;
- política explícita de retry (somente para operações idempotentes);
- proveniência de documentos/trechos e estado de incerteza;
- limite de payload e de chunks;
- comportamento de fallback, sem converter falha de fonte em falsa certeza.

Evitar guardar conteúdo integral de conversa em logs de telemetria por padrão. Métricas devem priorizar contadores, duração, códigos de erro e IDs de correlação, com minimização de dados.

## 10. Validação de CI consultada

Execução consultada: [GitHub Actions run 38043211532](https://github.com/instituto-delyone/idmt-site/actions/runs/38043211532).

- Compilação `compileall`: passou.
- Instalação de dependências: passou.
- Testes: **4 falharam, 4 passaram**.
- Falhas observadas:
  1. `test_executable_language_is_connected_to_runtime`: entrada “O que foi a Revolução Agrícola” interpretada como `phatic`, esperado `concept_basic`.
  2. `test_continuity_uses_session_memory`: entrada “continue” interpretada como `unknown`, esperado `continuity`.
  3. `test_definition_question_is_structured`: pergunta de definição interpretada como `phatic`, esperado `concept_basic`.
  4. `test_function_question_is_scoped`: tipo de pergunta retornado como `None`, esperado `function`.

Essas falhas são problemas reais de comportamento/contrato do interpretador e do runtime, não falhas causadas apenas pelo renomeamento. Precisam ser corrigidas e testadas antes de declarar a migração validada. O inventário não as corrigiu.

## 11. Próxima sequência segura

1. Confirmar os bindings R2/D1 reais no ambiente Cloudflare e se o `wrangler.jsonc` é a fonte de configuração completa.
2. Completar o mapa de dependências e de chamadas externas, incluindo o local real de `memory_lab.py` e o Workflow.
3. Corrigir os quatro testes de linguagem/runtime sem alterar os contratos públicos.
4. Adicionar testes de contrato para cada rota e testes de falha para GitHub, AI, R2, D1 e Workflow.
5. Instrumentar latência, cache hit/miss, timeouts e erros por etapa antes de decidir a divisão física em Workers.
6. Extrair primeiro uma responsabilidade por vez, preservando a rota pública e com rollback.
7. Atualizar este inventário com SHA, testes executados e resultado real de cada etapa.

## 12. Estado da mudança

- Documento novo de inventário; sem alteração de código de runtime.
- Branch de trabalho: `neurocognitive-migration`.
- PR #13 permanece draft e não mesclado no momento da consulta.
- Nenhum deploy de produção realizado por esta etapa.
