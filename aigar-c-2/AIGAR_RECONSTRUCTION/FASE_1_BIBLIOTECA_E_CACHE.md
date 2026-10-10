# AIGAR — Fase 1: Biblioteca, Chunks e Cache

## Objetivo

Restaurar a capacidade de o AIGAR receber fontes documentais, transformá-las em unidades recuperáveis e carregar apenas o conhecimento necessário durante uma conversa.

## O que foi implementado

### 1. Builder

`AIGAR_LIBRARY_BUILDER/build.py` aceita PDF, TXT e MD.

PDF:
- PyPDF2;
- 25 páginas por chunk por padrão;
- preservação do texto;
- sem sumarização.

TXT/MD:
- divisão aproximada por caracteres;
- preservação de parágrafos.

### 2. Identidade dos chunks

Cada chunk recebe um ID derivado da fonte, posição e checksum do texto.

A sequência é mantida como metadado. O ID não precisa ser `chunk_001`.

Isso permite:
- localizar uma unidade;
- verificar integridade;
- reconstruir uma sequência;
- detectar alteração da fonte.

### 3. Separação índice/cache

O índice descreve:
- ID;
- fonte;
- sequência;
- páginas;
- checksum;
- tamanho.

O texto processado fica no cache local.

### 4. Retriever

`AIGAR_LIBRARY/retriever.py` implementa:
- busca lexical local;
- carregamento por ID;
- reconstrução ordenada de vários chunks.

### 5. Runtime

`AIGAR_RUNTIME/library.py` agora usa o Retriever real, substituindo o placeholder de biblioteca.

## Sapiens

A fonte existente foi registrada como `sapiens`, com 25 páginas por chunk.

O índice público registra a fonte e seu checksum, mas os textos dos chunks não são publicados no GitHub. O processamento efetivo deve ser executado localmente pelo bootstrap.

Isso preserva a arquitetura desejada sem transformar o repositório em uma cópia textual do livro.

## Estado

- Builder: implementado.
- IDs: implementados.
- Cache: implementado.
- Retriever: implementado.
- Integração Runtime → Library: implementada.
- Registro Sapiens: implementado.
- Cache local Sapiens: pronto para execução local.
- API: **não necessária ainda**.

## Próximo passo arquitetural

Com esta base funcionando, a camada HTML pode apenas comandar fases e mostrar estado:

```
FASE 1 — Linguagem
FASE 2 — Humanidade
FASE 3 — Matemática
FASE 4 — Computação
...
```

O HTML não precisa conhecer o conteúdo dos livros. Ele apenas aciona módulos e consulta seus estados.


## Adendo de localização atual na branch de migração (2026-10-10)

Este documento registra a reconstrução histórica de builder, cache e retriever; seus caminhos iniciais não foram apagados do texto para preservar o contexto da época. Na árvore atual de `neurocognitive-migration`, o crosswalk observado é:

- Builder/pipeline de ingestão: `knowledge_encoding/encode_knowledge.py` e `knowledge_encoding/encode_existing_chunks.py`.
- Busca híbrida, semântica, índices e cache: pacote independente `knowledge_retrieval/`, em particular `knowledge_retrieval/retriever.py` e `knowledge_retrieval/semantic_retriever.py`.
- Adapter de integração no runtime: `CORTEX/engram/knowledge_retrieval.py`, usando contratos de `CORTEX/thalamus/models.py`.
- A entrada operacional do runtime permanece `AIGAR_RUNTIME/main.py`.

O pacote externo `knowledge_retrieval/` não foi movido nem substituído por `CORTEX/engram`; o adapter chama o pacote independente. O cache local/indexes devem permanecer no pacote e não devem ser renomeados junto com o código sem mapear cada caminho.

**Limites:** o registro histórico de que uma integração funcionava numa etapa anterior não substitui uma validação atual. Testes do pacote e runtime permanecem sujeitos ao gate geral: concluir a auditoria estática de caminhos/configurações antes de executar. Sem merge/deploy e sem qualquer alteração ao Cloudflare Worker.
