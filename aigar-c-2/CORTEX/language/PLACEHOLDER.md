# Language — estado de implementação

**Estado:** parcialmente implementado; este arquivo documenta o que já existe e o que ainda não foi migrado.

## Componentes existentes em `CORTEX/language/`
- `interpreter.py`: interpretador determinístico `AIGARLanguage`.
- `language.json` e `portuguese_language_knowledge.json`: dados carregados relativamente ao diretório do interpretador.
- `language_network_adapter.py`: adaptação do resultado para `ConversationReading`.

## Artefatos históricos ainda fora do destino
- `language_network/test_interpreter.py` continua no pacote histórico; não foi movido nesta fase e não foi executado.
- `language_network/portuguese_language_knowledge.pdf` permanece no caminho histórico, sem destino final definido.
- `language_network/README.md` e `language_network/__init__.py` também permanecem no diretório histórico.

Não existe atualmente um `CORTEX/language/README.md`; esta nota é o documento de estado local. Não afirmar que o teste foi movido.

## Ainda não implementado
A decomposição planejada em componentes conceituais para Wernicke, giro angular, Broca, gramática e léxico não está materializada como módulos separados. `CORTEX/thalamus/linguistic_interpreter.py` permanece uma heurística histórica independente para comparação; não é equivalente ao interpretador ativo.

## Regra de migração
Não substituir implementações nem alterar o conhecimento-fonte por inferência. Preservar os artefatos históricos enquanto seus destinos e consumidores não forem totalmente classificados. Testes continuam adiados até a conclusão da movimentação e atualização de referências.
