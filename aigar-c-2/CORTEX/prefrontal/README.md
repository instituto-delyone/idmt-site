# Prefrontal — planejamento executivo e documentação de evolução

Esta pasta contém tanto módulos ativos do runtime quanto documentação arquitetural. A formulação anterior que a descrevia como destinada somente à documentação não corresponde mais à árvore atual.

## Módulos ativos
- `prefrontal_controller.py`: seleciona até três sentenças candidatas a evidência e produz um `ReasoningPlan`; é uma implementação inicial baseada em sobreposição lexical, não um motor geral completo.
- `aurora.py`: apresenta a resposta com base na leitura, no contexto e no plano; a API pública tipada é `respond(AuroraRequest) -> AuroraResult`.

## Documentos
- `EVOLUTION.md`: evolução efetivamente observada e capacidades desenvolvidas.
- `ARCHITECTURE.md`: arquitetura e relações entre módulos.
- `TRENDS.md`: tendências, hipóteses e oportunidades de melhoria.
- `DECISIONS.md`: decisões arquiteturais e suas justificativas.
- `CHANGELOG.md`: mudanças realmente realizadas.
- `MIGRATION_INVENTORY_v1.md`: inventário por arquivo, estado de migração e referências.
- `MIGRATION_MAP_FINAL_v1.md`: mapa de destino e registro da fase de tradução.
- `ROADMAP.md`: etapas futuras.

## Limites
Os nomes neuroanatômicos são analogias organizacionais/funcionais, não equivalências literais com estruturas biológicas. A existência dos módulos não valida execução integral do runtime. Testes permanecem adiados até a conclusão da movimentação e atualização das referências.
