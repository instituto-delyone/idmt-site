# Auditoria estática do AIGAR_SOURCE_MANIFEST_v1

**Branch:** `neurocognitive-migration`  
**Escopo:** conferir os caminhos declarados em `association_network/AIGAR_SOURCE_MANIFEST_v1.json` contra a árvore Git da branch.  
**Método:** comparação literal dos caminhos declarados com a árvore recursiva, sem executar código.

## Resultado por entrada declarada

| Papel | Caminho declarado | Resultado na árvore | Tratamento |
|---|---|---|---|
| language_mother | `Engines/Aurora/Bibliotecas/Linguagem-materna/00_texto_mae.md` | Existe | Preservar como fonte canônica |
| human_intents | `Engines/Aurora/Bibliotecas/Linguagem-materna/01_intencoes_humanas.md` | Existe | Preservar como fonte canônica |
| response_depth | `Engines/Aurora/Bibliotecas/Linguagem-materna/02_profundidade_resposta.md` | Existe | Preservar como fonte canônica |
| ambiguity_uncertainty | `Engines/Aurora/Bibliotecas/Linguagem-materna/03_ambiguidade_incerteza.md` | Existe | Preservar como fonte canônica |
| insertion_zone | `Engines/Aurora/Bibliotecas/Linguagem-materna/04_area_de_insercao.md` | Existe | Preservar como fonte canônica |
| aigar_base_memory | `Engines/Aurora/AIGAR-engine/MC_BASE_AIGAR_v1.1.yaml` | Existe | Preservar fonte de memória histórica |
| aurora_principles | `Engines/Aurora/AIGAR-engine/MC_PRINCIPIOS_AURORA.yaml` | Existe | Preservar fonte de princípios |
| reasoning | `Engines/Aurora/AIGAR-engine/raciocinio_rapido_hibrido.txt` | Existe | Preservar fonte de raciocínio |
| aigar_manifest | `Engines/Aurora/Aigar_manifest.json` | Existe | Preservar manifesto |
| historical_memory_fragments | `aigar-c-2/fragments-history/` | Existe | Preservar artefatos históricos |
| conversation_reconstruction | `aigar-c-2/conversational-engine/AIGAR_AURORA_RECONSTRUCAO_LINGUAGEM_MEMORIA_v1_0.html` | Existe | Preservar documento de reconstrução |
| diagnosis_runtime | `docs/Js/engine.js` | **Não encontrado** | Destino/fonte operacional não confirmado |
| diagnosis_knowledge | `docs/knowledge_base/` | **Não encontrado** | Pasta/corpus no caminho declarado não confirmado |

## Investigação complementar do Diagnosis

Na árvore consultada também não existem caminhos sob `docs/Js/` nem sob `docs/knowledge_base/`, e não foi encontrado um arquivo chamado `engine.js` ou uma pasta chamada `knowledge_base` no snapshot consultado.

Existe a aplicação/página em `docs/pesquisas/Diagnosis/Index.html` e sua contraparte em `docs/pesquisas/Diagnosis/index.html`; também há cópias sob `pesquisas/Diagnosis/`. Esses itens **não foram automaticamente declarados equivalentes** ao antigo `docs/Js/engine.js` ou à base clínica ausente. A ligação exige comparação do conteúdo e dos consumidores. O adaptador `aigar-c-2/CORTEX/reasoning_engine/diagnosis.py` é o adaptador atualmente presente; retorna estado `missing` e não simula achados clínicos. A referência anterior `aigar-c-2/Diagnosis/diagnosis.py` não existe na árvore atual.

## Decisão segura

1. Não substituir os dois caminhos faltantes por candidatos apenas pelo nome.
2. Manter o manifesto original intacto como registro da origem declarada.
3. Resolver a proveniência do motor e da base Diagnosis com documentação/conteúdo histórico antes de integrar o motor real.
4. Manter esse resultado no inventário e no changelog.

Esta é uma auditoria de caminhos, não validação da aplicação clínica. Não foram executados testes, não houve merge ou deploy e nenhum arquivo do Cloudflare Worker foi alterado.


## Esclarecimento de escopo — 2026-10-10

As referências históricas ao motor e à base clínica do Diagnosis pertencem a um projeto mantido em repositório separado. Elas não são dependências locais do AIGAR-C. Este relatório preserva o registro histórico; nenhuma pasta ou arquivo do Diagnosis foi alterado. O manifesto ativo de fontes canônicas não deve tratar esses caminhos externos como fontes do AIGAR-C.
