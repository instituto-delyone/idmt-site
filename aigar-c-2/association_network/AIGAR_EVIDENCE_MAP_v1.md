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


## Adendo de auditoria da árvore atual — 2026-10-10

Os itens acima registram evidências de reconstrução histórica e devem continuar preservados. A árvore e os contratos executáveis atuais acrescentam os seguintes limites:

- O runtime conversacional da branch agora usa os módulos de `CORTEX/` com entry point em `AIGAR_RUNTIME/main.py`; consulte `CORTEX/prefrontal/MIGRATION_MAP_FINAL_v1.md` para o crosswalk.
- O campo “Diagnosis” está evidenciado historicamente como motor especializado, mas o adaptador executável `aigar-c-2/Diagnosis/diagnosis.py` permanece desconectado e retorna `SourceTrace.status="missing"` sem inventar achados.
- As duas entradas do manifesto para `docs/Js/engine.js` e `docs/knowledge_base/` não existem com esses caminhos na árvore consultada. A existência de páginas em `docs/pesquisas/Diagnosis/` não prova que sejam equivalentes ao motor ou à base ausente. A auditoria está em `AIGAR_SOURCE_MANIFEST_AUDIT_v1.md`.
- O contrato documental `AIGAR_RUNTIME_CONTRACT_v1.json` e os modelos Pydantic de `CORTEX/thalamus/models.py` têm diferenças de schema para ambiguidade, incerteza e resultado estruturado. Não converter o contrato v1 silenciosamente; consulte `AIGAR_RUNTIME_CONTRACT_RECONCILIATION_v1.md`.
- A comparação de código confirmou a existência de um interpretador linguístico executável, de memória de sessão, de recuperação híbrida de documentos e de um controlador de planejamento inicial. Isso não prova recuperação persistente, raciocínio avançado ou integração clínica.
- A auditoria desta fase não modifica `AIGAR_CLOUDFLARE/`. O mapa dedicado do Worker é uma etapa posterior, depois do fechamento do mapa da arquitetura remontada.

Essa atualização separa a evidência do histórico daquilo que a árvore atual demonstra. Nenhum teste foi executado nesta etapa.
