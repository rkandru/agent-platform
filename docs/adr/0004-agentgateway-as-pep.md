# 0004 — agentgateway is the access-control point in front of kagent

- Status: Accepted (2026-10-10)
- Decisions: D25, D41

## Context

- Open-source kagent's `trusted-proxy` mode decodes JWTs **without verifying the signature or expiry**.
- Its authorizer is a no-op: any logged-in user can invoke any agent.
- Per-agent `AccessPolicy` exists only in Solo Enterprise.

## Decision

agentgateway (`agw-inbound`) sits in front of every way into kagent: the UI API, A2A, the intake service and agent-to-agent calls.

- It verifies Keycloak JWTs (`jwtAuthentication: Strict`).
- It applies a per-agent deny rule unless the caller is in the agent's `audience` group. The rule is rendered from Agent CR labels by `tools/render_agent_policies.py`.
- A NetworkPolicy makes agentgateway and the UI the only callers of controller port 8083.
- AD groups (synced to Keycloak) are the source of truth for teams. Each group maps to a `team-<group>` namespace, an ACL, a budget and approvers.

## Consequences

- The kagent UI still *lists* every agent; it just can't invoke unauthorized ones. This is acceptable for v1.
- Solo Enterprise isn't pursued now. Revisit it if the in-house authorizer and broker become a burden.
