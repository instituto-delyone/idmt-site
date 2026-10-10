# Registro de mudanças

**Estado atual:** migração estrutural realizada para os módulos listados; tradução inicial dos imports e caminhos em andamento. Nenhum teste executado, nenhum merge/deploy realizado. Cloudflare Worker intocado.

## Migrações estruturais MIG-001 a MIG-012

- MIG-001 `AIGAR_RUNTIME/working_memory.py` → `CORTEX/memory/working_memory.py`; destino `8696e405dc243185c6ec7466ccbf11399273b2ca`, remoção `e8f93d45be923b7408b1fbbf233f077d386953d1`.
- MIG-002 `AIGAR_RUNTIME/hippocampal_memory.py` → `CORTEX/memory/hippocampal_memory.py`; destino `e621392c9cf788fa2c33c3a38ce7fe39431d3511`, remoção `0f045161f72132370b5d7b5e6da636ace9ab80e6`.
- MIG-003 `AIGAR_RUNTIME/prefrontal_controller.py` → `CORTEX/prefrontal/prefrontal_controller.py`; destino `e5a774ae146ea683c656e23ba5ed887588068050`, remoção `5b3a189e50a5020721fa8ca407b22b678ec6f019`.
- MIG-004 `AIGAR_RUNTIME/language_network_adapter.py` → `CORTEX/language/language_network_adapter.py`; destino `edc3ac9588df0cc7bc43357e6bc5f053f492fbc8`, remoção `e64ff61e0fd2627339b68b6390083f35189723ed`.
- MIG-005 `language_network/interpreter.py` → `CORTEX/language/interpreter.py`; destino `e09a9e405d9b944afd127b36a4114e0727d0121a`, remoção `62f406a5bab8268efafb3a846fe5848334af378a`.
- MIG-006 `language_network/language.json` → `CORTEX/language/language.json`; destino `eb481a022f22b1917699709867fa37937e9a951a`, remoção `4ab15fb011bb9dfac984341bba6daaec4cd11488`.
- MIG-007 `language_network/portuguese_language_knowledge.json` → `CORTEX/language/portuguese_language_knowledge.json`; destino `c52a588710191c65ffc9f01c383d73228d87d04d`, remoção `a4c2bd996bd127f84036c1498a806e39ecd7faf3`.
- MIG-008 `AIGAR_RUNTIME/models.py` → `CORTEX/thalamus/models.py`; destino `ef085c38f830d0ff41d015bd10ab59266454008e`, remoção `2a3cdf194709c99f7d06b25f6871905f8611672a`.
- MIG-009 `AIGAR_RUNTIME/aurora.py` → `CORTEX/prefrontal/aurora.py`; destino `5496836375806c97055be1e95ff0378ee11c3b81`, remoção `458ed2b83b326719010f0b58b9b792603981337d`.
- MIG-010 `AIGAR_RUNTIME/knowledge_retrieval.py` → `CORTEX/engram/knowledge_retrieval.py`; destino `35928d54858f0e7ae41312312f4bea819b794e24`, remoção `71fbd16e3e201670d872088dd02d47631e6e5db2`.
- MIG-011 `AIGAR_RUNTIME/linguistic_interpreter.py` → `CORTEX/thalamus/linguistic_interpreter.py`; destino `ebb4bb8575f8b21e345d7ec265246fad8519b405`, remoção `6bce2443bb83afa1e766b8203ad39af17b01cfac`.
- MIG-012 `AIGAR_RUNTIME/diagnosis.py` → `Diagnosis/diagnosis.py`; destino `7507d8769f47dceff570fd3a5557a103ef8351f7`, remoção `ea9655ca498b08cdf8621eb5868db9c2e03988a0`.

## Contratos e imports canônicos

- `CORTEX/thalamus/models.py` define `Intent`, `Depth`, `SourceStatus`, `ConversationReading`, `ConversationState`, `SourceTrace`, `RuntimeRequest` e `RuntimeResponse`; commit `327be124ff163e39f20e7db8304de287c550ba58`.
- `CORTEX/memory/working_memory.py`: `2f0d56d9887f1550795bf1bda25bd66e994d18d8`.
- `CORTEX/memory/hippocampal_memory.py`: `fddc5b1ecd68612f80d36713a6b2aa215c985f00`.
- `CORTEX/prefrontal/prefrontal_controller.py`: `627c615dbb659b5924ed0292545ed9e9f60d2b22`.
- `CORTEX/prefrontal/aurora.py`: `2f75be4937f8f4bf105ed4de74b726b01505d17f`.
- `CORTEX/engram/knowledge_retrieval.py`: `388538db9c535545be6948fad3c0b7b6feaf6344`.
- `Diagnosis/diagnosis.py`: `a5c063c7a4e960755a04cc588c28139a61826faf`.

