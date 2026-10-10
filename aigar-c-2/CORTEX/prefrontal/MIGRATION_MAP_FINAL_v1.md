# AIGAR-C — Mapa de migração v1

Branch: `neurocognitive-migration`

## Método
1. Mapear origem e destino.
2. Mover/renomear arquivos selecionados preservando o código como referência.
3. Registrar cada mudança real com ID, origem, destino, dependências e commit.
4. Traduzir imports, caminhos, nomes e referências para a estrutura nova.
5. Reconstruir o funcionamento a partir do comportamento antigo.
6. Implementar ideias futuras separadamente, com placeholders explícitos.
7. Só validar depois de concluídas a movimentação/renomeação e a atualização das referências.

## Estrutura-alvo
```text
CORTEX/
├── sara/                 # placeholder: boot, health check, status
├── thalamus/             # placeholder: contexto, Pattern Reasoner, seleção de recursos
├── sensory/              # placeholder: adapters de entrada
├── default_mode_network/ # placeholder: estado interno e reflexão
├── language/             # interpretador e módulos linguísticos existentes
├── reasoning_engine/     # placeholder: planejamento e avaliação de evidências
├── memory/               # memória de trabalho, continuidade e adaptadores
├── worker_bridge/        # placeholder: contratos e comunicação
├── prefrontal/           # controlador executivo candidato e documentação de evolução
└── occipital/            # interface visual: index, assets, components
```

## Mapa inicial por arquivo
| Origem | Destino/decisão | Observação |
|---|---|---|
| `AIGAR_RUNTIME/main.py` | Manter temporariamente | Ponto de entrada; não mover nesta primeira passagem |
| `AIGAR_RUNTIME/models.py` | Manter até definir contratos compartilhados | Revisar dependências |
| `AIGAR_RUNTIME/language_network_adapter.py` | `CORTEX/language/` | Preservar lógica; traduzir imports depois |
| `language_network/interpreter.py` | `CORTEX/language/` | Migrar junto dos JSONs necessários |
| `language_network/language.json` | Junto do interpretador | Atualizar caminho de dados |
| `language_network/portuguese_language_knowledge.json` | Junto do interpretador | Atualizar caminho de dados |
| `AIGAR_RUNTIME/working_memory.py` | `CORTEX/memory/` | Preservar lógica |
| `AIGAR_RUNTIME/hippocampal_memory.py` | `CORTEX/memory/` | Preservar lógica |
| `AIGAR_RUNTIME/knowledge_retrieval.py` | Revisar destino entre `CORTEX/memory/` e integração | Adaptador do runtime |
| `AIGAR_RUNTIME/prefrontal_controller.py` | `CORTEX/prefrontal/` | Preservar comportamento implementado |
| `AIGAR_RUNTIME/aurora.py` | Revisar entre `CORTEX/language/` e camada de saída | Confirmar papel |
| `AIGAR_RUNTIME/diagnosis.py` | Revisar para `CORTEX/worker_bridge/` | Confirmar contrato |
| `AIGAR_RUNTIME/requirements.txt` | Manter junto do ponto de entrada | Não mover ainda |
| `AIGAR_RUNTIME/test_runtime.py` | Manter junto do runtime | Não executar antes da etapa combinada |
| `knowledge_encoding/` | Manter pacote | Pipeline de ingestão/encoding |
| `knowledge_retrieval/` | Manter pacote e dados | Preservar índices, cache e imports |
| `association_network/` | Manter por enquanto | Documentação/contratos; revisar separadamente |
| `AIGAR_PHASES/` | Manter até mapear consumidores | Revisar referências |
| `AIGAR_RECONSTRUCTION/` e documentos de arquitetura | Preservar; selecionar documentos para `CORTEX/prefrontal/` | Não apagar histórico |
| `aigar_ui_chat_mvp/web/` | Candidato a `CORTEX/occipital/` | Confirmar relação com runtime antes de mover |
| `aigar_ui_chat_mvp/` backend | Manter como aplicação separada | Não misturar automaticamente com o runtime |
| `biblioteca/` | Manter | Corpus documental, não código de runtime |
| `aigar-jarvis-sync/`, `drive-do-aigar/`, `fragments-history/`, `conversational-engine/` | Manter até provar dependências | Revisão separada |

## Regras de proteção
- Não apagar código por parecer redundante.
- Não executar testes durante a migração e tradução de referências.
- Não fazer merge nem deploy.
- A área Cloudflare Worker está excluída: não alterar arquivos, nomes, símbolos, configurações, bindings, chaves JSON ou workflows próprios.
- Não declarar uma migração concluída antes de ela existir no repositório.

## Registro obrigatório
Para cada mudança real: ID sequencial, origem, destino, função preservada, dependências, referências atualizadas, estado e SHA real do commit. Consolidar em `CORTEX/prefrontal/CHANGELOG.md` e no inventário. Placeholders são planos, não funcionalidades implementadas.

## Critério de encerramento
A migração termina quando os arquivos selecionados estão nos destinos aprovados e cada mudança está registrada. Em seguida, reconstruir os códigos traduzindo referências antigas para novos caminhos e nomes. Validar apenas após a conclusão dessa fase.
