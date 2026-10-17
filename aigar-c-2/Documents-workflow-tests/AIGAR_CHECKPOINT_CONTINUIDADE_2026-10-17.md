# AIGAR — checkpoint de continuidade
Data de atualização: 2026-10-17
Projeto/repositório: `instituto-delyone/idmt-site`
Branch consultada pelo conector: `main`
Pasta auditada: `aigar-c-2/AIGAR_CLOUDFLARE/`

## Objetivo
Auditoria somente de leitura do AIGAR para entender os fluxos reais de linguagem, contexto, núcleo cognitivo, biblioteca e persistência antes de corrigir código. Preservar o comportamento existente, não inventar reconstruções e melhorar a continuidade/memória de contexto com evidências.

## Estado atual — resumo rápido
- **Testes locais:** 12/12 aprovados, 0 falhas e 0 erros; duração reportada de 0,010 s.
- **Suítes executadas:** `test_cognitive_core.py` (3), `test_cortex_compat.py` (4), `test_memory_lab.py` (5).
- **Integridade dos chunks:** validação local anterior confirmou 73/73 hashes e comprimentos depois de normalizar CRLF para LF; o primeiro resultado divergente era causado pela conversão de finais de linha no Windows.
- **Progresso estimado da auditoria estática pré-correção:** aproximadamente 66%, estimativa de planejamento, não métrica automática.
- **Código alterado nesta etapa:** não.
- **Deploy/Worker publicado alterado:** não.
- **Push para GitHub:** não.

## Restrições que continuam valendo
- Não modificar código-fonte nem Worker de produção nesta etapa.
- Não fazer push de documentação sem autorização explícita.
- Um comando PowerShell por vez quando pedir leitura local; analisar a saída antes do próximo comando.
- Separar em cada fase (A) funcionamento/evidência observada e (B) problemas, riscos e correções propostas.
- Distinguir observação de código, hipótese e resultado de teste.
- Não afirmar que código local e Worker implantado são idênticos sem verificação.

## Testes executados em 2026-10-17
Comando executado pelo usuário:
```powershell
python -B -m unittest discover `
  -s ".\aigar-c-2\AIGAR_CLOUDFLARE" `
  -p "test_*.py" `
  -v
