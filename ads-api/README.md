# IDMT Ads API

Worker separado para enviar eventos de conversão do Instituto Delyone para a OpenAI Ads Measurement Conversions API.

## Configuração

Secrets do Cloudflare Worker:

```bash
wrangler secret put OPENAI_ADS_API_KEY
wrangler secret put IDMT_INGEST_SECRET
```

O `OPENAI_ADS_PIXEL_ID` está em `wrangler.toml` porque o Pixel ID não é a credencial secreta usada para autenticação.

## Endpoint

Após publicar o Worker:

```text
POST /events
Authorization: Bearer <IDMT_INGEST_SECRET>
Content-Type: application/json
```

Exemplo de evento real de consulta confirmada:

```json
{
  "validate_only": false,
  "event": {
    "id": "EVENT-ID-UNICO",
    "type": "appointment_scheduled",
    "timestamp_ms": 1760000000000,
    "source_url": "https://www.delyone.com/teleconsulta/medicina/",
    "action_source": "web",
    "data": {
      "type": "customer_action"
    }
  }
}
```

O Worker encaminha o evento para:

```text
https://bzr.openai.com/v1/events?pid=TZrpbXCpUoNe2fLiVrFMs9
```

A API key da OpenAI Ads fica somente como secret no servidor e nunca deve ser colocada em HTML, JavaScript público, GitHub ou memória do projeto.

## Teste de saúde

```text
GET /health
```

## Observação importante

`appointment_scheduled` deve ser enviado somente quando a consulta estiver realmente confirmada. Cliques em "Solicitar consulta" e contatos pelo WhatsApp são tratados pelo site como `lead_created`.
