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
- `language_network/test_interpreter.py` (permanece neste diretório histórico; não foi movido nesta fase).

O teste continua no caminho original e não foi executado. Sua migração depende de revisar os imports e referências junto com o restante da tradução, sem alterar seu comportamento.

O PDF histórico `portuguese_language_knowledge.pdf` permanece nesta pasta. Seu destino definitivo ainda não foi decidido porque a relação entre esse arquivo de referência e os dados compilados precisa ser rastreada; ele foi preservado deliberadamente.

A sequência funcional documentada permanece: carregar linguagem, interpretar entrada, estimar intenção, definir escopo e profundidade, decidir sobre memória/biblioteca e entregar estado ao runtime. A geração da resposta permanece separada do interpretador.
