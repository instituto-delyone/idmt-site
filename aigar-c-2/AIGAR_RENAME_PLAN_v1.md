# AIGAR C-2 — Plano de renomeações
Versão: 1.0
Branch: `neurocognitive-migration`
Escopo desta etapa: mapear e registrar nomes. Nenhuma renomeação adicional, edição de referências de código, alteração funcional, teste ou deploy faz parte desta etapa.

## Ordem de execução acordada

1. Mapear e registrar os pares de nomes.
2. Renomear os arquivos e diretórios conforme o mapa, sem alterar conteúdo ou funcionamento.
3. Registrar as renomeações efetivamente realizadas no histórico de migração.
4. Atualizar referências aos nomes antigos nos arquivos de código e configuração para os nomes novos, preservando o comportamento existente.
5. Só depois iniciar qualquer mudança funcional ou implementação de ideias futuras.

## Renomeações já presentes na branch

Estes pares já foram executados antes deste plano; não devem ser repetidos.

| Origem anterior | Nome atual |
|---|---|
| `aigar-c-2/AIGAR_RUNTIME/reasoning.py` | `aigar-c-2/AIGAR_RUNTIME/prefrontal_controller.py` |
| `aigar-c-2/AIGAR_RUNTIME/memory.py` | `aigar-c-2/AIGAR_RUNTIME/hippocampal_memory.py` |
| `aigar-c-2/AIGAR_RUNTIME/language_bridge.py` | `aigar-c-2/AIGAR_RUNTIME/language_network_bridge.py` |
| `aigar-c-2/AIGAR_RUNTIME/library.py` | `aigar-c-2/AIGAR_RUNTIME/knowledge_retrieval.py` |
| `aigar-c-2/AIGAR_RUNTIME/conversation.py` | `aigar-c-2/AIGAR_RUNTIME/working_state.py` |

## Renomeações planejadas — ainda não executadas

| ID | Origem atual | Destino planejado | Tipo |
|---|---|---|---|
| R01 | `aigar-c-2/AIGAR_CORE/` | `aigar-c-2/association_network/` | Diretório |
| R02 | `aigar-c-2/AIGAR_LANGUAGE/` | `aigar-c-2/language_network/` | Diretório |
| R03 | `aigar-c-2/AIGAR_LIBRARY/` | `aigar-c-2/knowledge_retrieval/` | Diretório |
| R04 | `aigar-c-2/AIGAR_LIBRARY_BUILDER/` | `aigar-c-2/knowledge_consolidation/` | Diretório |
| R05 | `aigar-c-2/AIGAR_CLOUDFLARE/cognitive_core.py` | `aigar-c-2/AIGAR_CLOUDFLARE/association_core.py` | Arquivo |

## Nomes mantidos nesta rodada

| Caminho atual | Decisão |
|---|---|
| `aigar-c-2/AIGAR_CLOUDFLARE/main.py` | Manter o nome e caminho atuais nesta rodada. |
| `aigar-c-2/AIGAR_RUNTIME/main.py` | Manter como entrypoint do runtime. |
| `aigar-c-2/AIGAR_CLOUDFLARE/wrangler.jsonc` | Não renomear. |
| Arquivos de dados, corpus, PDFs, cache, índices, arquivos de usuário e artefatos históricos | Fora do escopo de renomeação por nome neurocognitivo nesta rodada. |

## Regras para executar o mapa

- Este documento registra intenção; só marcar um par como concluído depois que a mudança de nome estiver presente na branch.
- Não alterar o conteúdo dos arquivos durante a etapa de renomeação.
- Não atualizar imports, caminhos, configurações ou referências nesta primeira etapa de renomeação; isso será a etapa seguinte, separada.
- Não mudar lógica, comportamento, contratos, endpoints, bindings ou arquitetura de Workers.
- Não executar testes nesta etapa.
- Não fazer merge nem deploy.
- Se algum destino já existir ou houver colisão de nomes, interromper aquele par e registrar a colisão, sem sobrescrever conteúdo.
- Preservar este plano e registrar cada alteração realizada no histórico após a etapa de renomeação.


## Histórico de renomeações executadas — 2026-10-10

Commit de renomeação: `332b26ad372001cb329485e40b1ec235188b8cfa`

