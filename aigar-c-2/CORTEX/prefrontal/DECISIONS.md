# Decisões arquiteturais

Este documento registra decisões sustentadas pela árvore e pelos contratos presentes. Propostas futuras permanecem separadas.

## D-001 — Branch isolada
**Decisão:** manter as alterações em `neurocognitive-migration`; não fazer merge nem deploy durante a fase de migração.  
**Justificativa:** preservar produção e permitir revisão por etapa.

## D-002 — Contratos canônicos
**Decisão:** `CORTEX/thalamus/models.py` é a fonte canônica dos contratos compartilhados do runtime.  
**Justificativa:** evita modelos duplicados com semântica divergente.

## D-003 — Entry point preservado
**Decisão:** manter `AIGAR_RUNTIME/main.py` e `AIGAR_RUNTIME.main:app` como ponto de entrada operacional durante a reorganização.  
**Justificativa:** reduz risco de quebra de comandos de execução enquanto os módulos migram.

## D-004 — Recuperação documental independente
**Decisão:** manter `knowledge_retrieval/` e `knowledge_encoding/` como pacotes independentes; CORTEX usa adaptadores.  
**Justificativa:** preserva índices, cache, fontes e pipeline de ingestão sem renomeação anatômica indevida.

## D-005 — Diagnosis como fronteira separada
**Decisão:** manter `Diagnosis/diagnosis.py` separado e utilizar `DiagnosisRequest`/`DiagnosisResult`.  
**Justificativa:** o adaptador atual ainda não conecta o motor clínico e deve declarar `missing`, em vez de fabricar achados.

## D-006 — Persistência não presumida
**Decisão:** não descrever o recall atual como memória de longo prazo.  
**Justificativa:** `HippocampalMemoryAdapter` recupera apenas turnos da sessão; Memory Card persistente não está ligado.

## D-007 — Placeholders são explicitamente não funcionais
**Decisão:** arquivos `PLACEHOLDER.md` documentam lacunas, não subsistemas prontos.  
**Justificativa:** separar estrutura arquitetural de implementação existente.

## D-008 — Integridade histórica
**Decisão:** preservar o interpretador legado `CORTEX/thalamus/linguistic_interpreter.py` e artefatos históricos até que consumidores e equivalência tenham sido revisados.  
**Justificativa:** suas regras e contrato diferem do interpretador ativo.

## D-009 — Gate de testes
**Decisão:** não executar testes até finalizar movimentos/renomeações e auditoria de referências de código, dados, manifestos, comandos e documentação operacional.  
**Justificativa:** separar reconstrução estrutural de validação comportamental, conforme o plano acordado.

## D-010 — Cloudflare Worker fora do escopo atual
**Decisão:** não alterar arquivos, nomes, símbolos, configurações, bindings, chaves JSON ou workflows sob `AIGAR_CLOUDFLARE/` nesta fase.  
**Justificativa:** montar e revisar o mapa da arquitetura remontada antes de uma etapa futura específica do Worker.

## D-011 — Sem percentual inventado
**Decisão:** não declarar percentual global do plano sem uma lista fechada dos arquivos-alvo imaginados.  
**Justificativa:** quantidade de arquivos no destino não fornece o denominador do escopo total planejado.
