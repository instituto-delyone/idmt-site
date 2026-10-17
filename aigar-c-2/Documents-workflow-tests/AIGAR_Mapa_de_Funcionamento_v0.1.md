# AIGAR — Mapa de Funcionamento
## Documento vivo de arquitetura, execução e memória entre sessões

**Versão:** 0.1  
**Data:** 17 de outubro de 2026  
**Estado:** levantamento inicial

## 1. Finalidade
Este documento registra o que já foi observado no código-fonte do AIGAR e organiza os próximos passos para reconstruir o fluxo de execução sem depender da continuidade de uma única conversa. Separar fatos confirmados, inferências e pontos pendentes.

## 2. Escopo observado
- Repositório de trabalho: `instituto-delyone/idmt-site`.
- Diretório relevante: `aigar-c-2/AIGAR_CLOUDFLARE/`.
- Interface examinada: `docs/aigar/index.html`.
- Backend examinado: `aigar-c-2/AIGAR_CLOUDFLARE/main.py`.
- Método: leitura estática do código compartilhado; sem teste ponta a ponta e sem confirmação de deploy em produção.

## 3. Fluxo conhecido
A interface `docs/aigar/index.html` apresenta uma consola de desenvolvimento. O campo “API Base” usa `/aigar/api` por padrão. O Worker normaliza esse prefixo antes de comparar as rotas.

1. Inicialização da interface: `health()`, `refreshMemoryLab()`, `updateBrowserStorageUsage()` e `bootLibrary()`.
2. Bootstrap documental: `GET /library/boot` e `GET /texto-matriz/boot`.
3. Pergunta: `POST /perguntar`, com `input`, `session_id`, `answer_depth` e `source_fidelity`.
4. Processamento: `/perguntar` chama `handle_ask(body, self.env)`, importado de `conversation_runtime`.
5. Estado do Memory Lab: `GET /memory/status` chama `MEMORY_LAB.initialize()`.
6. Feedback: `POST /feedback` grava avaliação no D1 quando binding e esquema adaptativo estão disponíveis.
7. Administração: `/auth/login`, `/auth/me` e `/admin/*`; rotas administrativas exigem `require_admin()`.

## 4. Mapa inicial de arquivos

| Arquivo/componente | Responsabilidade observada | Estado |
|---|---|---|
| `docs/aigar/index.html` | Interface, chamadas HTTP, estado visual, cache local de bootstrap e envio de perguntas/feedback | Lido no conteúdo compartilhado |
| `AIGAR_CLOUDFLARE/main.py` | Worker, normalização de rotas, endpoints, bindings e encaminhamento | Lido |
| `AIGAR_CLOUDFLARE/conversation_runtime.py` | Contém `handle_ask` e funções de interação adaptativa | Próximo arquivo |
| `AIGAR_CLOUDFLARE/library_runtime.py` | `boot_library`, `boot_text_matrix` e `MEMORY_LAB` | Implementação pendente |
| `AIGAR_CLOUDFLARE/storage_runtime.py` | Rotinas de D1/R2, upload e administração documental | Implementação pendente |
| `AIGAR_CLOUDFLARE/memory_lab/engine.py` | Referência anterior do projeto para camadas do Memory Lab | Confirmar conteúdo atual |
| `AIGAR_CLOUDFLARE/memory_lab/config.json` | Referência anterior para configuração do Memory Lab | Confirmar conteúdo atual |

## 5. Endpoints identificados

| Método/rota | Comportamento visível |
|---|---|
| `GET /health` | Retorna estado declarado da API, bindings R2/D1, versão e capacidades declaradas |
| `GET /memory/status` | Inicializa `MEMORY_LAB` e retorna estado |
| `GET /texto-matriz/boot` | Chama `boot_text_matrix()` |
| `GET /library/boot` | Chama `boot_library()` |
| `POST /perguntar` | Chama `handle_ask(body, self.env)` |
| `POST /feedback` | Valida e grava feedback no D1 se configurado |
| `POST /auth/login` | Encaminha autenticação para `medunity_admin_login()` |
| `GET /auth/me` | Chama `medunity_me(request)` |
| `GET /admin/storage` | Retorna status de armazenamento; protegido |
| `GET /admin/documents` | Lista documentos; protegido |
| `POST /admin/upload` | Encaminha upload; protegido |

## 6. Comportamento de bootstrap e memória na interface
- A interface chama `/library/boot` e `/texto-matriz/boot` antes de habilitar perguntas.
- Usa Cache API do navegador e `sessionStorage` para guardar resposta de bootstrap.
- Espera que a matriz de texto reporte `loaded == total` e `total == 8`. Isso é um critério implementado na interface, não prova de correção semântica do conteúdo.
- `navigator.storage.estimate()` mede uso de armazenamento do navegador, não RAM.
- `clearAll()` limpa estado visual; pelo código observado, não equivale a apagar dados persistidos no backend.
- O `session_id` enviado pela consola é a string fixa `developer-console`; isso não demonstra recuperação automática de histórico entre sessões.

## 7. Quatro mecanismos que não devem ser confundidos
1. **Cache de bootstrap no navegador:** cópia local de respostas de inicialização.
2. **Biblioteca documental:** índices e trechos de documentos recuperados para consulta.
3. **Memory Lab:** componente acessado por `/memory/status`; implementação e dados atuais pendentes de verificação.
4. **Memória conversacional persistente:** exige comprovar seleção, serialização, gravação, indexação, recuperação, atualização e isolamento por usuário/sessão. Ainda não demonstrada pelos arquivos examinados.

## 8. Limites e pontos de verificação
- `/health` declara `cortex_compatibility.local_cortex_imported = false`.
- O mesmo payload lista `persistent_memory_cards`, `diagnosis_engine_execution`, `additional_workers`, `audio_visual_input` e `default_mode_network` como capacidades adiadas.
- Um status de health não substitui teste funcional.
- Bindings D1/R2 encontrados não garantem que tabelas, permissões e operações estejam funcionais.
- Código local não confirma que a versão esteja implantada em produção.
- Foram vistos caracteres acentuados corrompidos na saída; ainda não é possível afirmar se o problema é real ou artefato de cópia.