As renomeações abaixo foram aplicadas à árvore da branch preservando os blobs/conteúdos existentes. Nenhuma referência interna, import, configuração ou lógica foi alterada nesta etapa.

| ID | Caminho anterior | Caminho novo | Arquivos movidos |
|---|---|---|---:|
| R01 | `aigar-c-2/AIGAR_CORE/` | `aigar-c-2/association_network/` | 6 |
| R02 | `aigar-c-2/AIGAR_LANGUAGE/` | `aigar-c-2/language_network/` | 7 |
| R03 | `aigar-c-2/AIGAR_LIBRARY/` | `aigar-c-2/knowledge_retrieval/` | 108 |
| R04 | `aigar-c-2/AIGAR_LIBRARY_BUILDER/` | `aigar-c-2/knowledge_consolidation/` | 5 |
| R05 | `aigar-c-2/AIGAR_CLOUDFLARE/cognitive_core.py` | `aigar-c-2/AIGAR_CLOUDFLARE/association_core.py` | 1 |

### Estado após a etapa de renomeação

- [x] Mapa de nomes registrado.
- [x] Renomeações planejadas executadas.
- [x] Histórico atualizado com os pares efetivamente renomeados.
- [x] Referências de código e configuração atualizadas para os nomes novos.
- [ ] Etapa de alteração funcional — ainda não autorizada nesta fase.

### Referências atualizadas nesta etapa

- Runtime: caminho do interpretador para `language_network/` e import do retriever para `knowledge_retrieval.retriever`.
- Recuperação e indexação: módulo do builder, caminho padrão de saída e variável de raiz atualizados para os novos nomes.
- Cloudflare Worker: caminhos de índices/cache e import do módulo `association_core.py` atualizados.
- Teste existente do core: import atualizado para `association_core`; o arquivo de teste manteve o próprio nome.
- Workflows: caminhos de gatilho, compilação e referências de arquivos atualizados para os novos diretórios e módulo.
- Manifesto de fontes e catálogo de fases: caminhos/módulos atualizados.

Identificadores de bindings de runtime como `AIGAR_LIBRARY_BUCKET`, `AIGAR_LIBRARY_BUILDER` e `AIGAR_DB` foram mantidos deliberadamente: são nomes de recursos/contratos já existentes, não caminhos de arquivos, e alterá-los poderia mudar o funcionamento.

**Testes:** não executados por instrução nesta fase. Nenhuma alteração funcional, merge ou deploy foi realizado.


## Proposta aprovada para o mapa neurocognitivo — 2026-10-10

| ID | Caminho/função atual | Nome proposto | Estado | Observação |
|---|---|---|---|---|
| N01 | `aigar-c-2/AIGAR_RUNTIME/main.py` — entrada HTTP e coordenação do fluxo | `aigar-c-2/AIGAR_RUNTIME/thalamus.py` — módulo de integração e encaminhamento cognitivo | Mapeado; implementação pendente | `main.py` permanece como entrypoint técnico. A extração da lógica para o Tálamo exige etapa de implementação separada; não é um simples renome de arquivo. Nenhum código foi alterado nesta etapa. |

### Limites desta decisão

- O `main.py` do Cloudflare Worker permanece totalmente intocado.
- Não criar um `thalamus.py` vazio nem duplicar a lógica existente.
- Não mover funções nem atualizar imports nesta etapa de mapeamento.
- A futura implementação do Tálamo deve ser planejada separadamente para preservar endpoints e o comando de inicialização do runtime.
- Testes, alterações funcionais, merge e deploy continuam fora desta etapa.


## Mapa complementar dos nomes residuais — 2026-10-10

Esta seção amplia o mapa; **não executa renomeações**. Os nomes abaixo foram avaliados pela função que o código atual realmente exerce, evitando atribuir capacidades ainda não implementadas. O Worker continua fora do escopo.

