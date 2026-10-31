# Branch reconciliation — AIGAR

## Purpose

This note prevents an accidental merge of independent AIGAR histories.

## Current policy

- `main` remains the protected integration baseline.
- `neurocognitive-migration` is a separate migration history.
- Do not merge the entire migration branch solely to resolve ahead/behind counts.
- Review the commit graph and changed files first; cherry-pick only commits whose contracts and dependencies have been reviewed.
- Preserve the Worker migration boundary documented in `aigar-c-2/AIGAR_CLOUDFLARE/README.md`.

## Re-check before integration

Run from a local clone:

```bash
git fetch origin
git rev-list --left-right --count origin/main...origin/neurocognitive-migration
git log --left-right --graph --oneline origin/main...origin/neurocognitive-migration
git diff --stat origin/main...origin/neurocognitive-migration
git diff --name-status origin/main...origin/neurocognitive-migration
```

The ahead/behind count is a snapshot, not a merge recommendation. Recompute it immediately before any integration work.

## Acceptance criteria

1. Identify the commits that introduce each runtime or contract change.
2. Check Python dependencies, import paths, Worker packaging, and tests.
3. Confirm no protected Worker directory or production binding is overwritten unintentionally.
4. Run the relevant CI workflows on the proposed integration branch.
5. Integrate selected changes through a reviewed pull request.

This document records a safe integration procedure; it does not claim that the two branches have already been reconciled.
