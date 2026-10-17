# AIGAR — Mapa Organizacional de Funcionamento
## Arquitetura, fluxo de execução, memória e plano de validação funcional

**Versão:** 1.0  
**Data de consolidação:** 17 de outubro de 2026  
**Baseline:** GitHub release `3.9` — `IDMT - aigar baseline`  
**Estado:** mapa organizacional consolidado; validação funcional ponta a ponta em andamento  
**Regra:** documentação e testes somente de leitura até autorização explícita para corrigir/publicar.

> **Importante:** este mapa separa leitura estática, testes relatados, observações e pendências. Não afirma que o código local, GitHub Pages e Worker implantado sejam equivalentes.

## M00 — Controle do documento e regras de leitura

- Documento vivo de arquitetura e execução do AIGAR, consolidado em 17/10/2026 a partir do mapa v0.1, do registro de problemas v0.1 e do checkpoint de continuidade.
- Baseline documental: release GitHub `3.9`, denominado `IDMT - aigar baseline`, com ZIP referenciado na descrição do release. A presença do link e a possibilidade de download foram confirmadas pelo usuário. Não confundir anexo referenciado no corpo do release com asset formal listado pela API.
- Regra de segurança: este documento não autoriza mudanças. Nenhum código, Worker, banco, bucket ou publicação foi alterado durante a consolidação. Qualquer correção ou deploy requer autorização explícita.
- Legenda: [CÓDIGO] leitura estática documentada; [TESTE RELATADO] resultado reportado no checkpoint; [OBSERVADO] comportamento diretamente visto; [INFERÊNCIA] leitura arquitetural plausível ainda não comprovada ponta a ponta; [PENDENTE] requer teste ou inspeção.

## M01 — Visão executiva do sistema

- O ponto de entrada web analisado é `docs/aigar/index.html`, apresentado como AIGAR Developer Console. O campo API Base usa `/aigar/api` por padrão.
- A interface executa inicialização de status, consulta do Memory Lab, medição de armazenamento do navegador e bootstrap da biblioteca. O fluxo documental inclui `GET /library/boot` e `GET /texto-matriz/boot`.
- A pergunta da interface é enviada por `POST /perguntar`, com `input`, `session_id`, `answer_depth` e `source_fidelity`. O Worker em `aigar-c-2/AIGAR_CLOUDFLARE/main.py` normaliza rotas e encaminha a pergunta para `handle_ask(body, self.env)`, importado de `conversation_runtime.py`.
- O runtime de conversa integra recuperação documental, boot de biblioteca/matriz, núcleo cognitivo, interpretador linguístico, ponte de compatibilidade CORTEX, resolução de contexto assimétrico, pesquisa de biblioteca, geração de resposta e logging analítico. A ordem exata está detalhada em M05 e deve ser confirmada por testes funcionais no ambiente publicado.
- A arquitetura possui mecanismos distintos que não devem ser tratados como sinônimos: cache de bootstrap do navegador, biblioteca documental/chunks, Memory Lab e memória conversacional persistente. A persistência conversacional entre instâncias e Memory Cards persistentes não foram demonstradas como capacidades ativas.

## M02 — Fluxo ponta a ponta — da página à resposta