| ID | Caminho atual | Nome proposto | Decisão/justificativa | Estado |
|---|---|---|---|---|
| N02 | `aigar-c-2/AIGAR_RUNTIME/working_state.py` | `aigar-c-2/AIGAR_RUNTIME/working_memory.py` | O módulo mantém estado temporário por sessão e limita o histórico recente; “memória de trabalho” é uma analogia mais clara que “estado”. | Proposto |
| N03 | `aigar-c-2/AIGAR_RUNTIME/language_network_bridge.py` | `aigar-c-2/AIGAR_RUNTIME/language_network_adapter.py` | A classe já se chama `LanguageNetworkAdapter`; o arquivo adapta a rede de linguagem ao contrato do Runtime. | Proposto |
| N04 | `aigar-c-2/AIGAR_RUNTIME/language.py` | `aigar-c-2/AIGAR_RUNTIME/linguistic_interpreter.py` | Interpreta a entrada por regras heurísticas simples e produz intenção/profundidade; o nome explicita a função sem alegar compreensão semântica avançada. | Proposto |
| N05 | `aigar-c-2/knowledge_consolidation/` | `aigar-c-2/knowledge_encoding/` | Os scripts normalizam, dividem, identificam e indexam conteúdo. “Codificação do conhecimento” é mais preciso que “consolidação” biológica, que sugeriria processos adicionais não demonstrados. | Proposto |
| N06 | `aigar-c-2/knowledge_consolidation/build.py` | `aigar-c-2/knowledge_consolidation/encode_knowledge.py` | O script constrói chunks/cache/índices a partir de fontes; o nome atual é genérico. O destino final deve acompanhar N05 se N05 for aprovado. | Proposto |
| N07 | `aigar-c-2/knowledge_consolidation/index_existing.py` | `aigar-c-2/knowledge_consolidation/encode_existing_chunks.py` | Indexa chunks TXT/MD existentes e os grava no cache/índices; o destino final deve acompanhar N05 se N05 for aprovado. | Proposto |
| N08 | `aigar-c-2/knowledge_retrieval/retriever.py` / classe `LibraryRetriever` | manter arquivo `retriever.py`; avaliar classe `KnowledgeRetriever` | O nome do arquivo é convencional e curto dentro do pacote de recuperação. A classe `LibraryRetriever` é o resíduo mais evidente; renomear símbolo exige atualizar referências na etapa 4, não agora. | Proposto |
| N09 | `aigar-c-2/AIGAR_RUNTIME/hippocampal_memory.py` | manter | O código declara explicitamente que é uma analogia hipocampal limitada a contexto recente; renomear para “episodic memory” poderia exagerar a persistência/recuperação realmente conectada. | Manter |
| N10 | `aigar-c-2/AIGAR_RUNTIME/prefrontal_controller.py` | manter | O nome já é neurocognitivo e corresponde à função heurística atual de selecionar evidências e organizar a resposta, sem presumir controle executivo completo. | Manter |
| N11 | `aigar-c-2/AIGAR_RUNTIME/knowledge_retrieval.py` | manter | É o adaptador do Runtime para recuperação documental; nome funcional claro e coerente com a classe `KnowledgeRetrievalAdapter`. | Manter |
| N12 | `aigar-c-2/AIGAR_RUNTIME/main.py` | manter | É o entrypoint técnico do Runtime. Não deve ser renomeado para Tálamo: a proposta `thalamus.py` representa um módulo futuro de integração/encaminhamento e requer implementação funcional separada. | Manter |
| N13 | `aigar-c-2/AIGAR_RUNTIME/models.py`, `diagnosis.py`, `aurora.py`, `requirements.txt`, `test_runtime.py` | manter | São nomes de contratos, adaptador de domínio, camada de saída, dependências e testes; não há ganho claro em forçar nomes anatômicos. | Manter |
| N14 | `aigar-c-2/AIGAR_NEUROCOGNITIVE_DICTIONARY_v1.txt`, `aigar-c-2/AIGAR_RENAME_PLAN_v1.md` | manter | São documentos de governança/histórico; preservar nomes estáveis facilita rastreabilidade e links. | Manter |

### Regras específicas para os próximos passos

- Nenhum par N02–N14 foi renomeado nesta atualização; são decisões propostas para fechar o mapa.
- O diretório e os scripts de codificação (N05–N07) devem ser tratados como um único conjunto na etapa de renomeação, para evitar destinos inconsistentes.
- O símbolo `LibraryRetriever` só será alterado depois da etapa de renomeação de caminhos, na etapa separada de atualização de referências.
- Não renomear nem editar qualquer arquivo, símbolo, binding, chave JSON, configuração ou workflow em `aigar-c-2/AIGAR_CLOUDFLARE/`; o Worker permanece expressamente excluído.
- `thalamus.py` não será criado durante a fase de nomes; sua implementação será uma decisão funcional posterior, mantendo `AIGAR_RUNTIME/main.py` como entrypoint.


