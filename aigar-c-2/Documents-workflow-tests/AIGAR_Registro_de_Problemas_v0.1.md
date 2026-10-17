# AIGAR — Registro de Problemas, Inconsistências e Alterações

**Versão:** 0.1  
**Data:** 17/10/2026  
**Escopo:** auditoria estática inicial da UI `docs/aigar/index.html`, `main.py` e `conversation_runtime.py`, com itens pendentes para inspeção de módulos relacionados.

## Regras do registro
- Não misturar fatos observados, hipóteses e testes ainda não realizados.
- Nenhuma alteração de código é considerada concluída sem teste de regressão.
- Prioridades: **P0** crítica; **P1** alta; **P2** média; **P3** baixa.
- A confirmação de código local não comprova, por si só, comportamento do Worker implantado.

## Resumo inicial
- Resumo inicial preservado como histórico; o registro foi ampliado em fases posteriores.
- Resultado mais recente: **12/12 testes locais aprovados**, sem falhas ou erros (2026-10-17).
- As prioridades são preliminares e não equivalem a defeitos reproduzidos.

## Lista de problemas

### AIGAR-001 — Persistência de conversa entre instâncias
- **Prioridade:** P1 — alta
- **Status:** Confirmado no código-fonte analisado
- **Arquivo/área:** `aigar-c-2/AIGAR_CLOUDFLARE/conversation_runtime.py`
- **Evidência:** A sessão é mantida em SESSIONS, com turns/context_cache em memória do runtime. O próprio rastreamento de fontes informa que a persistência conversacional entre instâncias não está configurada.
- **Impacto:** Uma conversa pode perder o contexto quando a instância do Worker reinicia, muda ou não compartilha o mesmo estado em memória.
- **Correção proposta:** Projetar persistência explícita e segura de memória conversacional; separar memória episódica, preferências/perfil, estado de tarefa e documentos de biblioteca. Definir consentimento, retenção, limites, recuperação e exclusão antes de implementar.
- **Teste de validação:** Enviar vários turnos, simular nova instância/sessão de runtime e verificar quais dados são recuperados; testar isolamento entre session_id diferentes e exclusão.

### AIGAR-002 — Memory cards persistentes não demonstrados como capacidade ativa
- **Prioridade:** P1 — alta
- **Status:** Confirmado como limitação declarada; implantação ainda não verificada
- **Arquivo/área:** `aigar-c-2/AIGAR_CLOUDFLARE/main.py (GET /health) e conversation_runtime.py`
- **Evidência:** O contrato de compatibilidade do health declara persistent_memory_cards como capacidade deferred. MEMORY_LAB.retrieve_with_fallback recupera documentos, mas isso, isoladamente, não prova armazenamento/recuperação de memórias pessoais entre sessões.
- **Impacto:** A interface pode sugerir uma capacidade de memória mais ampla do que a execução atual garante.
- **Correção proposta:** Definir contrato de memória (escrita, leitura, atualização, proveniência, confiança, expiração e exclusão) e só anunciar capacidade como ativa após teste integrado.
- **Teste de validação:** Criar uma memória explicitamente autorizada, terminar a sessão, recuperar em outra sessão e conferir proveniência, isolamento e exclusão.

### AIGAR-003 — Seleção de contexto assimétrico
- **Prioridade:** P1 — alta
- **Status:** Pendente de inspeção do módulo
- **Arquivo/área:** `aigar-c-2/AIGAR_CLOUDFLARE/context_runtime.py`
- **Evidência:** conversation_runtime.py chama AsymmetricContextManager().resolve(text, prior_turns[-40:], needs_context=bool(routing_decision['use_memory'])). A lógica de seleção ainda precisa ser inspecionada diretamente.
- **Impacto:** Não é possível ainda confirmar se o sistema recupera contexto relevante, evita distrações e lida corretamente com referências a turnos anteriores.
- **Correção proposta:** Inspecionar critérios, pontuação, limites, exclusões, ordenação, tratamento de contradições e comportamento quando needs_context é falso; propor mudanças só depois dessa leitura.
- **Teste de validação:** Montar casos de referência: pronome/referência a turno anterior, assunto novo, correção do usuário, memória contraditória, contexto irrelevante e sessão vazia.

### AIGAR-004 — Limite de histórico em memória
- **Prioridade:** P2 — média
- **Status:** Confirmado no código-fonte analisado
- **Arquivo/área:** `aigar-c-2/AIGAR_CLOUDFLARE/conversation_runtime.py`
- **Evidência:** O fluxo mantém no máximo os últimos 80 turnos em turns/context_cache; a resolução de contexto recebe os últimos 40 turnos anteriores.
- **Impacto:** Informações importantes mais antigas podem deixar de ser candidatas ao contexto, mesmo quando ainda são relevantes.
- **Correção proposta:** Não aumentar limites às cegas. Definir sumarização/extração de fatos, referências a fontes e recuperação seletiva, preservando a diferença entre resumo inferido e conteúdo literal.
- **Teste de validação:** Colocar um fato importante no início de uma conversa longa e verificar recuperação correta, atribuição da fonte e ausência de invenção.

### AIGAR-005 — Limites de sessão e validação de entrada
- **Prioridade:** P2 — média
- **Status:** Confirmado no código-fonte analisado
- **Arquivo/área:** `aigar-c-2/AIGAR_CLOUDFLARE/conversation_runtime.py`
- **Evidência:** handle_ask limita input a 20.000 caracteres e session_id a 128 caracteres; o histórico é truncado por quantidade de turnos.
- **Impacto:** Os limites existem, mas ainda não foi demonstrado se há validação de tipo, normalização, limites de payload e tratamento consistente de entradas malformadas em todos os caminhos.
- **Correção proposta:** Auditar os validadores e respostas HTTP, incluindo JSON inválido, tipos inesperados, strings vazias, IDs extremos e payloads grandes. Não presumir falha antes dos testes.
- **Teste de validação:** Testes automatizados de fronteira para corpo inválido, input vazio, tamanho máximo e máximo + 1, session_id e tipos incorretos.

