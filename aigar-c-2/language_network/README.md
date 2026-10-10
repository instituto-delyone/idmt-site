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
- `CORTEX/language/test_interpreter.py`

O teste do interpretador foi movido para junto do módulo e importa o novo caminho canônico. Ele ainda não foi executado nesta fase.

O PDF histórico `portuguese_language_knowledge.pdf` permanece nesta pasta. Seu destino definitivo ainda não foi decidido porque a relação entre esse arquivo de referência e os dados compilados precisa ser rastreada; ele foi preservado deliberadamente.

A sequência funcional documentada permanece: carregar linguagem, interpretar entrada, estimar intenção, definir escopo e profundidade, decidir sobre memória/biblioteca e entregar estado ao runtime. A geração da resposta permanece separada do interpretador.
