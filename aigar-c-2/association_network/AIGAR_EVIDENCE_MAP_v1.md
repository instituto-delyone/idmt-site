# AIGAR — mapa de evidências da reconstrução

## Confirmado

### Linguagem
A biblioteca **Linguagem materna** existe no repositório e foi organizada como camada anterior às bibliotecas temáticas. Ela contém texto-mãe, intenções humanas, profundidade, ambiguidade/incerteza e área de inserção.

### Biblioteca documental
Existe uma arquitetura documental baseada em PDF → extração → cache. O projeto histórico também registra processamento progressivo de 50 páginas por rodada.

### Raciocínio
Existe `raciocinio_rapido_hibrido.txt`, com divisão em etapas, conectivos lógicos, hipóteses alternativas, comparação, coesão, analogias, exemplos e declaração explícita de incerteza.

### AIGAR Core
O `aigar-core.js` histórico implementa leitura da entrada, detecção de função/profundidade, chamada ao backend e fallback local com memória, CSI, LibraryRouter, TimeEngine e ReasoningEngine.

### Diagnosis
O repositório atual possui uma arquitetura modular para Knowledge Base, estado clínico, geração de paciente/caso, hipóteses, investigações e orquestração.

## Parcialmente reconstruído

- CSI / roteamento.
- Recall / memória.
- Integração entre Linguagem materna, memória e biblioteca.
- Integração conversacional com Diagnosis.

## Evidenciado, mas ainda não formalmente recuperado

A existência histórica de **fragmentação cognitiva** é sustentada pela combinação de Memory Cards, bibliotecas, chunks/indexação e mecanismos de recuperação.

Isso não prova ainda qual era a unidade mínima de fragmento nem como fragmentos eram recombinados.

## Ainda não recuperado

- unidade mínima do fragmento;
- algoritmo histórico de recombinação;
- estrutura completa de metadados de cada fragmento;
- eventual grafo de relações;
- eventual embeddings;
- eventual vector DB;
- conteúdo literal completo do antigo Grammar Card;
- prompt histórico integral.

## Regra de reconstrução

Não converter hipótese em fato.

Toda implementação nova deve ser marcada como **proposta** até que exista evidência histórica correspondente.

## Referências internas principais

- `Engines/Aurora/Bibliotecas/Linguagem-materna/`
- `Engines/Aurora/AIGAR-engine/`
- `aigar-c-2/fragments-history/`
- `aigar-c-2/conversational-engine/`
- `docs/Js/` do Diagnosis

## Próxima investigação técnica

1. localizar todos os artefatos de chunk/indexação;
2. localizar geradores de fragmentos;
3. localizar schemas/metadados;
4. localizar mecanismos de recall;
5. comparar versões temporais;
6. só então especificar a unidade mínima e a recombinação.
