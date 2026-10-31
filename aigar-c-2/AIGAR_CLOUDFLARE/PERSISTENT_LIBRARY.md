# AIGAR persistent library storage

Camada de persistência administrativa da biblioteca do AIGAR.

## Arquitetura

Admin autenticado → `POST /aigar/api/admin/upload` → arquivo original no R2 + metadados no D1 → status `uploaded` → processamento assíncrono → chunks de 25 páginas no R2 + metadados no D1.

## Recursos Cloudflare

O Worker `aigar-api` utiliza os seguintes bindings, declarados em `wrangler.jsonc`:

| Binding | Tipo | Recurso |
|---|---|---|
| `AIGAR_LIBRARY_BUCKET` | R2 | `aigar-library` |
| `AIGAR_DB` | D1 | `AIGAR` |

Na auditoria de 31/10/2026, os dois recursos já estavam presentes na conta Cloudflare conectada. Portanto, **não crie um segundo D1 chamado `aigar-library`**. O banco correto para este Worker é o D1 `AIGAR`.

Antes de executar comandos, confirme que o Wrangler está autenticado na conta e que os recursos listados correspondem ao ambiente pretendido:

```powershell
npx wrangler login
npx wrangler d1 list
npx wrangler r2 bucket list
```

A partir da raiz do repositório, para aplicar o schema idempotente ao banco já configurado:

```powershell
npx wrangler d1 execute AIGAR --remote --file=aigar-c-2/AIGAR_CLOUDFLARE/schema.sql --config=aigar-c-2/AIGAR_CLOUDFLARE/wrangler.jsonc
```

O schema utiliza `CREATE TABLE IF NOT EXISTS` e `CREATE INDEX IF NOT EXISTS`. Ainda assim, confira o ambiente e faça backup conforme a política operacional antes de qualquer alteração em produção.

Não execute `wrangler d1 create` nem `wrangler r2 bucket create` quando os recursos existentes forem os que o Worker deve utilizar. Se um ambiente novo for realmente necessário, crie recursos próprios e atualize os bindings e o arquivo de configuração de forma coordenada.

## API administrativa

- `GET /admin/storage` — verifica R2/D1.
- `POST /admin/upload` — exige Bearer de administrador validado pelo MedUnity; aceita PDF até 100 MB.
- `GET /admin/documents` — lista os 100 documentos mais recentes.

## Idempotência

A interface calcula SHA-256 e envia `X-File-SHA256`. Se o hash já existir, o Worker retorna `already_exists`.

## Segurança

Apenas `perfil=admin` acessa os endpoints administrativos. O PDF não é público; a senha não é armazenada pelo AIGAR; o arquivo original permanece no bucket R2 privado. Nunca versione tokens, senhas ou valores de secrets.

## Processamento documental

O status `uploaded` é consumido pelo processador de ingestão. A política documentada usa texto original, sem resumo, chunks de 25 páginas e IDs determinísticos, com metadados persistentes no D1.
