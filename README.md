# Agent platform

This repo holds the design and the phase-1 reference scaffold for our governed agent platform, built on kagent, agentgateway, Keycloak, LiteLLM and Grafana LGTM.

| Path | What it holds |
| --- | --- |
| `docs/architecture.md` | The design. A shareable copy for security is published at https://claude.ai/code/artifact/241c66e4-fa91-451b-b69a-b0d2a6aa0dfa |
| `docs/adr/` | One ADR per decision cluster (decision IDs D1–D46) |
| `docs/roadmap.md` | Phases and the phase-1 acceptance tests (the security gate) |
| `docs/runbooks/` | Operational runbooks (kill switch) |
| `gitops/` | Argo CD apps and platform config: Keycloak, agentgateway, kagent, LiteLLM, guardrails, OTel, Kyverno, Cilium. Team templates are in `gitops/teams/` |
| `services/` | API contracts for the three in-house services: intake, credential broker, approval service |
| `ci/` | garak red-team job |

**Status:** this is a reference scaffold. CRD fields were checked against agentgateway v1.6.0, kagent v0.10.3 and the Keycloak 26.8 federated-client demo. Values marked `# TODO(...)` or `# SPIKE(...)` need a decision or a test in your environment before you apply them. Placeholder domains use `example.com`.
