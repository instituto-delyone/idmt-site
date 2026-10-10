# AIGAR — Mapa Neurocognitivo, Vias de Comunicação e Visões Futuras

**Versão:** 1.0  
**Data:** 2026-10-10  
**Branch:** `neurocognitive-migration`  
**Fonte principal:** *Princípios de Neurociências*, 5ª edição, capítulos 60, 65, 66 e 67; apêndices E e F.  
**Documento de projeto:** visão evolutiva; não é descrição de capacidades já entregues.

## 1. Objetivo

Usar a neurociência como mapa para evoluir o AIGAR rumo a uma linguagem mais fluida, contextual e verificável. Os nomes neurocognitivos podem representar a direção desejada, mesmo quando a implementação atual ainda é simples. Cada item precisa, porém, distinguir:

- **Referência do livro:** o que a fonte descreve.
- **Analogia de engenharia:** qual problema computacional pode ser inspirado por isso.
- **Implementação observada:** o que o código faz hoje.
- **Lacuna/proposta:** o que ainda precisará ser construído.
- **Evidência de validação:** testes, logs e medidas que confirmam comportamento.

O cérebro não é uma sequência de módulos independentes nem há uma única região que explique o pensamento inteiro. A arquitetura proposta é distribuída e iterativa.

## 2. Base no livro: áreas e sistemas prioritários

### 2.1 Capítulo 60 — A linguagem (p. 1179 em diante)

**O que a fonte sustenta:** a linguagem depende de redes distribuídas. As regiões historicamente chamadas de Broca e Wernicke são referências úteis, mas não explicam isoladamente produção e compreensão. O capítulo descreve envolvimento de regiões temporais, frontais, parietais, sensório-motoras e conexões subcorticais em diferentes aspectos da linguagem. Lesões em diferentes pontos podem gerar perfis diferentes, inclusive dissociações entre fluência, compreensão e produção.

**Tradução para o AIGAR:**
- Não criar um “arquivo Broca” que sozinho produza toda a fala nem um “arquivo Wernicke” que sozinho compreenda tudo.
- Separar funções testáveis: interpretação da entrada, semântica e referências, organização da mensagem, formulação textual e revisão.
- Manter as partes conectadas por contratos explícitos; a qualidade emerge da coordenação e da informação que circula entre elas.
- A saída pode ser textual hoje; o modelo conceitual também pode acomodar entrada auditiva e visual no futuro.

**Arquivos relacionados já identificados:**
- `aigar-c-2/CORTEX/language/interpreter.py`: interpretador existente.
- `aigar-c-2/CORTEX/language/language_network_adapter.py`: adaptador entre interpretador e runtime.
- `aigar-c-2/CORTEX/prefrontal/aurora.py`: camada de resposta/persona a inspecionar em maior profundidade.
- `aigar-c-2/AIGAR_RUNTIME/main.py`: coordenação do runtime; evitar mudanças de nome sem mapa de imports e testes.

**Lacuna:** a ponte atual transforma o resultado do interpretador em `ConversationReading`; isso é uma boa fronteira de integração, mas não comprova módulos separados de semântica, planejamento de fala ou monitoramento.

### 2.2 Capítulo 65 — Aprendizado e memória (p. 1256 em diante)

**O que a fonte sustenta:** memória não é um sistema único. O capítulo diferencia memória de curto e longo prazo, memória explícita (episódica e semântica) e implícita, incluindo priming. Sistemas neurais diferentes contribuem para formas diferentes de aprendizagem e memória.

**Tradução para o AIGAR:**
- Separar estado transitório da conversa, memória de episódios, conhecimento semântico consolidado e biblioteca documental.
- Não tratar histórico textual bruto, banco de dados e memória contextual como sinônimos.
- A recuperação deve ser sensível à tarefa, ao contexto e à origem do conteúdo.

