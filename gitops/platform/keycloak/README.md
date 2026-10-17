# Keycloak: the agent identity plane (D11, D12)

Applied with [keycloak-config-cli](https://github.com/adorsys/keycloak-config-cli) as a partial import into the **existing AD-backed realm** (`platform` here). Token exchange V2 only works inside a single realm, so agents and users must share a realm.

## Prerequisites

- Keycloak **26.8**. Federated client authentication with Kubernetes ServiceAccount tokens has been supported since 26.6.
- Server features to enable for the `act` claim (Preview in 26.8):
  `--features=token-exchange-delegation,parameterized-scopes`
- Keycloak must be able to fetch `<cluster issuer>/.well-known/openid-configuration` from each Talos cluster:
  - **Keycloak outside the cluster:** expose the issuer anonymously and set `cluster.apiServer.extraArgs.service-account-issuer` accordingly.
  - **Keycloak inside the cluster:** it uses its own ServiceAccount to read the issuer.

## How an agent gets a token

The agent pod mounts a projected ServiceAccount token whose `audience` is the realm issuer, with `expirationSeconds: 600`. It then calls the realm's token endpoint:

```
POST /realms/platform/protocol/openid-connect/token
grant_type=client_credentials
client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer
client_assertion=<projected SA token>
```

The client matches when its `jwt.credential.issuer` is the IdP alias and its `jwt.credential.sub` is `system:serviceaccount:<ns>:<sa>`.

This pattern comes from Keycloak's own demo: https://github.com/keycloak/keycloak-playground/tree/main/federated-client-authentication/kubernetes

## Intersection (D3)

- `fullScopeAllowed: false` on every agent client: a token carries only the roles where the user's role mappings and the client's scope overlap.
- Standard token exchange V2 (`standard.token.exchange.enabled`): a requested `audience` can only narrow the token.
- The `agent-downscope` client policy rejects any exchange that adds scopes.
- The `agent_id` hardcoded claim identifies the agent until `act` is GA.

## Files

- `realm-platform-agents.json`: the Kubernetes IdPs, tool audience scopes, the downscope policy, and the broker and intake clients.
- `agent-client-template.json`: one client per agent, rendered by `tools/render_agent_policies.py` from the Agent CR labels.

## SPIKE(kagent-sts)

kagent 0.10 has an RFC 8693 client (`KAGENT_STS_WELL_KNOWN_URI`, `KAGENT_STS_AUDIENCE`). It sends the user's JWT as `subject_token` and the agent's ServiceAccount token as `actor_token`.

It is unverified whether Keycloak's token endpoint accepts this as-is: Keycloak expects the actor to be a *Keycloak* token. Test this in phase 1. If it fails, the credential broker fronts the exchange: it authenticates the agent with its ServiceAccount token, then calls Keycloak.
