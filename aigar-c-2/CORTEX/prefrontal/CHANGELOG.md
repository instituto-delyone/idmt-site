# Registro de mudanças

**Estado:** migração estrutural em andamento; imports e referências ainda pendentes. Nenhum teste executado.

Registrar somente mudanças realmente efetuadas, com caminho anterior, caminho novo, referências atualizadas e commit correspondente. Não executar testes nesta fase.


## Lote MIG-001 a MIG-007 — movimentação estrutural

- `AIGAR_RUNTIME/working_memory.py` → `CORTEX/memory/working_memory.py`
- `AIGAR_RUNTIME/hippocampal_memory.py` → `CORTEX/memory/hippocampal_memory.py`
- `AIGAR_RUNTIME/prefrontal_controller.py` → `CORTEX/prefrontal/prefrontal_controller.py`
- `AIGAR_RUNTIME/language_network_adapter.py` → `CORTEX/language/language_network_adapter.py`
- `language_network/interpreter.py` → `CORTEX/language/interpreter.py`
- `language_network/language.json` → `CORTEX/language/language.json`
- `language_network/portuguese_language_knowledge.json` → `CORTEX/language/portuguese_language_knowledge.json`

Os conteúdos foram preservados durante a movimentação; as referências antigas ainda não foram atualizadas. Os SHAs individuais de criação e remoção estão registrados em `MIGRATION_INVENTORY_v1.md`. Não houve teste, merge ou deploy. O Cloudflare Worker não foi alterado.


## Lote 2 — migrações MIG-008 a MIG-012

- `AIGAR_RUNTIME/models.py` → `CORTEX/thalamus/models.py`
- `AIGAR_RUNTIME/aurora.py` → `CORTEX/prefrontal/aurora.py`
- `AIGAR_RUNTIME/knowledge_retrieval.py` → `CORTEX/engram/knowledge_retrieval.py`
- `AIGAR_RUNTIME/linguistic_interpreter.py` → `CORTEX/thalamus/linguistic_interpreter.py`
- `AIGAR_RUNTIME/diagnosis.py` → `Diagnosis/diagnosis.py` (adaptador separado para integração posterior)

Conteúdo preservado; origens removidas após criar os destinos. Os commits e SHAs de blob estão registrados em `MIGRATION_INVENTORY_v1.md`. Referências/imports ainda não traduzidos. Nenhum teste, merge ou deploy. Cloudflare Worker intocado.

## Fechamento do inventário — sem movimentação adicional

Inspecionada a árvore recursiva da branch e revisados `AIGAR_RUNTIME/main.py`, READMEs do runtime/CORTEX/UI/biblioteca/encoding/linguagem e contratos centrais de `association_network/`. O inventário foi ampliado para documentar runtime legado, pacotes externos, contratos históricos, UI, sincronização, corpus, PDFs e artefatos gerados, além das pendências de tradução de referências.

O inventário foi registrado em commit `79b975cfbdd96e5616fa370df950946ff01c6871`. Esta atualização não moveu outros arquivos, não alterou imports, não executou testes, não fez merge/deploy e não tocou no Cloudflare Worker.

## Contratos — primeiro lote de codificação

- Contrato canônico atualizado em `CORTEX/thalamus/models.py`: documenta `Intent`, `Depth`, `SourceStatus`, `ConversationReading`, `ConversationState`, `SourceTrace`, `RuntimeRequest` e `RuntimeResponse`. Campos, nomes e defaults de runtime foram preservados; a mudança foi de documentação/organização do contrato, não uma alteração intencional de semântica.
- Commit do contrato: `327be124ff163e39f20e7db8304de287c550ba58`.
- Imports de contratos compartilhados agora apontam para `CORTEX.thalamus.models` em:
  - `CORTEX/memory/working_memory.py` — `2f0d56d9887f1550795bf1bda25bd66e994d18d8`
  - `CORTEX/memory/hippocampal_memory.py` — `fddc5b1ecd68612f80d36713a6b2aa215c985f00`
  - `CORTEX/prefrontal/prefrontal_controller.py` — `627c615dbb659b5924ed0292545ed9e9f60d2b22`
  - `CORTEX/prefrontal/aurora.py` — `2f75be4937f8f4bf105ed4de74b726b01505d17f`
  - `CORTEX/engram/knowledge_retrieval.py` — `388538db9c535545be6948fad3c0b7b6feaf6344`
  - `Diagnosis/diagnosis.py` — `a5c063c7a4e960755a04cc588c28139a61826faf`

**Limite desta etapa:** o entry point `AIGAR_RUNTIME/main.py` e demais imports legados ainda não foram traduzidos. Nenhum teste executado; não houve merge/deploy; Worker não alterado.
