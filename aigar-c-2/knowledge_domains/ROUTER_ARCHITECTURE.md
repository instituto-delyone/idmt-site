# Router hierárquico — contrato de arquitetura (proposta)

## Objetivo
Navegar no conhecimento em níveis explícitos, com rastreabilidade, sem confundir classificação temática com recuperação de evidência.

## Pipeline
1. Normalização da consulta sem apagar termos originais.
2. Geração de candidatos de domínio a partir de sinais, contexto e metadados.
3. Seleção/retensão de múltiplos candidatos quando houver ambiguidade.
4. Navegação para subdomínio e tópico usando índices locais.
5. Planejamento de recuperação de documentos/unidades.
6. Validação de proveniência: documento, edição/identificador, página ou seção, checksum e estado de revisão.
7. Retorno com referências às fontes; declarar insuficiência quando não houver evidência.

## Separação de responsabilidades
- Domain Router: domínio(s) candidato(s).
- Hierarchical Index Navigator: percorre domínio, subdomínio e tópico.
- Retrieval Planner: seleciona documentos e chunks já identificados.
- Evidence Validator: verifica proveniência e status.
- Cross-domain Linker: FUTURO; desativado até existir avaliação e relações tipadas confiáveis.

## Regras de fidelidade
- Não inventar subtemas, relações ou citações.
- Não tratar sinais lexicais como prova de relação conceitual.
- Não misturar chunks sintéticos de teste com fontes verificadas.
- Preservar localização original (página/capítulo/seção) e checksum.
- Se a classificação não for segura, retornar mais de um candidato ou abster-se.
- Cross-link só poderá ser ativado quando cada aresta tiver tipo, justificativa, fonte/proveniência e avaliação.

## Estados de conteúdo
- scaffold: domínio/estrutura cadastrado, sem corpus validado.
- prototype: dados de teste ou taxonomia preliminar.
- reviewed: classificado/revisado, ainda sujeito a validação de fonte.
- verified: fonte e localização verificadas segundo critérios do projeto.

## Fora do escopo desta etapa
Ingestão completa de livros, indexação vetorial, integração de catálogo R2, alterações D1, ativação ACLR candidate e deploy do Worker.