```
Resultado reportado:
- `test_cognitive_core.py`: 3/3 aprovados.
- `test_cortex_compat.py`: 4/4 aprovados.
- `test_memory_lab.py`: 5/5 aprovados.
- Total: 12 testes, `OK`, 0,010 s.

Interpretação: os testes cobertos passaram; isso não prova persistência conversacional entre instâncias, integração completa da biblioteca, checksum em tempo de execução, nem comportamento do Worker publicado.

## Arquivos e componentes examinados
- `docs/aigar/index.html` — frontend da Developer Console.
- `aigar-c-2/AIGAR_CLOUDFLARE/main.py` — rotas e dispatch do Worker.
- `conversation_runtime.py` — fluxo de pergunta, sessão e logging mínimo.
- `context_runtime.py` — seleção assimétrica de contexto.
- `language_runtime.py` — interpretação heurística e sinais.
- `cortex_compat.py` — normalização e roteamento do contrato.
- `association_core.py` — seleção lexical de chunks.
- `library_runtime.py` — bootstrap e carregamento de índices/chunks.
- `storage_runtime.py` e `schema.sql` — bindings, persistência documental e metadados.
- `test_cognitive_core.py`, `test_cortex_compat.py`, `test_memory_lab.py` — testes lidos e executados.
- Workflow de validação do runtime local — lido; ele não executa necessariamente as suítes do pacote Worker.

## Conclusões que permanecem relevantes
- `SESSIONS` é memória em processo e guarda turnos limitados; não é prova de memória durável entre instâncias.
- `adaptive_interactions` registra metadados/snapshot mínimo; não demonstra persistência integral do histórico conversacional.
- `persistent_memory_cards` aparece como capacidade adiada no contrato de compatibilidade; ativação em produção não foi verificada.
- O schema consultado não apresenta tabela explícita dedicada a cartões de memória conversacional.
- O loader da biblioteca depende de `cache_file`, tenta GitHub Raw e Contents API, mas não valida checksum/comprimento em tempo de execução; o cache é indexado somente por ID. Faltam testes específicos de fallback e indisponibilidade.
- Os 73 chunks locais correspondem aos checksums registrados depois da normalização de quebras de linha. Isso não prova que todos os mesmos arquivos estão acessíveis ao Worker publicado.
- Os testes unitários aprovados são evidência positiva apenas para os casos cobertos.

## Próximo passo recomendado
Confirmar em PowerShell, somente em leitura, se `library_runtime.py` local corresponde ao blob de `main` consultado no GitHub e se há alterações locais nesse arquivo. Em seguida, procurar cobertura adicional de testes para loader/checksum/fallback. Não corrigir nem publicar código antes de documentar o fluxo e propor testes de regressão.

## Documentação local
- `AIGAR_Mapa_de_Funcionamento_v0.1.md` e `.docx`
- `AIGAR_Registro_de_Problemas_v0.1.md` e `.docx`
- `AIGAR_CHECKPOINT_CONTINUIDADE_2026-10-17.md`

Os documentos foram atualizados localmente nesta etapa. **Ainda não foram sincronizados com o GitHub.**


## Continuidade — Fase 14 (2026-10-17)
- `library_runtime.py` local: SHA `5f180853d26b1551c840d7c5098a667a2a751fe4`, igual ao blob remoto de `main`; `git status --short -- <arquivo>` não retornou saída.
- Busca por referências diretas a `load_chunk_text`, `chunk_urls`, `library_search`, `checksum`, `SHA-256`, `sha256`, `INDEX_URLS` e `CHUNK_CACHE` nos três testes encontrados não retornou resultados.
- Testes existentes continuam 12/12 aprovados. A busca só cobre os três arquivos `test_*.py` dentro de `AIGAR_CLOUDFLARE`; não prova ausência de cobertura indireta ou de outros testes fora dessa pasta.
- Próximo passo: inspecionar workflows/configuração de CI e localizar eventuais testes fora do pacote; depois planejar testes específicos do loader, sem alterar código até documentar a proposta.
- Nenhuma alteração de código, push ou implantação foi feita.

## Continuidade — Fase 15: workflows de CI
- O workflow `aigar-cognitive-core.yml` compila o pacote Worker, executa os mesmos três arquivos de teste (12 testes) e valida a sintaxe JavaScript inline. Não há teste específico do loader/checksum/fallback.
- O workflow `aigar-runtime-validation.yml` cobre o runtime/retriever local, não o loader de `AIGAR_CLOUDFLARE/library_runtime.py`.
- Divergência observada: `pyproject.toml` pede Python `>=3.13`, mas o workflow de validação cognitiva configura Python `3.12`; impacto ainda não demonstrado.
- README do pacote afirma que é candidato de migração e que alterações no repositório não publicam nem alteram o Worker ativo.
- Próximo passo: verificar estados recentes de CI; depois planejar testes do loader com HTTP simulado. Não alterar código/configuração nem publicar sem autorização.

## Recalibração de progresso — 2026-10-17

A estimativa antiga de 66% foi substituída porque não estava sendo recalculada quando novas fases eram adicionadas. Método atual: 20 pacotes de trabalho com peso igual; concluído = 1, parcial = 0,5, pendente = 0.

- 12 concluídos, 4 parciais, 4 pendentes.
- Pontuação: 12 + (4 × 0,5) = 14/20.
- **Auditoria documental/estática: 70% (estimativa estruturada).**
- Isso não mede a funcionalidade do AIGAR nem prontidão de produção.
- Testes locais: 12/12 aprovados.
- Integridade dos chunks locais: 73/73 após normalização CRLF→LF.
- Pendentes críticos para encerrar: consultar estado recente de CI; testar loader/checksum/fallback; validar memória entre instâncias; verificar Worker implantado; consolidar documentação.
- Nenhum código/configuração foi alterado, nenhum push foi feito e nenhum deploy foi realizado.
\n\n## Continuidade — Fase 16: verificação Cloudflare read-only (2026-10-17)\n- O usuário confirmou que o PC está sincronizado com GitHub; a consulta independente mostrou que o Worker implantado não está na revisão atual do GitHub.\n- Worker `aigar-api`; rota `delyone.com/aigar/api*`; subdomínio `dr-delyone.workers.dev` habilitado. Versão publicada nº 40, 100% do tráfego, anotada com commit `0b6a19289543dc64bdc4cf02c7953491b3433651`.\n- `main` atual `4c09801d07f4ed15493985bdc0ed8683f7956e7b` está 78 commits à frente daquele commit. Não fazer deploy automaticamente; a diferença precisa ser analisada e o usuário deve autorizar qualquer implantação.\n- D1 `PRAGMA quick_check` = `ok`; queries read-only, sem linhas gravadas. Tabelas adaptativas esperadas existem. Contagens: documents 3; document_chunks 0; adaptive_interactions 26; adaptive_feedback 3; reviews/evaluation_cases/useful logs/audit log 0. Estados de documents: 2 uploaded, 1 error.\n- Bucket R2 `aigar-library` existe e a listagem mostrou 3 PDFs originais. O pipeline de chunks precisa de investigação, pois D1 contém zero `document_chunks`.\n- O schema ativo não tem tabela dedicada de Memory Cards; isso corresponde à capacidade adiada documentada.\n- Tentativas de abrir `/health`, `/memory/status`, `/library/boot` e `/texto-matriz/boot` pelo navegador de pesquisa não obtiveram respostas. Isso é inconclusivo quanto à saúde real do endpoint, não uma prova de indisponibilidade. O conteúdo multipart da API de Worker foi truncado para módulos grandes; não foi possível confirmar equivalência byte a byte do código publicado.\n- Nenhum código, configuração, D1 ou R2 foi alterado; nenhum commit ou deploy realizado.\n- Progresso estimado: 13 concluídos, 5 parciais, 2 pendentes de 20 = **77,5%** pelo método estruturado. Pendências críticas: testes específicos do loader (checksum/fallback/cache) e teste de persistência/recuperação entre instâncias. Verificação HTTP e comparação integral do deploy continuam parciais.\n- Próximo passo seguro: ao retornar, decidir se fazemos testes HTTP de leitura diretamente pelo navegador/PowerShell do usuário e se autorizamos uma comparação direcionada entre código implantado e revisão atual antes de qualquer correção ou deploy.\n