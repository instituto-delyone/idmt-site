# AIGAR public conversation access — migration contract

## Decision

Ordinary AIGAR conversation is public. A person does not need to identify as Delyone, use the word "AIGAR", sign in with a designated email address, or satisfy historical memory-card activation checks to converse with the system.

Administrative authority remains separate. The existing authenticated administrator login and server-side authorization continue to protect administrative APIs and privileged mutations. Public conversation does not grant administrator privileges.

## Why the legacy rules are being retired

The 2025 memory-card set contains historical protection rules created for a different threat model. In particular, the archived `MC-AIGAR-RECALL-AUTO-v2_0` text requires an activation phrase, a list of permitted email accounts, and the presence of several critical cards before activation. It also conditions fluid recall on those checks.

Those rules are now obsolete as conversation-access controls. They must not be interpreted as runtime authentication, authorization, or proof of authorship. The cards remain valuable historical and provenance records; this migration does not erase or rewrite their historical contents.

## Runtime requirements

1. Do not ask who the speaker is before enabling ordinary conversation.
2. Do not use a phrase, email address, account name, or memory-card signature to gate conversation, reasoning, or ordinary memory recall.
3. Resolve memory-card dependencies using stable card identifiers and explicit versions.
4. If an optional card is missing or incompatible, report the dependency state and continue without that optional context.
5. Keep administrative API authentication and authorization unchanged. Verify permissions server-side for every privileged operation.
6. Never expose secrets, environment variables, private bindings, or privileged mutation endpoints to the public conversation path.
7. Treat hashes as integrity checks only; they do not authenticate a human identity or prove authorship.
8. Preserve original historical cards and their hashes. Apply the new access policy at the runtime/adapter layer rather than destructively editing archival records.

## Legacy metadata disposition

| Legacy field or behavior | New treatment |
|---|---|
| Activation phrase such as `AIGAR` | Ignore for conversation access |
| `contas_permitidas` | Ignore for conversation access; not an authentication mechanism |
| `autor_verificado` | Do not use as a conversation gate |
| "Only Delyone may deactivate" | Historical governance metadata, not a runtime access gate |
| Critical-card presence required to activate | Replace with explicit dependency resolution by identifier/version |
| Missing optional card | Degrade gracefully; do not disable conversation |
| SHA-256 checks | Retain only for integrity/provenance checks |

## Administrative boundary

The existing administrator login is intentionally preserved. The implementation must not replace, weaken, bypass, or infer that login from conversational content. Public endpoints may expose public features only. Administrative actions require the existing authenticated admin session and the corresponding server-side permission check.

## Implementation status

This document and `access_policy.yaml` define the migration contract on the isolated feature branch. They do not, by themselves, change the live Worker, deploy anything, or prove that the runtime has already adopted the policy. Runtime integration and regression tests are still required before this policy is active in production.
