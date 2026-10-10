# AIGAR-C — Inventário de migração neurocognitiva v1

- Repositório: `instituto-delyone/idmt-site`
- Branch auditada: `neurocognitive-migration`
- Commit-base auditado: `6cee97808ad62c7fe5203b753d82e9fdde25f933`
- Escopo: inventário estático de caminhos e dependências; o inventário foi criado antes da migração; consulte a seção 'Registro de migração executada' abaixo para os movimentos efetivamente realizados.
- Estado: **migração estrutural iniciada — referências ainda não traduzidas; não executar testes**.

## Regras obrigatórias

1. Preservar a lógica existente durante a migração estrutural.
2. Registrar cada movimentação real como par caminho antigo → caminho novo, com commit e atualização de referências associadas.
3. Não apagar arquivos por parecerem redundantes; confirmar consumidores e dependências primeiro.
4. Não executar testes antes de terminar a fase de renomeação/movimentação e atualização das referências.
5. Não fazer merge nem deploy nesta etapa.
6. **Cloudflare Worker está fora do escopo e não deve ser alterado**: arquivos, nomes, símbolos, configurações, bindings e chaves JSON ficam intocados.
7. Placeholders representam ideias ainda não implementadas; não devem fingir que já existe funcionalidade.

## 1. Runtime conversacional ativo — inventário por import direto

O ponto de entrada atual é `aigar-c-2/AIGAR_RUNTIME/main.py`. Ele importa diretamente os módulos abaixo. Estes são os primeiros candidatos à migração porque fazem parte do caminho de execução do runtime.

| Caminho atual | Função observada no código | Destino arquitetural proposto | Decisão inicial |
|---|---|---|---|
| `AIGAR_RUNTIME/main.py` | API FastAPI, endpoints `/health` e `/perguntar`, orquestração de todos os adaptadores | Manter como entrypoint durante a migração; destino final a decidir sem quebrar comando de inicialização | MANTER por enquanto |
| `AIGAR_RUNTIME/models.py` | Contratos Pydantic: leitura, estado, rastros de fonte, request e response | Contratos compartilhados de runtime; destino exato precisa ser decidido antes de mover | REVISAR |
| `AIGAR_RUNTIME/language_network_adapter.py` | Carrega `language_network/interpreter.py` e converte resultado em `ConversationReading` | `CORTEX/language/` | MOVER candidato |
| `language_network/interpreter.py` | Interpretador determinístico da linguagem; lê `language.json` e `portuguese_language_knowledge.json` | `CORTEX/language/` ou manter como motor externo com adaptador | MOVER candidato; preservar os JSONs associados |
| `language_network/language.json` | Dados/regras usados pelo interpretador | Junto ao interpretador ou caminho de dados equivalente | MOVER junto somente após mapear caminhos |
| `language_network/portuguese_language_knowledge.json` | Base de conhecimento linguístico carregada pelo interpretador | Junto ao interpretador ou caminho de dados equivalente | MOVER junto somente após mapear caminhos |
| `AIGAR_RUNTIME/working_memory.py` | Armazena estado de sessão em memória do processo; mantém até 40 entradas | `CORTEX/memory/` | MOVER candidato |
| `AIGAR_RUNTIME/hippocampal_memory.py` | Adaptador de continuidade; usa os turnos da sessão, sem recall persistente conectado | `CORTEX/memory/` | MOVER candidato |
| `AIGAR_RUNTIME/knowledge_retrieval.py` | Adaptador do runtime para `KnowledgeRetriever` | Adaptador de recuperação em `CORTEX/memory/` ou camada de integração a decidir | REVISAR antes de mover |
| `knowledge_retrieval/retriever.py` | Busca híbrida sobre índices e chunks de cache local | `knowledge_retrieval/` permanece como pacote de dados/recuperação até mapear dependências | MANTER por enquanto |
| `knowledge_retrieval/semantic_retriever.py` | Expansão semântica determinística e pontuação de fontes | `knowledge_retrieval/` junto ao retriever | MANTER por enquanto |
| `AIGAR_RUNTIME/prefrontal_controller.py` | Seleciona até três sentenças por sobreposição lexical e monta plano de resposta | `CORTEX/prefrontal/` | MOVER candidato |
| `AIGAR_RUNTIME/aurora.py` | Apresenta resposta com base no plano e nas evidências/contexto disponíveis | `CORTEX/language/` (formulação) ou camada de saída a decidir | REVISAR |
| `AIGAR_RUNTIME/diagnosis.py` | Adaptador de fronteira; motor Diagnosis separado ainda não conectado | Adaptador de integração/worker bridge, conforme contrato existente | MOVER candidato após mapear integração |
| `AIGAR_RUNTIME/requirements.txt` | Dependências Python do runtime (FastAPI, Uvicorn, Pydantic) | Manter junto ao entrypoint ou consolidar depois de verificar instruções de instalação | MANTER por enquanto |
| `AIGAR_RUNTIME/test_runtime.py` | Testes existentes do runtime | Permanecer associados ao runtime até o fim da migração; não executar ainda | MANTER por enquanto |
| `AIGAR_RUNTIME/README.md` | Documenta execução, arquitetura e renomeações históricas | Atualizar depois da migração de caminhos | ATUALIZAR após migração |