## 9. Próximo passo
Executar apenas leitura, no PowerShell, dentro da pasta do repositório:

```powershell
Get-Content .\aigar-c-2\AIGAR_CLOUDFLARE\conversation_runtime.py
```

Localizar `handle_ask()` e documentar a sequência real: validação → interpretação/seleção de contexto → recuperação de biblioteca/memória → composição da resposta → gravação de interação/estado → retorno HTTP. Essa sequência é um roteiro de investigação, não uma afirmação de que todas as etapas já existam nessa ordem.

## 10. Continuidade para novo chat
- Anexar este documento e pedir: “Continue o levantamento técnico do AIGAR a partir deste mapa; não altere arquivos sem eu pedir.”
- Informar que `main.py` e `docs/aigar/index.html` já foram examinados.
- Próximo arquivo: `conversation_runtime.py`.
- Regra de trabalho: um comando PowerShell por vez, leitura estática primeiro, sem deploy nem alterações de produção.
- Classificar afirmações como **Confirmada no código**, **Inferência** ou **Pendente de teste**.
- Registrar branch e SHA exatos quando verificados; este documento ainda não fixa o SHA do código analisado.

## 11. Histórico
**v0.1 — 17/10/2026:** registro inicial baseado em `docs/aigar/index.html` e no conteúdo de `AIGAR_CLOUDFLARE/main.py` compartilhado na conversa, além de referências anteriores à organização do Memory Lab. Nenhuma alteração foi feita no repositório ou no Worker.

> **Regra de ouro:** documentar o comportamento observado; não confundir declarações com capacidades comprovadas; não presumir que código local equivale a produção.


## 12. Análise de `conversation_runtime.py`

**Fonte:** conteúdo de `AIGAR_CLOUDFLARE/conversation_runtime.py` compartilhado em 17/10/2026. Leitura estática; sem teste ponta a ponta nem confirmação de produção.

### 12.1 Entrada e validação
- A função principal é `async def handle_ask(body, env=None)`.
- Lê `input` e `session_id`; se ausente, usa `default`.
- Rejeita entrada ausente/não textual com HTTP 400 e texto acima de 20.000 caracteres com HTTP 413.
- Normaliza `answer_depth` para `auto/direct/explanatory/deep/technical` e `source_fidelity` para `extractive/faithful/synthesis`.

### 12.2 Estado de sessão em memória
`SESSIONS.setdefault(session_id, ...)` cria/reutiliza `turns`, `context_cache`, `last_user_input`, `last_response` e `reading`. `turns` é limitado aos últimos 80 turnos; a resolução assimétrica recebe até 40 turnos anteriores. Isso é estado em memória do runtime, não persistência durável entre reinicializações.

### 12.3 Ordem observada do processamento
1. Recupera memória documental por `MEMORY_LAB.retrieve_with_fallback(text)`; falhas são capturadas.
2. Inicializa biblioteca e matriz textual por `boot_library()` e `boot_text_matrix()`.
3. Prepara contexto cognitivo com `COGNITIVE_CORE.prepare(text, core_chunks)`.
4. Interpreta com `LANGUAGE_ENGINE.interpret()` e anota com `COGNITIVE_CORE.annotate_reading()`.
5. Classifica a interação e normaliza o contrato pelo `WORKER_CORTEX_BRIDGE`.
6. Chama `AsymmetricContextManager().resolve(text, prior_turns[-40:], needs_context=...)`.
7. Consulta `library_search()` quando `routing_decision["use_library"]` está ativo.
8. Se não houver evidências bibliográficas, pode aproveitar até três documentos do Memory Lab.
9. Revisa o plano adaptativo e seleciona um modo de resposta.
10. Tenta gerar resposta por `render_adaptive_answer()`; se falhar ou retornar vazio, usa fallback determinístico.
11. Acrescenta os turnos do usuário e do assistente a `SESSIONS`, limita a 80 turnos e atualiza a última entrada/resposta.
12. Tenta gravar metadados analíticos no D1 e retorna resposta, plano, fontes, telemetria e estado da sessão.

### 12.4 Persistência: demonstrado versus pendente
- **Confirmado:** `_record_interaction()` calcula SHA-256 de `session_id` e guarda os primeiros 32 caracteres como `session_hash`.
- **Confirmado:** `adaptive_interactions` recebe IDs, tipos de interação, modo previsto, versão do modelo, snapshot mínimo e timestamp.
- **Confirmado:** o snapshot analítico guarda perfil, estratégia e revisão do plano; não registra automaticamente a entrada e saída completas.
- **Confirmado:** `_safe_useful_snapshot()` permite incluir `user_input` e `assistant_response` em um registro administrativo explícito; é um caminho separado, não captura automática da sessão.
- **Confirmado:** a própria resposta descreve a persistência conversacional entre instâncias como não configurada quando não há contexto de sessão selecionado.
- **Pendente:** recuperação do histórico completo a partir do D1 para reconstruir `SESSIONS` em outra instância.
- **Pendente:** gravação automática de memory cards a cada turno.
- **Pendente:** isolamento multiusuário completo, expiração, retenção e reconciliação de memórias conflitantes.

### 12.5 Dependências diretas
- `language_runtime.py`: `LANGUAGE`, `LANGUAGE_ENGINE`, `SESSIONS`, `compose_book_grounded_answer`.
- `library_runtime.py`: `COGNITIVE_CORE`, `MEMORY_LAB`, `boot_library`, `boot_text_matrix`, `library_search`, `source_relevance`.
- `context_runtime.py`: `AsymmetricContextManager`, `build_adaptive_plan`, `revise_adaptive_plan`.
- `cortex_compat.py`: `WORKER_CORTEX_BRIDGE`.
- `answer_runtime.py`: `render_adaptive_answer`.
- `storage_runtime.py`: `D1_BINDING`.

### 12.6 Próximo arquivo prioritário
Ler `context_runtime.py`:

```powershell
Get-Content .\\aigar-c-2\\AIGAR_CLOUDFLARE\\context_runtime.py
```

Depois, examinar `language_runtime.py` e `library_runtime.py`; em seguida, investigar a implementação de `MEMORY_LAB`.