**Arquivos relacionados:**
- `aigar-c-2/CORTEX/memory/working_memory.py`: mantém o estado da sessão em memória do processo.
- `aigar-c-2/CORTEX/memory/hippocampal_memory.py`: hoje retorna turnos recentes; a memória persistente não está ligada a este adaptador.
- `aigar-c-2/CORTEX/engram/knowledge_retrieval.py`: recupera trechos documentais com metadados de fonte.
- `aigar-c-2/AIGAR_CLOUDFLARE/memory_lab/`: existe como diretório; sua disponibilidade e seus contratos precisam ser testados antes de assumir que está operacional.
- D1/R2 e Memory Cards: infraestrutura e artefatos potenciais a mapear; armazenamento não equivale a mecanismo biológico de memória.

**Lacuna principal:** falta demonstrar um ciclo explícito e testado de seleção do que guardar, registro episódico, associação, atualização, recuperação, retenção e esquecimento.

### 2.3 Capítulo 66 — Mecanismos celulares da memória implícita (p. 1274 em diante)

**O que a fonte sustenta:** aprendizagem implícita pode envolver mudanças na eficácia da transmissão sináptica; o capítulo aborda habituação, sensibilização, condicionamento, mecanismos moleculares e contribuições da amígdala para memória de medo e do estriado para hábitos. A função de uma experiência pode mudar conforme o sistema de memória envolvido.

**Tradução para o AIGAR:**
- Não chamar toda alteração de arquivo ou indexação de “aprendizagem” do sistema.
- Distinguir regras explícitas, exemplos recuperáveis, preferências contextuais e qualquer adaptação persistente.
- Se futuramente o AIGAR adaptar comportamento a feedback, registrar qual mecanismo realmente muda, onde é persistido e como pode ser revertido.

**Lacuna:** a busca/indexação de uma biblioteca não prova aprendizagem adaptativa. A mudança de comportamento precisa ter mecanismo reproduzível, política de retenção e teste de antes/depois.

### 2.4 Capítulo 67 — Córtex pré-frontal, hipocampo e memória explícita (p. 1297 em diante)

**O que a fonte sustenta:** a memória de trabalho depende de atividade neural persistente em redes que incluem o córtex pré-frontal; o capítulo discute contribuições de propriedades neuronais e conectividade recorrente. A eficiência da memória de trabalho é modulada por sistemas como a dopamina via receptores D1, com relação não linear — não significa que “mais ativação é sempre melhor”. O hipocampo e estruturas temporais mediais participam de formas de memória explícita de longa duração.

**Tradução para o AIGAR:**
- `WorkingStateStore` é uma analogia funcional para o contexto ativo; não é um modelo neuronal de atividade persistente.
- `PrefrontalController` pode evoluir para manter objetivos, restrições, passos e critérios de parada, revisar progresso e pedir nova recuperação quando faltar informação.
- `HippocampalMemoryAdapter` pode orientar a futura memória episódica/contextual, mas precisa de operações persistentes e recuperação associativa reais.
- D1 é infraestrutura de persistência, se os bindings e schema confirmarem esse uso; não é receptor D1 nem hipocampo literal.

**Lacuna principal:** o controlador atual seleciona sentenças por sobreposição lexical e prepara um plano curto. Ainda não implementa controle executivo completo, verificação sistemática de restrições ou memória de trabalho dinâmica sofisticada.

### 2.5 Apêndices E e F — Redes neurais e abordagens teóricas

Esses apêndices são úteis para pensar em múltiplas escalas: unidades, conexões, circuitos e redes. Para o AIGAR, a analogia deve ajudar a formular interfaces e hipóteses de distribuição; não autoriza dizer que funções/classes são neurônios biológicos.

## 3. Modelo funcional integrado proposto

