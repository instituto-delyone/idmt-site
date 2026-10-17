# AIGAR-C2 — Guia de estado, execução e restrições

> Documento de orientação operacional. Reflete a documentação encontrada na branch `neurocognitive-migration`; não é uma certificação de que todos os componentes executam corretamente.

## 1. O que é este diretório

`aigar-c-2/` contém a reconstrução do AIGAR-C, incluindo um runtime Python local, módulos compartilhados em `CORTEX/`, recuperação e ingestão documental em pacotes separados, a interface MVP e uma implementação Cloudflare Worker separada.

## 2. Runtime local

O entry point documentado é `AIGAR_RUNTIME.main:app`. A partir deste diretório, depois de conferir a versão e as dependências:

```powershell
python -m AIGAR_RUNTIME.main
```

Ou, como API local:

```powershell
python -m pip install -r AIGAR_RUNTIME/requirements.txt
python -m uvicorn AIGAR_RUNTIME.main:app --host 127.0.0.1 --port 8000
```

Endpoints documentados:
- `GET /health`: sinal de estado do processo; não prova que todas as integrações estão prontas.
- `POST /perguntar`: entrada conversacional. Exemplo de JSON: `{"input":"Olá, AIGAR","session_id":"teste-local"}`.

Não instale dependências nem execute o runtime até confirmar que a cópia local está sincronizada e que as alterações locais foram preservadas.

## 3. Arquitetura observada

Fluxo documentado: entrada → interpretação de linguagem → estado de sessão → memória/biblioteca/adapter Diagnosis (quando selecionados) → planejamento → Aurora → resposta.

- Contratos compartilhados: `CORTEX/thalamus/models.py`.
- Entrada operacional: `AIGAR_RUNTIME/main.py`.
- Linguagem: `CORTEX/language/`.
- Estado de sessão e recall: `CORTEX/memory/`.
- Adapter documental: `CORTEX/engram/`, mantendo `knowledge_retrieval/` independente.
- Pipeline documental: `knowledge_encoding/`.
- Planejamento e apresentação: `CORTEX/prefrontal/`.
- Interface MVP: `aigar_ui_chat_mvp/` e arquivos associados.

A presença de um módulo, contrato ou placeholder não prova que a capacidade especializada esteja implementada.

## 4. Limitações funcionais registradas

1. **Memória persistente:** o recall documentado recupera turnos da sessão; o Memory Card persistente ainda não está conectado ao runtime local.
2. **Diagnosis:** o adapter declara a fronteira de integração, mas o motor clínico especializado pertence a outro projeto/repositório e não está conectado aqui.
3. **Linguagem:** o interpretador ativo é descrito como determinístico/heurístico, não como parser linguístico completo.
4. **Estado:** a memória de trabalho é mantida no processo e não constitui persistência entre reinicializações.
5. **Health check:** `/health` sinaliza estado do processo; não valida por si só banco, biblioteca, memória ou outros serviços.
6. **Placeholders:** documentação de intenção não deve ser apresentada como implementação operacional.

Esses pontos não são bloqueios éticos nem proibições permanentes. São lacunas técnicas que precisam ser implementadas e testadas.

## 5. Restrições de migração encontradas na documentação

Os documentos `CORTEX/README.md`, `CORTEX/prefrontal/DECISIONS.md` e `CORTEX/prefrontal/ROADMAP.md` registram estas regras de trabalho para a fase de migração:

- Manter as alterações na branch `neurocognitive-migration`; não fazer merge nem deploy durante esta fase.
- Preservar `AIGAR_RUNTIME/main.py` como entry point operacional.
- Usar `CORTEX/thalamus/models.py` como fonte canônica de contratos compartilhados.
- Manter `knowledge_retrieval/` e `knowledge_encoding/` como pacotes independentes.
- Preservar artefatos históricos até revisar consumidores e equivalência.
- Adiar a execução dos testes até concluir a auditoria de imports, caminhos de dados, configurações e referências.
- Não alterar arquivos, símbolos, configurações, bindings, chaves JSON ou workflows em `AIGAR_CLOUDFLARE/` durante esta fase.
- Não inventar percentuais globais de progresso sem definir o conjunto de arquivos-alvo.

**Como interpretar essas regras:** são guardrails documentados para a fase de migração, não necessariamente restrições permanentes do produto. Não removê-las automaticamente. Para retomar a operação, primeiro separar a reconstrução local da mudança do Worker de produção, revisar o escopo e registrar uma decisão explícita sobre quais regras deixam de valer.

## 6. Plano seguro para retomar

1. Conferir a branch local, o remoto e o estado do Git; preservar alterações não commitadas.
2. Comparar `main` e `neurocognitive-migration` e escolher conscientemente a base de trabalho.
3. Fechar a auditoria de imports, arquivos de dados, configurações, requirements e comandos.
4. Instalar apenas as dependências necessárias em ambiente isolado.
5. Executar os testes locais e registrar os resultados reais, inclusive falhas.
6. Validar `/health` e `/perguntar` localmente.
7. Implementar e testar a persistência de Memory Cards como tarefa própria.
8. Tratar o Cloudflare Worker numa etapa separada, após revisar contratos, bindings e rotas. Nenhum deploy é realizado por este documento.

## 7. Estado da documentação

Este README resume os limites descritos nos documentos de arquitetura e migração. A inspeção documental, por si só, não prova que o runtime passe nos testes nem que os bindings do Worker estejam configurados na conta Cloudflare.