- 1. Navegador abre `docs/aigar/index.html` publicado pelo GitHub Pages (o caminho exato do artefato entregue deve ser reconfirmado no teste do index).
- 2. A página constrói a interface, define API Base (`/aigar/api`) e apresenta status inicial. O overlay de boot informa a inicialização do núcleo cognitivo.
- 3. A página executa chamadas de inicialização: `health()`, `refreshMemoryLab()`, `updateBrowserStorageUsage()` e `bootLibrary()`.
- 4. O bootstrap documental consulta `GET /library/boot` e `GET /texto-matriz/boot`; a interface mantém cache local via Cache API e `sessionStorage` e verifica o critério implementado de matriz carregada (`loaded == total` e `total == 8`). Esse critério é um gate de interface, não prova de qualidade semântica.
- 5. O usuário preenche pergunta, profundidade (`auto/direct/explanatory/deep/technical`) e fidelidade (`faithful/extractive/synthesis`) e aciona “Perguntar ao AIGAR”.
- 6. A interface envia `POST /perguntar` com o texto, um identificador de sessão e as opções de resposta. O valor `session_id` da consola foi observado como string fixa `developer-console`; isso não comprova isolamento nem restauração automática de histórico entre sessões.
- 7. O Worker normaliza o prefixo da rota e despacha a chamada para `handle_ask(body, env)`.
- 8. `handle_ask` valida entrada, carrega/reusa estado de sessão em memória, tenta recuperar trechos do Memory Lab, inicializa biblioteca e Text Matrix, prepara contexto cognitivo, interpreta a pergunta, classifica a interação, resolve contexto assimétrico e decide se consulta a biblioteca.
- 9. O runtime tenta compor uma resposta adaptativa; se a geração falha ou retorna vazia, há caminho de fallback determinístico. A presença do fallback não significa que a resposta final esteja correta ou sustentada pelas fontes.
- 10. O runtime acrescenta turnos ao estado local `SESSIONS`, limita a janela armazenada e tenta registrar metadados analíticos em D1. Retorna resposta, plano, fontes, telemetria e estado de sessão à interface.
- 11. A interface apresenta resposta, métricas de intenção/escopo/profundidade/confiança, leitura linguística e opções de feedback. `POST /feedback` pode gravar avaliação em D1 quando binding e esquema adaptativo estão disponíveis.
- 12. Teste de aceitação funcional deve verificar cada elo por evidência observável: interação da página, request, status/JSON, fonte recuperada, resposta e comportamento após uma segunda pergunta. Não inferir sucesso de um único indicador de boot.

## M03 — Mapa de arquivos e responsabilidades

- `docs/aigar/index.html` — frontend da consola: campos de pergunta, profundidade e fidelidade; status; overlay de boot; métricas; painel de leitura linguística; feedback; login/admin; chamadas HTTP e cache local de bootstrap.
- `aigar-c-2/AIGAR_CLOUDFLARE/main.py` — Worker: normalização de rota/prefixo, dispatch de endpoints, exposição de bindings/estado e encaminhamento para módulos runtime.
- `aigar-c-2/AIGAR_CLOUDFLARE/conversation_runtime.py` — orquestração da pergunta: validação, sessão em memória, recuperação, interpretação, contexto, pesquisa, geração/fallback e logging.
- `aigar-c-2/AIGAR_CLOUDFLARE/context_runtime.py` — gerenciamento assimétrico do contexto e seleção de turnos relevantes; detalhes e riscos listados nas seções de contexto do mapa-fonte e na matriz de falhas.
- `aigar-c-2/AIGAR_CLOUDFLARE/language_runtime.py` — interpretação heurística da linguagem, intenção, necessidade de memória/biblioteca, profundidade e sinais de ambiguidade.
- `aigar-c-2/AIGAR_CLOUDFLARE/cortex_compat.py` — normalização/ponte de compatibilidade do contrato cognitivo e roteamento.
- `aigar-c-2/AIGAR_CLOUDFLARE/association_core.py` — seleção/associação lexical de chunks e preparação de contexto cognitivo.
- `aigar-c-2/AIGAR_CLOUDFLARE/library_runtime.py` — bootstrap da biblioteca e da Text Matrix, índices, chunks e funções de pesquisa/carregamento.
- `aigar-c-2/AIGAR_CLOUDFLARE/storage_runtime.py` e `schema.sql` — rotinas de armazenamento documental, D1/R2, uploads e administração.
- `aigar-c-2/AIGAR_CLOUDFLARE/memory_lab/engine.py` e `memory_lab/config.json` — referências do Memory Lab; o estado e os caminhos ativos devem ser verificados no runtime publicado.
- `test_cognitive_core.py`, `test_cortex_compat.py`, `test_memory_lab.py` — três suítes relatadas como executadas; total 12 testes aprovados. Cobertura limitada aos casos testados.
- Workflows `aigar-cognitive-core.yml` e `aigar-runtime-validation.yml` — o primeiro executa as mesmas três suítes do pacote Worker e valida JavaScript inline; o segundo cobre runtime/retriever local, não necessariamente o loader de `library_runtime.py`.

## M04 — Interface e bootstrap — comportamento conhecido