### AIGAR-006 — Boot da biblioteca e matriz textual
- **Prioridade:** P2 — média
- **Status:** Pendente de verificação integrada
- **Arquivo/área:** `docs/aigar/index.html; main.py; library_runtime.py`
- **Evidência:** A UI espera matrix.ready e loaded === total === 8; tenta /library/boot e /texto-matriz/boot, com cache local como fallback. O caminho do Worker e a correspondência com o estado implantado ainda não foram verificados de ponta a ponta.
- **Impacto:** A interface pode bloquear perguntas ou entrar em modo reduzido se o contrato de boot, os oito itens esperados ou as rotas divergirem.
- **Correção proposta:** Comparar contrato do frontend, respostas reais do Worker e conteúdo disponível. Documentar se 8 é requisito fixo ou configuração; tornar mensagens de falha explícitas.
- **Teste de validação:** Testar boot normal, biblioteca parcial, cache disponível, cache inválido e API indisponível; conferir os campos reais retornados.

### AIGAR-007 — Limpeza da interface não equivale a apagar dados persistidos
- **Prioridade:** P2 — média
- **Status:** Confirmado no código-fonte analisado
- **Arquivo/área:** `docs/aigar/index.html`
- **Evidência:** clearAll() limpa o estado da interface; não foi identificado nesse fluxo um endpoint de exclusão de histórico no backend.
- **Impacto:** O usuário pode interpretar a ação visual como exclusão de dados no servidor, embora o código observado só limpe o estado da UI.
- **Correção proposta:** Renomear/explicar a ação como limpeza local ou implementar um fluxo explícito de exclusão remota, com autorização, confirmação e auditoria, se esse for o requisito.
- **Teste de validação:** Após limpar a interface, verificar separadamente UI, sessionStorage/cache, estado do Worker e armazenamento persistente.

### AIGAR-008 — Cache local do boot
- **Prioridade:** P2 — média
- **Status:** Pendente de verificação
- **Arquivo/área:** `docs/aigar/index.html`
- **Evidência:** O boot usa Cache API e sessionStorage como fallback. O uso de navigator.storage.estimate() mede estimativa de armazenamento do navegador, não RAM.
- **Impacto:** Dados de boot antigos ou inválidos podem ser reutilizados; métricas de armazenamento podem ser interpretadas incorretamente como memória RAM.
- **Correção proposta:** Verificar versionamento, validade, integridade e invalidação do cache. Rotular a métrica como armazenamento estimado do navegador.
- **Teste de validação:** Alterar a versão do contrato, simular JSON inválido e respostas antigas; conferir invalidação e fallback.

### AIGAR-009 — Divergência entre fonte local e Worker implantado
- **Prioridade:** P1 — alta
- **Status:** Pendente de verificação
- **Arquivo/área:** `aigar-c-2/AIGAR_CLOUDFLARE/ e configuração de deploy`
- **Evidência:** A análise até aqui é estática. A equivalência entre o código local, o código publicado e a configuração de rotas não foi comprovada.
- **Impacto:** Correções locais podem não refletir no ambiente servido; a UI pode chamar rotas diferentes das esperadas.
- **Correção proposta:** Registrar commit local, branch, configuração de deploy, rotas e versão implantada. Comparar respostas observadas com contratos do código, sem alterar o ambiente durante a auditoria.
- **Teste de validação:** Executar uma matriz somente de leitura de endpoints e comparar respostas com a versão do repositório e os contratos documentados.

### AIGAR-010 — Erros silenciosos e fallbacks
- **Prioridade:** P2 — média
- **Status:** Pendente de inspeção
- **Arquivo/área:** `aigar-c-2/AIGAR_CLOUDFLARE/conversation_runtime.py; library_runtime.py; answer_runtime.py`
- **Evidência:** O fluxo isola exceções de alguns componentes e mantém resposta fallback quando o renderizador falha; isso favorece continuidade, mas é preciso verificar observabilidade e distinção entre resposta completa e degradada.
- **Impacto:** Falhas internas podem parecer respostas normais se o estado degradado não ficar claro para operador e usuário.
- **Correção proposta:** Padronizar códigos de estado internos, logs sem dados pessoais desnecessários, indicação de fallback e correlação por interaction_id; não expor detalhes internos sensíveis na UI.
- **Teste de validação:** Forçar falhas controladas em retrieval, boot e renderer; verificar resposta, telemetria e logs.

### AIGAR-011 — Codificação de caracteres
- **Prioridade:** P3 — baixa
- **Status:** Pendente de confirmação
- **Arquivo/área:** `docs/aigar/index.html`
- **Evidência:** O conteúdo copiado durante a inspeção apresentou caracteres acentuados corrompidos (mojibake); ainda não está confirmado se isso existe no arquivo real ou se surgiu durante a cópia.
- **Impacto:** Se for real, pode afetar textos da interface, legibilidade e testes de strings.
- **Correção proposta:** Inspecionar bytes/encoding do arquivo original e cabeçalhos; normalizar para UTF-8 apenas se a corrupção for confirmada.
- **Teste de validação:** Abrir o arquivo original em UTF-8 e validar acentos em navegador, sem alterar o arquivo antes da confirmação.

## Próximo passo de auditoria
Inspecionar `aigar-c-2/AIGAR_CLOUDFLARE/context_runtime.py` para transformar o item AIGAR-003 em achados específicos, confirmados por código. Comando local sugerido:

```powershell
Get-Content .\aigar-c-2\AIGAR_CLOUDFLARE\context_runtime.py
```

## Histórico de alterações deste registro
- v0.1: criado com base nos trechos de frontend, `main.py` e `conversation_runtime.py` já analisados. Nenhum código do repositório foi modificado.

## Atualização da Fase 3 — `context_runtime.py` (v0.2)
Itens identificados a partir do código compartilhado nesta conversa. A possível falha de codificação está marcada como pendente porque a cópia pode ter alterado os caracteres.

