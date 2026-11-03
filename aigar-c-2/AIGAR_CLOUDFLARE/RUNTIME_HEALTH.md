# AIGAR Runtime Health — primeira entrega

## Objetivo
Acrescentar telemetria operacional ao endpoint existente `GET /health`, sem executar boot, chamadas de rede ou mutações durante a consulta.

## O que passa a ser informado
- Estado do Worker.
- Quantidade de índices em cache e idade do cache.
- Quantidade de chunks carregados pelo boot e idade do cache.
- Progresso da Text Matrix (documentos carregados / esperados).
- Quantidade de chunks no cache linguístico.
- Presença dos bindings R2 e D1.
- Estado observável do Memory Lab.

O bloco novo é `runtime_health`, com `schema_version`, `status`, `observed_at_epoch`, `components` e `resources`.

## Estados
- `READY`: componente observado como pronto.
- `NOT_INITIALIZED`: ainda não há evidência de inicialização.
- Estado global `READY`, `DEGRADED` ou `INITIALIZING`.

## Limites deliberados
O runtime desta aplicação não expõe uma métrica confiável de RSS/memória real do isolate. Por isso `resources.isolate_memory.value` permanece `null` e `status=not_exposed`. Contagens de chunks não são bytes de RAM. Não inferir capacidade disponível a partir dessas contagens.

A consulta é passiva: não dispara `boot_library()`, `boot_text_matrix()`, `MEMORY_LAB.initialize()` nem acessa R2/D1 para testar leitura. Ela apenas observa caches e bindings já presentes no isolate.

## Compatibilidade
O campo legado `status: online`, os campos `checks`, `features` e as rotas existentes são preservados. A telemetria é adicionada sem substituir o contrato anterior.

## Testes
Executar no diretório do Worker:
```bash
python -m unittest test_runtime_health.py
```

## Fora do escopo desta entrega
- Não altera produção nem configurações Cloudflare.
- Não mede RSS real.
- Não cria armazenamento persistente de telemetria.
- Não modifica a política de boot, seleção ou recuperação de chunks.
