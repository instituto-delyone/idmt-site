# AIGAR — Matriz de Falhas Referenciada ao Mapa de Funcionamento

**Versão:** 1.0  
**Data:** 17 de outubro de 2026  
**Documento relacionado:** `AIGAR_Mapa_Organizacional_de_Funcionamento_v1.0_2026-10-17.docx`  
**Finalidade:** permitir que cada problema seja rastreado até o fluxo arquitetural correspondente e ordenar a investigação sem corrigir por suposição.

## Regras
- Os IDs AIGAR são mantidos do registro anterior; não significam que a falha foi reproduzida no GitHub Pages.
- Prioridade e descrição detalhada continuam no `AIGAR_Registro_de_Problemas_v0.1.md` original.
- “Investigar” não significa “corrigir imediatamente”. Primeiro reproduzir, registrar evidência e avaliar impacto.
- Mxx refere-se às seções do mapa v1.0; a numeração de subseções deve ser usada nos registros de teste.

## Ordem sugerida para a Fase 2
1. **Caminho de pergunta e resposta** — M02, M05, M06, M13.1.
2. **Recuperação de conhecimento/fonte** — M08, M13.1, AIGAR-006, AIGAR-010, AIGAR-025.
3. **Contexto dentro da conversa** — M06, M07, M13.2–M13.3, AIGAR-003, AIGAR-012–AIGAR-018, AIGAR-022, AIGAR-030–AIGAR-033.
4. **Profundidade, intenção e fidelidade** — M07, M13.4–M13.5, AIGAR-017, AIGAR-019–AIGAR-021, AIGAR-029.
5. **Persistência entre sessões** — M09, M13.6, AIGAR-001, AIGAR-002, AIGAR-004, AIGAR-027.
6. **Cache/fallback e interface** — M04, M08, M13.7, AIGAR-007, AIGAR-008, AIGAR-010, AIGAR-011.
7. **Pipeline documental/armazenamento** — M08, M10, M11; testar em ambiente controlado antes de gravar dados de produção.
8. **Segurança/admin e divergência de publicação** — M10, M11, M14; sem tentativa de alteração/deploy sem autorização.

## Índice de rastreabilidade

