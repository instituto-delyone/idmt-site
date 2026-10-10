# Evolução do AIGAR-C

Este histórico separa alterações encontradas na branch de capacidades ainda não validadas em execução.

## Marco 1 — Estrutura CORTEX e migrações iniciais

Registrados no inventário os movimentos MIG-001 a MIG-012 para memória de trabalho, continuidade, controlador pré-frontal, adaptador/interpretador de linguagem, dados linguísticos, contratos compartilhados, Aurora, adaptador de recuperação, interpretador histórico e fronteira Diagnosis. Cada movimento possui SHAs de commits de destino/remoção no inventário.

## Marco 2 — Contratos compartilhados

`CORTEX/thalamus/models.py` tornou-se a fonte canônica de:
- leitura e decisão de roteamento;
- plano de raciocínio;
- estado conversacional e rastros de proveniência;
- request/response do runtime e envelope sensorial;
- envelopes de recuperação de memória e biblioteca;
- envelopes de Diagnosis e Aurora.

A existência desses modelos não garante conexão com motores especializados.

## Marco 3 — Orquestração do runtime

`AIGAR_RUNTIME/main.py` preserva a API e o entry point, mas importa adaptadores dos destinos CORTEX. O fluxo observado é entrada textual, interpretação, roteamento, recuperação opcional, planejamento, apresentação e resposta com fontes.

## Marco 4 — Estado explícito por subsistema

- Memória: estado e recall são tipados, mas limitados à sessão.
- Biblioteca: o adaptador Engram usa o pacote independente `knowledge_retrieval/`.
- Diagnosis: fronteira tipada presente; conexão do motor real ausente.
- Aurora: solicitação e resposta tipadas, com modos de apresentação preservados.
- SARA: status de processo presente; prontidão externa não verificada.
- Sensory: envelope de texto presente; multimodalidade não implementada.

## Marco 5 — MIG-013: teste linguístico

O teste do interpretador foi movido para `CORTEX/language/test_interpreter.py` e sua importação foi atualizada. O arquivo de destino foi confirmado antes da remoção da origem `language_network/test_interpreter.py`. A configuração `AIGAR_PHASES/phases.json` também foi alinhada aos módulos ativos.

## O que ainda não é um marco concluído

- Nenhum teste automatizado foi executado nesta fase.
- O runtime não foi declarado funcional/validado.
- Memory Card persistente e motor Diagnosis permanecem desconectados.
- O motor geral `reasoning_engine`, o ciclo `default_mode_network`, o bridge de serviços e a integração da UI em `occipital` continuam não implementados ou não definidos.
- Nenhum merge/deploy foi realizado; Cloudflare Worker permanece intocado.