## Tradução de referências e documentação

- `AIGAR_RUNTIME/main.py`: imports agora apontam aos módulos canônicos de `CORTEX` e `Diagnosis`; entry point mantido como `AIGAR_RUNTIME.main:app`. Commit `88380ee4102bcfe409a151734fff91ac9f850848`.
- `CORTEX/language/language_network_adapter.py`: importa `ConversationReading` do contrato canônico e `AIGARLanguage` de `.interpreter`, eliminando o caminho antigo inexistente. Commit `286dfdb96b56cf019e2ca4d37474321117f0f6b0`.
- `CORTEX/README.md`: documenta mapa provisoriamente imutável, contratos e entry point. Commit `695620e49784e2b69fe89ec38cdeb27dbfe5ac52`.
- `AIGAR_RUNTIME/test_runtime.py`: import de `RuntimeRequest` atualizado para `CORTEX.thalamus.models`; testes não executados. Commit `59af9877cf6abe60877ed03c10b859d3a9d354c8`.
- `AIGAR_RUNTIME/README.md`: instruções e caminhos alinhados à migração; commit `df98d3653714cc6991c2430909ff92890440f17d`.
- `CORTEX/prefrontal/CHANGELOG.md`: este registro consolidado; commit atual será registrado no histórico Git.

## Limites e pendências

- O mapa CORTEX é provisoriamente imutável: não mover diretórios ou redefinir responsabilidades sem decisão explícita registrada.
- `knowledge_retrieval/` e `knowledge_encoding/` permanecem pacotes independentes; o adapter de Engram consome o primeiro.
- `Diagnosis/` permanece separado; seu adapter ainda retorna status `missing` até a integração com o motor especializado ser implementada.
- Os módulos placeholder em `sara/`, `sensory/`, `default_mode_network/`, `reasoning_engine/`, `worker_bridge/` e `occipital/` não são considerados funcionalidades implementadas.
- Não foram executados testes, validação funcional, merge ou deploy. Não alterar o Cloudflare Worker.
## Roteamento explícito do tálamo — 2026-10-10

- `CORTEX/thalamus/models.py`: contrato aditivo `RoutingDecision`, sem remover nem renomear campos dos contratos existentes. Commit: `c12408e33c10e71afd231271b44b9c5679acf49a`.
- `CORTEX/thalamus/context_router.py`: novo roteador que converte `ConversationReading` em seleção explícita de memória, biblioteca, Diagnosis e raciocínio. O roteador decide seleção; não executa subsistemas nem afirma disponibilidade. Commit: `301395d41fe6e3475af541b1112e5f2f7718583f`.
- `AIGAR_RUNTIME/main.py`: delega as decisões de seleção opcional ao roteador canônico. A sequência de raciocínio e resposta foi mantida; a política `use_reasoning` ainda não desliga o estágio de raciocínio, para evitar mudança de comportamento antes da revisão completa do pipeline. Commit: `ef3f02cc723792d32ef71bb669e52fd037e45250`.

**Limites:** nenhuma execução de testes; nenhuma validação funcional; nenhum merge/deploy. Cloudflare Worker não foi consultado nem alterado. A etapa seguinte continua sendo revisar referências e caminhos restantes, depois completar contratos/implementações dos módulos CORTEX conforme os artefatos arquiteturais históricos.

## Fronteiras explícitas de pacote Python — 2026-10-10

Foram adicionados marcadores `__init__.py` aos pacotes ativos, sem mover módulos nem alterar a lógica dos adaptadores:

- `CORTEX/__init__.py` — `9743b59081b93b7dbaee8a8af9df822d021a780c`.
- `CORTEX/thalamus/__init__.py` — `f5ba53994475bc0d396313b0d19deb56ee121e6a`.
- `CORTEX/language/__init__.py` — `4f5c1928d409d63477389bf369ee425b3f4186ed`.
- `CORTEX/memory/__init__.py` — `beffe89eb7c41fa3ab1bcf34bc6fe49bf03afa68`.
- `CORTEX/engram/__init__.py` — `f8f788ec87485c2a0e0c31df206ca67a258fb544`.
- `CORTEX/prefrontal/__init__.py` — `1a59652565934c6d5f60252b5665a91db28b13c9`.
- `Diagnosis/__init__.py` — `d4b2ccf20c046a7219c913b03c62625d05945f3f`.

Objetivo: tornar explícitas as fronteiras dos pacotes Python para os imports canônicos. Isto não valida a execução nem garante que todos os caminhos de dependências estejam corretos.

