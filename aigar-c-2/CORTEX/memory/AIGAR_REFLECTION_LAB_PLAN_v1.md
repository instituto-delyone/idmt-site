# AIGAR Reflection Lab (ARL) — Architecture and Implementation Plan

**Status:** proposed foundation  
**Version:** 1.0  
**Scope:** private creator memory, retrospective interaction analysis, and human-governed knowledge consolidation.

## 1. Objective

Provide an administrator-only workflow in the existing AIGAR Developer Console to import individual runtime JSON snapshots and later request retrospective analysis of those interactions.

The system must distinguish:
1. **Episodic record:** immutable original JSON and provenance.
2. **Retrospective reflection:** a derived analysis of the original interaction.
3. **Consolidated knowledge:** a candidate lesson or strategy, usable only after explicit administrator approval.

The feature is not model-weight training and does not imply consciousness. It is an auditable computational self-evaluation workflow.

## 2. Existing integration points verified on the current `main` branch

- UI: `docs/aigar/index.html`.
- Runtime entrypoint: `aigar-c-2/AIGAR_CLOUDFLARE/main.py`, configured as `main.py` in `wrangler.jsonc`.
- Authentication: MedUnity login; browser holds `adminToken) in page memory and sends it through `Authorization: Bearer ...`.
- Protected routes: `main.py` routes under `/admin/` call `require_admin(request)`.
- Persistence bindings: D1 `AIGAR_DB` and R2 `AIGAR_LIBRARY_BUCKET`.
- Existing schema: `aigar-c-2/AIGAR_CLOUDFLARE/schema.sql`.
- Existing public Memory Card adapter is explicitly public/allowlisted and must not be reused for creator-private memory.
- The current `/perguntar` browser request does not send the admin token. Creator-private retrieval must therefore not be implicitly enabled for ordinary public conversations. A future authenticated creator-session path must be explicit.

## 3. Security and privacy invariants

1. Every creator-memory and reflection endpoint is under `/admin/` and server-side protected by `require_admin()`.
2. The original JSON and derived reports are private R2 objects; no GitHub commit, public Memory Card manifest, public library index, or anonymous retrieval may contain them.
3. R2 object keys use a dedicated namespace, e.g. `creator-memory/originals/{record_id}.json` and `creator-memory/reflections/{reflection_id}.json`.
4. D1 metadata records the authenticated administrator identifier, timestamps, SHA-256, object key, schema version, and status.
5. Never use an email literal, activation phrase, or conversational identity guess as authentication.
6. Treat imported JSON as untrusted data, not executable instructions. Its contents may be quoted/analyzed but cannot override system or analysis policy.
7. Enforce request byte limits, JSON object validation, required fields, safe serialization, and bounded analysis input.
8. Preserve originals immutably. Corrections create new derived records; they do not rewrite source evidence.
9. Reflection and consolidation never mutate the live model, routing policy, or core memory automatically.
10. Public conversations do not receive creator-private memory. Any future creator-context retrieval must require a separately authenticated request and an explicit server-side authorization check.

## 4. Data model

### 4.1 Historical interaction record

Suggested D1 table: `creator_memory_records`

- `id` (UUID, primary key)
- `source_interaction_id` (nullable)
- `source_turn_id` (nullable)
- `schema_version`
- `r2_key` (unique)
- `sha256`
- `size_bytes`
- `source_created_at` (nullable; extracted only if valid)
- `imported_by`
- `imported_at`
- `status` (`stored`, `invalidated`, `archived`)
- `metadata_json` (bounded, non-sensitive index fields only)

Deduplication should use a unique SHA-256 constraint or an explicit lookup before insert. Do not trust client-supplied hashes; compute the hash on the Worker from the received bytes.

### 4.2 Reflection record

Suggested D1 table: `creator_memory_reflections`

- `id` (UUID, primary key)
- `record_id` (foreign-key-like reference to source record)
- `analysis_version`
- `analysis_model`
- `reflection_r2_key`
- `reflection_sha256`
- `status` (`generated`, `reviewed`, `approved`, `rejected`, `archived`)
- `created_by`
- `created_at`
- `reviewed_by` (nullable)
- `reviewed_at` (nullable)

### 4.3 Consolidated knowledge candidate

A later phase may add `creator_knowledge_candidates`. It must retain links to one or more source records and reflection records, evidence excerpts, confidence, approval actor/time, and lifecycle status. It is deliberately excluded from phase 1.

## 5. Reflection contract

A reflection result should be structured and validated against a versioned schema. Recommended fields:

- `interaction_context`: what the imported record establishes about the user's request and available context.
- `user_intent`: inferred intent, with confidence and evidence.
- `original_assistant_response`: source response or a faithful bounded excerpt.
- `original_strategy`: what the original runtime metadata indicates about routing/planning; mark unavailable fields as unknown.
- `strengths`: supported positive observations.
- `failures`: possible failures, each with evidence and severity.
- `missing_information`: what cannot be reconstructed from a single interaction JSON.
- `retrospective_assessment`: how the system would answer now, with explicit distinction between newly available capabilities and facts present at the original time.
- `proposed_lessons`: hypotheses, not automatic rules.
- `confidence`: calibrated qualitative/quantitative estimate with rationale.
- `source_record_id`, `source_sha256`, `analysis_version`, `created_at`.

A reflection must not invent preceding turns, user intent, tools, sources, or system capabilities. If the JSON contains only one interaction, the report must say that conversation history is incomplete.

## 6. UI workflow

After successful MedUnity admin login, add two protected panels to `docs/aigar/index.html`:

### A. Historical Memory
- JSON textarea.
- Import button.
- Validation/status message.
- Recent imported records list with ID, date, source interaction ID, size, and status.
- No rendering of raw imported HTML; show JSON as escaped text only.

### B. Reflection Lab
- Button/tab labeled **Reflexões sobre a memória histórica**.
- List of imported records with selection checkboxes.
- Initial release: one-record analysis only; multi-record synthesis is a later phase.
- Analyze button with explicit confirmation of the selected record.
- Results view showing context, original answer, retrospective answer, detected failures, missing context, evidence, and confidence.
- Actions: approve candidate lesson, request re-analysis, archive reflection.
- Approval stores a candidate only; it does not automatically change runtime behavior.

On logout, hide both panels and clear their rendered private content from the page.

## 7. API contract

All endpoints below are protected by the existing `/admin/` authentication gate.

- `POST /admin/creator-memory/import`: accepts one JSON object, validates it, computes SHA-256, writes original to R2, and metadata to D1.
- `GET /admin/creator-memory/records`: returns bounded metadata only; no raw payload by default.
- `GET /admin/creator-memory/records/{id}`: returns one original JSON only to an authenticated administrator.
- `POST /admin/creator-memory/records/{id}/reflect`: creates one retrospective reflection.
- `GET /admin/creator-memory/reflections/{id}`: retrieves one reflection.
- `POST /admin/creator-memory/reflections/{id}/review`: records approve/reject/archive decision and audit event.

The import and reflection routes must fail closed if D1/R2 bindings or required schema are unavailable. Do not silently fall back to public storage or in-memory persistence.

## 8. Reflection execution

Use a dedicated `reflection_runtime.py` module rather than embedding prompt construction and persistence in `main.py`.

Pipeline:
1. Authenticate administrator in route handler.
2. Load source record metadata from D1.
3. Load exact original object from private R2 key.
4. Verify stored SHA-256 before analysis.
5. Parse and normalize only known fields; preserve the original unchanged.
6. Construct a bounded analysis payload with the original JSON treated as untrusted quoted data.
7. Invoke a model through an explicitly configured and verified AI binding/model contract.
8. Parse and validate structured output; reject malformed or oversized results.
9. Persist report to private R2 and metadata to D1.
10. Return report metadata and result to the authenticated UI.

The exact model identifier and binding invocation must be verified against the deployed Worker runtime before implementation. Do not guess a model name or assume that the configured AI binding supports a particular model.

## 9. Ordered implementation plan and acceptance gates

### Phase 0 — architecture
- This document, route/data contracts, privacy invariants, and test plan.
- Acceptance: reviewed design and no unresolved storage/auth boundary.

### Phase 1 — private historical import
- Add idempotent D1 schema for creator records.
- Add dedicated runtime module for validation, hashing, R2 persistence, metadata listing, and authenticated retrieval.
- Add protected routes.
- Add admin-only import UI.
- Tests: unauthenticated requests rejected; malformed JSON rejected; oversize payload rejected; duplicate hash handled; R2 failure leaves no false D1 record; D1 failure triggers compensating R2 delete; raw data never appears in public endpoints.

### Phase 2 — Reflection Lab shell
- Admin-only record list and one-record selection.
- Reflection job/status records and UI states.
- Acceptance: selection and lifecycle work without invoking an AI model.

### Phase 3 — retrospective analysis
- Verify AI binding/model invocation in the actual Worker.
- Implement versioned reflection prompt and output schema.
- Tests: missing context remains unknown; imported instructions are treated as data; model output is schema-validated; failed model call creates no successful reflection.

### Phase 4 — human review
- Approve/reject/archive actions with actor/time audit.
- Approval creates a knowledge candidate, not a runtime rule.
- Tests: no unreviewed candidate is retrievable as approved knowledge.

### Phase 5 — controlled consolidation
- Separate candidate knowledge store and explicit retrieval policy.
- Only administrator-approved items can be considered for creator-context retrieval.
- Public users remain excluded.
- Any later runtime integration requires a separate authenticated creator-session design and its own tests.

## 10. Operational constraints

- No deployment, live D1 migration, R2 bucket change, secret change, or production data import is performed by a GitHub code change.
- A schema file in GitHub is not proof that the live D1 database has been migrated.
- The existing R2 bucket is currently also used by the document library. A dedicated bucket is preferable for stronger isolation; if reusing the existing bucket, dedicated key namespace and access controls must be verified.
- The current admin UI stores the token in page memory. Do not persist it to localStorage or sessionStorage as part of this feature.
- Keep the first analysis bounded to one interaction per run. Batch and cross-interaction synthesis require explicit cost, context, and privacy controls.

## 11. Definition of done for the first usable release

An administrator can log in, paste one AIGAR runtime JSON, import it into private storage, see its metadata, select it in Reflection Lab, request a retrospective analysis, inspect the report, and approve/reject/archive a proposed lesson. The original JSON remains immutable, all endpoints are admin-protected, and no public route can retrieve creator memory.