## 2. Arquivos com função ainda não confirmada no caminho ativo

| Caminho atual | Observação estática | Decisão |
|---|---|---|
| `AIGAR_RUNTIME/linguistic_interpreter.py` | Implementa outro interpretador simples, mas `main.py` não o importa diretamente; o adapter carrega `language_network/interpreter.py` | REVISAR consumidores e referências antes de classificar como legado |
| `AIGAR_RUNTIME/__init__.py` | Arquivo de pacote Python | Manter até a reorganização de imports ficar definida |
| `AIGAR_RUNTIME/README.md` | Descreve nomes históricos que divergem de alguns caminhos atuais; deve ser reconciliado usando a árvore real, sem presumir que texto antigo prova que um arquivo ainda existe | Atualizar após o inventário completo |

## 3. Subsistemas existentes fora do runtime direto

| Caminho atual | Conteúdo/função observada | Destino inicial |
|---|---|---|
| `association_network/` | README, YAML de arquitetura, contratos e manifestos de integração | Avaliar como arquitetura/contratos; não duplicar dentro de CORTEX sem necessidade |
| `knowledge_encoding/` | Codificador de PDF/TXT/MD em chunks, IDs, índices e cache | Manter como pipeline de ingestão/encoding; integração com a nova árvore será registrada |
| `knowledge_retrieval/` | Retriever, router semântico, config, índices, cache e documentação | Manter pacote de recuperação e dados até o mapa de dependências ficar completo |
| `language_network/` | Interpretador, dados linguísticos, documentação e teste próprio | Integrar ao domínio `CORTEX/language/` somente após mapear os caminhos dos dados |
| `AIGAR_PHASES/` | Configuração de fases | Revisar consumidores antes de mover |
| `AIGAR_RECONSTRUCTION/` | Documentação de reconstrução | Documentação de projeto; considerar `CORTEX/prefrontal/` somente após revisar conteúdo e referências |
| `AIGAR_NEUROCOGNITIVE_*.md/.txt` e `AIGAR_RENAME_PLAN_v1.md` | Dicionário, mapa, roadmap e plano de renomeações existentes | Preservar; reconciliar documentação sem apagar histórico |
| `aigar_ui_chat_mvp/` | Aplicação separada com servidor FastAPI, UI HTML/CSS/JS, módulos AIGAR/Jarvis e memory cards | Tratar como aplicação separada; não presumir que faz parte do runtime neurocognitivo sem mapear sua relação |
| `biblioteca/` | Fontes documentais (PDF/TXT e outros arquivos) | Manter como corpus-fonte; não mover junto com código |
| `aigar-jarvis-sync/`, `drive-do-aigar/`, `fragments-history/`, `conversational-engine/` | Pacotes/artefatos históricos e de sincronização | Revisar separadamente; não misturar com o runtime sem evidência de dependência |
| PDFs e materiais de referência na raiz de `aigar-c-2/` | Documentos de estudo | Fora da migração de código |

