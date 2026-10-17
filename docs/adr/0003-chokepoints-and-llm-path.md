# 0003 — Every agent call passes a chokepoint; agents hold no keys

- Status: Accepted (2026-10-10)
- Decisions: D5, D30, D36

## Decision

1. **Network:** Cilium default-deny egress in agent namespaces. Allowed destinations are DNS, agentgateway egress, the Keycloak token endpoint and the allowlisted egress proxy.
2. **Model calls:** agent → agentgateway → LiteLLM. LiteLLM is the key and budget authority. agentgateway's own LLM-gateway features stay off.
3. **Tool and agent-to-agent calls:** MCP and A2A go through agentgateway only.
4. **No standing downstream credentials.** Tokens are minted per call or per task.
5. **Data:** every provider behind LiteLLM has ZDR terms, so any data class may be sent to it.

## How the "no keys in agents" rule works on kagent 0.10

kagent 0.10 can't present a ServiceAccount token as an LLM API key. So the gateway does the following:

- strips the agent's placeholder key;
- injects its own LiteLLM credential;
- sets `x-agent-id` from the calling pod's workload identity (`source.unverifiedWorkload`);
- applies rate limits per agent.

LiteLLM then tracks spend and budgets per `x-agent-id`.

Coding tasks get per-task LiteLLM keys (`max_budget` $20, 60-minute expiry) minted by intake. On kagent 1.x, the built-in egress gateway injects secrets natively.

## Consequences

- One gateway credential reaches LiteLLM. LiteLLM must be reachable only from the gateway, which a NetworkPolicy enforces.
- SPIKE: confirm the gateway's workload store resolves pod identity in our install. Fallbacks:
  - per-agent Keycloak tokens on LLM calls;
  - Cilium mutual authentication / SPIFFE (`source.spiffeId`).