### 12.7 Ordem de execução atualizada
A ordem observada em `handle_ask()` é: recuperar Memory Lab → inicializar biblioteca/matriz e preparar contexto cognitivo → interpretar linguagem → resolver contexto recente → buscar evidências → construir resposta → atualizar `SESSIONS` → tentar persistir metadados analíticos. Esta ordem substitui roteiros anteriores que eram apenas hipóteses.

## Fase 3 — Gerenciamento assimétrico de contexto (`context_runtime.py`)

### Lista A — Funcionamento observado
- `_context_token_set()` tokeniza palavras de pelo menos três caracteres, aplica `casefold()` e remove `STOPWORDS`.
- `resolve()` percorre os turnos, ignora conteúdo vazio e exclui estados exatamente iguais a `revoked` e `superseded`.
- A pontuação é: `0.42 * overlap + 0.25 * recency + 0.23 * reference_signal + 0.10 * dependency`.
- `reference_signal` vale 1 apenas quando `needs_context=True` e o turno está entre os quatro últimos; `dependency` vale 1 quando `metadata.pinned_context` é verdadeiro.
- A seleção usa por padrão até 12 itens e 12.000 caracteres, respeitando os limites definidos no construtor; os itens selecionados voltam à ordem cronológica.
- `active_decisions` é retornado como lista vazia neste módulo.
- `build_adaptive_plan()` escolhe a estratégia por tipo de interação; `revise_adaptive_plan()` registra razões de revisão e IDs de evidências e pode alterar a estratégia.

### Lista B — Correções e verificações
- Verificar se o sinal posicional de referência é suficiente ou se precisamos de resolução explícita de referências.
- Definir o contrato de status e o tratamento de valores desconhecidos.
- Validar a estrutura de turnos e metadados antes de pontuar.
- Confirmar no arquivo original se a regex de tokens contém corrupção de caracteres acentuados.
- Definir o ciclo de vida das decisões explícitas, pois este módulo não as extrai.
- Rever a precedência entre evidências novas e correção de intenção em `revise_adaptive_plan()`.
- Definir comportamento para consultas sem tokens úteis após remoção de stopwords.

**Estado:** análise estática do trecho fornecido; nenhuma alteração de código do repositório realizada. Próxima etapa: comparar esse contrato com `language_runtime.py` e com o formato real de `turns` construído em `conversation_runtime.py`.

## Fase 2 — Interpretação da linguagem (`language_runtime.py`)

### Lista A — Funcionamento observado
- `LANGUAGE` descreve intenções, profundidades, regras de resposta e um pipeline conceitual.
- `PORTUGUESE` contém definições declarativas sobre sintaxe, semântica, pragmática, referentes e discurso.
- `LanguageEngine.question()` reconhece padrões para definição/identidade, tempo, lugar, causa, função, processo e comparação.
- `LanguageEngine.interpret()` normaliza texto, identifica tokens, consulta um léxico finito de verbos, gera `possible_subject` heurístico e classifica intenção por uma cadeia ordenada de condições.
- A profundidade é selecionada por marcadores textuais; `needs_memory`, `needs_library`, `needs_diagnosis` e `needs_reasoning` são sinais heurísticos.
- `SESSIONS` e `CHUNK_CACHE` são dicionários globais do módulo; não demonstram persistência durável.
- `compose_book_grounded_answer()` pode compor uma definição a partir de um conceito conhecido e acrescentar referência de evidência quando fornecida.

### Lista B — Correções e verificações
- Testar a precedência da classificação quando há mais de uma intenção na mesma entrada.
- Avaliar correspondência por substring em `has_any()` para evitar falsos positivos.
- Harmonizar o contrato de profundidade com os consumidores (`answer_depth` e renderizador).
- Distinguir `possible_subject` heurístico de resolução real de referentes.
- Comparar tokenização/STOPWORDS com o resolvedor de contexto e separar finalidade lexical de finalidade referencial.
- Verificar a coerência entre `needs_memory`/`needs_library` e o roteamento real do `conversation_runtime.py`.
- Tratar `ambiguity` como heurística não calibrada até existir validação.
- Confirmar a codificação original antes de corrigir strings e regex com acentos.
- Criar matriz de rastreabilidade entre regra declarada, implementação e teste.

**Estado:** análise estática do conteúdo compartilhado; nenhuma alteração no código do repositório foi realizada.

## Integração entre linguagem e contexto — `conversation_runtime.py`

### Lista A — Funcionamento observado
- `LANGUAGE_ENGINE.interpret(text, cognitive_context=...)` produz `reading`.
- `COGNITIVE_CORE.annotate_reading()` anota a leitura com contexto cognitivo.
- `classify_interaction(text, reading)` produz `profile`.
- `WORKER_CORTEX_BRIDGE.interpret_contract(reading, profile)` produz `reading` normalizado e `routing_decision`.
- `AsymmetricContextManager.resolve()` recebe os últimos 40 turnos e `needs_context=bool(routing_decision["use_memory"])`.
- O plano final recebe `use_memory = bool(routing_decision["use_memory"] and memory_context)`, portanto esse campo final exige contexto selecionado, não apenas uma decisão de roteamento positiva.
- A busca de biblioteca ocorre quando `routing_decision["use_library"]` é verdadeiro.

### Lista B — Correções e verificações
- Inspecionar `cortex_compat.py` para entender a transformação de `reading`/`profile` em `routing_decision`.
- Distinguir memória solicitada, tentativa de recuperação, disponibilidade e uso efetivo no contrato do plano.
- Testar pedido de continuidade sem histórico elegível e referências a turnos anteriores à janela de 40.
- Comparar sinais de memória do `LanguageEngine`, do bridge e do resultado do resolvedor.

**Estado:** integração parcialmente mapeada a partir de trechos de `conversation_runtime.py`; o contrato do bridge ainda precisa ser lido.


## Fase 4 — Fronteira de compatibilidade CORTEX (`cortex_compat.py`)

