# 0001 — Agents have their own identity; humans only narrow it

- Status: Accepted (2026-10-10)
- Decisions: D3

## Context

Security's main concern: if an agent acts with an engineer's credentials, it inherits permissions that are often broader than the task needs. At machine speed, that can cause outsized damage. Two further risks:

- A low-privilege user could use a powerful agent as a confused deputy.
- A high-privilege user could hand an agent more power than its purpose warrants.

## Decision

Every agent has its own non-human identity (NHI). There are three cases:

- **A person starts the task.** The user's token is exchanged for a tool-specific token. Its effective permissions are **intersection(agent's allowed scopes, user's permissions)**, and the token carries `sub=user, act=agent`.
- **An autonomous run** (webhook, schedule). The run uses the agent's NHI only.
- **Human credentials.** Agents never hold them: no PATs, session cookies or refresh tokens. User and vendor tokens stay in platform components (the credential broker and agentgateway).

## Consequences

- Every tool server must accept tokens issued for its audience and check the user's real permission where a user is present.
- For autonomous runs, the agent's own grants must be small. Agents are scoped per purpose, not "one agent that can do everything".
- `act` is Preview in Keycloak 26.8. Until it is GA, a custom `agent_id` claim carries the agent identity.

## Alternatives rejected

- **Agent identity only.** It ignores who asked, so a low-privilege user could use a powerful agent as a confused deputy.
- **Delegated user identity only.** Agents would inherit over-broad human permissions, which is the problem we are solving.