### AIGAR-012 — Sinal de referência não identifica referências linguísticas
- **Prioridade:** P1 — alta
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``context_runtime.py` — `AsymmetricContextManager.resolve()``
- **Evidência:** O código usa `needs_context` e a posição nos últimos quatro turnos como `reference_signal`; não há, neste módulo, detecção explícita de expressões como “isso”, “aquilo”, “o anterior” ou resolução do referente.
- **Impacto:** Perguntas que dependem de uma referência podem receber contexto recente sem que o referente correto seja identificado.
- **Correção proposta:** Projetar detecção/resolução de referência com fallback explícito para pedir esclarecimento quando houver ambiguidade. Avaliar junto ao `language_runtime` antes de duplicar lógica.
- **Teste de validação:** Testar referências claras, ambíguas, múltiplos candidatos e ausência de antecedente.

### AIGAR-013 — Decisões ativas não são extraídas pelo resolvedor
- **Prioridade:** P2 — média
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``context_runtime.py` — campo `active_decisions``
- **Evidência:** A função retorna sempre `active_decisions: []`; o comentário diz que decisões devem ser marcadas explicitamente.
- **Impacto:** Planos/decisões importantes não são representados por este resolvedor, a menos que outro módulo os forneça por mecanismo separado.
- **Correção proposta:** Definir um esquema explícito para decisões confirmadas, revogadas e substituídas; não inferir decisão apenas por repetição. Verificar primeiro se outro módulo já faz essa marcação.
- **Teste de validação:** Criar, atualizar, revogar e substituir uma decisão; conferir se a versão vigente é a única apresentada como ativa.

### AIGAR-014 — Status de contexto é comparado de forma estritamente literal
- **Prioridade:** P2 — média
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``context_runtime.py` — `context_status``
- **Evidência:** A exclusão ocorre apenas quando o valor é exatamente `revoked` ou `superseded`; não há normalização de espaços ou caixa neste trecho.
- **Impacto:** Valores como `Revoked`, `SUPERSEDED` ou valores desconhecidos não são excluídos por essa condição e acabam tratados como elegíveis.
- **Correção proposta:** Definir enumeração/validação central de status e normalização consistente na entrada; decidir explicitamente o tratamento de estados desconhecidos.
- **Teste de validação:** Testar todos os estados válidos, caixa diferente, espaços, nulo e estado desconhecido.

### AIGAR-015 — Sinal de contexto fixado depende de estrutura de metadados não validada aqui
- **Prioridade:** P2 — média
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``context_runtime.py` — leitura de `metadata.pinned_context``
- **Evidência:** O código assume que `turn` e `metadata` têm estrutura compatível com dicionários; o acesso a `(turn.get('metadata') or {}).get(...)` pode falhar se `metadata` for um tipo não mapeável.
- **Impacto:** Um turno malformado pode interromper a resolução de contexto, dependendo de quem constrói o histórico.
- **Correção proposta:** Validar/normalizar turnos e metadados na fronteira de entrada; registrar erro sem incluir conteúdo pessoal desnecessário.
- **Teste de validação:** Passar turnos com metadata ausente, nulo, string, lista e objeto válido.

### AIGAR-016 — Regex de tokenização pode ter problema de codificação de caracteres acentuados
- **Prioridade:** P2 — média
- **Status:** Pendente de confirmação no arquivo original
- **Arquivo/área:** ``context_runtime.py` — `_context_token_set()``
- **Evidência:** O texto compartilhado mostra a classe `r"[a-zA-ZÃ€-Ã¿0-9_]{3,}"`, com caracteres que parecem mojibake. Como o conteúdo foi copiado, é necessário confirmar os bytes do arquivo original.
- **Impacto:** Se a expressão estiver literalmente assim no arquivo, a segmentação de palavras acentuadas em português pode ser inconsistente.
- **Correção proposta:** Inspecionar o arquivo original e testar palavras com acentos; corrigir a classe Unicode somente se o problema for confirmado.
- **Teste de validação:** Testar `memória`, `decisão`, `sessão`, `ação`, palavras sem acento e texto misto.

### AIGAR-017 — Revisão do plano pode sobrescrever a estratégia de resposta
- **Prioridade:** P2 — média
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``context_runtime.py` — `revise_adaptive_plan()``
- **Evidência:** Quando há evidências, a estratégia vira `synthesize_with_source_evidence`; se `corrected_intent` também for verdadeiro, depois é substituída por `reclassify_intent_before_answering`.
- **Impacto:** A estratégia final pode indicar reclassificação em vez de síntese com evidências, embora `evidence_required` e `use_library` permaneçam verdadeiros. É necessário definir se isso é intencional como próxima etapa ou conflito de estado.
- **Correção proposta:** Especificar se a revisão de intenção deve suspender a resposta, preservar evidências ou compor etapas explícitas do plano; representar estratégia e etapa separadamente se necessário.
- **Teste de validação:** Testar combinações: evidência apenas, correção apenas, ambas juntas e contexto não resolvido.

### AIGAR-018 — Normalização de pontuação e metadados pode ser mais robusta
- **Prioridade:** P3 — baixa
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``context_runtime.py` — `_context_token_set()` e `resolve()``
- **Evidência:** A sobreposição é calculada sobre o conjunto de tokens da consulta; com consulta sem tokens úteis, o denominador é protegido por `max(1, len(q_tokens))`, mas a relevância lexical fica zero para todos os turnos.
- **Impacto:** Em consultas muito curtas, só recência, sinal de referência e contexto fixado diferenciam os candidatos; isso pode ser aceitável, mas não é sinalizado como modo degradado.
- **Correção proposta:** Registrar quando não há tokens úteis e definir comportamento explícito para consultas curtas, sem inventar relevância lexical.
- **Teste de validação:** Testar consultas vazias após normalização, só stopwords e consultas com um único termo útil.

### Nota de revisão
A pontuação atual é `0.42 * overlap + 0.25 * recency + 0.23 * reference_signal + 0.10 * dependency`. O sinal de referência é posicional (últimos quatro turnos quando `needs_context=True`), não uma resolução semântica do referente. `active_decisions` é sempre retornado vazio neste módulo.