- A página contém uma consola de desenvolvimento com estado de API, API Base, entrada, profundidade, fidelidade, botão de pergunta, botão de limpeza, métricas, área de resposta, leitura linguística, feedback e áreas administrativas.
- O fluxo de inicialização chama `health()`, `refreshMemoryLab()`, `updateBrowserStorageUsage()` e `bootLibrary()`.
- O bootstrap documental usa `/library/boot` e `/texto-matriz/boot`. A interface usa Cache API e `sessionStorage` para respostas de boot; cache pode permitir renderização/continuidade degradada ou obsoleta e deve ser testado quando houver sinal concreto.
- `navigator.storage.estimate()` mede estimativa de armazenamento do navegador, não memória RAM do computador.
- `clearAll()` limpa estado visual na página; pelo código observado, não equivale a apagar dados persistidos no backend.
- A interface considera a Text Matrix pronta quando `loaded == total` e `total == 8`; é um critério programático do frontend, não uma validação de completude semântica, qualidade ou fidelidade de cada capítulo.
- Caracteres acentuados corrompidos foram vistos em uma cópia do HTML compartilhada. A causa pode ser a própria codificação do arquivo ou um artefato de cópia; confirmar no arquivo publicado antes de corrigir.

## M05 — Worker e tabela de endpoints

- `GET /health` — retorna estado declarado da API, bindings D1/R2, versão e capacidades declaradas. Não comprova por si só que todos os caminhos estão operacionais.
- `GET /memory/status` — chama `MEMORY_LAB.initialize()` e retorna o estado do Memory Lab.
- `GET /texto-matriz/boot` — chama `boot_text_matrix()`.
- `GET /library/boot` — chama `boot_library()`.
- `POST /perguntar` — chama `handle_ask(body, self.env)`.
- `POST /feedback` — valida e tenta gravar feedback em D1 quando binding e esquema adaptativo estão disponíveis.
- `POST /auth/login` — encaminha autenticação para `medunity_admin_login()`.
- `GET /auth/me` — chama `medunity_me(request)`.
- `GET /admin/storage`, `GET /admin/documents`, `POST /admin/upload` — rotas administrativas protegidas por `require_admin()` conforme leitura estática.
- A interface usa `/aigar/api` como prefixo padrão; o Worker normaliza esse prefixo antes de comparar rotas. Em teste funcional, observar URL final, método, status HTTP e payload, sem pressupor que o prefixo foi corretamente removido em todos os cenários.

## M06 — Processamento de pergunta em conversation_runtime.py

- A função principal identificada é `async def handle_ask(body, env=None)`. Lê `input` e `session_id`; quando ausente, usa valor default. Rejeita entrada ausente/não textual com HTTP 400 e entrada acima de 20.000 caracteres com HTTP 413.
- Normaliza `answer_depth` para `auto/direct/explanatory/deep/technical` e `source_fidelity` para `extractive/faithful/synthesis`.
- `SESSIONS.setdefault(session_id, ...)` cria/reusa estruturas `turns`, `context_cache`, `last_user_input`, `last_response` e `reading`. O histórico é limitado aos últimos 80 turnos; a resolução assimétrica recebe até 40 turnos anteriores. É memória em processo, não persistência durável após reinicialização/instância diferente.
- Ordem estática observada: (a) `MEMORY_LAB.retrieve_with_fallback(text)`; (b) `boot_library()` e `boot_text_matrix()`; (c) `COGNITIVE_CORE.prepare(text, core_chunks)`; (d) `LANGUAGE_ENGINE.interpret()` e `COGNITIVE_CORE.annotate_reading()`; (e) classificação da interação e normalização via `WORKER_CORTEX_BRIDGE`; (f) `AsymmetricContextManager().resolve(text, prior_turns[-40:], needs_context=...)`; (g) `library_search()` se `routing_decision['use_library']` estiver ativo; (h) até três documentos do Memory Lab se não houver evidências bibliográficas; (i) revisão de plano adaptativo e seleção do modo; (j) `render_adaptive_answer()` ou fallback determinístico; (k) atualização de `SESSIONS`; (l) tentativa de registro analítico em D1; (m) retorno de resposta/plano/fontes/telemetria/estado.
- `_record_interaction()` calcula SHA-256 de `session_id` e guarda os primeiros 32 caracteres como `session_hash`. A tabela `adaptive_interactions` recebe IDs, tipo de interação, modo previsto, versão do modelo, snapshot mínimo e timestamp.
- O snapshot analítico mínimo não é histórico integral. `_safe_useful_snapshot()` pode incluir entrada e resposta em um caminho administrativo explícito, distinto da gravação automática padrão.
- A própria resposta/código descreve persistência conversacional entre instâncias como não configurada quando não há contexto de sessão selecionado. Recuperação do histórico integral de D1 para reconstruir `SESSIONS` em outra instância permanece pendente.

