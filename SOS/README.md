# Delyone SOS

Initial scaffold for a minimal SOS page. This is not an operational emergency service.

## Safety status
- API endpoint is not deployed or configured.
- No SMS or institutional forwarding is enabled.
- The contact `+55 62 3239-4405` remains unverified and must not receive automatic location data.
- In immediate danger in Brazil, call 190.

## Deployment checklist
1. Implement and host the API over HTTPS.
2. Keep provider credentials and recipient numbers server-side.
3. Verify recipient identity, purpose, and consent before enabling forwarding.
4. Add rate limiting, abuse prevention, delivery confirmation, and minimal logging.
5. Configure DNS and TLS for the chosen subdomain.

A `noindex` directive can discourage search indexing but does not make a public page private. The proposed hostname `sos-7k4m2.delyone.com.br` is only a suggestion until DNS and hosting are configured.