# AIGAR Knowledge Retrieval

Camada independente de recuperação documental do AIGAR. A busca híbrida é implementada em `retriever.py` e usa `semantic_retriever.py` para expansão semântica e pontuação por fonte. O adapter de integração do runtime fica em `CORTEX/engram/knowledge_retrieval.py`; ele não substitui este pacote.

## Fluxo

`fonte → knowledge_encoding → chunks/IDs → índices e cache → KnowledgeRetriever → CORTEX/engram adapter → runtime`

O índice guarda IDs, ordem, páginas, checksums e metadados; o texto processado está nos arquivos de cache. O loader só retorna chunks recuperados/solicitados. O pacote não substitui Linguagem Materna, Reasoning, Memory ou Diagnosis.

## Contrato de caminho

- O caminho default do retriever é o próprio diretório `knowledge_retrieval/`, com subdiretórios `indexes/` e `cache/`.
- `bootstrap_sapiens.py` usa a fonte `biblioteca/Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf` relativa à raiz `aigar-c-2/` e invoca `knowledge_encoding.encode_knowledge` a partir dessa raiz. A fonte foi confirmada na árvore.
- O pipeline `knowledge_encoding/` permanece separado e sua saída default é `knowledge_retrieval/`.

## Configuração ainda não reconciliada em execução

O arquivo `config.json` declara `retrieval.method = "lexical"`, enquanto o código atual em `KnowledgeRetriever.search()` calcula score híbrido com componentes lexical, semântico e relevância da fonte. Na revisão estática, o construtor e o método de busca não carregam `config.json`; portanto esses valores não são tratados como configuração efetiva do código neste momento. Não alteramos a estratégia de busca nem conectamos a configuração durante a migração estrutural.

O arquivo de configuração também declara `cache_policy = "private_local"`, mas a árvore atual contém artefatos de cache/texto e índices versionados historicamente. A regra de ignore não cobre de forma geral todos os `.txt` de cache. Esses artefatos foram preservados; não foi feita exclusão nem mudança da política de distribuição. Antes de alterar cache ou regras de publicação, a política desejada deve ser reconciliada explicitamente fora da etapa de movimentação.

## Limites da validação

A descrição acima é baseada na inspeção estática do código e da árvore Git. Não demonstra que todos os índices/cache estejam presentes no ambiente de execução, nem que o ranking tenha sido validado em comportamento. Os testes do pacote permanecem incluídos na futura etapa de validação, após a conclusão da auditoria de referências.
