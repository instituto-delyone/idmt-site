# AIGAR Railway Backend

Backend HTTP mínimo do AIGAR para Railway. O serviço expõe uma rota de saúde e verifica a disponibilidade da biblioteca de fisiologia sem publicar o conteúdo dos arquivos.

## Estrutura esperada

```text
idmt-site/
├── package.json
├── Server/
│   └── leitor.js
└── Engines/
    └── Aurora/
        └── Bibliotecas/
            └── Fisiologia/
                └── *.md
```

## Execução local

Na raiz do repositório:

```bash
npm install
npm start
```

O serviço escuta em `0.0.0.0` e utiliza `process.env.PORT`, com fallback local para a porta `3000`.

- `GET /` — identificação do serviço.
- `GET /health` — estado do serviço e disponibilidade da biblioteca.
- `/health` retorna HTTP 200 quando o diretório da biblioteca está acessível e HTTP 503 quando não está.

Teste local:

```bash
curl http://localhost:3000/health
```

## Configuração no Railway

- Root Directory: raiz do repositório (`/`).
- Build Command: `npm install` (ou o comando padrão detectado pelo Railway).
- Start Command: `npm start`.
- Healthcheck Path: `/health`.
- Porta: fornecida automaticamente pela variável `PORT` do Railway.

Não é necessário criar `railway.json` nem `.env.example` para essa configuração mínima. Se futuramente forem adicionadas variáveis próprias, documente apenas nomes e exemplos não sensíveis em um arquivo `.env.example`; nunca versione segredos.

## Observações

O leitor verifica e contabiliza arquivos Markdown; não expõe o conteúdo clínico da biblioteca por HTTP. O diretório de fisiologia deve existir no repositório para que o healthcheck retorne sucesso.
