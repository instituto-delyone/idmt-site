# Roadmap da migração AIGAR-C

**Princípio:** concluir movimentações e referências antes da validação; preservar históricos; manter branch isolada e o Cloudflare Worker fora de escopo.

## Fase A — estrutura
**Estado:** movimentos MIG-001 a MIG-012 registrados e seus destinos presentes; MIG-013 moveu o teste do interpretador para junto do código ativo. Não apagar mais artefatos históricos sem referência cruzada.

## Fase B — contratos e runtime
**Estado:** implementada estaticamente.
- Contratos canônicos em `CORTEX/thalamus/models.py`.
- Entry point preservado em `AIGAR_RUNTIME/main.py`.
- Imports do entry point apontam para os destinos CORTEX.
- Adaptadores de linguagem, memória, biblioteca, Diagnosis e Aurora usam envelopes tipados.

## Fase C — referências de código/configuração
**Estado:** em fechamento.
1. Conferir imports de todos os módulos Python ativos e testes.
2. Conferir caminhos de dados dos JSONs e do retrieval/cache.
3. Conferir configurações de fase, comandos de execução e requirements.
4. Distinguir referências históricas de referências operacionais; atualizar documentação de mapa sem apagar a proveniência.
5. Registrar os resultados no inventário e changelog.
6. Não alterar Worker nem os seus arquivos/configurações/bindings/workflows.

## Fase D — congelamento do mapa
**Estado:** pendente até encerrar Fase C.
- Fechar a tabela por pasta/arquivo: destino, recodificação, dependências, pendência ou decisão de preservar.
- Não calcular percentagem global enquanto o denominador de arquivos-alvo imaginados não estiver fechado.
- Confirmar que o plano atual da branch continua isolado e o PR está aberto sem merge.

## Fase E — validação
**Estado:** ainda não iniciada.
- Somente depois das fases C e D, executar os testes existentes em ambiente com as dependências instaladas.
- Registrar resultados reais, inclusive falhas, sem corrigir silenciosamente diferenças de comportamento.
- Nenhum deploy é necessário ou autorizado para validação local.

## Fase futura separada — Worker
O mapa do Worker será tratado depois de a arquitetura remontada ficar documentada e revisável. Até lá, não alterar `AIGAR_CLOUDFLARE/`, seus símbolos, configs, bindings, chaves JSON ou workflows.