## 4. Destino dos placeholders em CORTEX

Os diretórios já existentes em `CORTEX/` continuam sendo a arquitetura-alvo; os placeholders não equivalem a implementações funcionais.

| Pasta-alvo | Módulos existentes candidatos | Ideias ainda não implementadas |
|---|---|---|
| `CORTEX/sara/` | Nenhum módulo dedicado identificado no runtime atual | Boot, health check, status do runtime |
| `CORTEX/thalamus/` | Parte do roteamento atualmente distribuída entre adapter, flags `needs_*` e controlador | Context router, Pattern Reasoner, seleção de recursos |
| `CORTEX/sensory/` | Entrada HTTP atualmente recebida por `AIGAR_RUNTIME/main.py`; interpretação fica no adapter de linguagem | Adapters sensoriais dedicados |
| `CORTEX/default_mode_network/` | Nenhum ciclo de autorreflexão dedicado identificado | Estado interno, self-model, reflection cycle |
| `CORTEX/language/` | Adapter e interpretador de linguagem; Aurora é candidata para formulação/saída | Separação futura Wernicke, giro angular, Broca, gramática e léxico |
| `CORTEX/reasoning_engine/` | `prefrontal_controller.py` atualmente seleciona evidências e monta plano; não é um motor geral completo | Planner, evidence evaluator e sufficiency checker dedicados |
| `CORTEX/memory/` | `working_memory.py`, `hippocampal_memory.py` e integração com recuperação a mapear | Recall persistente e integração futura de Memory Cards |
| `CORTEX/worker_bridge/` | `diagnosis.py` é um adaptador não conectado; nenhum bridge geral confirmado | Worker client, contratos de mensagem e registry |
| `CORTEX/prefrontal/` | `prefrontal_controller.py` é candidato funcional; documentação de evolução já está nesta pasta | Planejamento de complexidade executável e módulos executivos futuros |
| `CORTEX/occipital/` | A UI `aigar_ui_chat_mvp/web/` é candidata, mas pertence a aplicação separada e precisa de análise de dependência | Consolidar `index.html`, assets e components após decidir a relação entre as interfaces |

## 5. Dependências e pontos de atenção antes de mover

1. `AIGAR_RUNTIME/main.py` importa os adaptadores via imports relativos e inicia Uvicorn com `AIGAR_RUNTIME.main:app`. O caminho de entrada precisa continuar válido durante a transição.
2. `language_network_adapter.py` calcula `INTERPRETER_PATH` com base na raiz do repositório e aponta para `aigar-c-2/language_network/interpreter.py`. Mover o interpretador exige atualizar esse caminho e mover/atualizar os JSONs carregados relativamente a ele.
3. `AIGAR_RUNTIME/knowledge_retrieval.py` importa `knowledge_retrieval.retriever.KnowledgeRetriever`. O pacote de recuperação não pode ser movido isoladamente sem corrigir e mapear esse import.
4. `knowledge_retrieval/retriever.py` usa `indexes/`, `cache/` e metadados de cache relativos ao diretório-raiz do pacote. Os dados e caminhos de cache devem permanecer coerentes.
5. `knowledge_retrieval/bootstrap_sapiens.py` chama `python -m knowledge_encoding.encode_knowledge`; o pacote de encoding é uma dependência real do fluxo de ingestão.
6. `AIGAR_RUNTIME/linguistic_interpreter.py` é candidato a duplicação, mas não deve ser removido sem pesquisa de referências em todo o repositório.
7. `aigar_ui_chat_mvp/` tem sua própria API e frontend. Não mover seus arquivos para `CORTEX/occipital/` até confirmar se o runtime principal deve consumi-los ou se continuarão sendo uma aplicação independente.
8. O plano antigo de renomeações contém referências históricas à pasta Cloudflare. Isso não autoriza alterações: o Worker permanece completamente excluído do escopo desta migração.

