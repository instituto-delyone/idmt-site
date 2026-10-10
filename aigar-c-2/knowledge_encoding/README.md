# AIGAR Knowledge Encoding

O Codificador transforma PDF/TXT/MD em **IDs de chunks + índice + cache local**.

```
PDF/TXT/MD
   |
   v
Codificador
   +--> índice público: IDs, ordem, páginas, checksums
   +--> cache privado: texto dos chunks
                 |
                 v
             Retriever
                 |
                 v
               AIGAR
```

## PDF

O padrão é 25 páginas por chunk, alinhado à organização histórica observada na biblioteca de Fisiologia:

```bash
python -m knowledge_encoding.encode_knowledge "biblioteca/Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf" --key sapiens
```

O texto processado vai para `knowledge_retrieval/cache/`, que está no `.gitignore`. O índice pode ser versionado sem publicar o texto.

## IDs

O ID é derivado de fonte + posição + checksum do texto. A sequência é metadado; ela não precisa aparecer no ID.

## TXT/MD

O Codificador preserva parágrafos e usa aproximadamente 24.000 caracteres por chunk por padrão.

## Princípio

O Codificador não resume nem reescreve a fonte. Ele cria unidades recuperáveis. Fontes protegidas devem permanecer em cache privado quando não houver autorização para redistribuir seu texto.
