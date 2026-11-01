# ACLR transition contract

## Runtime modes
- \`shadow\` (default): ACLR traverses the versioned R2 catalogue for diagnostics; legacy evidence remains authoritative.
- \`candidate\`: opt-in through Worker environment variable \`ACLR_MODE=candidate\`; only evidence with \`source_status: verified\` or \`reviewed\` may enter CORTEX.
- Unknown values fail closed to \`shadow\`.

## Safety and compatibility
- No public endpoint, request/response input contract, route, HREF, or frontend change.
- ACLR failure, empty retrieval, or synthetic/prototype-only content preserves the legacy evidence list.
- Response adds \`aclr_transition\` diagnostics; \`aclr_shadow\` remains a compatibility alias.

## Catalogue promotion
The current catalogue remains \`aclr/catalog/v1/\`. This change does not promote synthetic fixtures or automatically classify existing uploaded PDFs. Real-library indexing still requires reviewed mapping from domain/subdomain entries to \`documents\` / \`document_chunks\` identifiers and verified R2 keys. Do not enable candidate mode until populated and audited.

## Rollback
Set \`ACLR_MODE=shadow\` or remove the variable. Shadow is the default when unset or invalid.
