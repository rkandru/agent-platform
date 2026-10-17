# 0002 — Keycloak is the agent identity plane

- Status: Accepted (2026-10-10)
- Decisions: D11, D12

## Context

Keycloak (owned by DevOps, users sourced from AD) and Okta (owned by IT) run in parallel and are not federated.

**Okta:**

- Cross App Access (ID-JAG) is GA in core SSO.
- Agent identities and agent token exchange need the separate *Okta for AI Agents* subscription.
- Every resource app must implement ID-JAG.

**Keycloak 26.8:**

- Clients can authenticate with Kubernetes ServiceAccount tokens (`federated-jwt`). This has been supported since 26.6.
- Token exchange V2 is supported. A requested audience can only narrow, and a downscope enforcer policy blocks added scopes.
- `act` delegation is Preview.

## Decision

Keycloak is the identity plane for agents. Okta stays the human SSO for SaaS apps.

- Each agent is a confidential Keycloak client using `federated-jwt` against a `kubernetes` identity provider, one per cluster.
- `fullScopeAllowed=false` and the `agent-downscope` client policy enforce the intersection rule.
- Users link their accounts once (D12). Slack can't reach Keycloak, so the in-cluster intake service sends a link and the user's browser logs in. The credential broker keeps the refresh token in Vault.
- **Upgrade from roughly 26.5 to 26.8** before phase 1.

## Consequences

- Agents and users must be in the **same realm**, because V2 exchange only works internal-to-internal.
- Keycloak must reach each cluster's OIDC discovery endpoint.
- SPIKE: confirm Keycloak can serve as kagent 0.10's STS (`KAGENT_STS_*`), which sends the user's JWT as subject and the ServiceAccount token as actor. If not, the broker fronts the exchange.

## Alternatives rejected

- **Okta for AI Agents.** It's a paid add-on owned by IT, and resource apps must support ID-JAG. Revisit it for SaaS apps that support XAA.
- **SPIFFE/SPIRE plus Keycloak.** More moving parts, and Keycloak's JWT-SVID support is still Preview.
