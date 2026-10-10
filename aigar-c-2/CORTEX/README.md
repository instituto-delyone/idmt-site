# CORTEX — Arquitetura neurocognitiva do AIGAR-C

Esta pasta receberá, por etapas, os módulos da arquitetura neurocognitiva do AIGAR-C.

## Regra desta fase
- Esta etapa cria somente a estrutura e seus placeholders.
- Os arquivos funcionais existentes permanecem nos caminhos atuais até o inventário e a migração controlada.
- Placeholders documentam intenção; não representam código funcional.
- Nenhum teste, merge ou deploy faz parte desta fase.
- O Cloudflare Worker existente permanece intocado.

## Módulos
- `sara/`: inicialização, prontidão e estado do runtime.
- `thalamus/`: roteamento contextual, seleção de recursos e Pattern Reasoner.
- `sensory/`: entrada e classificação de sinais.
- `default_mode_network/`: estado interno, autorrepresentação e reflexão.
- `language/`: processamento linguístico.
- `reasoning_engine/`: planejamento, avaliação de evidências e suficiência.
- `memory/`: coordenação dos mecanismos de memória.
- `worker_bridge/`: contratos e comunicação entre componentes, sem alterar Workers existentes.
- `prefrontal/`: documentação da evolução, decisões, tendências e roadmap.
- `occipital/`: interface visual, index, assets e components, a organizar depois.