## 6. Sequência proposta para a migração

1. Revisar este inventário e confirmar o limite entre o runtime principal e aplicações/pacotes separados.
2. Registrar uma tabela final por arquivo: origem, destino, tipo de mudança, dependências, referências a atualizar e critério de conclusão.
3. Mover/renomear somente os arquivos confirmados, preservando conteúdo e registrando cada par efetivamente realizado.
4. Atualizar imports, caminhos de dados, comandos de execução, documentação e workflows relevantes — exceto quaisquer artefatos do Cloudflare Worker.
5. Consolidar o registro real de migração em `CORTEX/prefrontal/CHANGELOG.md` e atualizar este inventário com status por arquivo.
6. Somente após concluir a fase de nomes e referências, combinar a validação funcional. Nenhum teste, merge ou deploy nesta etapa.

## 7. Modelo obrigatório para o registro de cada migração

| Campo | Valor a registrar |
|---|---|
| ID | MIG-001, MIG-002, ... |
| Origem | Caminho completo antes da mudança |
| Destino | Caminho completo após a mudança |
| Tipo | MOVER, RENOMEAR, MANTER ou PLACEHOLDER |
| Motivo | Responsabilidade arquitetural |
| Dependências | Imports, dados, configs e workflows afetados |
| Referências atualizadas | Lista real dos arquivos alterados |
| Integridade | Se o conteúdo foi preservado ou se houve mudança de código separada |
| Commit | SHA real do commit que registrou a mudança |
| Estado | Planejado, executado, referências atualizadas ou bloqueado |

**Nota de precisão:** este documento é um inventário estático baseado na árvore e nos arquivos inspecionados. Não declara que o runtime está funcionando nem substitui a futura validação. Nenhum teste foi executado.


## Registro de migração executada — lote 1

**Estado:** arquivos movidos preservando o conteúdo; referências e imports ainda não atualizados. A quebra temporária do runtime é esperada nesta fase. Nenhum teste foi executado.

| ID | Origem | Destino | Tratamento | Estado |
|---|---|---|---|---|
| MIG-001 | `aigar-c-2/AIGAR_RUNTIME/working_memory.py` | `aigar-c-2/CORTEX/memory/working_memory.py` | Conteúdo copiado sem alteração; origem removida após confirmar destino | Migrado; referências pendentes |
| MIG-002 | `aigar-c-2/AIGAR_RUNTIME/hippocampal_memory.py` | `aigar-c-2/CORTEX/memory/hippocampal_memory.py` | Conteúdo copiado sem alteração; origem removida após confirmar destino | Migrado; referências pendentes |
| MIG-003 | `aigar-c-2/AIGAR_RUNTIME/prefrontal_controller.py` | `aigar-c-2/CORTEX/prefrontal/prefrontal_controller.py` | Conteúdo copiado sem alteração; origem removida após confirmar destino | Migrado; referências pendentes |
| MIG-004 | `aigar-c-2/AIGAR_RUNTIME/language_network_adapter.py` | `aigar-c-2/CORTEX/language/language_network_adapter.py` | Conteúdo copiado sem alteração; origem removida após confirmar destino | Migrado; referências pendentes |
| MIG-005 | `aigar-c-2/language_network/interpreter.py` | `aigar-c-2/CORTEX/language/interpreter.py` | Conteúdo copiado sem alteração; origem removida após confirmar destino | Migrado; referências pendentes |
| MIG-006 | `aigar-c-2/language_network/language.json` | `aigar-c-2/CORTEX/language/language.json` | Dados copiados sem alteração; origem removida após confirmar destino | Migrado; referências pendentes |
| MIG-007 | `aigar-c-2/language_network/portuguese_language_knowledge.json` | `aigar-c-2/CORTEX/language/portuguese_language_knowledge.json` | Dados copiados sem alteração; origem removida após confirmar destino | Migrado; referências pendentes |

