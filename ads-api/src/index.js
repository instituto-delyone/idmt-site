const OPENAI_EVENTS_URL = "https://bzr.openai.com/v1/events";
const DEFAULT_PIXEL_ID = "TZrpbXCpUoNe2fLiVrFMs9";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store"
    }
  });
}

function validEventType(type) {
  return typeof type === "string" && /^[a-zA-Z0-9_-]{1,64}$/.test(type);
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204 });
    }

    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, service: "idmt-ads-api" });
    }

    if (request.method !== "POST" || url.pathname !== "/events") {
      return json({ error: "Rota não encontrada." }, 404);
    }

    const ingestSecret = env.IDMT_INGEST_SECRET;
    const openaiAdsApiKey = env.OPENAI_ADS_API_KEY;
    const pixelId = env.OPENAI_ADS_PIXEL_ID || DEFAULT_PIXEL_ID;

    if (!ingestSecret || !openaiAdsApiKey) {
      return json({ error: "API de conversões não configurada no servidor." }, 503);
    }

    const authorization = request.headers.get("Authorization") || "";
    if (authorization !== `Bearer ${ingestSecret}`) {
      return json({ error: "Não autorizado." }, 401);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "JSON inválido." }, 400);
    }

    const event = body && body.event;
    if (!event || !validEventType(event.type)) {
      return json({ error: "Evento inválido." }, 400);
    }

    const payload = {
      validate_only: Boolean(body.validate_only),
      events: [{
        id: event.id || crypto.randomUUID(),
        type: event.type,
        timestamp_ms: Number.isFinite(event.timestamp_ms) ? event.timestamp_ms : Date.now(),
        source_url: event.source_url || "https://www.delyone.com/",
        action_source: event.action_source || "web",
        data: event.data || { type: "customer_action" }
      }]
    };

    const upstream = await fetch(`${OPENAI_EVENTS_URL}?pid=${encodeURIComponent(pixelId)}`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${openaiAdsApiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const text = await upstream.text();
    return new Response(text, {
      status: upstream.status,
      headers: {
        "content-type": upstream.headers.get("content-type") || "application/json; charset=utf-8",
        "cache-control": "no-store"
      }
    });
  }
};
