# 0012 — NeMo Guardrails as defence in depth

- Status: Accepted (2026-10-10)
- Decisions: D23, D34

## Decision

One NeMo Guardrails check service, pinned to 0.24.x, is called from three places:

- a LiteLLM custom guardrail on prompts and responses;
- agentgateway's MCP guardrail processor on `tools/call` requests and results, which fails closed;
- agentgateway's LLM webhook.

A small adapter translates agentgateway's calls to `/v1/checks`.

**Phases:**

- **Phase 1, on CPU:** regex, secret and PII checks plus jailbreak heuristics.
- **Later:** an LLM judge using a small approved model through LiteLLM. **No GPU.**

**Red-teaming:** garak runs weekly in CI against LiteLLM, and before each agent is promoted.

## Not adopted from NVIDIA

- **The "Safety for Agentic AI" blueprint:** deprecated.
- **NeMo microservices:** sunset.
- **OpenShell:** incompatible with gVisor, with best-effort audit only. Revisit in 2027.
- **Agent Toolkit / Helix:** duplicate kagent, LGTM and Argo CD.
- **NIM containers:** they need an AI Enterprise licence, and the open weights can be self-hosted if a GPU is ever justified.