## Atualização da Fase 2 — `language_runtime.py` (v0.2)
Achados baseados no conteúdo compartilhado. Possíveis problemas de codificação permanecem pendentes até inspeção dos bytes do arquivo original.

### AIGAR-019 — Heurísticas de intenção podem produzir classificações concorrentes ou prematuras
- **Prioridade:** P1 — alta
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — `LanguageEngine.interpret()``
- **Evidência:** A classificação segue uma cadeia `if/elif` ordenada: padrões de pergunta são avaliados antes de phatic, caso clínico, continuidade, correção, dúvida e ação. Assim, o primeiro ramo compatível vence.
- **Impacto:** Uma entrada com mais de uma função comunicativa pode ser classificada pela primeira regra compatível, sem registrar as intenções concorrentes.
- **Correção proposta:** Definir precedência documentada e/ou classificador multissinal; preservar intenção primária, intenções secundárias e evidência usada na classificação.
- **Teste de validação:** Testar entradas com pedido + correção, pergunta clínica + continuidade, saudação com pergunta e comandos que contêm termos de outras categorias.

### AIGAR-020 — Correspondência por substring em várias categorias
- **Prioridade:** P1 — alta
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — `has_any()` e chamadas em `interpret()``
- **Evidência:** `has_any()` verifica `value in text`; `has_phrase()` evita falsos positivos por substring, mas só é usada no ramo phatic. Exemplos como `action`, `continuity`, `correction` e `doubt` usam `has_any()`.
- **Impacto:** Palavras ou expressões contidas dentro de outras palavras podem acionar categorias indevidamente; a extensão do problema depende das expressões concretas e deve ser medida por testes.
- **Correção proposta:** Usar correspondência por limites de palavra ou frases normalizadas para as categorias que exigem expressão completa; manter regras explícitas para variantes flexionadas.
- **Teste de validação:** Testar pares como `oi` dentro de `foi`, verbos dentro de palavras maiores e expressões com acento/pontuação.

### AIGAR-021 — Profundidade solicitada não corresponde necessariamente ao vocabulário configurado
- **Prioridade:** P1 — alta
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — `LANGUAGE.depth` e `interpret()``
- **Evidência:** A configuração define níveis `brief`, `simple`, `technical` e `deep`, mas o código inicia em `normal` e percorre os níveis configurados. O primeiro marcador encontrado define a profundidade; não há resolução de conflito entre vários marcadores.
- **Impacto:** Pedidos com marcadores múltiplos ou variantes linguísticas não previstas podem resultar em profundidade inesperada; também é necessário verificar como consumidores tratam `brief` e `simple`.
- **Correção proposta:** Especificar enumeração de profundidade e precedência; testar normalização, múltiplos marcadores e compatibilidade com `answer_depth` da API.
- **Teste de validação:** Testar cada marcador isolado, marcadores conflitantes, maiúsculas, acentos e ausência de marcador; comparar saída do interpretador e renderizador.

### AIGAR-022 — Resolução de referentes está descrita na base, mas não é executada integralmente por este interpretador
- **Prioridade:** P1 — alta
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — `PORTUGUESE.discourse_and_context`, `interpret()``
- **Evidência:** A base descreve resolução de anáfora, catáfora e elipse. Já `interpret()` seleciona `subject` como o primeiro pronome ou, na ausência dele, a primeira combinação artigo + palavra; não resolve antecedente discursivo nessa função.
- **Impacto:** A análise linguística pode fornecer um `possible_subject` superficial, sem identificar a entidade correta a que um pronome se refere.
- **Correção proposta:** Separar a representação heurística da resolução de referência; integrar a saída com o resolvedor de contexto e permitir ambiguidade não resolvida.
- **Teste de validação:** Testar `Ele chegou`, múltiplos antecedentes possíveis, `isso` após duas ideias, catáfora e elipse.

### AIGAR-023 — Detecção de verbos e sujeito é baseada em listas/posições
- **Prioridade:** P2 — média
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — `verbs()` e `interpret()``
- **Evidência:** `verbs()` usa um léxico finito; `possible_subject` toma o primeiro pronome, ou o primeiro artigo seguido de uma palavra. A análise é explicitamente rotulada `heuristic_structural_reading`.
- **Impacto:** Flexões, verbos desconhecidos e estruturas com sujeito posposto ou orações múltiplas podem ser analisados de forma incompleta.
- **Correção proposta:** Manter o resultado como pista heurística, não como análise sintática garantida; adicionar testes de cobertura e/ou um parser dedicado se a precisão exigida justificar.
- **Teste de validação:** Testar sujeito posposto, sujeito oculto, orações compostas, flexões não listadas e frases sem sujeito.

### AIGAR-024 — STOPWORDS e tokenização divergem entre módulos
- **Prioridade:** P2 — média
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — `STOPWORDS`, `tokens()`; `context_runtime.py` — `_context_token_set()``
- **Evidência:** A função `tokens()` usa palavras com pelo menos 2 caracteres e `lower()`, enquanto `_context_token_set()` usa pelo menos 3 caracteres e `casefold()`. A lista de stopwords inclui termos como `isso`, `esse`, `essa`, `qual` e `como`, que também podem ser relevantes para intenção ou referência.
- **Impacto:** Busca lexical e seleção de contexto podem produzir conjuntos de termos diferentes para a mesma entrada; remover palavras referenciais pode ser adequado para ranking lexical, mas inadequado se o mesmo conjunto for reutilizado para resolver referência.
- **Correção proposta:** Definir tokenizadores por finalidade (busca lexical versus referência/contexto), documentar os critérios e evitar compartilhar uma única lista de stopwords sem avaliar cada uso.
- **Teste de validação:** Executar as duas funções sobre o mesmo conjunto de frases e comparar tokens, acentos, pronomes e consultas curtas.

