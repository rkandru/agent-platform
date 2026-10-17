# Guardrails check service (D23, D34)

- **NeMo Guardrails server**, pinned to **0.24.x**. Each minor release breaks the API, so upgrade only with a regression run.
  - Runs on CPU.
  - Phase 1 rails: regex/secret patterns, PII (Presidio) and the jailbreak heuristics in `config/config.yml`.
  - Later: self-check rails that use the `guardrail-judge` model through LiteLLM. No GPU needed.
- **guardrails-adapter.** A small in-house sidecar that translates agentgateway's calls into `POST /v1/checks`, because agentgateway has no native NeMo integration. It has three inputs:
  - the MCP guardrail processor (gRPC, port 4317), on `tools/call` requests and results;
  - the LLM webhook;
  - an Envoy ext_proc endpoint (gRPC, port 9002) for A2A messages (D47, ADR 0016). Requests arrive buffered and responses streamed. Rules can use the `caller`, `callee` and `edge` (same-team / cross-team) metadata.
- **Fail closed** on `tools/call` and A2A (set in `agentgateway/egress.yaml`).
- **The phase-3 LLM judge** follows the per-tier runtime rules in ADR 0018.
- **Defence in depth only.** Identity, intersection and approval grants are the primary controls.