**Estado:** testes não executados; sem merge/deploy; Cloudflare Worker intocado.

## SARA — estado explícito do runtime (2026-10-10)

- Criado `CORTEX/sara/runtime_status.py` com `RuntimeStatus` e `current_runtime_status()`. Commit inicial `74bbde6b972bf828e9bff64c3d77df136bbea556`; ajuste de import de dependências `473efd66da37215ea4dbe468248594eabc4a62ce`.
- Criado `CORTEX/sara/__init__.py` para declarar o pacote. Commit `cb5bedb5dab5c01bdff0ec7bdd73c1d76923b1af`.
- `AIGAR_RUNTIME/main.py`: `/health` agora delega a resposta a `current_runtime_status().model_dump()`, commit `cf7d716dce4054a4dcd7010f072b00167649b95d`.
- O payload declara apenas inicialização do processo e avisa que a conectividade dos subsistemas não foi validada; não apresenta prontidão integral como fato.

**Limites:** testes e validação funcional não executados; sem merge/deploy; Cloudflare Worker intocado.


## Sensory — contrato de entrada do runtime (2026-10-10)

- `CORTEX/thalamus/models.py`: adicionado o contrato `SensoryInput` como envelope canônico de entrada textual, sem alterar campos existentes. Commit: `9d877ba0adf20cad957527e89c452a1a720bc516`.
- `CORTEX/sensory/__init__.py`: pacote sensory declarado e exporta `capture_request`. Commit: `69ed53f4e3bc7dea500f369e5b5cf0fb7c8f02d6`.
- `CORTEX/sensory/ingress.py`: `capture_request()` converte `RuntimeRequest` em `SensoryInput` preservando exatamente o texto e o identificador da sessão. Não normaliza, classifica nem aciona subsistemas. Commit: `fd3b9c5d97cc5d089c0a674e298398fb6c2bd41d`.
- `AIGAR_RUNTIME/main.py`: o pipeline agora recebe o envelope sensorial e usa `signal.raw_text` e `signal.session_id` nos mesmos pontos onde antes usava a requisição diretamente. Commit: `7b8d9e69706d5f1036b37d5b101b7e8895dcdd9e`.

**Limites:** nenhuma execução de testes nem validação funcional; sem merge/deploy. Cloudflare Worker intocado. A camada sensorial formaliza a fronteira de entrada, mas não implementa ainda classificação multimodal ou sensores adicionais.

## Reasoning Engine — contrato estruturado de plano (2026-10-10)

- `CORTEX/thalamus/models.py`: adicionado `ReasoningPlan`, mantendo o formato de saída existente por serialização explícita. Commit: `a3e5f271b935b10c2b91ed7193064756c681a46c`.
- `CORTEX/prefrontal/prefrontal_controller.py`: o controlador constrói e retorna o contrato `ReasoningPlan`, em vez de montar um dicionário sem validação de esquema. Commit: `e33c1925c69720f39c1e4f17dbf9785849162ad7`.
- `AIGAR_RUNTIME/main.py`: converte o plano para dicionário na fronteira do runtime, preservando o formato usado por Aurora e RuntimeResponse. Commit: `78abf66938d7bc156ad8fd1a7707ab863fd6b728`.

**Limites:** alteração estática sem execução de testes ou validação funcional; sem merge/deploy. Cloudflare Worker intocado. A validação do contrato e sua compatibilidade em execução permanece pendente até a fase de testes autorizada.


## Diagnosis — contratos tipados da fronteira clínica (2026-10-10)

- `CORTEX/thalamus/models.py`: adicionados `DiagnosisRequest` e `DiagnosisResult` como contratos aditivos para entrada e saída do subsistema clínico. Commit: `248d87194ecf25c8c278cd304a20dd678bb8d6d2`.
- `Diagnosis/diagnosis.py`: `DiagnosisAdapter.evaluate()` agora recebe `DiagnosisRequest` e retorna `DiagnosisResult`. O adaptador continua explicitamente não conectado ao motor especializado; não fabrica achados clínicos. Commit: `9929f873ff27e8d65ff8c866b5c4646d561dbf9c`.
- `AIGAR_RUNTIME/main.py`: o runtime passa o envelope tipado e extrai achados e rastreabilidade do resultado; commit `120fd7a2e4bd653aa058885ca30b5dba2e5c0f11`.

**Estado:** contrato e chamada traduzidos estaticamente; integração real com Diagnosis ainda pendente. Nenhum teste executado, sem merge/deploy; Cloudflare Worker intocado.