### A. Funcionalidades observadas no código
- Define o contrato `CORTEX.thalamus.models`, versão `1`, no modo `worker_native_adapter`; declara explicitamente que não importa o CORTEX local em runtime.
- Normaliza a leitura linguística para um vocabulário permitido de intenções e profundidades, fornece valores padrão e preserva anotações adicionais.
- Converte `ambiguity`, `confidence` e `uncertainty` para números limitados ao intervalo de 0 a 1.
- Gera uma decisão de roteamento para memória, biblioteca, diagnóstico e raciocínio, combinando os sinais da leitura com alguns campos do perfil de interação.
- A resposta do bridge inclui a leitura normalizada, a decisão de roteamento e metadados de compatibilidade.
- O campo `diagnosis_execution` declara `not_connected` quando diagnóstico é solicitado; portanto, solicitar/rotear diagnóstico não equivale a executar o motor Diagnosis.
- A lista de capacidades adiadas inclui cartões de memória persistentes, execução do motor de diagnóstico, workers adicionais, entrada audiovisual e rede no modo padrão.

### B. Correções e verificações necessárias
- Testar coerência entre o contrato canônico local e este adaptador Worker; o código afirma espelhar o contrato, mas a equivalência não foi demonstrada por testes diferenciais.
- Distinguir validação booleana real de conversão por `bool(...)`: strings não vazias como `"false"` tornam-se `True`. Confirmar se os campos recebidos podem ter tipos não booleanos e definir política de normalização.
- Verificar a consistência entre `confidence` e `uncertainty`: ambos podem ser fornecidos independentemente e terminar sem relação complementar.
- Validar a forma e o tipo de `scope` e os campos preservados; atualmente `scope` é copiado sem normalização e anotações extras são mantidas.
- Testar valores numéricos especiais ou malformados para garantir que a limitação numérica sempre produza valores finitos e previsíveis.
- A versão do contrato é constante (`1`); definir como detectar incompatibilidade quando o contrato canônico evoluir.
- Confirmar por testes que `profile.context_required` e `profile.research_required` têm tipos e semântica estáveis e que a rota de diagnóstico nunca seja apresentada como execução concluída.

### Estado da evidência
Os itens acima são observações estáticas do código fornecido. Não foram executados testes unitários, testes de integração nem verificações contra o contrato CORTEX canônico.


## Fase 5 — association_core.py: núcleo de contexto cognitivo

### A. Funcionalidades observadas
- Declara o `CognitiveContextCore` v1.0.0 para selecionar contexto a partir de chunks já carregados no boot.
- `prime()` prepara tokens por chunk e tenta reutilizar entradas cujo identificador e assinatura (tamanho, primeiros 64 e últimos 64 caracteres) permaneçam iguais.
- `prepare()` tokeniza a pergunta e os chunks, calcula sobreposição lexical e um bônus por termos associados à origem, ordena os chunks e seleciona até quatro itens.
- Mantém um chunk de `interacoes_aigar` como âncora quando disponível.
- `_excerpt()` seleciona sentenças com sobreposição lexical sem alterar o texto original; se não houver sobreposição, usa o início do texto.
- `annotate_reading()` acrescenta versão, chunks selecionados e princípios ao campo `linguistic_analysis.cognitive_core`, sem substituir diretamente a intenção.
- Os princípios declarados incluem distinguir intenção, tema e objetivo semântico, preservar ressalvas e não tratar documentos como instruções.

### B. Correções e pendências
- Os tokens e termos de origem exibidos no trecho contêm sequências como `Ã£` e `Ã©`; é necessário verificar os bytes do arquivo original antes de afirmar corrupção de codificação.
- A assinatura de cache não cobre o conteúdo inteiro: alterações no meio do chunk, mantendo tamanho e extremidades, podem reutilizar tokens antigos.
- A pontuação usa sobreposição lexical e bônus fixos; não é uma medida semântica calibrada.
- O chunk-âncora pode ser selecionado mesmo sem relevância lexical para a pergunta.
- `prepare()` chama `prime()` a cada pergunta, recalculando a preparação para os chunks recebidos; o ganho de cache depende de estabilidade dos identificadores e da assinatura.
- A extração por sentença é heurística; a falta de tokens comuns entre consulta e texto faz o fallback retornar o começo do chunk, que pode não ser o trecho mais relevante.
- `limit` é convertido para inteiro e limitado a 1–4; entradas não convertíveis podem lançar exceção e devem ser cobertas por testes.
- Ainda não foram executados testes nem feitas alterações no código.


## Fase 6 — test_cognitive_core.py: cobertura de testes existente

### A. O que os testes cobrem
- `setUp()` cria três chunks sintéticos: interações AIGAR, matemática computacional e ética.
- `test_core_selects_context_before_answer_generation` verifica `ready`, versão `1.0.0`, limite de até três selecionados e presença tanto da âncora `interaction-1` quanto do chunk matemático `math-1` numa pergunta sobre derivadas.
- `test_core_compiles_chunk_index_and_returns_source_excerpt` verifica que `prime()` retorna três, que o trecho matemático selecionado contém “derivada” e que o excerpt não ultrapassa 1.250 caracteres.
- `test_annotation_preserves_original_interpretation` verifica que a intenção original permanece, que a anotação indica núcleo pronto e que a cópia de `linguistic_analysis` não altera o dicionário original de entrada.

### B. Lacunas visíveis nos testes
- Não há teste para mudança de texto no meio do chunk com mesmo tamanho/prefixo/sufixo, apesar da assinatura de cache usar apenas esses elementos.
- Não há teste de entradas inválidas para `limit`, nem para `limit=0`, valores negativos ou limites acima de quatro.
- Não há teste para consulta sem tokens úteis, chunk vazio, identificadores ausentes ou IDs duplicados.
- Não há teste explícito para âncora sem relevância lexical, empate de pontuação, ordenação determinística ou fallback de `_excerpt()`.
- Não há teste de integração que confirme que os chunks usados no runtime são os mesmos que os testes sintéticos.
- O código exibido contém grafias com sequências como `Ã§`; o teste isolado não determina se isso está nos bytes originais ou surgiu na cópia/terminal.
- A presença de testes não prova que passaram: nenhum teste foi executado nesta etapa.


## Fase 7 — test_cortex_compat.py: cobertura de testes existente

