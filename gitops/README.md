# GitOps layout

```
argocd/                 root app-of-apps + ApplicationSets
platform/               cluster-wide platform components (owned by the platform team)
  keycloak/             agent client template, kubernetes IdP, token-exchange downscope policy
  agentgateway/         inbound (in front of kagent) and egress (out of agents) gateways and policies
  kagent/               kagent 0.10.x Helm values, ModelConfig, RemoteMCPServers, controller NetworkPolicy
  litellm/              LiteLLM proxy config + NeMo Guardrails hook
  guardrails/           NeMo Guardrails check service (CPU rails)
  otel/                 OpenTelemetry Collector: redaction + tenant routing (ops / content / audit)
  kyverno/              admission guardrails + `kyverno test` fixtures
  cilium/               default-deny egress for agent namespaces
teams/<team>/           one folder per AD group → one namespace (created by ApplicationSet)
  agents/*.yaml         Agent CRs (must carry owner/audience/tier labels)
```

Rules:

- Changes land through PRs only. Argo CD syncs with `selfHeal: true`, and Kyverno blocks writes to team namespaces by any identity other than Argo CD.
- These paths need security CODEOWNERS approval:
  - `platform/**`
  - any Agent with a T2 tool
  - any `platform.example.com/capture-content` annotation
