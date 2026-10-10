# Reasoning Engine — estado de implementação

**Estado:** parcialmente representado por componentes existentes, mas ainda não consolidado como subsistema independente em `CORTEX/reasoning_engine/`.

## Componentes relacionados já existentes
- `CORTEX/prefrontal/prefrontal_controller.py`: seleciona evidências da biblioteca e constrói um `ReasoningPlan`.
- `CORTEX/thalamus/models.py`: define o contrato compartilhado `ReasoningPlan`.
- `AIGAR_RUNTIME/main.py`: orquestra a chamada ao controlador e entrega o plano à camada Aurora.

Esses componentes permanecem nos caminhos atuais durante a migração. A presença deles não significa que o subsistema esteja consolidado no diretório `reasoning_engine/`.

## Lacunas e decisão pendente
- Coordenar raciocínio, planejamento, avaliação de evidências, verificação de suficiência e construção de respostas em uma fronteira arquitetural explícita.
- Resolver a política de execução: `RoutingDecision.use_reasoning` existe, mas o runtime ainda chama o controlador independentemente desse campo.
- Comparar propostas históricas antes de mover ou duplicar componentes.

Não mover nem duplicar o controlador durante esta etapa sem registrar a decisão e atualizar todas as referências. Nenhum teste deve ser executado antes da conclusão da fase de movimentação e tradução das referências.
