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
