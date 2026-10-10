# Plano de migração — AIGAR para a fundação do IDMT

## Fase 0 — preservação

Não apagar nem substituir os artefatos históricos.

A pasta `AIGAR_CORE` funciona inicialmente como camada de integração/documentação.

## Fase 1 — Linguagem

Usar como fonte canônica:

`Engines/Aurora/Bibliotecas/Linguagem-materna/`

Componentes:

- `00_texto_mae.md`
- `01_intencoes_humanas.md`
- `02_profundidade_resposta.md`
- `03_ambiguidade_incerteza.md`
- `04_area_de_insercao.md`

## Fase 2 — raciocínio

Usar:

`Engines/Aurora/AIGAR-engine/raciocinio_rapido_hibrido.txt`

Não transformar as regras de raciocínio em um bloco monolítico dentro do Diagnosis.

## Fase 3 — memória

Usar os Memory Cards históricos como fontes de reconstrução.

Criar depois um adaptador único de memória/recall, em vez de espalhar leitura de YAML por vários módulos.

## Fase 4 — CSI

Criar uma interface de contrato entre linguagem e roteamento.

Entrada: leitura conversacional.

Saída: intenção, domínio, candidatos de biblioteca/módulo e necessidade de memória.

## Fase 5 — biblioteca

Manter a biblioteca documental independente do diálogo.

O AIGAR solicita contexto; a biblioteca devolve evidência.

## Fase 6 — Diagnosis

O Diagnosis recebe uma solicitação estruturada e devolve estado/resultado estruturado.

Ele não precisa produzir sozinho a frase final.

## Fase 7 — Aurora

Aurora recebe:

- leitura da conversa;
- contexto recuperado;
- resultado do raciocínio;
- nível de profundidade;
- limites/incertezas.

Então produz a resposta final.

## Fase 8 — testes

Criar testes para:

1. saudação;
2. definição simples;
3. pergunta delimitada;
4. pedido profundo;
5. continuação ambígua;
6. ausência de fonte;
7. caso clínico;
8. consulta de biblioteca;
9. recall;
10. integração com Diagnosis.

## Critério de sucesso

A camada conversacional deve conseguir manter uma sequência de diálogo sem obrigar o usuário a saber qual módulo foi chamado.

O fluxo desejado é:

`conversa → linguagem → memória/biblioteca/Diagnosis → raciocínio → Aurora → resposta`