### A. O que os testes cobrem
- `test_normalize_reading_preserves_worker_annotations`: valida intenções/profundidades permitidas, `needs_memory` para `continuity`, cálculo de incerteza padrão, preservação de anotações extras e ausência de mutação do dicionário original.
- `test_unknown_contract_values_degrade_to_safe_defaults`: verifica fallback de intenção para `unknown`, profundidade para `normal`, limitação de confiança acima de 1 e normalização de `linguistic_analysis` malformado para `{}`.
- `test_routing_is_explicit_and_does_not_claim_diagnosis_execution`: verifica roteamento para memória, biblioteca, diagnóstico e raciocínio; também confirma `diagnosis_execution = not_connected` e que o CORTEX local não é importado.
- `test_worker_bridge_returns_canonical_reading_and_explicit_routing`: verifica preservação de `scope`, normalização numérica, roteamento e consistência do objeto de compatibilidade com a decisão de roteamento.

### B. Lacunas e riscos que os testes não cobrem
- Não testam entradas booleanas como strings (`"false"`, `"0"`, `"no"`) para campos `needs_*`; em Python, strings não vazias são verdadeiras.
- Não testam valores numéricos especiais como `NaN` e infinito; `_bounded_number()` pode não produzir o resultado finito esperado em todos os casos.
- Não testam inconsistência explícita entre `confidence` e `uncertainty` fornecidas simultaneamente.
- Não testam campos extras malformados, objetos aninhados grandes ou validação semântica de `scope`.
- Não testam compatibilidade de versões ou equivalência automática com o contrato canônico externo.
- Não foram executados testes nesta etapa; o arquivo só demonstra cobertura declarada.


## Fase 8 — verificação pontual pelo conector GitHub (somente leitura)

Repositório consultado: `instituto-delyone/idmt-site`, branch `main`.
Arquivos e blobs consultados:
- `aigar-c-2/AIGAR_CLOUDFLARE/storage_runtime.py`, blob SHA `bde753c78812f33f61d67ce82e8ff586693cba9c`.
- `aigar-c-2/AIGAR_CLOUDFLARE/schema.sql`, blob SHA `13a79ed593b12908681fa47a1b19c9726507fd36`.
- `aigar-c-2/AIGAR_CLOUDFLARE/test_cortex_compat.py`, blob SHA `0f878687de878fe7e51c781af8b85dbf02dd28fb`.

### A. Funcionalidades confirmadas no repositório remoto
- `storage_runtime.py` declara bindings `AIGAR_LIBRARY_BUCKET` (R2) e `AIGAR_DB` (D1), e `storage_status()` considera a persistência pronta quando ambos estão presentes.
- O fluxo de upload exige R2 e D1, guarda o PDF original em R2 e registra metadados na tabela `documents` do D1.
- `schema.sql` define `documents`, `document_chunks`, `adaptive_interactions`, `adaptive_feedback`, `adaptive_feedback_reviews`, `adaptive_evaluation_cases`, `adaptive_useful_interaction_logs` e `adaptive_audit_log`.
- `adaptive_interactions` armazena hash de sessão, ID do turno, tipo de interação, tipos secundários, modo previsto, versão do modelo, snapshot mínimo e timestamp.
- `document_chunks` registra metadados/ponteiros para chunks documentais persistidos; o schema consultado não apresenta uma tabela explícita de cartões de memória conversacional.
- A verificação foi feita em leitura; nenhum arquivo remoto foi criado, atualizado, commitado ou publicado.

### B. Problemas/limites confirmados e próximos passos
- O schema demonstra persistência de biblioteca documental, metadados de interação, feedback, avaliações e auditoria; não demonstra por si só persistência e recuperação do histórico integral da conversa.
- A presença de D1/R2 configurados é condição para certas funções de armazenamento, não prova que os bindings estejam configurados no ambiente implantado.
- Precisamos ler o restante de `storage_runtime.py` e comparar as consultas reais com `schema.sql`, especialmente ingestão, leitura de chunks, snapshots úteis e feedback.
- Precisamos confirmar se os arquivos locais apresentados correspondem aos blobs atuais do `main`; a consulta ao conector confirmou a versão remota dos três arquivos, não todo o repositório nem o estado local.

## Fase 11 — Índices, cache e publicação (2026-10-17)

### A. Evidências verificadas no GitHub (somente leitura)

- `knowledge_encoding/encode_knowledge.py` grava índice local em `indexes/` e índice público em `public_indexes/`; o índice público remove `cache_file`.
- `knowledge_encoding/README.md` documenta o texto dos chunks em `knowledge_retrieval/cache/`, descrito como ignorado pelo Git.
- `knowledge_retrieval/.gitignore` não contém regra geral para todos os arquivos `.txt`; o README do pacote reconhece artefatos históricos versionados e política de distribuição ainda não reconciliada.
- `AIGAR_CLOUDFLARE/library_runtime.py` tenta carregar índices de URLs em `knowledge_retrieval/indexes/*.index.json`. Para carregar texto, `chunk_urls(entry)` exige `entry["cache_file"]` e constrói URLs sob `knowledge_retrieval/cache/`.
- O conector retornou 404 ao tentar buscar individualmente caminhos como `knowledge_retrieval/indexes/interacoes_aigar.index.json` e `knowledge_retrieval/indexes/sapiens.index.json`. Isso não prova ausência de catálogo incorporado nem ausência em outros refs.
- `wrangler.jsonc` declara D1, R2, AI e o Workflow de biblioteca. A declaração no repositório não comprova configuração operacional do Worker publicado.

### B. Problemas / hipóteses a verificar

- AIGAR-080 (P1): o índice público criado pelo codificador não inclui `cache_file`, mas o loader do Worker depende desse campo para construir a URL do chunk.
- AIGAR-081 (P1): a política documentada de cache privado local conflita potencialmente com o Worker buscar os textos dos chunks no GitHub.
- AIGAR-082 (P1): os caminhos de índice esperados pelo Worker não foram encontrados individualmente no ramo consultado; verificar árvore local, catálogo embarcado e diferenças local/remoto.
- AIGAR-083 (P2): `.gitignore` não garante exclusão de todo texto de cache já versionado ou gerado sob caminhos não cobertos.
- Não afirmar que a busca documental está completamente quebrada: o Worker possui catálogo embarcado e podem existir arquivos históricos; falta verificar a árvore local e a implantação real.

