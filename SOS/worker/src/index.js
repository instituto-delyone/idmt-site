/**
 * Delyone SOS — Cloudflare Worker (scaffold)
 *
 * SAFETY: dispatch is disabled unless SOS_DISPATCH_ENABLED=true and all
 * required secrets/configuration are present. Never treat HTTP acceptance
 * as proof that an SMS reached a recipient.
 */
const JSON_HEADERS = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), { status, headers: { ...JSON_HEADERS, ...headers } });
}

function allowedOrigins(env) {
  return (env.ALLOWED_ORIGINS || "").split(",").map(v => v.trim()).filter(Boolean);
}

function corsHeaders(request, env) {
  const origin = request.headers.get("Origin") || "";
  const allowed = allowedOrigins(env);
  if (!origin || !allowed.includes(origin)) return {};
  return {
    "access-control-allow-origin": origin,
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "Content-Type",
    "access-control-max-age": "86400",
    "vary": "Origin",
  };
}

function validCoordinates(body) {
  return Number.isFinite(body.latitude) && body.latitude >= -90 && body.latitude <= 90 &&
    Number.isFinite(body.longitude) && body.longitude >= -180 && body.longitude <= 180 &&
    Number.isFinite(body.accuracy_m) && body.accuracy_m >= 0 && body.accuracy_m <= 100000;
}

async function verifyTurnstile(token, request, env) {
  if (!env.TURNSTILE_SECRET_KEY || !token) return false;
  const form = new URLSearchParams();
  form.set("secret", env.TURNSTILE_SECRET_KEY);
  form.set("response", token);
  const ip = request.headers.get("CF-Connecting-IP");
  if (ip) form.set("remoteip", ip);

  const response = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: form,
  });
  if (!response.ok) return false;
  const result = await response.json();
  return result.success === true;
}

async function sendSms(message, env) {
  // Twilio is an optional adapter; no credentials or destination belong in source control.
  const { TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, SOS_FROM_E164, SOS_RECIPIENT_E164 } = env;
  if (!TWILIO_ACCOUNT_SID || !TWILIO_AUTH_TOKEN || !SOS_FROM_E164 || !SOS_RECIPIENT_E164) {
    throw new Error("SMS_PROVIDER_NOT_CONFIGURED");
  }

  const endpoint = `https://api.twilio.com/2010-04-01/Accounts/${encodeURIComponent(TWILIO_ACCOUNT_SID)}/Messages.json`;
  const body = new URLSearchParams({
    To: SOS_RECIPIENT_E164,
    From: SOS_FROM_E164,
    Body: message,
  });
  const auth = btoa(`${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}`);
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      authorization: `Basic ${auth}`,
      "content-type": "application/x-www-form-urlencoded",
    },
    body,
  });

  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.sid) throw new Error("SMS_PROVIDER_REJECTED");
  return { provider: "twilio", messageId: result.sid, providerStatus: result.status || "accepted" };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const cors = corsHeaders(request, env);

    if (request.method === "OPTIONS") {
      if (!cors["access-control-allow-origin"]) return new Response(null, { status: 403 });
      return new Response(null, { status: 204, headers: cors });
    }

    if (url.pathname === "/health" && request.method === "GET") {
      return json({ service: "delyone-sos", status: "ok", dispatchEnabled: env.SOS_DISPATCH_ENABLED === "true" }, 200, cors);
    }

    if (url.pathname !== "/api/sos") return json({ error: "not_found" }, 404, cors);
    if (request.method !== "POST") return json({ error: "method_not_allowed" }, 405, { ...cors, allow: "POST, OPTIONS" });
    if (!cors["access-control-allow-origin"]) return json({ error: "origin_not_allowed" }, 403);

    if (request.headers.get("content-type")?.split(";")[0].trim() !== "application/json") {
      return json({ error: "content_type_must_be_json" }, 415, cors);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "invalid_json" }, 400, cors);
    }

    if (!validCoordinates(body)) return json({ error: "invalid_location" }, 400, cors);
    if (typeof body.captured_at !== "string" || !Number.isFinite(Date.parse(body.captured_at))) {
      return json({ error: "invalid_captured_at" }, 400, cors);
    }

    // Dispatch remains off by default while the recipient and operational workflow are verified.
    if (env.SOS_DISPATCH_ENABLED !== "true") {
      return json({ error: "dispatch_disabled", message: "SOS backend is not activated; no alert was sent." }, 503, cors);
    }

    // Anti-abuse verification is mandatory before dispatch.
    const verified = await verifyTurnstile(body.turnstileToken, request, env).catch(() => false);
    if (!verified) return json({ error: "challenge_failed", message: "No alert was sent." }, 403, cors);

    const mapsUrl = `https://maps.google.com/?q=${body.latitude},${body.longitude}`;
    const message = [
      "ALERTA SOS — Delyone",
      "Um usuário acionou o botão SOS.",
      `Localização: ${mapsUrl}`,
      `Precisão informada: ${Math.round(body.accuracy_m)} m`,
      `Horário UTC: ${new Date(body.captured_at).toISOString()}`,
    ].join("\n");

    try {
      const delivery = await sendSms(message, env);
      // Return only a provider acceptance reference, not recipient numbers or credentials.
      return json({ acceptedByProvider: true, provider: delivery.provider, messageId: delivery.messageId,
        message: "O provedor aceitou a solicitação de envio; isso não confirma entrega ao destinatário." }, 202, cors);
    } catch (error) {
      // Do not log coordinates, message bodies, credentials, or phone numbers.
      const code = error?.message === "SMS_PROVIDER_NOT_CONFIGURED" ? "provider_not_configured" : "provider_error";
      return json({ error: code, message: "Não foi possível confirmar o envio do alerta." }, 502, cors);
    }
  },
};