## Histórico complementar — renomeações de nomes residuais — 2026-10-10

Commit de renomeação: `9e5269eb9ddc63a55665ef3b9b9ea66ff9d2b42d`

Os caminhos abaixo foram renomeados preservando os blobs/conteúdos. Nesta etapa, **não foram atualizados imports, referências, comandos, workflows ou configurações**.

| ID | Caminho anterior | Caminho novo | Conteúdo |
|---|---|---|---|
| N02 | `aigar-c-2/AIGAR_RUNTIME/working_state.py` | `aigar-c-2/AIGAR_RUNTIME/working_memory.py` | Blob preservado |
| N03 | `aigar-c-2/AIGAR_RUNTIME/language_network_bridge.py` | `aigar-c-2/AIGAR_RUNTIME/language_network_adapter.py` | Blob preservado |
| N04 | `aigar-c-2/AIGAR_RUNTIME/language.py` | `aigar-c-2/AIGAR_RUNTIME/linguistic_interpreter.py` | Blob preservado |
| N05 | `aigar-c-2/knowledge_consolidation/` | `aigar-c-2/knowledge_encoding/` | 5 arquivos movidos; conteúdo preservado |
| N06 | `aigar-c-2/knowledge_encoding/build.py` | `aigar-c-2/knowledge_encoding/encode_knowledge.py` | Blob preservado |
| N07 | `aigar-c-2/knowledge_encoding/index_existing.py` | `aigar-c-2/knowledge_encoding/encode_existing_chunks.py` | Blob preservado |

### Estado da migração após este commit

- [x] Mapa complementar registrado.
- [x] Renomeações de caminhos N02–N07 realizadas.
- [x] Histórico das renomeações residuais registrado.
- [ ] Atualização de referências internas, imports, comandos e configurações — próxima etapa; não executada neste commit.
- [ ] Testes — adiados conforme instrução.
- [ ] Implementação do módulo futuro `thalamus.py) — fora desta etapa.
- [ ] Cloudflare Worker — permanece expressamente intocado nesta rodada.

**Nota operacional:** o repositório pode ficar temporariamente com referências antigas até a etapa separada de atualização de referências. Nenhum teste, merge ou deploy foi executado.


## Histórico complementar — atualização de referências — 2026-10-10

Após os renomes N02–N07, foram atualizadas as referências atuais fora do Cloudflare Worker:

- `AIGAR_RUNTIME/main.py`: imports para `language_network_adapter` e `working_memory`.
- `knowledge_retrieval/bootstrap_sapiens.py`: chamada do módulo de codificação para `knowledge_encoding.encode_knowledge`.
- `knowledge_retrieval/BOOTSTRAP_LOCAL.md`: caminho de dependências atualizado para `knowledge_encoding/requirements.txt`.
- `.github/workflows/aigar-runtime-validation.yml`: gatilhos e compilação incluem `knowledge_encoding`.
- `knowledge_encoding/README.md`: comando de execução atualizado para `knowledge_encoding.encode_knowledge`.

Não foram alterados arquivos, símbolos, bindings, chaves JSON, configurações ou workflows dentro de `aigar-c-2/AIGAR_CLOUDFLARE/`. Referências antigas mantidas em seções históricas do plano/README são registros do histórico, não instruções de execução atuais.

### Situação da rodada

- [x] Mapear e registrar nomes residuais.
- [x] Renomear caminhos aprovados N02–N07.
- [x] Registrar as renomeações efetivamente realizadas.
- [x] Atualizar referências operacionais identificadas fora do Worker.
- [ ] Fazer auditoria final e executar testes — pendente conforme a sequência acordada.
- [ ] Implementar `thalamus.py` — fora desta etapa; `AIGAR_RUNTIME/main.py` continua sendo o entrypoint.
- [ ] Merge e deploy — não realizados.

**Importante:** os testes continuam sem execução nesta etapa, conforme a instrução anterior. A migração de nomes e referências deve ser auditada antes de qualquer validação funcional.