### Commits efetivos do lote 1

- MIG-001 destino: `8696e405dc243185c6ec7466ccbf11399273b2ca`; remoção da origem: `e8f93d45be923b7408b1fbbf233f077d386953d1`.
- MIG-002 destino: `e621392c9cf788fa2c33c3a38ce7fe39431d3511`; remoção da origem: `0f045161f72132370b5d7b5e6da636ace9ab80e6`.
- MIG-003 destino: `e5a774ae146ea683c656e23ba5ed887588068050`; remoção da origem: `5b3a189e50a5020721fa8ca407b22b678ec6f019`.
- MIG-004 destino: `edc3ac9588df0cc7bc43357e6bc5f053f492fbc8`; remoção da origem: `e64ff61e0fd2627339b68b6390083f35189723ed`.
- MIG-005 destino: `e09a9e405d9b944afd127b36a4114e0727d0121a`; remoção da origem: `62f406a5bab8268efafb3a846fe5848334af378a`.
- MIG-006 destino: `eb481a022f22b1917699709867fa37937e9a951a`; remoção da origem: `4ab15fb011bb9dfac984341bba6daaec4cd11488`.
- MIG-007 destino: `c52a588710191c65ffc9f01c383d73228d87d04d`; remoção da origem: `a4c2bd996bd127f84036c1498a806e39ecd7faf3`.

**Próxima etapa:** continuar a migração dos arquivos confirmados no mapa. Depois de concluir movimentações/renomeações, traduzir imports e caminhos de dados em um lote dedicado. O Cloudflare Worker permanece totalmente fora do escopo.


## Registro de migração executada — lote 2 (decisão anatômica v2)

**Estado:** os cinco arquivos abaixo foram copiados para os destinos aprovados e suas origens foram removidas após a criação dos destinos. O conteúdo dos arquivos foi preservado byte a byte no nível do texto UTF-8 conforme SHA de blob original e SHA de destino idênticos. Imports e referências ainda não foram traduzidos. Nenhum teste foi executado.

| ID | Origem | Destino | Decisão/estado |
|---|---|---|---|
| MIG-008 | `aigar-c-2/AIGAR_RUNTIME/models.py` | `aigar-c-2/CORTEX/thalamus/models.py` | Contratos compartilhados; migrado, imports pendentes |
| MIG-009 | `aigar-c-2/AIGAR_RUNTIME/aurora.py` | `aigar-c-2/CORTEX/prefrontal/aurora.py` | Apresentação da resposta; migrado, imports pendentes |
| MIG-010 | `aigar-c-2/AIGAR_RUNTIME/knowledge_retrieval.py` | `aigar-c-2/CORTEX/engram/knowledge_retrieval.py` | Adaptador de recuperação; migrado, dependência externa preservada |
| MIG-011 | `aigar-c-2/AIGAR_RUNTIME/linguistic_interpreter.py` | `aigar-c-2/CORTEX/thalamus/linguistic_interpreter.py` | Interpretação/classificação inicial; migrado, imports pendentes |
| MIG-012 | `aigar-c-2/AIGAR_RUNTIME/diagnosis.py` | `aigar-c-2/Diagnosis/diagnosis.py` | Adaptador clínico mantido fora de CORTEX para integração posterior |

### Commits efetivos do lote 2

- MIG-008 destino: `ef085c38f830d0ff41d015bd10ab59266454008e`; remoção da origem: `2a3cdf194709c99f7d06b25f6871905f8611672a`. Blob preservado: `826ae4f2b96a11f94d938e2f3c32f4de60ccb175`.
- MIG-009 destino: `5496836375806c97055be1e95ff0378ee11c3b81`; remoção da origem: `458ed2b83b326719010f0b58b9b792603981337d`. Blob preservado: `a7a4555dabb5a25be02b2675df6f5d9c0c061452`.
- MIG-010 destino: `35928d54858f0e7ae41312312f4bea819b794e24`; remoção da origem: `71fbd16e3e201670d872088dd02d47631e6e5db2`. Blob preservado: `f5c4562e0d8d9a4713ce8baf202ef1a1dba10cbd`.
- MIG-011 destino: `ebb4bb8575f8b21e345d7ec265246fad8519b405`; remoção da origem: `6bce2443bb83afa1e766b8203ad39af17b01cfac`. Blob preservado: `5eaebbccf6ec80904780a1cfeec24f9ae2839a88`.
- MIG-012 destino: `7507d8769f47dceff570fd3a5557a103ef8351f7`; remoção da origem: `ea9655ca498b08cdf8621eb5868db9c2e03988a0`. Blob preservado: `4039ddfa274086e9af621a7b9e762c59208f075b`.

