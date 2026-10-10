# AIGAR Language Runtime — documentação histórica da fonte

Este README documenta a organização histórica do runtime de linguagem e a origem da representação JSON consumida pelo interpretador.

A fonte canônica do conhecimento linguístico continua sendo:
`Engines/Aurora/Bibliotecas/Linguagem-materna/`

`language.json` é uma camada compilada para execução; não substitui os textos-fonte.

## Estado após a migração

O módulo ativo do interpretador e os dois JSONs usados diretamente por ele foram migrados para `CORTEX/language/`:

- `CORTEX/language/interpreter.py`
- `CORTEX/language/language.json`
- `CORTEX/language/portuguese_language_knowledge.json`
- `CORTEX/language/language_network_adapter.py`
- `CORTEX/language/test_interpreter.py` (localização atual do teste; import atualizado para o caminho canônico).

O teste permanece sem execução manual nesta fase. O workflow de validação agora aponta para seu caminho atual em `CORTEX/language/`.

O PDF `portuguese_language_knowledge.pdf` está em `CORTEX/language/`; uma cópia de fonte preservada está em `knowledge_retrieval/sources/`. Não existe cópia operacional do PDF em `language_network/` na árvore atual.

A sequência funcional documentada permanece: carregar linguagem, interpretar entrada, estimar intenção, definir escopo e profundidade, decidir sobre memória/biblioteca e entregar estado ao runtime. A geração da resposta permanece separada do interpretador.
