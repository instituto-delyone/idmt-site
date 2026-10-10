# AIGAR Cloudflare Runtime

Production adapter for AIGAR Runtime using Cloudflare Python Workers + FastAPI.

- Worker: aigar-api
- Public endpoint: https://aigar-api.dr-delyone.workers.dev
- Production site API path target: /aigar/api
- Local Python Runtime remains under aigar-c-2/AIGAR_RUNTIME.
- Library chunks are retrieved from the versioned GitHub repository and cached per Worker isolate.
- Session memory is isolate-local for this first production cut; persistent Memory Cards are not replaced by this layer.

The Cloudflare implementation deliberately keeps the existing local Runtime intact while providing a production-compatible deployment surface.

## Current Worker module map

The Cloudflare Worker keeps its existing public routes and behavior. The language runtime was extracted to `language_runtime.py` so the entrypoint can import the language functions instead of defining them inline. This is a behavior-preserving extraction of the current Worker implementation; it is **not yet** a direct import of the local `CORTEX/language/*` modules, whose contracts and runtime packaging need a compatible bridge before substitution.

| Responsibility | Current implementation | Status |
|---|---|---|
| HTTP entrypoint, routes, orchestration, adaptive response, admin, storage and Workflow | `main.py` | Existing entrypoint; remaining concentrated responsibilities |
| Worker language interpretation and language concepts | `language_runtime.py` | Extracted from the prior inline implementation |
| Context ranking and evidence selection | `association_core.py` | Separate module already imported by `main.py` |
| Three-layer repository-backed memory | `memory_lab/engine.py` via `memory_lab` package | Separate module already imported by `main.py` |
| Local-runtime language implementation | `../CORTEX/language/interpreter.py` and `language_network_adapter.py` | Not wired into Cloudflare Worker yet; preserve behavior until compatibility is verified |
| Local-runtime memory, retrieval, controller and Aurora | `../CORTEX/memory/*`, `../CORTEX/engram/*`, `../CORTEX/prefrontal/*` | Local-runtime modules; not assumed interchangeable with Worker services |

Future Workers are architectural ideas only. No new Worker, Service Binding, route, or deployment is introduced by this refactor.
