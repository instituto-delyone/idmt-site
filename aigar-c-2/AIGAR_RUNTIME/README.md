# AIGAR Neurocognitive Runtime — foundation v0.3

Runtime conversacional modular para reconstrução funcional do AIGAR-C. O entry point operacional permanece em AIGAR_RUNTIME/main.py; os módulos compartilhados e seus contratos canônicos estão organizados em CORTEX/.

## Princípio

ENTRADA → LINGUAGEM → ESTADO → MEMÓRIA / BIBLIOTECA / DIAGNOSIS → PLANEJAMENTO → AURORA → SAÍDA

O runtime orquestra os componentes especializados; não absorve a lógica interna de motores separados.

## Contratos

- Contratos compartilhados: CORTEX/thalamus/models.py.
- Interpretador e dados linguísticos: CORTEX/language/.
- Estado e continuidade de sessão: CORTEX/memory/.
- Adapter de recuperação: CORTEX/engram/knowledge_retrieval.py; pacote knowledge_retrieval/ permanece separado.
- Planejamento e apresentação: CORTEX/prefrontal/.
- Adapter clínico: CORTEX/reasoning_engine/diagnosis.py; o motor especializado ainda precisa de integração explícita.

## Execução prevista

A partir do diretório aigar-c-2/:

    python -m AIGAR_RUNTIME.main

Ou como API:

    pip install -r AIGAR_RUNTIME/requirements.txt
    uvicorn AIGAR_RUNTIME.main:app --host 127.0.0.1 --port 8000

Endpoint: POST /perguntar

Exemplo de corpo JSON:

    {"input":"O que é insuficiência adrenal?","session_id":"demo"}

## Regra de evidência

O runtime usa SourceTrace para diferenciar estados confirmed, inferred, proposed e missing. Quando um componente especializado ainda não está conectado, o adaptador deve declarar essa limitação em vez de simular integração.

## Regra de migração

- CORTEX/thalamus/models.py é a fonte canônica dos contratos compartilhados.
- Os diretórios e responsabilidades documentados em CORTEX/README.md são provisoriamente imutáveis; mudanças futuras exigem decisão explícita e registro.
- Os testes importam RuntimeRequest do contrato canônico. Permanecem sem execução manual nesta fase.
- Não fazer merge/deploy durante esta fase e não alterar o Cloudflare Worker.
