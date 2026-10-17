# credential-broker (D12, D42, D45)

The credential broker holds human and vendor tokens, so that agents and kagent never do. It runs in namespace `agent-platform` with ServiceAccount `credential-broker`, authenticates to Keycloak with its ServiceAccount token (`federated-jwt`), and stores tokens in Vault using Vault Kubernetes auth.

## Endpoints

| Method | Path | Caller | Purpose |
| --- | --- | --- | --- |
| GET | `/connect/{provider}` | User's browser (link from intake or the kagent UI) | Starts linking. Logs the user into Keycloak, checks that the signed `state` belongs to the same `sub`, then redirects to the provider with PKCE (S256) and `offline_access` |
| GET | `/callback/{provider}` | Provider | Exchanges the code and stores tokens at `vault: kv/mcp-tokens/{provider}/{kc_sub}` |
| POST | `/oauth/token` | agentgateway `oauthTokenExchange` | RFC 8693. Validates `subject_token` as a Keycloak JWT, using `sub` and ignoring `act`. Returns the stored vendor `access_token` and `expires_in`, refreshing it first if less than 5 minutes remain. Refresh is single-flight, with a Vault-backed lock per `(provider, sub)`, because Atlassian rotates refresh tokens and allows 10 minutes for reuse |
| GET | `/v1/links/{provider}?sub=` | approval-service (link check) | Returns `linked` / `expired` / `missing` plus a `connect_url` |
| GET | `/accounts` | User's browser | Connected-accounts page: list and disconnect |
| DELETE | `/accounts/{provider}` | User's browser | Revokes the token at the provider (`https://auth.atlassian.com/oauth/revoke`) and deletes it from Vault |

## Providers

- **`keycloak`**: the user's own Keycloak refresh token, for delegated flows that start in Slack (D12).
- **`atlassian`**: Rovo MCP v2 at `https://mcp.atlassian.com/v2/mcp`.
  - The broker registers once as a confidential client, using a Client ID Metadata Document or dynamic client registration against `auth.atlassian.com`.
  - Scopes are the minimum needed, for example `read:jira:agent-interface write:jira:agent-interface offline_access`.
  - An Atlassian admin must allowlist the broker's domain and the gateway's egress IPs.

## Linking flow

```mermaid
sequenceDiagram
  autonumber
  participant U as User (browser)
  participant A as kagent agent
  participant G as agw-egress
  participant P as approval-service (ext_authz)
  participant B as credential-broker
  participant V as Vault
  participant X as Atlassian MCP
  A->>G: tools/call (Authorization: user's Keycloak JWT)
  G->>P: ext_authz (sub, agent, tool, args)
  P->>B: GET /v1/links/atlassian?sub=
  B-->>P: missing, connect_url
  P-->>G: deny 401 + JSON-RPC -32042 {url: connect_url}
  G-->>A: error with connect URL (shown to user as text)
  U->>B: GET /connect/atlassian (Keycloak login, same sub)
  B->>X: OAuth authorize + PKCE; callback with code
  B->>V: store tokens at mcp-tokens/atlassian/{sub}
  A->>G: retry tools/call
  G->>P: ext_authz -> allow
  G->>B: POST /oauth/token (subject_token = user JWT)
  B->>V: read (refresh if near expiry)
  B-->>G: access_token (vendor)
  G->>X: tools/call with vendor token (Keycloak JWT never forwarded)
```

## Non-negotiables

- **Never log tokens.** Spans carry `sub`, the provider and the outcome only.
- **Treat Vault policy as the security boundary.** Only `credential-broker` can read `kv/mcp-tokens/*`.
- **Delete the stored token on `invalid_grant`**, and return `missing` so the user re-links.