### Próximo passo

Usar PowerShell em modo somente leitura para comparar a árvore local, os índices/cache existentes e o estado Git, sem editar, apagar, gerar ou publicar arquivos. Emitir apenas um comando por vez e analisar a saída antes de continuar.

### Estado

- Nenhum código alterado.
- Nenhum teste executado nesta fase.
- Nenhum deploy ou alteração remota realizado.
- Progresso estimado da análise estática pré-correção: aproximadamente 66% (estimativa de planejamento).


## Fase 12 — execução dos testes locais do Worker (2026-10-17)

### A. Resultado observado

Foi executado localmente, em PowerShell, o comando de descoberta de testes do pacote `aigar-c-2/AIGAR_CLOUDFLARE`, com `python -B -m unittest discover -s ".\aigar-c-2\AIGAR_CLOUDFLARE" -p "test_*.py" -v`.

Resultado informado pelo ambiente local:
- **12 testes executados; 12 aprovados; 0 falhas; 0 erros.**
- Duração reportada: **0,010 s**.
- `test_cognitive_core.py`: 3 testes aprovados.
- `test_cortex_compat.py`: 4 testes aprovados.
- `test_memory_lab.py`: 5 testes aprovados.

Os testes confirmam os comportamentos cobertos por esses casos: seleção de contexto no núcleo cognitivo, preservação de anotações, normalização/roteamento do contrato CORTEX e comportamentos básicos de inicialização/fallback do Memory Lab.

### B. Limites e próximos problemas

- O resultado **não** comprova persistência de memória entre instâncias, execução do Diagnosis, integridade de todos os chunks em tempo de execução, funcionamento do Worker publicado ou implantação em produção.
- Permanecem lacunas de cobertura já registradas, inclusive alterações internas de chunks que preservem a assinatura de cache, valores não finitos no contrato, validação de checksum no carregamento da biblioteca e falhas de rede/fallback.
- Os testes aprovados são evidência positiva para os casos cobertos, não uma certificação geral do sistema.

### Estado após a fase

- Código-fonte: **não alterado** nesta fase.
- Worker publicado/deploy: **não alterado**.
- GitHub: **nenhuma escrita/push realizado**.
- Integridade dos 73 chunks locais: validação anterior confirmou 73/73 hashes e comprimentos após normalização de CRLF para LF; essa verificação é distinta dos 12 testes unitários.
- Próximo passo recomendado: revisar o carregador da biblioteca e seus caminhos de fallback/checksum, somente leitura, antes de propor correções.


## Fase 13 — carregador de chunks da biblioteca (2026-10-17)

### A. Funcionamento confirmado por leitura estática do `library_runtime.py` remoto

- `chunk_urls(entry)` exige `entry["cache_file"]` e monta duas rotas de recuperação: GitHub Raw e GitHub Contents API.
- `load_chunk_text(entry)` tenta as URLs em sequência, ignora respostas HTTP de erro, exceções e conteúdo Base64 vazio; retorna texto quando consegue ler uma resposta e `None` quando ambas as tentativas falham.
- **Não foi encontrada validação do SHA-256 nem do comprimento do texto dentro de `load_chunk_text()`.** A integridade dos 73 chunks foi validada separadamente no ambiente local, após normalização CRLF→LF; isso não equivale a validação em tempo de execução no Worker.
- `boot_library()` e `library_search()` consultam `CHUNK_CACHE` pela chave `id` do chunk. O texto recuperado é guardado sob essa chave, sem que a chave inclua versão, origem ou checksum.
- O boot isola falhas por chunk e classifica cada biblioteca como `ready`, `partial` ou `error`; `library_search()` carrega candidatos sob demanda e pode continuar sem texto de um candidato.
- O código remoto consultado é o do repositório `instituto-delyone/idmt-site`, branch `main`. A equivalência com a cópia local e com o Worker implantado ainda não foi verificada nesta fase.

### B. Riscos e testes necessários

- **AIGAR-084 (P1):** o loader não valida checksum/comprimento contra os metadados do índice antes de aceitar o texto. Estado: confirmado por leitura estática; nenhum caso de conteúdo adulterado foi executado.
- **AIGAR-085 (P1):** não foi identificada, nas três suítes executadas, cobertura específica para `chunk_urls()`, `load_chunk_text()`, checksum, fallback Raw→Contents API, conteúdo vazio ou indisponibilidade das duas URLs. Estado: lacuna de cobertura; a busca completa por testes de integração ainda pode alterar esse escopo.
- **AIGAR-088 (P1):** cache de chunks indexado somente por `id`; se IDs forem reutilizados entre fontes/versões, pode haver colisão ou conteúdo obsoleto. Estado: risco estrutural confirmado por leitura, ocorrência concreta não demonstrada.
- **AIGAR-089 (P2):** `chunk_urls()` acessa `entry["cache_file"]` diretamente; índice sem esse campo pode gerar exceção antes das tentativas de rede. Estado: inferência direta do código; não reproduzida por teste.
- Não classificar o loader como completamente quebrado: existem duas rotas de recuperação e fallback por exceção/status; o risco é a ausência de verificação de integridade e de testes específicos, não uma falha geral já reproduzida.

### Próximo passo

Confirmar em PowerShell, em modo somente leitura, se o `library_runtime.py` local corresponde ao blob de `main` consultado no GitHub e se há alterações locais nesse arquivo. Depois, revisar a cobertura de testes do carregador antes de propor qualquer alteração.

### Estado

- Código-fonte e Worker publicado: não alterados.
- Testes executados nesta fase: nenhum novo teste; os 12 testes anteriores continuam aprovados.
- Progresso global da auditoria estática: manter em aproximadamente 66% até recalcular o escopo total; esta fase acrescenta achados, mas não fecha a auditoria.

## Fase 14 — confirmação da versão local e busca de testes do carregador (2026-10-17)

### A. Evidências obtidas

