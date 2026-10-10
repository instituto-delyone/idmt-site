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

### Diagnosis — fronteira externa
O Diagnosis é um projeto mantido em repositório separado. Ele não faz parte da árvore AIGAR-C e não deve ser tratado como dependência local deste runtime. Dentro do AIGAR-C existe apenas o adaptador `CORTEX/reasoning_engine/diagnosis.py`, que declara a integração como ausente até que uma ligação explícita seja implementada.

## Parcialmente reconstruído

- CSI / roteamento.
- Recall / memória.
- Integração entre Linguagem materna, memória e biblioteca.
- Integração conversacional com o projeto Diagnosis externo (pendente e fora do escopo desta revisão).

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
- Projeto Diagnosis externo (não é fonte operacional local do AIGAR-C)

## Próxima investigação técnica

1. localizar todos os artefatos de chunk/indexação;
2. localizar geradores de fragmentos;
3. localizar schemas/metadados;
4. localizar mecanismos de recall;
5. comparar versões temporais;
6. só então especificar a unidade mínima e a recombinação.


## Adendo de auditoria da árvore atual — 2026-10-10

Os itens acima registram evidências de reconstrução histórica e devem continuar preservados. A árvore e os contratos executáveis atuais acrescentam os seguintes limites:

- O runtime conversacional da branch agora usa os módulos de `CORTEX/` com entry point em `AIGAR_RUNTIME/main.py`; consulte `CORTEX/prefrontal/MIGRATION_MAP_FINAL_v1.md` para o crosswalk.
- O Diagnosis é externo ao AIGAR-C. O adaptador local `CORTEX/reasoning_engine/diagnosis.py` retorna `SourceTrace.status="missing"` sem inventar achados.
- As referências históricas ao motor e à base de conhecimento clínico pertencem ao projeto Diagnosis separado; não são dependências locais do AIGAR-C e não devem ser substituídas por candidatos não comprovados.
- O contrato documental `AIGAR_RUNTIME_CONTRACT_v1.json` e os modelos Pydantic de `CORTEX/thalamus/models.py` têm diferenças de schema para ambiguidade, incerteza e resultado estruturado. Não converter o contrato v1 silenciosamente; consulte `AIGAR_RUNTIME_CONTRACT_RECONCILIATION_v1.md`.
- A comparação de código confirmou a existência de um interpretador linguístico executável, de memória de sessão, de recuperação híbrida de documentos e de um controlador de planejamento inicial. Isso não prova recuperação persistente, raciocínio avançado ou integração clínica.
- A auditoria desta fase não modifica `AIGAR_CLOUDFLARE/`. O mapa dedicado do Worker é uma etapa posterior, depois do fechamento do mapa da arquitetura remontada.

Essa atualização separa a evidência do histórico daquilo que a árvore atual demonstra. Nenhum teste foi executado nesta etapa.
