# Arquitetura do AIGAR-C

**Estado:** mapa estático preenchido a partir da árvore real de `neurocognitive-migration`. Não constitui validação funcional.

## Fluxo do runtime

```text
HTTP RuntimeRequest
       |
       v
CORTEX.sensory.ingress.capture_request
       |
       v
CORTEX.language.language_network_adapter.LanguageNetworkAdapter
       |
       v
CORTEX.thalamus.models.ConversationReading
       |
       v
CORTEX.thalamus.context_router.route_reading
       |
       +----> CORTEX.memory.HippocampalMemoryAdapter (se selecionado)
       |
       +----> CORTEX.engram.KnowledgeRetrievalAdapter (se selecionado)
       |             |
       |             +--> pacote independente knowledge_retrieval
       |
       +----> CORTEX.reasoning_engine.diagnosis.DiagnosisAdapter (se selecionado; motor especializado pertence a outro repositório e está desconectado)
       |
       v
CORTEX.prefrontal.PrefrontalController
       |
       v
CORTEX.prefrontal.Aurora
       |
       v
RuntimeResponse (texto, estado, fontes, confiança e plano)
```

O entry point permanece `AIGAR_RUNTIME/main.py`. O desenho mostra a sequência observada no código e as fronteiras presentes, não garante que todas as dependências estejam operacionais.

## Componentes canônicos

| Área | Caminho ativo | Responsabilidade observada | Limite atual |
|---|---|---|---|
| Entrada | `CORTEX/sensory/ingress.py` | Envelopa texto e sessão em `SensoryInput` | Texto apenas; sem processamento multimodal |
| Contratos | `CORTEX/thalamus/models.py` | Modelos Pydantic compartilhados | Contratos não significam implementação especializada pronta |
| Roteamento | `CORTEX/thalamus/context_router.py` | Converte leitura em `RoutingDecision` | Política final de `use_reasoning` ainda não controla o pipeline |
| Linguagem | `CORTEX/language/interpreter.py` | Análise determinística/heurística, usando JSONs adjacentes | Não é parser linguístico completo |
| Adaptador linguístico | `CORTEX/language/language_network_adapter.py` | Converte resultado para `ConversationReading` | O interpretador legado é diferente e permanece preservado |
| Estado | `CORTEX/memory/working_memory.py` | Estado em memória do processo, até 40 entradas | Não persistente |
| Recall | `CORTEX/memory/hippocampal_memory.py` | Recupera turnos recentes por contratos tipados | Memory Card persistente não ligado |
| Biblioteca | `CORTEX/engram/knowledge_retrieval.py` | Adaptador para busca documental | Pacote `knowledge_retrieval/` mantém seus índices/cache |
| Planejamento | `CORTEX/prefrontal/prefrontal_controller.py` | Seleciona até três sentenças e constrói `ReasoningPlan` | Seleção inicial por sobreposição lexical |
| Apresentação | `CORTEX/prefrontal/aurora.py` | Produz `AuroraResult` com rastreio | Síntese e políticas executivas limitadas |
| Status | `CORTEX/sara/runtime_status.py` | Informa inicialização do processo em `/health` | Não verifica prontidão integral |
| Adaptador clínico | `CORTEX/reasoning_engine/diagnosis.py` | Fronteira tipada que declara estado ausente | Motor clínico especializado pertence a outro repositório e não está conectado |

## Pacotes mantidos independentes

- `knowledge_retrieval/`: implementação de busca híbrida, fontes, índices e cache.
- `knowledge_encoding/`: pipeline de ingestão/encoding e dependência de PyPDF2.
- Motor clínico Diagnosis: projeto/repositório separado; não faz parte da árvore AIGAR-C nem é dependência ativa deste runtime.
- `aigar_ui_chat_mvp/`: backend e cartões de memória da aplicação; o backend serve a interface estática que está em `CORTEX/occipital/`.

## Limites estruturais

`CORTEX/reasoning_engine/`, `CORTEX/default_mode_network/`, `CORTEX/worker_bridge/` e `CORTEX/occipital/` não devem ser descritos como subsistemas completos. Seus arquivos de documentação representam intenções/limites, não implementações prontas.

**Fronteira protegida:** `AIGAR_CLOUDFLARE/` não foi alterada nesta fase. Nenhuma alteração em Worker, símbolos, configurações, bindings, chaves JSON ou workflows está autorizada neste plano de migração.

## Validação

A arquitetura foi inspecionada estaticamente. Os testes permanecem adiados até o fechamento da auditoria de imports, caminhos de dados, configurações, comandos e referências. Não houve merge nem deploy.
