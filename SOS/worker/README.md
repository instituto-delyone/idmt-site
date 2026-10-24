# Delyone SOS Worker — initial scaffold

This is a separate Cloudflare Worker intended for the SOS page. It does not share the MedUnity authentication API.

## Current behavior

- `GET /health`: returns a basic health response.
- `POST /api/sos`: validates JSON and location fields.
- Dispatch is **disabled by default**; with dispatch disabled, the endpoint explicitly returns `503` and says no alert was sent.
- The optional SMS adapter uses Twilio, with all credentials and recipient numbers stored as Worker secrets, never in the repository.
- Turnstile verification is mandatory when dispatch is enabled.
- CORS only allows the configured exact origins.

## Required before any real use

1. Confirm the SOS page's production origin and update `ALLOWED_ORIGINS`.
2. Confirm the SMS provider, verified sender, and recipient. The previously mentioned recipient must not be used until independently verified and authorized.
3. Create/configure a Cloudflare Turnstile widget; update the SOS page to send its short-lived token as `turnstileToken`.
4. Add edge rate limiting and abuse monitoring.
5. Configure the secrets listed in `wrangler.toml` using the Cloudflare dashboard or Wrangler secret commands.
6. Test using an explicitly designated test recipient; verify delivery status with the provider.
7. Only then enable `SOS_DISPATCH_ENABLED=true`.

## Important limits

A successful API response from the SMS provider is not proof that a person received or acted on the alert. Production use requires delivery-status handling, clear user messaging, privacy/retention decisions, and an operational response plan. This scaffold is not yet an operational emergency service and must not be relied on for immediate danger.
