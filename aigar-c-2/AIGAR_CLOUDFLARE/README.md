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
- Repository-backed three-layer memory prototype: `memory_lab/`.

The Worker package remains independently bundleable. It does **not** import sibling `CORTEX/` Python modules at runtime, because those modules and their local retrieval dependencies are not packaged inside this Worker directory. Instead, `WorkerCortexBridge` normalizes the Worker-native interpretation to the canonical `ConversationReading` vocabulary and emits an explicit resource-routing contract. This boundary is tested in `test_cortex_compat.py`.

## Request flow

1. `language_runtime.py` interprets the input and attaches linguistic analysis.
2. `WorkerCortexBridge` validates shared fields, preserves extra annotations, and normalizes confidence/uncertainty.
3. `classify_interaction` identifies the interaction profile.
4. `context_runtime.py` selects eligible context and builds/revises the adaptive plan.
5. The existing library, memory, and answer-rendering services execute only when available.
6. The response reports routing, evidence, and availability metadata instead of implying an unconnected subsystem executed.

## Explicit capability boundary

- Session context is Worker-isolate-local; it is not persistent Memory Card recall.
- A diagnosis route flag is a selection decision only. The separate Diagnosis engine is **not connected** to this Worker.
- Audio/visual input, additional Workers/Service Bindings, and a default-mode/reflection subsystem are not implemented here.
- No production route, binding, secret, Cloudflare setting, or live script is changed by repository edits.

## Validation

The migration workflow compiles the Worker package and runs the cognitive-core, Memory Lab, and CORTEX-compatibility unit tests. A passing repository test run validates these checks only; it does not mean the candidate has been deployed to Cloudflare.