| ID | Problema resumido | Seções do mapa | Próxima verificação sugerida |
|---|---|---|---|
| AIGAR-001 | Persistência de conversa entre instâncias | M06, M09, M13.6 | Persistência conversacional entre instâncias; teste de recarga/nova sessão. |
| AIGAR-002 | Memory cards persistentes não demonstrados como capacidade ativa | M09, M14 | Memory Cards persistentes não demonstrados; confirmar arquitetura e armazenamento. |
| AIGAR-003 | Seleção de contexto assimétrico | M07, M13.2–M13.3 | Seleção de contexto assimétrico; testes de referente, continuidade e mudança de tópico. |
| AIGAR-004 | Limite de histórico em memória | M06, M07, M13.6 | Janela de histórico em memória limitada; avaliar impacto e semântica. |
| AIGAR-005 | Limites de sessão e validação de entrada | M06, M13 | Validação/limites de entrada; testar apenas se o comportamento da interface indicar necessidade. |
| AIGAR-006 | Boot da biblioteca e matriz textual | M04, M08, M13.1 | Boot e matriz; já há evidência inicial, não repetir sem sinal de falha. |
| AIGAR-007 | Limpeza da interface não equivale a apagar dados persistidos | M04, M10 | Limpeza visual não equivale a exclusão de dados persistidos. |
| AIGAR-008 | Cache local do boot | M04, M08, M13.7 | Cache de bootstrap pode servir estado antigo; testar quando houver evidência. |
| AIGAR-009 | Divergência entre fonte local e Worker implantado | M11, M14 | GitHub/main e Worker implantado não estão comprovados como equivalentes; não fazer deploy. |
| AIGAR-010 | Erros silenciosos e fallbacks | M06, M08, M13 | Erros capturados/fallbacks podem ocultar falha de recuperação; observar resposta e rede. |
| AIGAR-011 | Codificação de caracteres | M04, M07 | Codificação de caracteres; comparar arquivo bruto, página publicada e payload. |
| AIGAR-012 | Sinal de referência não identifica referências linguísticas | M07, M13.2 | Sinal de referência não identifica adequadamente referências linguísticas. |
| AIGAR-013 | Decisões ativas não são extraídas pelo resolvedor | M07, M13.2–M13.3 | Decisões ativas não extraídas pelo resolvedor; testar seguimentos dependentes de contexto. |
| AIGAR-014 | Status de contexto é comparado de forma estritamente literal | M07 | Comparação literal de status de contexto; confirmar impacto por testes. |
| AIGAR-015 | Sinal de contexto fixado depende de estrutura de metadados não validada aqui | M07 | Metadados exigidos para contexto fixado ainda não validados. |
| AIGAR-016 | Regex de tokenização pode ter problema de codificação de caracteres acentuados | M07, M04 | Tokenização/regex de acentos; confirmar se corrupção é real ou artefato de cópia. |
| AIGAR-017 | Revisão do plano pode sobrescrever a estratégia de resposta | M07, M13.4 | Revisão do plano pode sobrescrever estratégia; comparar profundidade solicitada e resultado. |
| AIGAR-018 | Normalização de pontuação e metadados pode ser mais robusta | M07 | Normalização de pontuação/metadados; validar casos concretos. |
| AIGAR-019 | Heurísticas de intenção podem produzir classificações concorrentes ou prematuras | M07, M13.1, M13.4 | Heurísticas de intenção podem conflitar; registrar métricas e comportamento. |
| AIGAR-020 | Correspondência por substring em várias categorias | M07 | Correspondência por substring pode gerar falsos positivos. |
| AIGAR-021 | Profundidade solicitada não corresponde necessariamente ao vocabulário configurado | M07, M13.4 | Profundidade solicitada pode não corresponder ao vocabulário/modo efetivo. |
| AIGAR-022 | Resolução de referentes está descrita na base, mas não é executada integralmente por este interpretador | M07, M13.2 | Resolução de referentes declarada mas não executada integralmente pelo interpretador. |
| AIGAR-023 | Detecção de verbos e sujeito é baseada em listas/posições | M07 | Detecção de verbos/sujeito baseada em listas/posições. |
| AIGAR-024 | STOPWORDS e tokenização divergem entre módulos | M07 | STOPWORDS/tokenização divergem entre módulos. |
| AIGAR-025 | `needs_memory` e `needs_library` são sinais simplificados | M07, M08, M13.1 | `needs_memory`/`needs_library` são sinais simplificados; conferir recuperação real. |
| AIGAR-026 | Campo de ambiguidade não representa todas as ambiguidades identificadas | M07 | Campo de ambiguidade não representa todas as ambiguidades identificadas. |
| AIGAR-027 | Cache e sessões são variáveis globais locais ao processo | M06, M09, M13.6 | Cache e sessões em variáveis globais do processo; não presumir persistência. |
| AIGAR-028 | Possível corrupção de caracteres acentuados na expressão regular e nas strings | M04, M07 | Possível corrupção de acentos em regex/strings. |
| AIGAR-029 | Base declarativa de linguagem é mais abrangente que a execução do runtime | M07, M14 | Base declarativa de linguagem mais ampla que execução do runtime. |
| AIGAR-030 | Sinalização de memória do interpretador não controla diretamente a seleção de contexto | M07, M13.2–M13.3 | Sinal de memória do interpretador não controla diretamente seleção de contexto. |
| AIGAR-031 | O plano final marca uso de memória apenas quando há turnos selecionados | M07, M13.2 | Plano marca uso de memória apenas se turnos foram selecionados. |
| AIGAR-032 | Resolução de contexto recebe apenas os últimos 40 turnos antes da seleção | M06, M07 | Resolvedor recebe até 40 turnos anteriores. |
| AIGAR-033 | Estado de memória fica ambíguo quando o roteamento pede memória, mas a seleção retorna vazia | M07, M13.2–M13.3 | Estado ambíguo quando roteamento pede memória mas seleção retorna vazia. |

## Evidências de base e limites

- Testes locais relatados: 12/12 aprovados (3 suítes). Isso não é teste ponta a ponta.
- Boot das bibliotecas e boot da Text Matrix são evidências separadas.
- Checkpoint relata 73/73 hashes/comprimentos locais após normalização CRLF→LF; não prova integridade do Worker publicado.
- Checkpoint relata divergência entre Worker publicado e `main`; não presumir equivalência e não fazer deploy automaticamente.
- D1 `document_chunks = 0` e R2 com três PDFs originais foram reportados; pipeline de chunking exige investigação.
