# agentgateway: the policy enforcement point (D5, D13, D21, D25, D29, D30, D39, D45)

Version **1.6.x**. CRDs are `agentgateway.dev/v1alpha1` (`AgentgatewayBackend`, `AgentgatewayPolicy`) plus Gateway API.

| File | Purpose |
| --- | --- |
| `gateways.yaml` | `agw-inbound` (in front of kagent) and `agw-egress` (the only way out of agent namespaces) |
| `inbound.yaml` | Routes to the kagent API/A2A and UI; JWT verification; per-agent ACL; per-user rate limit |
| `egress-backends.yaml` | LiteLLM, Grafana MCP, Atlassian Rovo MCP (vendor OAuth via the broker), kagent A2A, approval service, guardrails adapter |
| `egress.yaml` | Egress routes; agent identity; tool allowlists; approval-grant and link checks; guardrails; rate limits; telemetry |
| `kill-switch.yaml` | Per-agent deny list + global freeze (D39). Patched by on-call; see `docs/runbooks/kill-switch.md` |
| `generated/` | ACL and tool-allowlist policies rendered from Agent CR labels by `tools/render_agent_policies.py` |

## How the gateway identifies agents and users

- **Agent identity (egress).** `source.unverifiedWorkload.namespace` / `.serviceAccount` come from the gateway's workload store, matched by pod IP. Cilium policy (`../cilium/`) means agent pods can only reach the gateway, and pod IPs can't be spoofed across nodes.
  - **SPIKE(workload-identity):** confirm the workload store is populated in our kgateway-less, ambient-less install. If it isn't, use the Keycloak agent token (`jwt.agent_id`) on MCP routes, and Cilium mutual auth / SPIFFE (`source.spiffeId`) later. kagent 1.x has SPIFFE natively.
- **User identity.** `jwt.sub` / `jwt.groups` come from the Keycloak token that kagent forwards (`allowedHeaders: [Authorization]`). Autonomous runs carry no user JWT, so they are limited to the agent's own allowlist.

## Why the LLM route doesn't use per-agent LiteLLM keys in the pod

kagent 0.10 can't present a ServiceAccount token as an LLM API key. So the gateway does three things:

1. Strips whatever the agent sends.
2. Injects one gateway LiteLLM key.
3. Sets `x-agent-id` from the workload identity.

LiteLLM tracks spend and budget per `x-agent-id` (end-user budgets), so the agent never holds a key (D30). Coding tasks on the kagent 1.x pilot get per-task keys minted by intake.
