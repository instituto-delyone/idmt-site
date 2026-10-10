# Thalamus — estado de implementação

**Estado:** parcialmente implementado para contratos compartilhados e roteamento contextual básico.

## Componentes existentes
- `models.py`: contratos canônicos Pydantic para leitura, decisão de roteamento, plano, estado, rastros, entrada e saída de runtime, memória, biblioteca, Diagnosis e Aurora.
- `context_router.py`: converte `ConversationReading` em `RoutingDecision` sem executar diretamente os subsistemas.
- `linguistic_interpreter.py`: heurística histórica simples preservada para comparação; o runtime ativo usa `CORTEX.language.interpreter.AIGARLanguage` por meio de `LanguageNetworkAdapter`.

## Ainda não implementado
O Pattern Reasoner e a seleção contextual avançada de recursos não existem como componentes independentes. A decisão `use_reasoning` está representada no contrato, mas a política de execução final precisa ser resolvida na fase de integração, sem mudança comportamental acidental.
