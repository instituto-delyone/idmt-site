# ACLR — domínios e navegação hierárquica

Esta camada organiza a taxonomia de conhecimento e os índices de navegação. Ela não altera rotas públicas, runtime, HREFs, biblioteca R2, D1 ou mecanismos de recuperação em produção.

## Organização

- `router_index.json`: registro mestre dos domínios e sinais iniciais.
- `<domínio>/domain.json`: metadados e estado do domínio.
- `<domínio>/index/index.json`: índice hierárquico do domínio e seus subdomínios.
- `<domínio>/content/`: reservado a conteúdo extraído e validado; livros brutos não devem ser confundidos com chunks indexados.

## Domínios cadastrados

História, Matemática, Língua Portuguesa, Geografia, Filosofia, Física, Química, Biologia, Sociologia, Computação, Literatura e Economia.

Os três domínios iniciais mantêm seus índices de protótipo existentes. Os demais foram cadastrados como scaffolds taxonômicos, sem afirmar que já possuem livros ou conteúdo factual disponível.

## Navegação pretendida

`domínio → subdomínio → tópico → documento → unidade/chunk`

O Router deve preservar candidatos ambíguos em vez de escolher arbitrariamente. A recuperação de conteúdo só ocorre depois da seleção dos IDs e da verificação de proveniência.

## Cross-domain

Cross-links semânticos ficam desativados nesta etapa. Não criar relações entre disciplinas por mera coincidência de palavras. Uma futura camada interdisciplinar deverá exigir evidência explícita, relação tipada, proveniência e avaliação; se não puder fazê-lo com fidelidade, deve abster-se.

## Ingestão futura

Livros podem ser adicionados como fontes brutas. A pipeline posterior deverá extrair texto, segmentar unidades, preservar página/capítulo e checksum, classificar com revisão e só então publicar índices. A biblioteca R2 será integrada em etapa posterior.

**Estado:** estrutura taxonômica inicial em desenvolvimento; não é um corpus validado nem um Router de produção.