### AIGAR-025 — `needs_memory` e `needs_library` são sinais simplificados
- **Prioridade:** P2 — média
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — retorno de `interpret()``
- **Evidência:** `needs_memory` depende de classes de intenção e de um conjunto limitado de pronomes; `needs_library` é verdadeiro apenas para `concept_basic`, `concept_scoped` e `clinical_case`.
- **Impacto:** Necessidades de memória ou pesquisa fora dessas categorias podem não ser sinalizadas por esse módulo. A consequência real depende de como `conversation_runtime.py` combina esses sinais com `classify_interaction()`.
- **Correção proposta:** Definir um contrato único de roteamento e reconciliar os sinais do LanguageEngine com o classificador de interação; registrar motivo e confiança da decisão.
- **Teste de validação:** Comparar `reading.needs_memory`, `reading.needs_library` e `routing_decision` para casos sociais, continuidade, pesquisa, correção, artefatos e perguntas factuais.

### AIGAR-026 — Campo de ambiguidade não representa todas as ambiguidades identificadas
- **Prioridade:** P2 — média
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — cálculo de `ambiguity``
- **Evidência:** A ambiguidade é derivada principalmente de `len(words) <= 2`, intenção `continuity` ou pergunta sem `topic_candidate`; o valor final usa apenas três estados e um padrão fixo.
- **Impacto:** Frases longas ambíguas podem receber valor baixo, enquanto frases curtas mas claras podem receber um valor relativamente alto.
- **Correção proposta:** Tratar ambiguidade como avaliação separada, com razões observáveis; não interpretar esse número heurístico como probabilidade calibrada.
- **Teste de validação:** Criar pares de frases curtas claras, longas ambíguas, pronomes sem antecedente e perguntas com múltiplas leituras.

