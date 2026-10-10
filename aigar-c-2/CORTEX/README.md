# CORTEX — Arquitetura neurocognitiva do AIGAR-C

O CORTEX é a estrutura canônica provisória dos módulos neurocognitivos do AIGAR-C. Até uma decisão arquitetural explícita em contrário, os diretórios e responsabilidades abaixo são tratados como **provisoriamente imutáveis**: os módulos devem ser implementados e ter suas referências corrigidas dentro deste mapa, sem reorganizações oportunistas.

Essa imutabilidade é uma regra de trabalho para reduzir deriva arquitetural; não significa que a arquitetura esteja validada em produção nem impede uma futura mudança deliberada, documentada e versionada.

## Regras desta fase

- Preservar o ponto de entrada operacional **AIGAR_RUNTIME/main.py** enquanto ele consome os contratos e módulos canônicos do CORTEX.
- **CORTEX/thalamus/models.py** é a fonte canônica dos contratos compartilhados do runtime.
- Atualizar imports e caminhos para os destinos já definidos; não recriar cópias locais dos contratos.
- Preservar os pacotes independentes **knowledge_retrieval/**, **knowledge_encoding/** e **Diagnosis/**; o CORTEX integra-os por adaptadores.
- Placeholders documentam intenção; não representam código funcional até que sejam implementados.
- Não alterar o Cloudflare Worker nem seus arquivos, nomes, símbolos, configurações, bindings, chaves JSON ou workflows.
- Nesta fase, não executar testes, não fazer merge e não fazer deploy. A validação só vem depois de completar a movimentação e a tradução das referências.

## Mapa canônico provisório

- **sara/**: inicialização, prontidão e estado do runtime.
- **sensory/**: entrada e classificação de sinais.
- **thalamus/**: leitura contextual/linguística inicial, roteamento e contratos compartilhados.
- **language/**: processamento linguístico e adapter para o runtime.
- **memory/**: estado de trabalho e recuperação de contexto.
- **engram/**: adapter de recuperação de conhecimento documental; o pacote **knowledge_retrieval/** continua independente.
- **reasoning_engine/**: planejamento, avaliação de evidências e suficiência; componentes executivos existentes permanecem nos caminhos já definidos até uma decisão explícita.
- **prefrontal/**: controlador de planejamento e apresentação da resposta por Aurora, além de documentação arquitetural.
- **default_mode_network/**: estado interno, autorrepresentação e reflexão; ainda não implementado.
- **worker_bridge/**: contratos e comunicação entre componentes, sem alterar Workers existentes.
- **occipital/**: futura organização da interface visual; **aigar_ui_chat_mvp/** continua separada até a integração ser definida.

## Contratos compartilhados

O contrato canônico está em **thalamus/models.py**:

- **ConversationReading**: leitura estruturada da entrada.
- **ConversationState**: estado conversacional de uma sessão.
- **SourceTrace**: rastreabilidade da origem e do estado de evidência.
- **RuntimeRequest** e **RuntimeResponse**: fronteira de entrada/saída do runtime.
- **Intent**, **Depth** e **SourceStatus**: aliases compartilhados para valores controlados.

Consumidores devem importar os modelos deste módulo; não devem redefinir esses contratos em cada região.

## Entrada operacional

O ponto de entrada permanece **AIGAR_RUNTIME.main:app**, mas suas dependências são importadas dos caminhos canônicos do CORTEX. A partir do diretório **aigar-c-2/**, a forma prevista de execução é:

    uvicorn AIGAR_RUNTIME.main:app --host 127.0.0.1 --port 8000

A existência do entry point e a tradução estática dos imports não equivalem a validação de execução. Testes permanecem deliberadamente adiados até a conclusão das referências do repositório.