**Próxima etapa:** concluir o mapa dos demais arquivos e, em lote separado, atualizar imports e caminhos de dados. O Cloudflare Worker permanece fora do escopo.


## Inventário ampliado — fechamento da etapa de levantamento

**Base inspecionada:** árvore Git da branch `neurocognitive-migration`, SHA de referência `80687cc4b2911be41444b87261656d4421db0447`, mais leitura dos pontos de entrada e READMEs citados abaixo. Foram excluídos da avaliação de migração os diretórios `.venv/`, `__pycache__/` e caches/índices gerados, que não devem ser tratados como código-fonte comum. O Worker permanece expressamente excluído.

### A. Runtime legado ainda existente — manter como referência até traduzir dependências

| Arquivo | Papel/decisão |
|---|---|
| `AIGAR_RUNTIME/main.py` | Entry point FastAPI; orquestra linguagem, memória, biblioteca, Diagnosis, pré-frontal e Aurora. Não mover até planejar os imports de forma coordenada. |
| `AIGAR_RUNTIME/__init__.py` | Inicialização do pacote legado; revisar ao traduzir a entrada. |
| `AIGAR_RUNTIME/requirements.txt` | Dependências do runtime legado; decidir instalação comum/novo manifesto depois de mapear os pacotes. |
| `AIGAR_RUNTIME/test_runtime.py` | Testes existentes; preservados, não executados nesta fase. |
| `AIGAR_RUNTIME/README.md` | Documentação operacional e histórica; atualizar após definir novo entry point. |

**Dependência crítica confirmada:** `main.py` ainda importa `.models`, `.language_network_adapter`, `.working_memory`, `.hippocampal_memory`, `.knowledge_retrieval`, `.diagnosis`, `.prefrontal_controller` e `.aurora` do pacote antigo. Como cinco desses módulos foram movidos nos lotes anteriores, o entry point legado está temporariamente inconsistente por desenho. Isso será tratado na fase de tradução; não rodar testes antes dela.

### B. Pacotes funcionais externos ao CORTEX — preservar e mapear interfaces

| Área | Conteúdo identificado | Decisão |
|---|---|---|
| `knowledge_retrieval/` | `retriever.py`, `semantic_retriever.py`, bootstrap/config/README, fontes, testes, índices e cache | Manter pacote independente. `CORTEX/engram/knowledge_retrieval.py` é adaptador, não substituto desse pacote. Não mover cache/índices em lote de código. |
| `knowledge_encoding/` | `encode_knowledge.py`, `encode_existing_chunks.py`, `requirements.txt`, README e inicializador | Manter como pipeline de ingestão/encoding; documentar seu vínculo com a biblioteca. |
| `language_network/` | README, `__init__.py`, teste do interpretador e PDF de referência | O código principal e JSONs foram migrados no lote 1; preservar o teste e a fonte documental até revisar dependências e licença/origem. |
| `Diagnosis/` | `diagnosis.py` (adaptador) | Mantido separado do CORTEX para integração futura com o motor clínico especializado. |
| `aigar_ui_chat_mvp/` | backend FastAPI, módulos AIGAR/Jarvis, manifests, UI web, memory cards e READMEs | Aplicação separada. Não misturar backend/UI com o runtime cognitivo sem confirmar consumidores e contrato. A pasta `.venv/` é artefato local, não candidata a migração de fonte. |

