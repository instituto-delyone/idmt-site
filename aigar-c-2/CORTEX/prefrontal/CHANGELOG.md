# Registro de mudanças

**Estado:** migração estrutural e tradução de referências em andamento. Nenhum teste executado.

Registrar somente mudanças realmente efetuadas, com caminhos, referências atualizadas e commits correspondentes. Não executar testes nesta fase.

## Lote MIG-001 a MIG-007 — movimentação estrutural

- AIGAR_RUNTIME/working_memory.py → CORTEX/memory/working_memory.py
- AIGAR_RUNTIME/hippocampal_memory.py → CORTEX/memory/hippocampal_memory.py
- AIGAR_RUNTIME/prefrontal_controller.py → CORTEX/prefrontal/prefrontal_controller.py
- AIGAR_RUNTIME/language_network_adapter.py → CORTEX/language/language_network_adapter.py
- language_network/interpreter.py → CORTEX/language/interpreter.py
- language_network/language.json → CORTEX/language/language.json
- language_network/portuguese_language_knowledge.json → CORTEX/language/portuguese_language_knowledge.json

Os conteúdos foram preservados durante a movimentação; os SHAs individuais estão registrados em MIGRATION_INVENTORY_v1.md. Não houve teste, merge ou deploy. O Cloudflare Worker não foi alterado.

## Lote 2 — migrações MIG-008 a MIG-012

- AIGAR_RUNTIME/models.py → CORTEX/thalamus/models.py
- AIGAR_RUNTIME/aurora.py → CORTEX/prefrontal/aurora.py
- AIGAR_RUNTIME/knowledge_retrieval.py → CORTEX/engram/knowledge_retrieval.py
- AIGAR_RUNTIME/linguistic_interpreter.py → CORTEX/thalamus/linguistic_interpreter.py
- AIGAR_RUNTIME/diagnosis.py → Diagnosis/diagnosis.py

Conteúdo preservado; commits e SHAs estão em MIGRATION_INVENTORY_v1.md. Nenhum teste, merge ou deploy. Cloudflare Worker intocado.

## Contratos — primeiro lote

- CORTEX/thalamus/models.py é o contrato compartilhado de Intent, Depth, SourceStatus, ConversationReading, ConversationState, SourceTrace, RuntimeRequest e RuntimeResponse.
- Commit do contrato: 327be124ff163e39f20e7db8304de287c550ba58.
- Imports de contratos traduzidos: working_memory.py (2f0d56d9887f1550795bf1bda25bd66e994d18d8), hippocampal_memory.py (fddc5b1ecd68612f80d36713a6b2aa215c985f00), prefrontal_controller.py (627c615dbb659b5924ed0292545ed9e9f60d2b22), aurora.py (2f75be4937f8f4bf105ed4de74b726b01505d17f), knowledge_retrieval.py (388538db9c535545be6948fad3c0b7b6feaf6344), Diagnosis/diagnosis.py (a5c063c7a4e960755a04cc588c28139a61826faf).

## Tradução de referências — lote atual

- AIGAR_RUNTIME/main.py: imports locais legados substituídos por imports dos caminhos canônicos de CORTEX; DiagnosisAdapter permanece no pacote independente Diagnosis. O entry point HTTP foi mantido em AIGAR_RUNTIME.main:app.
- CORTEX/language/language_network_adapter.py: importa ConversationReading do contrato canônico e AIGARLanguage diretamente de CORTEX.language.interpreter; removida a referência ao caminho legado language_network/interpreter.py.
- CORTEX/README.md: registra o mapa provisoriamente imutável, os contratos canônicos, o entry point e as regras de escopo.

Os commits desta etapa serão anexados após cada gravação confirmada. Nenhum teste executado; sem merge/deploy; Worker intocado.
