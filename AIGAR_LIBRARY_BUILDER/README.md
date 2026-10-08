# AIGAR Library Builder

Fluxo histórico:
PDF/TXT -> extração -> chunks -> índice -> cache -> retrieval.

PDF: 25 páginas por chunk por padrão, alinhado ao padrão observado nos chunks históricos de Fisiologia.

TXT/MD: divisão por tamanho aproximado, preservando limites de parágrafo.

O builder preserva o texto. Não resume nem reescreve.

Exemplos:
python -m AIGAR_LIBRARY_BUILDER.build --input livro.pdf --library "Humanidade"
python -m AIGAR_LIBRARY_BUILDER.build --input livro.txt --library "Computação" --chars 24000

Para indexar chunks já existentes:
python -m AIGAR_LIBRARY_BUILDER.index_existing --library Engines/Aurora/Bibliotecas/Medicina/Fisiologia