## M07 — Linguagem, contexto assimétrico, CORTEX e associação

- `language_runtime.py`: interpretador heurístico, baseado em listas/regras, produz sinais de intenção, necessidade de memória/biblioteca, profundidade e ambiguidade. Não tratar os sinais como entendimento semântico garantido.
- `context_runtime.py`: seleciona turnos anteriores relevantes. O mapa-fonte registra riscos sobre resolução de referentes, decisões ativas, comparações literais de status, metadados de contexto, tokenização/acentos e revisão do plano. Esses pontos são problemas/hipóteses documentados no registro AIGAR; validar em teste antes de alterar.
- `cortex_compat.py`: ponte que normaliza contrato/roteamento entre os componentes. Os testes existentes cobrem compatibilidade em cenários específicos, mas não provam a correção integral da cadeia ponta a ponta.
- `association_core.py`: associação/seleção de chunks para contexto cognitivo. A cobertura de teste existente é limitada; não há prova reportada de que cada pergunta recupera os chunks semanticamente mais adequados.
- Risco de integração: sinais de memória do interpretador não necessariamente controlam diretamente a seleção assimétrica; o plano pode marcar uso de memória apenas quando turnos são selecionados; a resolução recebe somente os últimos 40 turnos disponíveis; o estado pode ficar ambíguo quando o roteamento pede memória, mas a seleção retorna vazia. Ver AIGAR-030 a AIGAR-033.

## M08 — Biblioteca, Text Matrix, chunks e cache

- O boot separado da biblioteca reportou sete bibliotecas em estado `ready`. Esse resultado não deve ser fundido com o resultado separado da Text Matrix.
- Resultado separado da Text Matrix: `ready: true`, `loaded: 8`, `total: 8`, com oito capítulos TM-01 a TM-08. É evidência de inicialização/contagem, não prova de que toda pergunta recupera o capítulo certo.
- O checkpoint reporta 73/73 hashes e comprimentos validados localmente depois de normalizar finais de linha CRLF para LF. Isso não comprova que os mesmos 73 chunks estejam acessíveis ou íntegros no Worker publicado.
- `library_runtime.py` tenta carregar arquivos por cache e fontes GitHub Raw/Contents API, segundo leitura estática. O cache foi descrito como indexado apenas por ID; o loader não valida hash/comprimento em tempo de execução. Testes específicos de fallback, indisponibilidade, checksum e cache não foram encontrados nas três suítes inspecionadas.
- Problema de armazenamento remoto: a inspeção read-only relatou D1 com `document_chunks = 0`, enquanto o bucket R2 `aigar-library` continha três PDFs originais; dois documentos estavam com estado `uploaded` e um `error`. O pipeline de chunking precisa de investigação. Não concluir que a biblioteca da Text Matrix e o pipeline de documentos de usuário são o mesmo mecanismo.
- Quando houver falha de resposta ou fonte inadequada, inspecionar a requisição de pergunta e as respostas de boot/retrieval relevantes; não repetir todo o health/boot sem motivo.

## M09 — Memória, sessões, Memory Lab e Memory Cards

- Camada 1 — cache de bootstrap no navegador: respostas de inicialização guardadas em Cache API/sessionStorage. É cache operacional da interface, não memória semântica ou autobiográfica.
- Camada 2 — biblioteca documental: índices e chunks consultados para apoiar respostas. É conhecimento recuperável, não histórico de conversa.
- Camada 3 — Memory Lab: componente acessado via `/memory/status`; a inicialização e recuperação têm fallbacks. Estado e comportamento publicados precisam ser testados em contexto real.
- Camada 4 — sessão transitória do runtime: `SESSIONS` guarda turnos e campos auxiliares em memória do processo. Não garante sobrevivência à reinicialização nem compartilhamento entre instâncias.
- Camada 5 — persistência analítica D1: `adaptive_interactions` registra metadados/snapshot mínimo; não equivale a persistência integral do histórico.
- Camada 6 — Memory Cards persistentes: a capacidade `persistent_memory_cards` aparece como adiada no contrato de compatibilidade; o schema examinado não tinha tabela dedicada para cartões conversacionais. Ativação funcional não foi demonstrada.
- Para afirmar memória entre sessões, precisamos comprovar a cadeia completa: extração/seleção → serialização → gravação durável → índice/chave de usuário e sessão → recuperação em nova sessão/instância → atualização/versionamento → isolamento e política de conflito. Atualmente, a cadeia não está comprovada ponta a ponta.

