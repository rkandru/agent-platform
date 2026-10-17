# 0005 — Risk tiers and argument-bound approval grants

- Status: Accepted (2026-10-10)
- Decisions: D4, D14, D29

## Decision

**Tiers:**

- **T0:** read-only.
- **T1:** reversible writes (PR, comment, ticket, non-prod sync).
- **T2:** irreversible, prod-impacting or externally visible actions.

**Approvals:**

- **Non-prod T2:** the requester may approve.
- **Prod T2:** four-eyes from the owning team; the requester can't approve their own action.
- **Autonomous runs:** requests go to the owning team's channel.
- **Argo CD-managed prod changes:** only through GitOps PRs.
- **Direct prod writes:** only from an allowlist of ops actions (restart, scale, cordon), with four-eyes approval.

**How it's enforced (layered):**

- kagent's `requireApproval` (or the harness prompt) is the user experience only. It runs inside the agent runtime, so it doesn't cover agents we didn't build or the coding harnesses.
- The **approval service** mints signed, single-use grants. Each grant is bound to the tool and to `sha256` of the canonical JSON of its arguments (RFC 8785), and expires after about 15 minutes.
- T2 tool servers verify grants in-process. For vendor MCPs, which can't verify grants, agentgateway's `extAuth` does it.

## Consequences

- Every self-hosted T2 MCP server embeds the verifier library.
- Grant replay is prevented with a `jti` store (Redis `SETNX`).
- Approval decisions are audit events.