```text
ENTRADAS
  ├── texto (modalidade primária atual; analogia funcional com conteúdo linguístico auditivo)
  ├── áudio → futuro adaptador/transcrição → contrato comum de linguagem
  └── imagem/captura → futuro adaptador visual ───────────────┐
                                                              v
INTERPRETAÇÃO DA LINGUAGEM → SEMÂNTICA/REFERÊNCIAS → ESTADO DE TRABALHO
             ^                                      │
             │                                      v
     contexto e feedback                  ROTEAMENTO / CSI
                                                    │
                            ┌───────────────────────┼───────────────────────┐
                            v                       v                       v
                      MEMÓRIA EPISÓDICA      BIBLIOTECA/EVIDÊNCIAS     MOTOR DE DOMÍNIO
                      (futura)               (recuperação atual)      (ex.: Diagnosis)
                            └───────────────────────┼───────────────────────┘
                                                    v
                                      CONTROLE EXECUTIVO / PLANO
                                                    │
                                      GATEKEEPER DE AÇÕES (quando aplicável)
                                                    v
                                      PLANEJAMENTO DA RESPOSTA
                                                    v
                                      MONITORAMENTO / VERIFICAÇÃO
                                                    v
                                          AURORA / SAÍDA FINAL
                                                    │
                              ┌─────────────────────┴──────────────────┐
                              v                                        v
                     atualização do estado                    proveniência/logs
```

O diagrama é uma visão lógica. Não implica que cada caixa deva ser um Worker separado, nem que todas as tarefas percorram todas as etapas. Tarefas simples devem poder usar caminhos curtos; tarefas complexas podem acionar mais módulos.

## 4. Arquivos existentes: papel atual, nome-guia e evolução

| Artefato atual na branch | Função observada nesta revisão | Guia neurocognitivo | Próxima evolução |
|---|---|---|---|
| `CORTEX/language/language_network_adapter.py` | Chama `AIGARLanguage` e converte análise para `ConversationReading` | Rede de linguagem / integração | Refinar semântica, incerteza e referências com testes após a migração |
| `CORTEX/language/interpreter.py` | Interpretador determinístico que lê os dois JSONs adjacentes e produz intenção/análise estruturada | Entrada e compreensão da linguagem | Separar parsing, referências e intenção somente se houver benefício mensurável |
| `CORTEX/memory/working_memory.py` | `WorkingStateStore` guarda sessões no processo e limita histórico a 40 entradas | Memória de trabalho/contexto ativo | Persistência, expiração e isolamento de sessão |
| `CORTEX/memory/hippocampal_memory.py` | `HippocampalMemoryAdapter` retorna turnos recentes por contratos tipados | Memória episódica contextual | Conectar Memory Card persistente, recall e políticas de seleção/atualização/esquecimento |
| `CORTEX/engram/knowledge_retrieval.py` | Adaptador que chama `knowledge_retrieval.retriever.KnowledgeRetriever`; índices/cache e busca híbrida permanecem no pacote independente | Recuperação documental, não hipocampo literal | Manter proveniência; calibrar ranking; distinguir score de similaridade de probabilidade de verdade |
| `CORTEX/prefrontal/prefrontal_controller.py` | Seleciona até três sentenças por sobreposição lexical e constrói `ReasoningPlan` | Controle executivo inicial | Planejamento por objetivos/restrições, critérios de parada, revisão, conflitos entre fontes e suficiência de evidência |
| `CORTEX/prefrontal/aurora.py` | `Aurora.respond()` apresenta resposta a partir de leitura, contexto e plano tipado | Formulação/expressão da resposta | Melhorar síntese semântica, tom, incerteza e coerência sem ocultar limites de evidência |
| `Diagnosis/diagnosis.py` | Adaptador que aceita `DiagnosisRequest` e retorna `DiagnosisResult`; hoje reporta integração ausente | Fronteira para motor clínico especializado | Conectar interface real sem inventar achados nem acoplar a todas as conversas |
| `AIGAR_CLOUDFLARE/association_core.py` | Componente atual no repositório do Worker, segundo o mapa versionado | Integração/associação funcional | Nenhuma mudança nesta fase; mapear rotas, dependências, bindings e comportamento antes de qualquer alteração futura |
| `AIGAR_CLOUDFLARE/main.py` | Entry point do Worker existente | Gateway e múltiplas responsabilidades a mapear | Nenhuma alteração nesta fase; registrar a topologia e preservar rotas, bindings e rollback |
| `AIGAR_CLOUDFLARE/memory_lab/` | Diretório presente; a prontidão operacional não foi validada nesta migração | Subsistema candidato de memória | Mapear contrato e autenticação no estudo do Worker, fora desta etapa |
| D1/R2 / Memory Cards | Persistência e artefatos a validar por schema/fluxos reais | Suporte físico à memória de software | Mapear tabelas, leitura/escrita, identidade, retenção e vínculo com recall |