## M10 — Feedback, autenticação, armazenamento e administração

- Feedback de resposta: a interface disponibiliza categoria, tipo de problema e comentário; o Worker recebe `POST /feedback` e pode gravar em D1 quando binding e esquema adaptativo estão disponíveis.
- Autenticação: a interface mostra login MedUnity; a autenticação é delegada ao Worker/MedUnity. O código observado não deve ser interpretado como prova de segurança operacional sem testes de fluxo e permissões.
- Administração: endpoints de storage, documentos e upload são protegidos por `require_admin()` segundo leitura estática. Testes de acesso autorizado e não autorizado não foram reportados nesta fase.
- Storage: D1 e R2 existem segundo a verificação read-only relatada. A existência de binding ou bucket não garante que upload, extração, chunking, consulta e restauração estejam funcionando.
- `clearAll()` da interface é limpeza de estado visual; não deve ser usado como prova de exclusão remota. A exclusão/retensão de dados exige endpoint e comportamento próprios, não demonstrados aqui.

## M11 — Testes, CI, hashes e divergência de ambientes

- Testes locais relatados: `test_cognitive_core.py` 3/3; `test_cortex_compat.py` 4/4; `test_memory_lab.py` 5/5; total 12/12 aprovados, 0 falhas/erros. Resultado cobre apenas os casos das suítes executadas.
- Workflow `aigar-cognitive-core.yml` executa as mesmas três suítes (12 testes) e valida JavaScript inline. `aigar-runtime-validation.yml` cobre runtime/retriever local, não necessariamente o loader do Worker.
- Foi relatada divergência de configuração: `pyproject.toml` pede Python `>=3.13`, enquanto workflow de validação cognitiva configura Python 3.12. Impacto não demonstrado.
- Comparação de versões relatada: Worker publicado `aigar-api`, rota `delyone.com/aigar/api*`, versão publicada nº 40, 100% do tráfego, anotada com commit `0b6a19289543dc64bdc4cf02c7953491b3433651`; `main` estava 78 commits à frente, em `4c09801d07f4ed15493985bdc0ed8683f7956e7b`. Portanto, não presumir equivalência entre código do GitHub Pages, branch `main` e Worker ativo.
- Verificação read-only reportou `PRAGMA quick_check = ok`; contagens D1: `documents` 3; `document_chunks` 0; `adaptive_interactions` 26; `adaptive_feedback` 3; reviews/evaluation_cases/useful logs/audit log 0. Estados de documents: 2 `uploaded`, 1 `error`.
- Tentativas anteriores de consultar endpoints pelo navegador de pesquisa não obtiveram resposta; isso foi classificado como inconclusivo, não como prova de indisponibilidade.
- Manifestos SHA-256 ajudam a verificar igualdade com um digest esperado. Sozinhos, não provam autoria, cronologia, origem do artefato ou equivalência de código implantado.

## M12 — Matriz de rotas e dependências

- Frontend → Worker: `/aigar/api` como base padrão; requisições relevantes: `GET /health`, `GET /memory/status`, `GET /library/boot`, `GET /texto-matriz/boot`, `POST /perguntar`, `POST /feedback`, autenticação e endpoints administrativos.
- `POST /perguntar` → `main.py` dispatch → `conversation_runtime.handle_ask` → `MEMORY_LAB.retrieve_with_fallback`, `boot_library`, `boot_text_matrix`, `COGNITIVE_CORE`, `LANGUAGE_ENGINE`, `WORKER_CORTEX_BRIDGE`, `AsymmetricContextManager`, `library_search`, `render_adaptive_answer`/fallback → atualização de `SESSIONS` → logging D1 → resposta HTTP.
- `GET /memory/status` → `MEMORY_LAB.initialize()` → estado devolvido à interface.
- `GET /library/boot` → `boot_library()`; `GET /texto-matriz/boot` → `boot_text_matrix()`; ambos são caminhos distintos e precisam de evidência separada.
- `POST /feedback` → validação → tentativa de persistência em D1; confirmar que a resposta da UI corresponde a gravação real quando isso for parte do teste.
- Admin routes → `require_admin()` → funções MedUnity/storage; validar autorização e rejeição de chamadas sem sessão administrativa.

