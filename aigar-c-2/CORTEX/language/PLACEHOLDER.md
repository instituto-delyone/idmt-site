# Language — estado de implementação

**Estado:** parcialmente implementado; este arquivo deixa de ser um placeholder de subsistema vazio.

## Componentes existentes
- `interpreter.py`: interpretador determinístico `AIGARLanguage`.
- `language.json` e `portuguese_language_knowledge.json`: dados carregados relativamente ao diretório do interpretador.
- `language_network_adapter.py`: adaptação do resultado para `ConversationReading`.
- `test_interpreter.py`: testes movidos junto ao módulo, ainda não executados.

Detalhes e limites estão em `CORTEX/language/README.md`.

## Ainda não implementado
A decomposição planejada em componentes conceituais para Wernicke, giro angular, Broca, gramática e léxico não está materializada como módulos separados. `CORTEX/thalamus/linguistic_interpreter.py` permanece uma heurística histórica independente para comparação; não é equivalente ao interpretador ativo.

## Regra de migração
Não substituir implementações nem alterar o conhecimento-fonte por inferência. Preservar `language_network/README.md` e o PDF histórico enquanto seus destinos/consumidores não forem totalmente classificados.