**Importante:** os cinco nomes atuais — `PrefrontalController`, `HippocampalMemoryAdapter`, `LanguageNetworkAdapter`, `KnowledgeRetrievalAdapter` e `WorkingStateStore` — permanecem como guias evolutivos. Não é necessário renomeá-los novamente só porque suas capacidades ainda são parciais.

## 5. Componentes futuros candidatos

Os nomes abaixo são propostas, não arquivos já existentes. Criar primeiro como funções/módulos internos quando possível; transformar em Worker separado somente quando houver fronteira de responsabilidade, necessidade de isolamento ou evidência de gargalo.

### Prioridade A — observabilidade e resiliência das vias
- **`PathwayHealthMonitor`**: mede latência, erro, timeout, retry, volume, CPU/subrequests e falha de dependência por etapa.
- **`CognitiveOrchestrator`**: escolhe o caminho de execução e orçamento por tarefa; impõe timeout e limites por etapa; suporta cancelamento e fallback.
- **Trace/correlation ID comum**: conecta logs de gateway, recuperação, memória, interpretação e resposta.

### Prioridade B — memória real e estado ativo
- **`EpisodicMemoryStore`**: registros contextualizados com sessão, data, participantes/referentes, evento, proveniência, consentimento e política de retenção.
- **`MemoryConsolidationPipeline`**: seleciona o que merece persistir, normaliza, deduplica, indexa e liga cada item à fonte/experiência.
- **`ContextResolver`**: resolve “isso”, “aquilo”, nomes e referências entre turnos com score e opção explícita de incerteza.
- **`WorkingGoalState`**: objetivos ativos, restrições, subtarefas, perguntas abertas e critério de conclusão.

### Prioridade C — fluidez e qualidade da linguagem
- **`SemanticInterpreter`**: representação explícita de entidades, relações, tópico, pressupostos e ambiguidades.
- **`SpeechProductionPlanner`**: organiza conteúdo em ordem discursiva antes de realizar o texto.
- **`ResponseMonitor`**: verifica se a resposta atende à pergunta, preserva fontes e restrições, evita contradições e calibra incerteza.
- **`ConversationalFluencyLoop`**: ciclo completo de interpretação, contexto, recuperação, plano, formulação, revisão e atualização de estado.

### Prioridade D — entradas multimodais
- **`TextInputAdapter`**: normaliza entrada textual para um contrato comum.
- **`AudioInputAdapter`**: futura captura/transcrição; distinguir erro de reconhecimento de ambiguidade semântica.
- **`VisualInputAdapter`**: futuro OCR/análise de imagens e capturas; anexar a extração à proveniência.
- Áudio, texto e imagem convergem para uma representação compartilhada de conteúdo, sem alegar que a entrada textual percorre literalmente o sistema auditivo.

## 6. Workers como vias de comunicação: hipótese arquitetural

A analogia do projeto é: **Workers e Service Bindings são vias computacionais de comunicação entre componentes**. Um Worker não é literalmente um neurônio, mas pode representar uma fronteira de processamento com capacidade, latência, limites e falhas próprias.

