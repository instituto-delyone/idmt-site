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
