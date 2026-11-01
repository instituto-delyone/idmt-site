# ACLR — protótipo de domínios de conhecimento

Este diretório é uma camada paralela de prototipagem para o ACLR. Não altera rotas, HREFs, runtime, biblioteca R2 nem os mecanismos atuais de recuperação.

## Estrutura

- `router_index.json`: índice mestre que associa sinais de assunto a domínios.
- `<domínio>/index/index.json`: índice do domínio, com subdomínios e referências a protochunks.
- `<domínio>/content/*.md`: protochunks textuais pequenos, escritos apenas para testar navegação e recuperação.

## Domínios iniciais

- `history`: história antiga, medieval, moderna e contemporânea.
- `mathematics`: álgebra, geometria e cálculo.
- `portuguese`: morfologia, sintaxe, semântica e pragmática.

## Contrato mínimo do protótipo

O índice mestre aponta para um domínio. O índice do domínio aponta para um subdomínio e para um ou mais chunks. O conteúdo só deve ser lido depois que a navegação pelos índices indicar os IDs correspondentes.

Os textos são conteúdo sintético de teste, não fontes acadêmicas nem material de referência factual. Quando a biblioteca real for adicionada ao R2, estes protótipos deverão ser substituídos ou marcados como exemplos, sem confundi-los com documentos verificados.

**Estado:** scaffolding e dados de teste; ainda não integrado ao Worker nem validado ponta a ponta.