A preocupação com “um Worker só” é uma hipótese válida para investigar: um gateway que executa muita lógica pode concentrar latência, recursos e risco de falha. Entretanto, a analogia com epilepsia não é um diagnóstico técnico. Saturação, concorrência excessiva e cascatas de retry são mecanismos computacionais que devem ser medidos diretamente.

### Topologia-alvo (proposta, não implantada)
1. **`aigar-api` — Gateway:** preservar domínio público e endpoints; autenticação/validação, roteamento, correlação de requisição e normalização.
2. **`aigar-cognition` — Orquestração:** planejar execução e coordenar contexto/estado; só separar quando contratos e métricas estiverem definidos.
3. **`aigar-library` — Recuperação:** carregar/buscar chunks e índices, com limites e proveniência.
4. **`aigar-memory` — Persistência/episódios:** operações de memória persistente via D1/R2 após schema, autorização, retenção e testes.
5. **Workers futuros especializados:** áudio, visão ou domínios específicos somente quando necessários.

### Regras para evitar uma nova fragilidade
- Não criar um Worker por cada estrutura anatômica. Primeiro delimitar responsabilidade e contrato.
- Evitar cadeias síncronas profundas; medir quantas chamadas cada requisição gera.
- Definir timeout, limites de payload, retry com backoff e idempotência onde apropriado.
- Falha de memória não deve derrubar uma resposta simples; falha de biblioteca deve produzir estado explícito; falha de um módulo opcional não deve invalidar o gateway inteiro.
- Manter health checks e fallback; não mascarar erro como resposta bem-sucedida.
- Preservar endpoints públicos e bindings existentes até a migração validada.
- Não publicar novos Workers nem alterar tráfego de produção durante esta etapa documental.

## 7. Como investigar quedas e “vias sobrecarregadas”

Instrumentar cada requisição com:
- correlation/request ID;
- serviço e etapa;
- duração por etapa e total;
- chamadas downstream e volume de dados;
- status de resposta, exceção, timeout e retry;
- uso/limites disponíveis no runtime;
- estado dos bindings e dependências;
- cache hit/miss e quantidade de chunks;
- versão/commit do Worker e ambiente.

Depois reproduzir cenários: pergunta simples, pergunta com biblioteca, conversa longa, memória indisponível, serviço auxiliar lento, payload grande, múltiplas requisições concorrentes e timeout downstream. Comparar p50/p95/p99, taxa de erro, chamadas por requisição e recuperação após falha. Só então decidir quais responsabilidades devem sair do Worker principal.

## 8. Contratos e proveniência compartilhados

Cada etapa deve transmitir, conforme aplicável:
- `request_id` e `session_id`;
- `intent`, `goal`, `constraints`, `ambiguity` e `uncertainty`;
- `context_refs` e `source_refs`;
- resultados e erros estruturados;
- duração/limites e versão do contrato;
- estado de evidência: confirmado, inferido, ausente ou conflitante.

Um score de busca não é probabilidade de verdade. Conclusões que dependam de documentos devem preservar fonte, página/trecho e a relação entre evidência e afirmação.

## 9. Ordem de implementação recomendada

1. **Documentação:** manter o dicionário como fonte de nomes e este roadmap como mapa de interações/lacunas.
2. **Inventário de vias:** listar Workers, bindings, rotas, chamadas HTTP, limites e dependências atuais; não presumir topologia sem ler os arquivos de configuração.
3. **Observabilidade:** correlation IDs e métricas por etapa antes de dividir tráfego.
4. **Contratos:** padronizar mensagens entre gateway, linguagem, recuperação, memória e controlador.
5. **Testes de resiliência:** simular indisponibilidade, timeout, payload excessivo e concorrência.
6. **Memória:** separar estado transitório, episódios persistentes e biblioteca semântica/documental.
7. **Fluidez:** implementar resolução de referências, planejamento discursivo e revisão da resposta.
8. **Workers adicionais:** extrair serviços apenas quando houver responsabilidade clara e benefício demonstrável; validar em branch/staging e preservar rollback.
9. **HTML de visualização:** gerar posteriormente a partir do dicionário e deste roadmap, sem torná-lo a fonte primária dos dados.