## Memória e biblioteca — contratos de recuperação tipados (2026-10-10)

- `CORTEX/thalamus/models.py`: adicionados `MemoryRecallRequest`, `MemoryRecallResult`, `LibraryQuery` e `LibrarySearchResult` como contratos aditivos para as fronteiras de memória e recuperação documental.
- Commit do contrato: `18623acd4b800f986c1efb4c713ec5668ca199de`.
- Os contratos descrevem envelopes e proveniência; não conectam automaticamente o Memory Card persistente nem alteram o pacote independente `knowledge_retrieval`.

**Estado:** escrita confirmada pelo GitHub. Sem testes, merge ou deploy; Cloudflare Worker intocado.

## Adaptadores de memória e biblioteca — envelopes tipados (2026-10-10)

- `CORTEX/memory/hippocampal_memory.py`: `recall()` recebe `MemoryRecallRequest` e retorna `MemoryRecallResult`. Continua limitado ao contexto da sessão; Memory Card persistente não foi conectado. Commit: `247c31fd41ba04350b8086dfd533db10b0c8d2fd`.
- `CORTEX/engram/knowledge_retrieval.py`: `search()` recebe `LibraryQuery` e retorna `LibrarySearchResult`, preservando a busca híbrida e o pacote `knowledge_retrieval` independente. Commit: `49fa92c28d59e3694bc1a0e6c8970b474c5cc5b3`.
- `AIGAR_RUNTIME/main.py`: constrói os envelopes de entrada e extrai `items`/`source` dos resultados. Commit: `ef96fcfafe7fe749b8767ce5ce83327122385415`.

**Estado:** alterações registradas no branch; ainda sem execução de testes, merge ou deploy. Cloudflare Worker intocado.

## Interpretadores — fronteira canônica documentada sem exclusão (2026-10-10)

- `CORTEX/language/interpreter.py` permanece o interpretador ativo, carregado por `LanguageNetworkAdapter` e convertido para `ConversationReading`.
- `CORTEX/thalamus/linguistic_interpreter.py` foi preservado e recebeu apenas documentação explícita de que é uma heurística legada mantida para comparação; nenhuma lógica foi removida ou alterada. Commit: `ae418ec23b712ddc913973fe4b1c882dbe631d58`.
- A busca de referências não encontrou correspondências para o nome `linguistic_interpreter` no índice de busca do GitHub; isso não substitui a revisão global de imports e caminhos.

**Estado:** decisão arquitetural documentada; comparação semântica e reconciliação futura continuam pendentes. Sem testes, merge ou deploy; Cloudflare Worker intocado.


## Fronteira tipada de apresentação — Aurora (2026-10-10)

- `CORTEX/thalamus/models.py`: contratos aditivos `AuroraRequest` e `AuroraResult` definem entrada estruturada e saída com proveniência. Commit: `7fa83e0c58a510af6366a5de944eed7426e36cc6`.
- `CORTEX/prefrontal/aurora.py`: novo método público `respond(request: AuroraRequest) -> AuroraResult` envolve as ramificações de apresentação existentes, preservando-as no método interno legado. Commit: `9d0143a8ce6f842ea15ef42a9b2de2f175c1ae6a`.
- `AIGAR_RUNTIME/main.py`: runtime envia `AuroraRequest` e consome `AuroraResult`. Commit: `9b8fa2d43ed07d5a1cbeb40886dfd54392bf7e57`.

**Limites:** esta é uma adaptação estática de contrato, não validação funcional. As ramificações de texto de Aurora foram preservadas. Testes não executados; sem merge/deploy; Cloudflare Worker intocado.


## Comparação estática dos interpretadores (2026-10-10)

- `CORTEX/language/interpreter.py` é o caminho ativo: `AIGARLanguage` carrega `language.json` e `portuguese_language_knowledge.json` por caminhos relativos ao próprio arquivo, retorna um dicionário com análise lexical/estrutural, intenção, ambiguidade textual e confiança; `LanguageNetworkAdapter` converte esse resultado em `ConversationReading`.
- `CORTEX/thalamus/linguistic_interpreter.py` é heurística histórica mais simples: usa marcadores embutidos e retorna `ConversationReading` diretamente. O import relativo `.models` resolve para o contrato canônico `CORTEX.thalamus.models`; não exigiu correção.
- As regras de classificação, a granularidade da análise e o cálculo de confiança não são equivalentes. Nenhuma implementação foi apagada ou substituída; a diferença fica explicitamente aberta para decisão arquitetural posterior.

**Estado:** revisão estática dos três arquivos concluída; nenhum teste executado. Sem merge/deploy; Cloudflare Worker intocado.