### C. Arquitetura e contratos históricos — fontes de reconstrução, não módulos automaticamente migráveis

- `association_network/AIGAR_ARCHITECTURE_v1.yaml`
- `association_network/AIGAR_RUNTIME_CONTRACT_v1.json`
- `association_network/AIGAR_SOURCE_MANIFEST_v1.json`
- `association_network/AIGAR_EVIDENCE_MAP_v1.md`
- `association_network/AIGAR_MIGRATION_PLAN.md` e README
- `AIGAR_PHASES/phases.json`
- `AIGAR_RECONSTRUCTION/FASE_1_BIBLIOTECA_E_CACHE.md`
- `conversational-engine/AIGAR_AURORA_RECONSTRUCAO_LINGUAGEM_MEMORIA_v1_0.html`
- Documentos de raiz: `AIGAR_NEUROCOGNITIVE_DICTIONARY_v1.txt`, `AIGAR_NEUROCOGNITIVE_MIGRATION_MAP_v1.md`, `AIGAR_NEUROCOGNITIVE_ROADMAP_v1.md`, `AIGAR_RENAME_PLAN_v1.md`, `AIGAR_WORKER_TOPOLOGY_INVENTORY_v1.md` e `AIGAR_PACOTE_COMPLEMENTAR_RECONSTRUCAO_v1_0.txt`.

**Decisão:** comparar esses contratos entre si antes de traduzir imports ou transformar proposta histórica em comportamento implementado. Preservar conflitos/diferenças como questões abertas, sem escolher silenciosamente uma fonte canônica.

### D. Interface, sincronização e dados auxiliares — revisão posterior

- `aigar_ui_chat_mvp/web/index.html`, `app.js`, `style.css`: candidatos à camada visual (`CORTEX/occipital/`) após confirmar integração.
- `aigar-jarvis-sync/` e `drive-do-aigar/`: ferramentas de sincronização/integração; mapear credenciais, caminhos e consumidores antes de qualquer mudança.
- `fragments-history/`: histórico de fragmentos; preservar como arquivo histórico.
- `biblioteca/`: corpus de documentos; manter separado de código e confirmar direitos de redistribuição antes de copiar documentos.
- PDFs na raiz de `aigar-c-2/`: fontes de conhecimento, não módulos de runtime. Não mover automaticamente.
- `main.backup.py`, `requirements-math.txt`: backup e dependências especializadas; manter até identificar consumidores.
- Diretórios de cache, índices gerados, `.venv/` e `__pycache__/`: não são parte da migração estrutural de código-fonte; preservar seus dados existentes e não copiar ambientes virtuais para a arquitetura nova.

### E. Arquitetura CORTEX — estado atual observado

- Funcionais migrados: `thalamus/models.py`, `thalamus/linguistic_interpreter.py`, `engram/knowledge_retrieval.py`, `memory/working_memory.py`, `memory/hippocampal_memory.py`, `language/language_network_adapter.py`, `language/interpreter.py`, os dois JSONs linguísticos, `prefrontal/prefrontal_controller.py` e `prefrontal/aurora.py`.
- Placeholders/documentação existentes: `sara/`, `sensory/`, `default_mode_network/`, `reasoning_engine/`, `worker_bridge/`, `language/`, `memory/`, `thalamus/`, `occipital/`, além dos documentos pré-frontais.
- `CORTEX/README.md` ainda descreve a fase original de placeholders; atualizar sua descrição depois de encerrar a movimentação e antes de codificar a nova arquitetura.

### F. Pendências objetivas para a etapa de tradução