## 10. Critérios de conclusão

- [ ] Cada módulo tem papel atual, papel-alvo, estado e dependências.
- [ ] Cada chamada entre Workers possui contrato, timeout, rastreabilidade e política de erro.
- [ ] O sistema mantém resposta simples quando uma capacidade opcional está indisponível.
- [ ] A memória persistente tem política de retenção, leitura/escrita autorizada, recall testado e procedimento de esquecimento.
- [ ] A resposta final é avaliada por pertinência, continuidade entre turnos, uso correto de fontes, consistência e calibração de incerteza.
- [ ] Os testes de regressão e de resiliência passam antes de merge/deploy.
- [ ] Nenhuma hipótese neurocognitiva é apresentada como equivalência biológica comprovada.

## 11. Referência de fonte e limites

- *Princípios de Neurociências*, 5ª edição: capítulo 60 “A linguagem” (p. 1179+); capítulo 65 “Aprendizado e memória” (p. 1256+); capítulo 66 sobre mecanismos celulares da memória implícita (p. 1274+); capítulo 67 “Córtex pré-frontal, hipocampo e biologia do armazenamento da memória explícita” (p. 1297+); apêndices E “Redes neurais” (p. 1378+) e F sobre abordagens teóricas de neurônios a redes (p. 1396+).
- As descrições acima são sínteses de tópicos e trechos consultados do livro, não uma revisão exaustiva de todos os capítulos.
- A topologia de Workers, os nomes de módulos e as funções futuras são inferências/propostas de engenharia, não afirmações do livro.
- Estado nesta versão: documentação proposta na branch de migração. Nenhum novo Worker, rename adicional, merge ou deploy de produção é executado por este documento.


## Estado da árvore atual — auditoria CORTEX (2026-10-10)

Os caminhos citados nas seções introdutórias/tabelas de versões anteriores foram reconciliados para os destinos atuais do runtime. Esta lista descreve código e contratos realmente presentes na branch, sem afirmar validação funcional:

- Entrada operacional: `AIGAR_RUNTIME/main.py`.
- Contratos e roteamento: `CORTEX/thalamus/models.py`, `CORTEX/thalamus/context_router.py`.
- Entrada textual: `CORTEX/sensory/ingress.py`.
- Linguagem: `CORTEX/language/interpreter.py`, `CORTEX/language/language_network_adapter.py`, `CORTEX/language/language.json`, `CORTEX/language/portuguese_language_knowledge.json` e `CORTEX/language/test_interpreter.py`.
- Estado/memória de sessão: `CORTEX/memory/working_memory.py` e `CORTEX/memory/hippocampal_memory.py`; a memória persistente segue pendente.
- Recuperação documental: adaptador `CORTEX/engram/knowledge_retrieval.py`, que integra o pacote independente `knowledge_retrieval/`; o pipeline de ingestão `knowledge_encoding/` também permanece independente.
- Planejamento/apresentação: `CORTEX/prefrontal/prefrontal_controller.py` e `CORTEX/prefrontal/aurora.py`.
- Diagnosis: `Diagnosis/diagnosis.py`, fronteira tipada sem motor especializado conectado.
- Catálogo de fases: `AIGAR_PHASES/phases.json`, atualizado para os caminhos CORTEX correspondentes.

### Fronteira do Worker

O inventário do Worker é um artefato de documentação separado. Nenhum arquivo ou configuração em `AIGAR_CLOUDFLARE/` foi alterado pela auditoria deste documento; também não foram alterados nomes de símbolos, bindings, chaves JSON ou workflows do Worker nesta fase. A decisão sobre eventual reconstrução/alteração fica para depois da conclusão e revisão do mapa da arquitetura remontada.

**Estado:** mapa de runtime atualizado estaticamente; verificação integral e testes ainda não concluídos. Sem merge/deploy.
