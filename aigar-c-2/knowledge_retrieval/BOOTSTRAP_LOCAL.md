# Bootstrap local da biblioteca

A fonte Sapiens já está registrada no repositório. Para transformar o PDF em chunks, execute localmente a partir de `aigar-c-2/`:

```bash
pip install -r AIGAR_LIBRARY_BUILDER/requirements.txt
python AIGAR_LIBRARY/bootstrap_sapiens.py
```

O Builder:
1. lê o PDF;
2. divide em blocos de 25 páginas;
3. cria IDs determinísticos;
4. grava o texto somente em `AIGAR_LIBRARY/cache/sapiens/`;
5. cria o índice local;
6. atualiza o índice público somente com metadados.

O cache está no `.gitignore`. Portanto o repositório não vira um espelho textual do livro.

Depois do bootstrap, o Runtime consegue usar o cache com o Retriever local. Nenhuma API é necessária nesta etapa.