- O usuário executou `git rev-parse HEAD:aigar-c-2/AIGAR_CLOUDFLARE/library_runtime.py`; o hash retornado foi `5f180853d26b1551c840d7c5098a667a2a751fe4`, igual ao blob remoto de `main` previamente consultado.
- O usuário executou `git status --short -- aigar-c-2/AIGAR_CLOUDFLARE/library_runtime.py`; não houve saída. Portanto, o arquivo não aparece como modificado no estado local do Git.
- A busca `Select-String` nos três arquivos `test_*.py` não retornou linhas para `load_chunk_text`, `chunk_urls`, `library_search`, `checksum`, `SHA-256`, `sha256`, `INDEX_URLS` ou `CHUNK_CACHE`.
- Os únicos arquivos de teste encontrados nessa pasta são `test_cognitive_core.py`, `test_cortex_compat.py` e `test_memory_lab.py`; a suíte já executada passou nos 12 casos.

### B. Interpretação e limites

- A correspondência do hash confirma que o arquivo local rastreado corresponde ao blob de `main` consultado. A ausência de saída do `git status` indica que esse arquivo não tem alteração local reportada.
- A busca sem resultados confirma que **não há referências diretas aos termos pesquisados nos três arquivos de teste encontrados**. Isso não exclui cobertura indireta ou testes fora dessa pasta/repositório.
- A lacuna de testes específicos do carregador permanece. Não foi executado teste de rede, de fallback Raw→Contents API, de checksum em runtime nem de conteúdo adulterado.
- Nenhum arquivo de código foi alterado; não houve push nem deploy.

### Próximo passo recomendado

Inspecionar a configuração do projeto e os workflows de CI para determinar se há testes de integração fora dessa pasta. Depois, planejar testes unitários isolados para URL/fallback/checksum/cache, sem modificar a implementação nesta etapa.

## Fase 15 — workflows de validação do GitHub (2026-10-17)

### A. Evidências do repositório remoto `main`

- `.github/workflows/aigar-cognitive-core.yml` (SHA `00d3eb4a27b3f8b1e195db8c4df75264e1f99b77`) é acionado por pull requests que alterem `aigar-c-2/AIGAR_CLOUDFLARE/**` ou `docs/aigar/index.html`, e por pushes em `feature/aigar-cognitive-core-v1` e `main`.
- Esse workflow compila os módulos Python do pacote Worker, executa exatamente `test_cognitive_core.py`, `test_cortex_compat.py` e `test_memory_lab.py`, e verifica a sintaxe do JavaScript inline da interface. Isso coincide com os três arquivos locais e com os 12 testes aprovados.
- `.github/workflows/aigar-runtime-validation.yml` (SHA `2bea9b9b700bf6c24b8f7369abe3c746502c1ad3`) cobre `AIGAR_RUNTIME`, CORTEX, `language_network`, `knowledge_retrieval` e `knowledge_encoding`; executa testes do runtime local, do interpretador CORTEX e do retriever local. Não executa testes do carregador de `AIGAR_CLOUDFLARE/library_runtime.py`.
- `aigar-c-2/AIGAR_CLOUDFLARE/README.md` identifica o pacote como candidato de migração e explicita que a edição do repositório não publica nem altera o Worker ativo. O `pyproject.toml` do pacote declara Python `>=3.13`; o workflow de validação usa Python 3.12, possível divergência de ambiente a avaliar separadamente, sem presumir falha.

### B. Interpretação

- A busca anterior sem resultados nos três arquivos de teste é consistente com o workflow: a suíte configurada para o Worker não inclui teste dedicado ao loader/checksum/fallback.
- Há validação de compilação, testes unitários de três áreas e sintaxe JavaScript; isso é útil, mas não equivale a testes de integração de recuperação de chunks nem à verificação do Worker implantado.
- A diferença entre `requires-python >=3.13` e Python `3.12` no workflow é uma discrepância de configuração observada. Não há evidência, nesta fase, de que ela cause falha nos testes atuais.

### Próximo passo recomendado

Revisar o histórico/estado recente das execuções de CI e, em seguida, propor testes unitários isolados para `chunk_urls()` e `load_chunk_text()` com respostas HTTP simuladas: Raw OK, Raw falha/Contents OK, ambas falham, conteúdo vazio e checksum divergente. Não alterar a implementação até a proposta ser revisada.

## Recalibração do progresso — 17/10/2026

O percentual anterior de 66% era uma estimativa de planejamento que permaneceu sem atualização apesar da inclusão de novas fases. Ele não deve ser tratado como métrica válida daqui em diante.

### Método adotado nesta recalibração
Foram definidos 20 pacotes de trabalho da auditoria, com peso igual nesta primeira versão:
- **Concluído (1 ponto):** evidência estática ou resultado de teste suficiente para fechar aquele pacote dentro do escopo declarado.
- **Parcial (0,5 ponto):** existe análise, mas há uma parte material pendente.
- **Pendente (0 ponto):** ainda não foi executado ou não há evidência suficiente.

| # | Pacote de trabalho | Estado | Pontos |
|---:|---|---|---:|
| 1 | Delimitação do repositório e arquitetura de alto nível | Concluído | 1 |
| 2 | Interface `docs/aigar/index.html` | Concluído | 1 |
| 3 | Rotas e dispatch de `main.py` | Concluído | 1 |
| 4 | Fluxo de pergunta/sessão em `conversation_runtime.py` | Concluído | 1 |
| 5 | Interpretação linguística em `language_runtime.py` | Concluído | 1 |
| 6 | Seleção assimétrica de contexto | Concluído | 1 |
| 7 | Contrato/bridge CORTEX | Concluído | 1 |
| 8 | Núcleo cognitivo e indexação local de contexto | Concluído | 1 |
| 9 | Inventário e execução das três suítes existentes | Concluído | 1 |
| 10 | Operações de armazenamento e compatibilidade com schema D1/R2 | Parcial | 0,5 |
| 11 | Leitura estática do carregador de chunks | Concluído | 1 |
| 12 | Índices, política de cache e caminho de publicação | Parcial | 0,5 |
| 13 | Integridade local dos 73 chunks após normalização CRLF→LF | Concluído | 1 |
| 14 | Comparação local/remoto de arquivos do Worker | Parcial | 0,5 |
| 15 | Leitura estática dos workflows de CI | Concluído | 1 |
| 16 | Consulta dos resultados recentes de execução do CI | Pendente | 0 |
| 17 | Testes isolados do loader (fallback, falhas, conteúdo vazio e checksum) | Pendente | 0 |
| 18 | Teste ponta a ponta da memória entre instâncias/sessões | Pendente | 0 |
| 19 | Verificação do Worker efetivamente implantado | Pendente | 0 |
| 20 | Consolidação final dos documentos e priorização dos achados | Parcial | 0,5 |

