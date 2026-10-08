# AIGAR Cloudflare Runtime

Production adapter for AIGAR Runtime using Cloudflare Python Workers + FastAPI.

- Worker: aigar-api
- Public endpoint: https://aigar-api.dr-delyone.workers.dev
- Production site API path target: /aigar/api
- Local Python Runtime remains under aigar-c-2/AIGAR_RUNTIME.
- Library chunks are retrieved from the versioned GitHub repository and cached per Worker isolate.
- Session memory is isolate-local for this first production cut; persistent Memory Cards are not replaced by this layer.

The Cloudflare implementation deliberately keeps the existing local Runtime intact while providing a production-compatible deployment surface.