### AIGAR-027 — Cache e sessões são variáveis globais locais ao processo
- **Prioridade:** P2 — média
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — `SESSIONS` e `CHUNK_CACHE``
- **Evidência:** Ambos são dicionários globais do módulo. O trecho não demonstra persistência durável nem compartilhamento garantido entre instâncias do Worker.
- **Impacto:** Reinícios ou distribuição entre instâncias podem perder estado local; é preciso separar isso do armazenamento durável de documentos/biblioteca.
- **Correção proposta:** Documentar explicitamente cache efêmero versus armazenamento persistente; mover somente os estados que precisam sobreviver para um backend com contrato de consistência e isolamento.
- **Teste de validação:** Verificar reinício/instância nova e comparar estado de sessão com conteúdo da biblioteca; testar isolamento por session_id.

### AIGAR-028 — Possível corrupção de caracteres acentuados na expressão regular e nas strings
- **Prioridade:** P2 — média
- **Status:** Pendente de confirmação no arquivo original
- **Arquivo/área:** ``language_runtime.py` — regex, STOPWORDS e literais linguísticos`
- **Evidência:** O texto compartilhado contém formas como `Ã©`, `Ã£` e a classe `[a-zA-ZÃ€-Ã¿...]`. Como isso pode ser efeito da codificação da cópia, ainda não está confirmado que os bytes do arquivo original estejam corrompidos.
- **Impacto:** Se o arquivo real contiver esses caracteres, padrões, stopwords e exemplos em português podem não corresponder ao texto normalizado esperado.
- **Correção proposta:** Inspecionar bytes/encoding do arquivo original antes de editar; corrigir para UTF-8 e classes Unicode apropriadas somente se a corrupção for real.
- **Teste de validação:** Executar testes de interpretação com `é`, `são`, `função`, `memória`, `ação`, além de frases sem acento.

### AIGAR-029 — Base declarativa de linguagem é mais abrangente que a execução do runtime
- **Prioridade:** P3 — baixa
- **Status:** Confirmado no código compartilhado
- **Arquivo/área:** ``language_runtime.py` — `LANGUAGE`, `PORTUGUESE`, `LanguageEngine``
- **Evidência:** O arquivo descreve pipeline com sintaxe, referentes, pragmática e contexto, mas `interpret()` aplica regras de padrões, léxico finito e sinais booleanos; não há neste módulo execução explícita de todos os conceitos declarados.
- **Impacto:** A documentação interna pode ser interpretada como capacidade implementada quando parte dela funciona apenas como conhecimento declarativo.
- **Correção proposta:** Adicionar uma matriz rastreável entre regra declarada, função executora, entrada/saída e teste; marcar regras como implementadas, parciais ou apenas documentais.
- **Teste de validação:** Para cada regra declarada, associar teste automatizado ou marcar como não implementada.

### Nota de integração
`LanguageEngine.interpret()` produz sinais heurísticos (`needs_memory`, `needs_library`, `confidence`, `ambiguity`). A fase seguinte deve comparar esses sinais com `classify_interaction()` e com a decisão efetiva de roteamento em `conversation_runtime.py`.

## Atualização — Integração linguagem/contexto em `conversation_runtime.py` (v0.3)
Baseado na saída de `Select-String`; não foram feitas alterações no código do repositório.

### AIGAR-030 — Sinalização de memória do interpretador não controla diretamente a seleção de contexto
- **Prioridade:** P1 — alta
- **Status:** Confirmado no fluxo compartilhado; regra final depende do bridge
- **Arquivo/área:** ``conversation_runtime.py` — integração entre `interpret()`, `interpret_contract()` e `AsymmetricContextManager.resolve()``
- **Evidência:** `LANGUAGE_ENGINE.interpret()` produz `needs_memory`, mas o resolvedor recebe `needs_context=bool(routing_decision['use_memory'])`, valor vindo de `WORKER_CORTEX_BRIDGE.interpret_contract()`. A equivalência entre esses sinais não foi demonstrada pelo trecho.
- **Impacto:** A necessidade de contexto sinalizada pelo interpretador pode ser alterada ou reinterpretada na camada de compatibilidade; sem inspecionar o bridge, não sabemos se os sinais divergem em casos reais.
- **Correção proposta:** Inspecionar `cortex_compat.py` e documentar a transformação de `reading`/`profile` em `routing_decision`. Definir uma fonte de verdade ou regras explícitas de reconciliação.
- **Teste de validação:** Para casos de continuidade, pronomes, correção, pergunta factual e intenção social, comparar `reading.needs_memory`, `routing_decision.use_memory` e o contexto efetivamente selecionado.

### AIGAR-031 — O plano final marca uso de memória apenas quando há turnos selecionados
- **Prioridade:** P2 — média
- **Status:** Confirmado no fluxo compartilhado
- **Arquivo/área:** ``conversation_runtime.py` — atribuição de `plan['use_memory']``
- **Evidência:** Depois de criar o plano, o código define `plan['use_memory'] = bool(routing_decision['use_memory'] and memory_context)`, enquanto a chamada ao resolvedor já recebeu a decisão de roteamento.
- **Impacto:** O campo final representa 'roteamento para memória e contexto selecionado não vazio', não simplesmente a decisão de consultar memória. Isso pode dificultar a distinção entre memória não solicitada e memória solicitada mas indisponível.
- **Correção proposta:** Separar no contrato do plano `memory_requested`, `memory_available` e `memory_used`; preservar o significado de cada campo para telemetria e depuração.
- **Teste de validação:** Testar quatro estados: memória não solicitada; solicitada e encontrada; solicitada sem turnos elegíveis; solicitada mas resolução falhou.

### AIGAR-032 — Resolução de contexto recebe apenas os últimos 40 turnos antes da seleção
- **Prioridade:** P2 — média
- **Status:** Confirmado no trecho; impacto requer teste
- **Arquivo/área:** ``conversation_runtime.py` — `prior_turns[-40:]``
- **Evidência:** O resolvedor não vê turnos anteriores aos últimos 40 nesta chamada, mesmo que a sessão em memória retenha até 80.
- **Impacto:** Um antecedente ou decisão importante fora dessa janela não pode ser escolhido pelo resolvedor nesta etapa, ainda que continue armazenado na sessão.
- **Correção proposta:** Definir estratégia de sumarização/recuperação para referências mais antigas; não aumentar a janela sem medir custo e qualidade.
- **Teste de validação:** Inserir antecedente relevante no turno 1, ultrapassar 40 turnos e avaliar se o sistema pede esclarecimento ou recupera um resumo fiel.

### AIGAR-033 — Estado de memória fica ambíguo quando o roteamento pede memória, mas a seleção retorna vazia
- **Prioridade:** P2 — média
- **Status:** Confirmado no fluxo compartilhado
- **Arquivo/área:** ``conversation_runtime.py` — `context_resolution`, `memory_context` e campos de plano`
- **Evidência:** Se `use_memory` for verdadeiro, mas `memory_context` ficar vazio, a anotação `recent_context_available` não é definida como verdadeira e o plano final grava `use_memory=False`; o resolvedor pode incluir `recent_context_unavailable` em `unresolved_references`.
- **Impacto:** A telemetria pode não distinguir claramente uma falha de recuperação de um caso em que memória não era necessária.
- **Correção proposta:** Usar estados separados para necessidade, tentativa, disponibilidade e resultado da recuperação; preservar `unresolved_references` na resposta e no plano.
- **Teste de validação:** Simular histórico vazio e histórico só com turnos revogados/superseded em um pedido de continuidade.



## Fase 4 — `cortex_compat.py`

| ID | Problema / risco observado | Prioridade | Estado |
|---|---|---:|---|
| AIGAR-034 | `bool(value)` considera strings não vazias como `"false"` verdadeiras nos sinais de roteamento; pode gerar decisões incorretas se os dados não forem booleanos reais. | P1 | Confirmado estaticamente; origem dos tipos precisa ser verificada |
| AIGAR-035 | `confidence` e `uncertainty` são normalizados separadamente; valores fornecidos podem ficar inconsistentes entre si. | P2 | Confirmado estaticamente |
| AIGAR-036 | `scope` e anotações extras são preservados sem validação de tipo/estrutura; isso pode propagar dados malformados a consumidores posteriores. | P2 | Confirmado estaticamente; impacto depende dos consumidores |
| AIGAR-037 | `_bounded_number` precisa de testes com `NaN`, infinito, strings numéricas e objetos não conversíveis para garantir saída finita e previsível. | P2 | Verificação pendente |
| AIGAR-038 | O adaptador fixa `CONTRACT_VERSION = "1"`; não há no trecho mecanismo de negociação/validação da versão canônica. | P2 | Confirmado estaticamente |
| AIGAR-039 | `use_diagnosis=True` pode indicar que o recurso foi selecionado embora `diagnosis_execution` diga `not_connected`; a interface deve separar intenção, roteamento e execução real. | P1 | Confirmado no contrato; apresentação ao usuário ainda precisa ser rastreada |
| AIGAR-040 | A equivalência entre o contrato Worker e o CORTEX canônico não foi demonstrada por testes de conformidade/diferenciais. | P1 | Pendente de teste |


## Fase 5 — association_core.py: achados adicionais

| ID | Achado | Prioridade preliminar | Estado |
|---|---|---|---|
| AIGAR-041 | Assinatura do cache usa tamanho, prefixo e sufixo; mudanças internas do texto podem passar despercebidas e deixar tokens desatualizados. | Alta | Confirmado pela leitura estática |
| AIGAR-042 | Pontuação de relevância é lexical com bônus fixos por origem, não uma avaliação semântica calibrada. | Média | Confirmado pela leitura estática |
| AIGAR-043 | Chunk de `interacoes_aigar` é priorizado como âncora mesmo sem sobreposição lexical. | Média | Confirmado pela leitura estática |
| AIGAR-044 | Fallback de `_excerpt()` pode devolver o início do chunk sem evidência de relevância lexical. | Média | Confirmado pela leitura estática |
| AIGAR-045 | Conversão de `limit` com `int(limit)` pode falhar para entradas inválidas. | Média | Confirmado pela leitura estática |
| AIGAR-046 | `prime()` é chamado em toda execução de `prepare()`; custo/benefício do cache precisa ser medido em teste. | Baixa | Precisa de medição |
| AIGAR-047 | Possível problema de codificação em tokens e termos; o texto colado não comprova que os bytes do arquivo original estejam corrompidos. | Média | Pendente de verificação do arquivo original |

As prioridades são preliminares e não equivalem a falhas demonstradas em produção.


## Fase 6 — test_cognitive_core.py: lacunas de cobertura

| ID | Lacuna | Prioridade preliminar | Estado |
|---|---|---|---|
| AIGAR-048 | Sem teste para alteração interna do chunk que preserve tamanho, prefixo e sufixo, possível causa de cache lexical desatualizado. | Alta | Lacuna confirmada no arquivo de teste fornecido |
| AIGAR-049 | Sem cobertura de `limit` inválido, zero, negativo ou maior que quatro. | Média | Lacuna confirmada |
| AIGAR-050 | Sem cobertura de chunks sem ID, IDs duplicados, chunks vazios ou consultas sem tokens úteis. | Média | Lacuna confirmada |
| AIGAR-051 | Sem teste explícito para âncora irrelevante, empates e determinismo de ordenação. | Média | Lacuna confirmada |
| AIGAR-052 | Sem teste específico do fallback de `_excerpt()` quando não há sobreposição lexical. | Média | Lacuna confirmada |
| AIGAR-053 | Sem teste de integração com os chunks realmente carregados pelo runtime. | Média | Lacuna confirmada neste arquivo; pode haver cobertura noutro lugar |
| AIGAR-054 | Sem teste específico para alteração interna de chunk mantendo tamanho, prefixo e sufixo. | Alta | Lacuna de cobertura confirmada; suíte executada e aprovada em 2026-10-17 |


## Fase 7 — test_cortex_compat.py: lacunas de cobertura

| ID | Lacuna | Prioridade preliminar | Estado |
|---|---|---|---|
| AIGAR-055 | Campos `needs_*` recebidos como strings não são testados; `bool("false")` é verdadeiro e pode ativar rotas indevidas. | Alta | Lacuna confirmada; comportamento é inferido diretamente da semântica Python |
| AIGAR-056 | `NaN` e infinito não são testados em confiança, incerteza e ambiguidade. | Alta | Lacuna confirmada; impacto depende dos valores aceitos a montante |
| AIGAR-057 | Não há teste de coerência quando confiança e incerteza são fornecidas simultaneamente com valores divergentes. | Média | Lacuna confirmada |
| AIGAR-058 | Não há teste de validação de `scope` nem de tamanho/estrutura de anotações extras preservadas. | Média | Lacuna confirmada |
| AIGAR-059 | Não há teste automatizado de compatibilidade de versão com o contrato canônico externo. | Média | Lacuna confirmada neste arquivo |
| AIGAR-060 | A suíte não cobria validação de contrato externo/versão canônica. | Alta | Lacuna de cobertura; os 4 testes atuais da suíte passaram em 2026-10-17 |


## Fase 8 — achados da verificação GitHub somente leitura

| ID | Achado | Prioridade preliminar | Estado |
|---|---|---|---|
| AIGAR-061 | O schema consultado não declara tabela explícita para cartões de memória conversacional; há tabelas de biblioteca, interações, feedback, avaliações e auditoria. | Alta | Confirmado no schema consultado |
| AIGAR-062 | `adaptive_interactions` persiste metadados e snapshot mínimo, não prova persistência do histórico integral da conversa. | Alta | Confirmado no schema; comportamento total depende do runtime |
| AIGAR-063 | Prontidão de storage no código depende de bindings R2 e D1, mas a leitura de código não confirma a configuração real do Worker implantado. | Alta | Pendente de verificação do ambiente |
| AIGAR-064 | Ainda é necessário comparar o restante das operações de `storage_runtime.py` com tabelas e restrições de `schema.sql`. | Média | Pendente |
| AIGAR-065 | A consulta remota não prova que a cópia local usada nos comandos PowerShell tenha o mesmo blob/commit. | Média | Pendente de comparação local/remota |

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


## Fase 12 — resultado dos testes automatizados locais (2026-10-17)

### Resultado confirmado

| Suíte | Aprovados | Falhas/erros | Observação |
|---|---:|---:|---|
| `test_cognitive_core.py` | 3 | 0 | Núcleo cognitivo, seleção e anotação |
| `test_cortex_compat.py` | 4 | 0 | Normalização do contrato e roteamento explícito |
| `test_memory_lab.py` | 5 | 0 | Inicialização, descoberta de documentos e fallback |
| **Total** | **12** | **0** | Execução local reportada em 0,010 s |

### Reclassificação dos registros anteriores

- **AIGAR-054:** atualizar de “resultado desconhecido” para **testes executados e aprovados nesta suíte**. A lacuna de cobertura descrita no próprio item continua válida; o resultado não elimina a ausência de testes adicionais.
- **AIGAR-060:** atualizar de “resultado desconhecido” para **testes executados e aprovados nesta suíte**. As lacunas de cobertura dos casos não testados permanecem.
- O mapa de testes não deve ser interpretado como teste de integração ou teste de implantação: a execução reportada cobre somente os 12 casos listados acima.

Nenhum novo defeito funcional foi reproduzido por essa execução. As lacunas existentes permanecem como lacunas de cobertura ou riscos inferidos, não como falhas demonstradas pelos 12 testes.


## Fase 13 — carregador de chunks da biblioteca

| ID | Achado | Prioridade preliminar | Estado |
|---|---|---|---|
| AIGAR-084 | `load_chunk_text()` aceita texto sem validar SHA-256/comprimento contra os metadados do índice. | Alta (P1) | Confirmado por leitura estática; não reproduzido como falha de conteúdo |
| AIGAR-085 | As três suítes executadas não cobrem explicitamente loader, checksum, fallback Raw/Contents API, texto vazio ou falha das duas URLs. | Alta (P1) | Lacuna de cobertura identificada; procurar outros testes de integração ainda é necessário |
| AIGAR-088 | `CHUNK_CACHE` é consultado pela chave `id` sem versão/origem/checksum; IDs reutilizados poderiam servir texto obsoleto ou de outra fonte. | Alta (P1) | Risco estrutural confirmado por leitura; colisão concreta não demonstrada |
| AIGAR-089 | `chunk_urls()` usa `entry["cache_file"]` diretamente; metadado ausente pode causar exceção antes do fallback de rede. | Média (P2) | Inferência direta do código; não reproduzida |

**Nota de interpretação:** existem duas rotas de recuperação (GitHub Raw e Contents API), e o código continua após respostas HTTP de erro/exceções. Portanto, não há base para declarar o carregador inteiramente quebrado. A ausência de checksum em tempo de execução é distinta da validação local 73/73 realizada anteriormente.

## Fase 14 — confirmação de versão e lacuna de cobertura

- **AIGAR-085 — atualização de evidência:** confirmada a ausência de referências diretas aos termos pesquisados (`load_chunk_text`, `chunk_urls`, `library_search`, `checksum`, `SHA-256`, `sha256`, `INDEX_URLS`, `CHUNK_CACHE`) nos três arquivos `test_*.py` localizados em `AIGAR_CLOUDFLARE`. A busca não cobre testes indiretos nem arquivos de teste fora dessa pasta; por isso, a lacuna é confirmada apenas para o escopo pesquisado.
- **Versão auditada:** o hash local de `library_runtime.py` é igual ao blob de `main` (`5f180853d26b1551c840d7c5098a667a2a751fe4`), e `git status --short` não reportou alteração para esse arquivo.
- **Estado:** nenhuma falha de runtime foi reproduzida; permanece uma lacuna de cobertura e um risco estático de ausência de validação de checksum no carregador.
- **Próximo passo:** verificar workflows e configuração de testes fora da pasta do Worker antes de concluir que não há cobertura adicional no repositório.

## Fase 15 — cobertura configurada pelos workflows

| ID | Achado | Prioridade preliminar | Estado |
|---|---|---|---|
| AIGAR-090 | Workflow do Worker executa os três testes existentes, mas não inclui teste dedicado para `chunk_urls()`/`load_chunk_text()`, checksum ou fallback de recuperação de chunks. | Alta (P1) | Confirmado por leitura do workflow; risco de cobertura, não falha funcional reproduzida |
| AIGAR-091 | `pyproject.toml` declara `requires-python >=3.13`, enquanto `.github/workflows/aigar-cognitive-core.yml` configura Python 3.12. | Média (P2) | Divergência de configuração confirmada; impacto não demonstrado |

**Contexto:** o workflow `aigar-runtime-validation.yml` testa os módulos do runtime local/retriever, não o loader da biblioteca do pacote Worker. O workflow `aigar-cognitive-core.yml` compila o pacote Worker, roda os três arquivos de teste e verifica a sintaxe JavaScript inline. O README descreve o pacote como candidato de migração e informa que editar o repositório não altera o Worker ativo.

**Próximo passo:** consultar os estados recentes de CI; depois, propor testes unitários com respostas HTTP simuladas para o loader. Não modificar código nem configuração nesta fase.

## Recalibração do progresso da auditoria — 17/10/2026

O percentual anterior de 66% permaneceu estático enquanto novas fases eram adicionadas, sem um denominador definido. Ele foi substituído por uma estimativa estruturada baseada em 20 pacotes de trabalho.

- **12 pacotes concluídos:** 12 pontos.
- **4 pacotes parciais:** 2 pontos (0,5 cada).
- **4 pacotes pendentes:** 0 ponto.
- **Total:** 14/20 = **70% da auditoria documental/estática**.

Os 70% não significam que o sistema esteja 70% funcional ou pronto para produção. O percentual mede a execução do plano de auditoria definido neste documento.

### Pendências que impedem o fechamento
1. Consultar resultados recentes dos workflows de CI.
2. Criar/rodar testes isolados do loader para Raw OK, Raw falha + Contents OK, ambas falham, conteúdo vazio, checksum divergente e metadado `cache_file` ausente.
3. Testar ponta a ponta a recuperação de contexto/memória entre instâncias, se a arquitetura pretendida suportar esse comportamento.
4. Verificar o Worker efetivamente implantado, sem presumir equivalência com `main`.
5. Consolidar os documentos e ordenar os achados por impacto, evidência e dependências.

### Métricas independentes
- Suítes existentes: **12/12 aprovados** na execução local informada.
- Chunks locais: **73/73 íntegros** após normalização de finais de linha.
- Falhas funcionais reproduzidas nesta etapa: **nenhuma**. Existem riscos estáticos e lacunas de teste; não devem ser descritos como defeitos reproduzidos.
- Alterações de código, push e deploy: **nenhuma**.
\n\n## Fase 16 — evidências de produção obtidas somente em leitura (2026-10-17)\n\n| ID | Achado | Prioridade preliminar | Estado |\n|---|---|---|---|\n| AIGAR-092 | Worker `aigar-api` publicado aponta para o commit `0b6a19289543dc64bdc4cf02c7953491b3433651`; a branch `main` atual (`4c09801d07f4ed15493985bdc0ed8683f7956e7b`) está 78 commits à frente. | Alta (P1) | Divergência de revisão confirmada por metadados da Cloudflare/GitHub; não prova por si só que o Worker esteja quebrado. |\n| AIGAR-093 | D1 tem 3 registros em `documents` e nenhum em `document_chunks`; status dos documentos: 2 `uploaded`, 1 `error`. O bucket R2 existe e a listagem apresentou três PDFs originais. | Alta (P1) | Estado confirmado por consultas read-only; precisa investigar o pipeline de conversão/chunking. Não foram feitas gravações. |\n| AIGAR-094 | Não há tabela dedicada de Memory Cards persistentes no schema D1 consultado. | Alta (P1) para a meta de memória entre sessões | Limite arquitetural confirmado e já indicado como capacidade adiada no README; não classificar como regressão inesperada. |\n\n**Verificações positivas:** `PRAGMA quick_check` do D1 retornou `ok`; as tabelas adaptativas exigidas por `adaptive_schema_ready()` existem; os bindings de AI, D1, R2 e Workflow estão configurados no Worker publicado.\n\n**Limites:** endpoints HTTP públicos não puderam ser lidos pelo canal de navegação disponível. A resposta da API de conteúdo do Worker foi truncada para módulos grandes, portanto não foi possível confirmar igualdade byte a byte entre todo o código publicado e `main`. A configuração/bindings nominais coincidem, mas a versão publicada está atrás da `main`.\n