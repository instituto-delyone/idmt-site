# AIGAR C-2 — Mapa pareado da migração neurocognitiva
Versão: 1.0
Branch de trabalho: `neurocognitive-migration`
Base: `main`
Status: migração inicial em andamento; não mesclada em produção.

## Regras da migração
1. Toda alteração de nome deve aparecer como par **origem → destino**.
2. Atualizar imports, chamadas, testes, documentação, caminhos de build e referências de runtime no mesmo conjunto lógico.
3. Não renomear corpus, PDFs, chunks, índices gerados, arquivos de usuário ou dependências vendorizadas só para lhes dar nomes neuroanatômicos.
4. Não afirmar equivalência literal entre uma região cerebral e um módulo de software.
5. Preservar contratos públicos e endpoints enquanto a nova arquitetura não for validada.
6. Produção permanece na branch `main`; mudanças nesta branch não são deploy de produção.

## Alterações executadas nesta branch

### Par 01 — raciocínio / controle executivo
- **Arquivo antigo:** `aigar-c-2/AIGAR_RUNTIME/reasoning.py`
- **Arquivo novo:** `aigar-c-2/AIGAR_RUNTIME/prefrontal_controller.py`
- **Símbolo antigo:** `ReasoningEngine`
- **Símbolo novo:** `PrefrontalController`
- **Referências atualizadas:** import e instanciação em `AIGAR_RUNTIME/main.py`; documentação em `AIGAR_RUNTIME/README.md`.
- **Contrato preservado:** `SourceTrace.kind="reasoning"` permanece inalterado para não quebrar consumidores.
- **Interpretação:** o módulo atual organiza evidências e um plano de resposta; é apenas uma primeira analogia funcional com controle executivo, não um modelo completo do córtex pré-frontal.

### Par 02 — memória contextual
- **Arquivo antigo:** `aigar-c-2/AIGAR_RUNTIME/memory.py`
- **Arquivo novo:** `aigar-c-2/AIGAR_RUNTIME/hippocampal_memory.py`
- **Símbolo antigo:** `MemoryAdapter`
- **Símbolo novo:** `HippocampalMemoryAdapter`
- **Referências atualizadas:** import e instanciação em `AIGAR_RUNTIME/main.py`; documentação em `AIGAR_RUNTIME/README.md`.
- **Contrato preservado:** `SourceTrace.kind="memory"`.
- **Limite importante:** a implementação atual recupera contexto da sessão; memória persistente de longo prazo continua não conectada nesse adaptador. O nome não deve sugerir que já reproduz a função biológica do hipocampo.

### Par 03 — ponte da linguagem
- **Arquivo antigo:** `aigar-c-2/AIGAR_RUNTIME/language_bridge.py`
- **Arquivo novo:** `aigar-c-2/AIGAR_RUNTIME/language_network_bridge.py`
- **Símbolo antigo:** `ExecutableLanguageAdapter`
- **Símbolo novo:** `LanguageNetworkAdapter`
- **Referências atualizadas:** import e instanciação em `AIGAR_RUNTIME/main.py`; documentação em `AIGAR_RUNTIME/README.md`.
- **Caminho de integração preservado por enquanto:** `aigar-c-2/AIGAR_LANGUAGE/interpreter.py`.
- **Limite importante:** a ponte executa o interpretador de linguagem existente; não implementa separadamente as áreas de Broca e Wernicke.

## Próximos pares candidatos — ainda NÃO executados

| Origem | Destino proposto | Motivo | Dependências a mapear antes de renomear |
|---|---|---|---|
| `aigar-c-2/AIGAR_CORE/` | `aigar-c-2/association_network/` | Arquitetura/contratos de integração distribuída | Manifestos, paths, workflow CI, documentação |
| `aigar-c-2/AIGAR_LANGUAGE/` | `aigar-c-2/language_network/` | Interpretador e conhecimento de linguagem | `INTERPRETER_PATH`, JSONs, testes, UI e scripts |
| `aigar-c-2/AIGAR_LIBRARY/` | `aigar-c-2/knowledge_retrieval/` | Busca/recuperação de conhecimento; não é literalmente hipocampo | imports, cache, índices, bootstrap e builders |
| `aigar-c-2/AIGAR_LIBRARY_BUILDER/` | `aigar-c-2/knowledge_consolidation/` | Construção e indexação da biblioteca | workflow Cloudflare, imports, requirements e scripts |
| `aigar-c-2/AIGAR_CLOUDFLARE/cognitive_core.py` | `aigar-c-2/AIGAR_CLOUDFLARE/association_core.py` | Preparação de contexto e seleção de chunks | import em `main.py`, testes, cache e deploy |
| `aigar-c-2/AIGAR_CLOUDFLARE/main.py` | Não renomear ainda | Arquivo de entrada de produção de 168 KB; deve ser modularizado antes de mover | `wrangler.jsonc`, workflow, bindings e rotas |
| `aigar-c-2/AIGAR_RUNTIME/main.py` | Manter `main.py` como entrypoint | Caminho de execução documentado e usado por Uvicorn | contratos de execução local |

## Proposta de divisão dos Cloudflare Workers

Objetivo: substituir o Worker monolítico por responsabilidades delimitadas, sem multiplicar Workers sem necessidade.

1. **`aigar-api` — Gateway / integração executiva**
   - Preserva a URL pública e os endpoints existentes.
   - Valida a requisição, roteia chamadas e normaliza respostas.
   - Não deve conter indexação pesada nem lógica extensa de recuperação.

2. **`aigar-cognition` — Contexto e planejamento**
   - Interpretar estado, preparar contexto e produzir planos explícitos.
   - Evolui para controle executivo computacional; não depende obrigatoriamente de LLM.
   - Só recebe chamadas por Service Binding depois de configuração e testes.

3. **`aigar-library` — Recuperação de conhecimento**
   - Boot e busca de chunks, índices e cache de biblioteca.
   - Acesso ao armazenamento estritamente necessário.
   - Manter limites de chunks e recursos medidos em produção.

4. **`aigar-memory` — Estado e memória persistente**
   - Operações de memória persistente via D1/R2, depois de definir schema, autorização, retenção e contrato.
   - Não confundir logs, estado de sessão e memória de longo prazo.

### Ordem sugerida para Workers
- Primeiro extrair a recuperação da biblioteca em módulo isolado e testar sem alterar rotas públicas.
- Depois definir contratos JSON versionados e Service Bindings entre Workers.
- Criar/deployar os Workers auxiliares sem mudar o tráfego de produção.
- Testar health, boot, pergunta, timeout, erros, CORS, autenticação e custos.
- Só então fazer o gateway encaminhar tráfego para os serviços auxiliares.
- Manter fallback/rollback para o Worker atual.

## Verificações obrigatórias antes de merge
- [ ] Imports Python sem referências aos nomes removidos.
- [ ] Testes do runtime e do núcleo passam.
- [ ] `/health`, `/library/boot` e `/perguntar` mantêm contrato.
- [ ] Wranger/workflow apontam para o entrypoint correto.
- [ ] Nenhuma rota pública foi removida.
- [ ] A branch de migração não foi mesclada nem publicada em produção sem validação.
- [ ] Atualizar este mapa com SHA de commit e resultado real de cada teste.

## Histórico da branch
- Branch criada a partir de `main`.
- Par 01: arquivos e import atualizados.
- Par 02: arquivos e import atualizados.
- Par 03: arquivos e import atualizados.
- Testes automatizados ainda precisam ser executados num ambiente com as dependências do runtime.
