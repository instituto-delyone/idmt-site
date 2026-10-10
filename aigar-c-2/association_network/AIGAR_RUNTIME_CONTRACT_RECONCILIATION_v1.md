# Reconciliação entre AIGAR_RUNTIME_CONTRACT_v1.json e os contratos CORTEX

**Branch:** `neurocognitive-migration`  
**Escopo:** comparação estática do contrato documental v1 com os modelos Pydantic e a orquestração existentes.  
**Regra:** este registro não altera nem substitui o contrato histórico; divergências são explicitadas para uma futura decisão versionada.

## Comparação dos campos

| Campo em `AIGAR_RUNTIME_CONTRACT_v1.json` | Implementação atual | Relação observada | Decisão |
|---|---|---|---|
| `input.raw` | `RuntimeRequest.input`, depois `SensoryInput.raw_text` | Conteúdo equivalente, nomes diferentes nas duas fronteiras | Preservar ambos os nomes em suas fronteiras; atualizar contrato somente com nova versão aprovada |
| `conversation_reading.intent` | `ConversationReading.intent` | Vocabulário controlado correspondente | Compatível em nível conceitual |
| `conversation_reading.scope` | `ConversationReading.scope` | Nome/tipo conceitual correspondente | Compatível |
| `conversation_reading.depth` | `ConversationReading.depth` | Valores correspondentes | Compatível |
| `conversation_reading.ambiguity.detected/referent` | `ConversationReading.ambiguity: float` e partes da análise em `linguistic_analysis` | Estruturas diferentes: objeto categórico no contrato documental, escalar no modelo executável | **Divergência de schema**; não converter silenciosamente |
| `conversation_reading.uncertainty.meaning_missing/source_missing` | `ConversationReading.uncertainty: float` | O contrato separa significado e fonte; o modelo runtime tem um escalar e rastros de fonte separados | **Divergência de schema**; requer decisão versionada |
| `routing.needs_memory/library/diagnosis/reasoning` | Flags `needs_*` em `ConversationReading` e `use_*` em `RoutingDecision` | Intenção de roteamento semelhante, mas representada em dois estágios/nomenclaturas | Compatibilidade conceitual, não identidade estrutural |
| `result.structured` | `DiagnosisResult.findings` para a fronteira clínica; `RuntimeResponse.plan` para plano | Sem equivalência global única | Separar os tipos de resultado por subsistema em revisão futura |
| `result.sources` / `response.source_trace` | `RuntimeResponse.sources: list[SourceTrace]` | Proveniência unificada na resposta externa | Conceitualmente correspondente |
| `result.confidence` | `RuntimeResponse.confidence` | Campo correspondente, embora calibragem atual seja heurística | Não tratar como probabilidade calibrada sem validação |
| `response.planned_depth` | `RuntimeResponse.state.reading.depth` e `RuntimeResponse.plan.depth` | Não existe campo externo direto chamado `planned_depth` | Exige mapeamento explícito se consumidor legado depender desse nome |
| `response.text` | `RuntimeResponse.text` | Correspondência direta | Compatível |

## Fonte executável atual

- Contratos Pydantic: `aigar-c-2/CORTEX/thalamus/models.py`.
- Orquestração: `aigar-c-2/AIGAR_RUNTIME/main.py`.
- Modelo histórico/documental: `aigar-c-2/association_network/AIGAR_RUNTIME_CONTRACT_v1.json`.

## Decisão conservadora

1. Manter v1 documental intacto como registro da arquitetura pretendida na sua versão.
2. Não forçar os modelos executáveis a caber no JSON histórico por renomeação ad hoc.
3. Antes de conectar consumidores históricos, definir um novo contrato versionado ou um adaptador explícito que converta os dois schemas.
4. Usar `SourceTrace` para deixar ausente/pendente o motor clínico real; não declarar integração por existir um envelope tipado.

**Estado:** divergências documentadas estaticamente. Nenhum teste foi executado, não houve merge/deploy e nenhum arquivo do Cloudflare Worker foi alterado.