## M13 — Plano de execução da Fase 2 — testes funcionais no GitHub Pages

- Objetivo: testar o comportamento do `index` publicado e escolher o próximo teste conforme o resultado real. Não repetir health/boot como rotina; consultar esses endpoints apenas quando uma falha apontar para inicialização, roteamento ou estado.
- Teste 2.1 — pergunta sobre capítulo específico: “Segundo o capítulo TM-02 da Text Matrix, o que é linguagem? Explique o conceito com base no conhecimento disponível no AIGAR.” Registrar resposta literal, status da requisição, fonte/capítulo se exibidos, tempo/estado de carregamento e métricas apresentadas.
- Teste 2.2 — coerência de contexto: fazer uma pergunta de seguimento que dependa explicitamente da resposta anterior. Verificar se o AIGAR resolve o referente correto e não responde como se fosse conversa nova.
- Teste 2.3 — mudança de tópico: perguntar sobre outro tema e depois retornar ao primeiro; observar se contexto irrelevante é descartado e o contexto útil é preservado.
- Teste 2.4 — profundidade e fidelidade: repetir pergunta equivalente com profundidades diferentes e comparar se a resposta muda de modo esperado sem inventar fontes.
- Teste 2.5 — fonte/evidência: pedir que indique qual capítulo ou trecho sustenta a resposta. Não considerar uma referência textual inventada como evidência; conferir se há metadado de fonte real no payload/rede.
- Teste 2.6 — continuidade da sessão: fazer duas ou mais perguntas na mesma página; depois recarregar e repetir referência à conversa anterior. Separar continuidade na mesma instância/página de persistência real entre sessões.
- Teste 2.7 — cache e fallback: só executar se houver suspeita observável de resposta antiga, carregamento parcial ou indisponibilidade. Registrar cache hit/miss e resposta efetiva antes de limpar cache.
- Teste 2.8 — feedback: enviar feedback controlado apenas com autorização do usuário e depois confirmar se foi registrado, sem criar dados de teste desnecessários em produção.
- Para cada teste registrar: ID, data/hora, URL publicada, navegador, pergunta exata, resultado literal, console/network relevante, classificação (passou/falhou/inconclusivo), vínculo com seções Mxx e IDs AIGAR-xxx. Não alterar o código durante a coleta.

## M14 — Limitações conhecidas e o que ainda não podemos afirmar

- Não está provado que o Worker implantado corresponde ao `main` atual ou ao mesmo commit do release 3.9.
- Não está provado que a Text Matrix seja usada corretamente em cada resposta, apesar de boot e contagem 8/8.
- Não está provada a recuperação do histórico completo entre instâncias.
- Não está provada a persistência de Memory Cards conversacionais.
- Não está provado o pipeline completo de documentos de usuário, especialmente criação/consulta de chunks em D1.
- Não há cobertura específica reportada para hash/comprimento em tempo de execução do loader, fallback sob indisponibilidade, nem comportamento do cache em falha.
- Os 12 testes aprovados são uma evidência positiva delimitada; não equivalem a teste end-to-end nem garantia de produção.

## M15 — Fontes e proveniência documental

- Fonte primária 1: `AIGAR_Mapa_de_Funcionamento_v0.1.md` e `.docx` — mapa estático anterior, incluindo `index.html`, `main.py`, `conversation_runtime.py`, contexto, linguagem, CORTEX, associação, testes e loader.
- Fonte primária 2: `AIGAR_Registro_de_Problemas_v0.1.md` e `.docx` — registros AIGAR-001 em diante e suas atualizações.
- Fonte primária 3: `AIGAR_CHECKPOINT_CONTINUIDADE_2026-10-17.md` — evidências de testes, hashes, CI, estado do Worker e D1/R2 reportadas em 17/10/2026.
- Fonte primária 4: relatórios de boot consolidados da fase anterior — evidências separadas para boot das bibliotecas e Text Matrix, limitações e plano de correção.
- Os detalhes marcados como reportados provêm dos registros de auditoria fornecidos; este documento não executou novamente os testes nem acessou o Worker para confirmar o estado atual.

## M16 — Índice cruzado de falhas

Consulte `AIGAR_Matriz_de_Falhas_Referenciada_v1.0_2026-10-17.md` para o vínculo entre IDs AIGAR, seções deste mapa, evidência e prioridade de investigação.
