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


## Adendo v2 — decisões aprovadas e lote 2 executado

| Origem anterior | Destino atual | Papel/observação |
|---|---|---|
| `AIGAR_RUNTIME/models.py` | `CORTEX/thalamus/models.py` | Contratos de leitura e estado compartilhados; imports relativos precisam de tradução posterior |
| `AIGAR_RUNTIME/aurora.py` | `CORTEX/prefrontal/aurora.py` | Apresentação da resposta subordinada ao planejamento |
| `AIGAR_RUNTIME/knowledge_retrieval.py` | `CORTEX/engram/knowledge_retrieval.py` | Adaptador de recuperação; pacote externo `knowledge_retrieval/` continua independente |
| `AIGAR_RUNTIME/linguistic_interpreter.py` | `CORTEX/thalamus/linguistic_interpreter.py` | Interpretação/classificação inicial; comparar contratos com `CORTEX/language/interpreter.py` |
| `AIGAR_RUNTIME/diagnosis.py` | `aigar-c-2/Diagnosis/diagnosis.py` | Mantido fora do CORTEX para integração posterior |

O lote 2 foi registrado como MIG-008–MIG-012 em `MIGRATION_INVENTORY_v1.md`. A alteração de caminho não incluiu tradução de imports nem testes. O conteúdo de origem foi preservado nos destinos, e cada remoção da origem ocorreu após a criação do destino.

### Arquitetura aprovada para este estágio

- `CORTEX/thalamus/`: `models.py` e `linguistic_interpreter.py`.
- `CORTEX/engram/`: adaptador `knowledge_retrieval.py`.
- `CORTEX/memory/`: `working_memory.py` e `hippocampal_memory.py`.
- `CORTEX/language/`: adaptador de rede, interpretador linguístico e JSONs.
- `CORTEX/prefrontal/`: controlador executivo e `aurora.py`.
- `aigar-c-2/Diagnosis/`: adaptador do Diagnosis independente até a integração posterior.

**Estado no fechamento do levantamento inicial:** movimentações dos lotes 1 e 2 registradas; a tradução de referências começou em lote controlado posteriormente. Consulte a atualização auditada ao final deste arquivo para o estado corrente. Sem merge/deploy; Cloudflare Worker fora do escopo.

## Fechamento do levantamento — dependências e fronteiras

A árvore do repositório e os contratos centrais foram revisados antes da codificação. Naquele momento, o entry point `AIGAR_RUNTIME/main.py` ainda tinha imports temporariamente inconsistentes; essa situação foi corrigida nos lotes seguintes e está registrada no changelog/inventário. O pacote `knowledge_retrieval/` e o pipeline `knowledge_encoding/` permanecem independentes. A UI `aigar_ui_chat_mvp/` continua aplicação separada. Os documentos de `association_network/`, `AIGAR_PHASES/`, `AIGAR_RECONSTRUCTION/` e `conversational-engine/` são fontes de reconstrução e contratos a comparar, não código a mover automaticamente.

O inventário ampliado e suas pendências estão em `MIGRATION_INVENTORY_v1.md`. Próxima etapa autorizada: começar a codificar a tradução de referências em lote controlado, preservando os contratos atuais e registrando cada alteração. Não executar testes antes da conclusão da tradução; não fazer merge/deploy; não alterar o Cloudflare Worker.


## Atualização auditada — conclusão de referências do lote de linguagem (2026-10-10)

Esta seção registra o estado posterior ao levantamento inicial e complementa os registros históricos acima.

### Estado constatado na árvore

- O entry point operacional continua sendo `AIGAR_RUNTIME/main.py`; seus imports apontam para `CORTEX.thalamus.models`, `CORTEX.sensory`, `CORTEX.thalamus`, `CORTEX.sara`, `CORTEX.language`, `CORTEX.memory`, `CORTEX.engram`, `CORTEX.prefrontal` e `Diagnosis`.
- `CORTEX/language/language_network_adapter.py` importa o interpretador pelo caminho relativo `.interpreter`; `interpreter.py` localiza ambos os JSONs por meio de `Path(__file__).parent`.
- O teste específico de linguagem, antes mantido em `language_network/test_interpreter.py`, foi movido para `CORTEX/language/test_interpreter.py` e seu import foi atualizado. Isso ficou registrado como MIG-013.
- `AIGAR_PHASES/phases.json` agora aponta as fases 1, 5, 6 e 7 para os módulos ativos/destinos CORTEX; os estados descritivos não foram alterados.
- README/PLACEHOLDER das pastas de linguagem, memória, tálamo, sensory e SARA foram reconciliados com a árvore real. `CORTEX/prefrontal/README.md` passou a reconhecer os módulos ativos de planejamento e apresentação.
- O PDF histórico em `language_network/`, os pacotes independentes de codificação/recuperação, a aplicação `aigar_ui_chat_mvp/` e os demais artefatos de reconstrução foram preservados. Seus destinos não foram presumidos sem mapear consumidores.

### Pendências que permanecem explícitas

- Executar validação somente após terminar a auditoria estática de imports, caminhos de dados, comandos, manifestos e referências de configuração relevantes.
- Comparar funcionalmente os dois interpretadores antes de decidir se algum deles pode ser substituído; nenhum foi eliminado.
- Conectar o motor clínico real à fronteira `DiagnosisRequest/DiagnosisResult`; o adaptador atual declara estado `missing`.
- Conectar recuperação persistente de Memory Card; o adaptador atual só recupera turnos da sessão.
- Decidir a política de execução de `RoutingDecision.use_reasoning` sem mudança acidental de comportamento; por ora o raciocínio continua no pipeline.
- Implementar separadamente as capacidades futuras indicadas por placeholders; sua documentação não deve ser lida como código pronto.
- Manter o Cloudflare Worker e seus arquivos/configurações/bindings/workflows fora desta fase. A revisão do Worker fica adiada até existir um mapa completo da reconstrução, em trabalho separado.

**Estado:** tradução estática avançada; auditoria de referências ainda em fechamento. Nenhum teste executado; sem merge/deploy; Cloudflare Worker não alterado nesta rodada.
