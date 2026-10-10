# Language — processamento linguístico

**Estado:** parcialmente implementado na estrutura CORTEX.

## Componentes ativos

- `interpreter.py`: implementa `AIGARLanguage`, interpretador determinístico que carrega `language.json` e `portuguese_language_knowledge.json` relativos ao próprio módulo.
- `language_network_adapter.py`: converte o resultado do interpretador no contrato canônico `ConversationReading`, definido em `CORTEX/thalamus/models.py`.
- `test_interpreter.py`: testes existentes do interpretador, mantidos associados ao módulo após a migração; **não executados durante a fase de movimentação e atualização de referências**.

## Dados e proveniência

Os arquivos JSON foram migrados de `language_network/` para esta pasta, e o interpretador resolve seus caminhos a partir de `Path(__file__).parent`. Isso mantém os dados compilados juntos do código que os consome.

O documento `language_network/README.md` foi preservado no caminho histórico. Ele identifica a biblioteca Linguagem-materna em `Engines/Aurora/Bibliotecas/Linguagem-materna/` como fonte canônica do conhecimento original. O PDF foi movido para `CORTEX/language/portuguese_language_knowledge.pdf` no lote MIG-014; a cópia de fonte em `knowledge_retrieval/sources/` permanece preservada.

## Limites conhecidos

- A análise é determinística e heurística; não é um parser linguístico completo.
- `CORTEX/thalamus/linguistic_interpreter.py` é uma implementação histórica distinta, preservada para comparação; não é equivalente a `AIGARLanguage`.
- A existência deste módulo não significa que toda a arquitetura linguística planejada (Wernicke, giro angular, Broca, gramática e léxico) esteja implementada.
