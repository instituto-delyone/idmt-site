# IDMT Forum API

Backend da Fase 1 do Fórum de Discussões Clínicas do Instituto Delyone.

## Arquitetura

- Cloudflare Worker
- Cloudflare D1
- `schema.sql` cria as tabelas `discussions` e `comments`
- `src/index.js` expõe a API REST

## Rotas

- `GET /health`
- `GET /discussions`
- `GET /discussions?category=Clínica`
- `GET /discussions/:id`
- `POST /discussions`
- `POST /discussions/:id/comments`

## Publicação do Worker

1. Criar um banco D1 chamado `idmt-forum` no Cloudflare.
2. Substituir `REPLACE_WITH_D1_DATABASE_ID` em `wrangler.toml` pelo ID do banco.
3. Aplicar o schema:

```bash
npx wrangler d1 execute idmt-forum --remote --file=./schema.sql
```

4. Publicar:

```bash
npx wrangler deploy
```

5. Configurar o domínio/rota do Worker e apontar `window.FORUM_API_BASE` na página do fórum para a URL pública da API, caso ela não seja exposta em `/api/forum` no mesmo domínio do site.

## Fase 1

A primeira versão permite listar discussões, abrir uma discussão, criar uma nova discussão e publicar comentários. Não há autenticação nesta etapa; o nome do participante é informado no formulário. Moderação, autenticação e perfis profissionais ficam para uma etapa posterior.
