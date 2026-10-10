# AIGAR Neurocognitive Runtime — foundation v0.1

Runtime conversacional mínimo e modular para reconstrução funcional do AIGAR.

## Princípio

O runtime não substitui os motores históricos. Ele os orquestra:

`ENTRADA → LINGUAGEM → ESTADO → MEMÓRIA/CSI/BIBLIOTECA/DIAGNOSIS → RACIOCÍNIO → AURORA → SAÍDA`

O runtime foi desenhado para ficar fora de `docs/`, porque `docs/` é área de deploy do site.

## Objetivos desta primeira versão

- transformar a Linguagem Materna em um contrato executável;
- manter estado explícito da conversa;
- oferecer adaptadores seguros para memória, biblioteca e Diagnosis;
- manter raciocínio separado da geração textual;
- permitir que Aurora module a resposta sem assumir o papel dos motores especializados;
- funcionar mesmo quando um componente ainda não estiver conectado.

## Regra de evidência

O runtime distingue:
- **confirmed** — comportamento/estrutura sustentados pelo repositório;
- **inferred** — interpretação de integração;
- **proposed** — implementação nova.

Esta versão é deliberadamente conservadora: quando um motor não está conectado, o runtime não finge que está.

## Execução

```bash
cd aigar-c-2
python -m AIGAR_RUNTIME.main
```

Ou como API:

```bash
pip install -r requirements.txt
uvicorn AIGAR_RUNTIME.main:app --reload
```

Endpoint:

`POST /perguntar`

Body:

```json
{"input":"O que é insuficiência adrenal?","session_id":"demo"}
```

## Próxima etapa

Conectar os adaptadores aos componentes reais existentes no repositório e, depois, criar o JSON mestre de mapeamento do ecossistema. Nenhum arquivo de `docs/` é necessário para isso.


## Migração neurocognitiva — primeira etapa

- `reasoning.py` → `prefrontal_controller.py`
- `ReasoningEngine` → `PrefrontalController`
- Importação do runtime atualizada em `main.py`.
- O trace de origem `reasoning` é mantido para não quebrar o contrato de resposta.
- Esta mudança foi isolada na branch `neurocognitive-migration`; não altera a produção.

- `memory.py` → `hippocampal_memory.py`; `MemoryAdapter` → `HippocampalMemoryAdapter` (the current implementation still only provides session-local continuity; persistent recall remains unwired).
