# AIGAR Language Runtime

Transforma a biblioteca histórica Linguagem-materna em uma representação JSON consumível pelo runtime.

A fonte canônica continua sendo:
Engines/Aurora/Bibliotecas/Linguagem-materna/

language.json é uma camada compilada para execução; não substitui os textos-fonte.

Ordem:
1. carregar linguagem
2. interpretar entrada
3. estimar intenção
4. definir escopo
5. estimar profundidade
6. decidir memória/biblioteca
7. entregar estado ao restante do AIGAR

A geração da resposta permanece separada do interpretador.