1. Definir como `main.py` será mantido como referência ou substituído por novo ponto de entrada do CORTEX.
2. Traduzir imports de modelos para `CORTEX.thalamus.models` (ou contrato compartilhado que vier a ser aprovado).
3. Atualizar a localização do interpretador referenciada por `language_network_adapter.py`.
4. Corrigir resolução dos dois JSONs no interpretador linguístico.
5. Traduzir os imports dos módulos de memória e do controlador, inclusive dependências de `models.py`.
6. Preservar o import do pacote externo `knowledge_retrieval.retriever` enquanto o pacote não for migrado.
7. Comparar `AIGAR_RUNTIME/linguistic_interpreter.py` migrado com `CORTEX/language/interpreter.py`; documentar diferença de contratos sem eliminar nenhum.
8. Definir interface de integração do adaptador em `Diagnosis/diagnosis.py` sem incorporar o motor clínico ao CORTEX.
9. Revisar entry points, requirements e instruções nos READMEs após a tradução.
10. Somente depois de concluir itens anteriores, autorizar testes de validação comportamental.

**Conclusão do inventário:** a fase de levantamento está concluída para os principais módulos do runtime, linguagem, memória, recuperação documental, Diagnosis, UI, contratos históricos e recursos auxiliares listados acima. Isto não significa que todas as migrações do repositório estejam concluídas: os itens nas seções B–D são explicitamente preservados ou candidatos a revisão posterior. Imports/caminhos não foram traduzidos e testes não foram executados.

## Atualização de estado — tradução inicial de referências (2026-10-10)

Esta seção supersede os estados históricos que diziam que todos os imports estavam pendentes. Os parágrafos anteriores são registros do estado à época em que foram escritos; não devem ser interpretados como estado atual.

- `AIGAR_RUNTIME/main.py` mantém-se como entry point operacional e importa contratos de `CORTEX.thalamus.models`, adaptadores de `CORTEX.language`, `CORTEX.memory`, `CORTEX.engram`, `CORTEX.prefrontal` e `Diagnosis.diagnosis`. Commit: `88380ee4102bcfe409a151734fff91ac9f850848`.
- `CORTEX/language/language_network_adapter.py` usa o contrato canônico e importa `AIGARLanguage` diretamente de `CORTEX.language.interpreter`; caminho legado corrigido. Commit: `286dfdb96b56cf019e2ca4d37474321117f0f6b0`.
- `AIGAR_RUNTIME/test_runtime.py` importa `RuntimeRequest` do contrato canônico. O arquivo foi atualizado, mas seus testes não foram executados. Commit: `59af9877cf6abe60877ed03c10b859d3a9d354c8`.
- `AIGAR_RUNTIME/README.md` e `CORTEX/README.md` documentam a entrada e o mapa provisório. Commits: `df98d3653714cc6991c2430909ff92890440f17d` e `695620e49784e2b69fe89ec38cdeb27dbfe5ac52`.

## Estado de conclusão desta etapa

Contratos compartilhados e as referências conhecidas do entry point foram traduzidos estaticamente. Ainda não se declara concluída a revisão de todas as referências no repositório. A comparação entre os dois interpretadores, integração real de Diagnosis, dependências/manifestos e eventuais referências em outros pacotes permanecem pendentes de inspeção. Nenhum teste foi executado; não houve merge/deploy; Cloudflare Worker permanece intocado.
## Atualização da arquitetura executável — roteamento (2026-10-10)

- `CORTEX/thalamus/models.py`: contrato compartilhado `RoutingDecision` adicionado de forma aditiva; os contratos anteriores permanecem.
- `CORTEX/thalamus/context_router.py`: implementa a tradução de `ConversationReading` para seleção explícita dos subsistemas opcionais.
- `AIGAR_RUNTIME/main.py`: consome `route_reading()` para selecionar memória, biblioteca e Diagnosis. A etapa de raciocínio permanece ativa para preservar o comportamento anterior enquanto os contratos são completados.
- Registro correspondente: `CORTEX/prefrontal/CHANGELOG.md`, commit `b5f5e40600b2663086d53786798bc27c8f1def14`.

**Estado real:** roteamento extraído para módulo canônico; ainda não validado em execução. A revisão de referências do repositório, comparação dos dois interpretadores, conexão real do adaptador Diagnosis, contratos dos módulos restantes e manifestos de dependência continua pendente. Testes não executados.
