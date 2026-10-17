# 0011 — All MCP servers behind the gateway; the broker holds vendor tokens

- Status: Accepted (2026-10-10)
- Decisions: D13, D38, D42, D43, D45, D46

## Decision

- **Every MCP server sits behind agentgateway.** Kyverno rejects any `RemoteMCPServer` not pointing at `agw-egress`.
- **Self-hosted servers** (Grafana MCP, kagent-tools for Kubernetes and Argo CD, GitHub) keep their downstream credentials server-side, sourced from Vault.
- **Vendor-hosted servers** (Atlassian Rovo MCP v2) use the vendor's own OAuth, held on the gateway side:
  1. The user is redirected to the vendor's consent page once, through our **credential broker**.
  2. The broker stores the tokens in Vault.
  3. On each call, agentgateway's open-source `backend.auth.oauthTokenExchange` calls the broker's RFC 8693 endpoint, keyed on `jwt.sub`.
  4. The gateway overwrites `Authorization`, so the Keycloak JWT never reaches the vendor and the vendor token never reaches the agent.
  5. If the user isn't linked, an `extAuth` check returns a connect URL (a -32042-style error).
- **Pre-check for vendor MCPs.** CEL tool allowlists, guardrails and approval-grant checks run at the gateway before any vendor call.
- **ServiceNow** is out of scope.

## Why not the alternatives

- **Keycloak as the token store.** Atlassian isn't a full OIDC provider, and Keycloak's generic OAuth 2.0 provider doesn't refresh tokens through the V2 API.
- **Solo Enterprise's built-in token vault.** Paid. Revisit it if the broker becomes a burden.
- **Plain MCP OAuth in the agent session.** It puts user tokens inside agents, which violates ADR 0001.

## Open

- An Atlassian admin must allowlist the broker's domain and the gateway's egress IPs.
- Unverified: whether a self-registered client can request the `*:agent-interface` scopes.
- kagent discovers tools under a fixed identity. Use a service-account API token for discovery, or per-session listing.
