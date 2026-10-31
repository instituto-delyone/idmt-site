# AIGAR Cloudflare Worker — migration package

This directory is the **self-contained Cloudflare Worker implementation** being aligned with the current AIGAR-C/CORTEX architecture. It is intentionally maintained as a migration candidate in the repository; editing this package does not publish or change the live Cloudflare Worker.

## Runtime boundary

- Worker entrypoint: `main.py` (`WorkerEntrypoint`).
- Worker packaging/configuration: `wrangler.jsonc`.
- Canonical local runtime: `../AIGAR_RUNTIME`.
- Shared CORTEX contracts: `../CORTEX/thalamus/models.py`.
- Worker-side contract bridge: `cortex_compat.py`.
- Worker language interpretation: `language_runtime.py`.
- Context selection and adaptive planning: `context_runtime.py`.
- Cognitive-context retrieval: `association_core.py`.
- Repository-backed three-layer document memory prototype: `memory_lab/`.
- Public Memory Card retrieval: `memory_card_runtime.py`, driven only by `CORTEX/memory/public_memory_manifest.json`.
- Public/admin access boundary: `CORTEX/memory/access_policy.yaml` and the existing `require_admin()` guard in `main.py`.

The Worker package remains independently bundleable. It does **not** import sibling `CORTEX/` Python modules at runtime, because those modules and their local retrieval dependencies are not packaged inside this Worker directory. Instead, `WorkerCortexBridge` normalizes the Worker-native interpretation to the canonical `ConversationReading` vocabulary and emits an explicit resource-routing contract. This boundary is tested in `test_cortex_compat.py`.

## Request flow

1. `language_runtime.py` interprets the input and attaches linguistic analysis.
2. `WorkerCortexBridge` validates shared fields, preserves extra annotations, and normalizes confidence/uncertainty.
3. `classify_interaction` identifies the interaction profile.
4. `context_runtime.py` selects eligible session context and builds/revises the adaptive plan.
5. `memory_card_runtime.py` retrieves only cards explicitly marked `visibility: public` in the versioned public manifest. It validates stable ID/version declarations and treats YAML as inert text; it never scans historical card folders.
6. The existing library, document Memory Lab, public Memory Card adapter, and answer renderer execute independently and fail open for ordinary conversation.
7. The response reports routing, evidence, and availability metadata instead of implying an unconnected subsystem executed.

## Explicit capability boundary

- Session context is Worker-isolate-local; it is not persistent cross-instance conversation history.
- Ordinary conversation is public: no activation phrase, designated email, or speaker-identity verification is required. Public retrieval is limited to individually allowlisted cards; the initial manifest is intentionally empty until cards are reviewed.
- Administrative routes remain separate and continue to call `require_admin()` before privileged operations. Public conversation does not grant admin permissions.
- A diagnosis route flag is a selection decision only. The separate Diagnosis engine is **not connected** to this Worker.
- Audio/visual input, additional Workers/Service Bindings, and a default-mode/reflection subsystem are not implemented here.
- No production route, binding, secret, Cloudflare setting, or live script is changed by repository edits.

## Validation

The migration workflow compiles the Worker package and runs the cognitive-core, Memory Lab, and CORTEX-compatibility unit tests. A passing repository test run validates these checks only; it does not mean the candidate has been deployed to Cloudflare.
