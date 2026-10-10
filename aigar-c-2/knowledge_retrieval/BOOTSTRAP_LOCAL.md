# Bootstrap local da biblioteca

A fonte Sapiens já está registrada no repositório. Para transformar o PDF em chunks, execute localmente a partir de `aigar-c-2/`:

```bash
pip install -r knowledge_encoding/requirements.txt
python knowledge_retrieval/bootstrap_sapiens.py
```

O Codificador de Conhecimento: 
1. lê o PDF;
2. divide em blocos de 25 páginas;
3. cria IDs determinísticos;
4. grava o texto somente em `knowledge_retrieval/cache/sapiens/`;
5. cria o índice local;
6. atualiza o índice público somente com metadados.

O cache está no `.gitignore`. Portanto o repositório não vira um espelho textual do livro.

Depois do bootstrap, o Runtime consegue usar o cache com o Retriever local. Nenhuma API é necessária nesta etapa.
