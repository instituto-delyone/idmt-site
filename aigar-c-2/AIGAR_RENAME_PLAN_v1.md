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

## Estado

- [x] Mapa de nomes registrado.
- [ ] Renomeações planejadas executadas.
- [ ] Histórico atualizado com os pares realmente renomeados.
- [ ] Referências antigas atualizadas para os nomes novos.
- [ ] Etapa de alteração funcional — ainda não autorizada nesta fase.

Última atualização: 2026-10-10.