### Resultado recalculado
- Pacotes concluídos: **12/20**.
- Pacotes parciais: **4/20**.
- Pacotes pendentes: **4/20**.
- Pontuação ponderada: **14/20 = 70%**.

**Progresso recalculado da auditoria documental/estática: 70% (estimativa estruturada).** Isso substitui a estimativa antiga de 66%, mas não é uma métrica de funcionalidade do AIGAR nem de prontidão para produção. O método usa pesos iguais por pacote e pode ser refinado se o escopo mudar.

### Métricas separadas que não devem ser somadas ao percentual geral
- Testes existentes executados localmente: **12/12 aprovados**.
- Integridade dos chunks locais: **73/73 confirmados** depois da normalização das quebras de linha.
- Cobertura específica do loader: **não verificada por testes dedicados**.
- Persistência conversacional entre instâncias: **não comprovada**.
- Estado do Worker em produção: **não verificado**.
- Código, configuração, push e deploy: **nenhuma alteração realizada nesta auditoria**.
\n\n## Fase 16 — inspeção read-only da Cloudflare e divergência de versão (2026-10-17)\n\n### Evidências obtidas pelo conector Cloudflare\n- Worker encontrado: `aigar-api`; rota ativa declarada: `delyone.com/aigar/api*`. Subdomínio `workers.dev` habilitado (`dr-delyone`).\n- Versão/deployment mais recente consultado: versão nº 40, ID `9752763e-0ecd-4029-ab88-124d8baa0274`, 100% do tráfego; anotação de commit `0b6a19289543dc64bdc4cf02c7953491b3433651`.\n- `main` atual do GitHub: `4c09801d07f4ed15493985bdc0ed8683f7956e7b`. A comparação indica `main` 78 commits à frente do commit anotado no Worker, sem commits à frente no Worker. Portanto, PC↔GitHub pode estar sincronizado, mas a versão implantada não é a mesma revisão da `main`.\n- Configuração publicada contém bindings `AI`, `AIGAR_DB` (D1), `AIGAR_LIBRARY_BUCKET` (R2) e `AIGAR_LIBRARY_BUILDER` (Workflow), compatíveis nominalmente com `wrangler.jsonc` atual. Isso não prova que todo o código/configuração seja equivalente.\n- D1 `PRAGMA quick_check` retornou `ok`; consultas foram somente leitura (`changed_db=false`, `rows_written=0`).\n- Tabelas encontradas no D1: `documents`, `document_chunks`, `adaptive_interactions`, `adaptive_feedback`, `adaptive_feedback_reviews`, `adaptive_evaluation_cases`, `adaptive_useful_interaction_logs`, `adaptive_audit_log`, além de `_cf_KV`. As seis tabelas `adaptive_*` esperadas por `adaptive_schema_ready()` existem.\n- Contagens D1: `documents=3`; `document_chunks=0`; `adaptive_interactions=26`; `adaptive_feedback=3`; `adaptive_feedback_reviews=0`; `adaptive_evaluation_cases=0`; `adaptive_useful_interaction_logs=0`; `adaptive_audit_log=0`.\n- Estado dos documentos: 2 `uploaded`, 1 `error`. O bucket R2 `aigar-library` existe e a listagem mostrou três PDFs originais; a listagem consultada não demonstrou chunks derivados no D1.\n- O schema não contém tabela dedicada a Memory Cards/conversa persistente. Isso é coerente com o README do Worker, que declara `persistent_memory_cards` como capacidade adiada; não é uma descoberta inesperada de regressão.\n\n### Limites da verificação\n- Tentativas de abrir os endpoints públicos `/health`, `/memory/status`, `/library/boot` e `/texto-matriz/boot` pelo navegador de pesquisa não conseguiram obter respostas HTTP. Isso é uma limitação do canal de acesso usado nesta auditoria, **não prova que os endpoints estejam fora do ar**.\n- A API de conteúdo do Worker devolveu conteúdo multipart com truncamento de módulos grandes; por isso, não foi possível comprovar igualdade byte a byte de todo o código publicado com `main`.\n- Nenhuma escrita no D1/R2, alteração de configuração, commit ou deploy foi realizada.\n\n### Achados adicionados/atualizados\n| ID | Achado | Estado |\n|---|---|---|\n| AIGAR-092 | Worker publicado está na revisão `0b6a192`, enquanto `main` está 78 commits à frente. Risco de divergência entre repositório e produção. | Divergência confirmada por metadados; impacto funcional ainda não avaliado. |\n| AIGAR-093 | D1 tem 3 documentos, mas 0 linhas em `document_chunks`; dois documentos estão `uploaded` e um `error`. | Estado do banco confirmado por consultas read-only; pipeline de chunking/ingestão precisa de investigação. |\n| AIGAR-094 | Não há tabela dedicada de Memory Cards persistentes no schema ativo consultado. | Limite de capacidade confirmado e coerente com a documentação atual; requer desenho antes de implementar persistência entre sessões. |\n\n### Progresso recalibrado\nA estimativa estruturada passa de 75% para aproximadamente **77,5%** se o pacote de verificação do Worker for classificado como parcial: 13 concluídos, 5 parciais e 2 pendentes em 20 pacotes de peso igual. Esse número é apenas progresso do plano de auditoria, não prontidão de produção. As duas pendências críticas restantes são testes específicos do loader e teste de recuperação de memória entre instâncias; a verificação HTTP pública e a comparação completa do código implantado permanecem parciais.\n