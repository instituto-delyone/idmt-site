# ACLR implementation prototype

This package implements the first isolated, pure-Python planning and evidence-contract layer.

- `aclr_contracts.py`: standard-library contract validators matching the v1 JSON contract drafts.
- `aclr_router.py`: fixture-driven Layer A plan construction; always includes the general index.
- `aclr_resolver.py`: evidence-envelope validation, deduplication and path-status aggregation.
- `tests/test_aclr_prototype.py`: deterministic tests over the 3-domain/11-protochunk fixture.

No existing Worker route, HREF, retrieval adapter, R2/D1 object, production library, or user-facing answer path is modified. This is not yet an R2/D1 adapter or production retrieval implementation. The router receives catalogue/index objects from its caller; storage integration is a later phase.
