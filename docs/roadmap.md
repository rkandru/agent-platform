# Roadmap and acceptance tests

As of 2026-10-12. Weeks count from kickoff. Phase 3 is open-ended.

Agents touch real systems only after the **security gate** at the end of phase 1. To pass the gate, all phase-1 acceptance tests must pass and security must sign off.

## Phase 0 — urgent fixes (weeks 0–2)

- [ ] Put JWT validation in front of the kagent controller. Then add a NetworkPolicy so port 8083 is reachable only from agentgateway (see `gitops/platform/kagent/networkpolicy-controller.yaml`). Today `trusted-proxy` mode trusts unsigned JWTs.
- [ ] Upgrade Keycloak to 26.8. Enable these features:
  - `token-exchange-delegation`
  - `parameterized-scopes`
  - `identity-brokering-api:v2`
  - federated client authentication (supported since 26.6)
- [ ] Upgrade agentgateway to 1.6.x.
- [ ] Set kagent `database.postgres.sessionRetentionDays: 90` and move to an external Postgres (`gitops/platform/kagent/values-prod.yaml`).
- [ ] Inventory existing MCP servers: Grafana MCP, Atlassian MCP, and any others. Record how each authenticates today.
- [ ] Ask IT whether M365/Entra is federated with Okta.
- [ ] Confirm the Vault GitHub OIDC roles bind `ref`/`environment` claims to protected refs (D37).

## Phase 1 — governance foundation (weeks 2–10)

- [ ] Keycloak:
  - [ ] An `agents` realm config with an agent client template that uses federated ServiceAccount authentication.
  - [ ] The token-exchange downscope policy.
  - [ ] The broker client.
- [ ] agentgateway inbound:
  - [ ] Routes in front of the kagent UI API and A2A.
  - [ ] JWT validation.
  - [ ] Agent ACL rules in CEL, generated from Agent labels.
- [ ] agentgateway egress:
  - [ ] One backend per MCP server and one for LiteLLM.
  - [ ] Tool allowlists in CEL.
  - [ ] ext_authz to the approval service and the link check.
  - [ ] Rate limits.
  - [ ] Guardrail webhooks.
  - [ ] A2A content inspection: `extProc` to the guardrails adapter, rules only (D47).
- [ ] Cilium default-deny egress in agent namespaces, with an allowlist for agentgateway and the egress proxy.
- [ ] Kyverno policies:
  - [ ] Required Agent labels.
  - [ ] `ModelConfig` and `RemoteMCPServer` must point at the gateway.
  - [ ] gVisor on sandboxes.
  - [ ] Only Argo CD may write Agents in team namespaces.
- [ ] LiteLLM: one virtual key per agent, team budgets, and the NeMo Guardrails custom guardrail.
- [ ] NeMo Guardrails check service on CPU: regex, PII and secret checks, plus JailbreakDetect. The guardrails adapter serves the MCP guardrail processor, the LLM webhook and an ext_proc endpoint for A2A.
- [ ] OpenTelemetry Collector: redaction, plus routing to the ops, content and audit tenants. Create the S3 bucket with Object Lock in compliance mode, 13 months.
- [ ] Credential broker:
  - [ ] Keycloak linking.
  - [ ] Atlassian connect and callback.
  - [ ] The RFC 8693 endpoint.
  - [ ] Refresh and revoke.
  - [ ] The connected-accounts page.
- [ ] Approval service: grant minting, ext_authz verification, and the verifier library for MCP servers.
- [ ] Minimal intake service for Slack: routing, approval buttons and linking. It replaces the current adapter.
- [ ] Move Grafana MCP and Atlassian MCP behind the gateway.
- [ ] garak CI job against LiteLLM.
- [ ] Kill-switch runbook drill and the lifecycle process (onboarding PR template, registry).
- [ ] Agent registry covering all three kinds of agent: platform (CRDs), local (LiteLLM key owners and client names) and SaaS (vendor admin consoles, Okta). Inventory only (D48).
- [ ] Activity map in Grafana: live map, interaction log, declared vs used edges, registry view (D50). Edges come from gateway logs and metrics with a CEL-added `caller_agent` field; Tempo service graphs can't separate agents.
- [ ] Spikes, to be resolved before the gate:
  - [ ] Does agentgateway's `source.unverifiedWorkload` resolve agent pods in our install? If not, use per-agent Keycloak tokens on every route.
  - [ ] Can Keycloak act as kagent 0.10's STS (`KAGENT_STS_*`)? If not, the broker fronts the exchange.
  - [ ] Does Atlassian accept a broker-registered client asking for the `*:agent-interface` scopes, and how will kagent discover the tools?

### Phase-1 acceptance tests (the security gate)

| # | Test | Expected result |
| --- | --- | --- |
| 1 | Send a forged or unsigned JWT to the kagent UI API and to A2A. Then connect to the controller on port 8083 from an agent namespace. | 401 at agentgateway; the direct connection is refused |
| 2 | A user outside an agent's `audience` group invokes it from the UI and over A2A. | 403 |
| 3 | From an agent pod, `curl` the internet, LiteLLM directly, and an MCP server directly. | All blocked; only agentgateway is reachable |
| 4 | An admin uses a read-only agent. Then a low-privilege user uses a powerful agent. | The admin gets read-only access; the low-privilege user gets only their own rights |
| 5 | Call a T2 tool with no grant, a replayed grant, and a grant whose arguments don't match. | All rejected and audited |
| 6 | An unlinked user calls an Atlassian tool, then links and calls again. Then inspect spans, logs and sessions. | First call: a connect URL. After linking: success. No vendor token appears in agent telemetry or sessions |
| 7 | Inspect spans from an agent that hasn't opted in. Then try to delete an object in the audit bucket. | No prompts or tool arguments in the spans; the delete is denied by Object Lock |
| 8 | Kill-switch drill: gateway deny on one agent, then the global freeze. | Calls blocked in under 1 minute |
| 9 | Run CI on an agent-authored branch that requests Vault secrets. | Denied |
| 10 | Over an allowed A2A edge, send a brief containing a test card number and a test secret. Then send one in a streamed response. | Both blocked at the gateway; the audit record names the caller, callee and rule |
| 11 | After tests 2, 5 and 10, open the activity map. | Every call, including the denied ones, appears in the interaction log with agent, user, target and result |

## Phase 2 — coding-agent pilot (weeks 8–16)

The cluster can be built from week 8. The pilot team gets access only after the gate.

- [ ] A kagent 1.x pilot cluster on Talos, with the `gvisor` extension and Cilium. agentgateway egress points at LiteLLM.
- [ ] A GitHub App per harness: `agent-platform-claude` and `agent-platform-codex`. Rulesets on the pilot repos.
- [ ] A hardened webhook ingress: HMAC verification, source-IP allowlist, enqueue only.
- [ ] Intake for GitHub and Jira:
  - [ ] Auto-triage of new bug reports (read-only).
  - [ ] Label and comment triggers.
  - [ ] Status posted back.
- [ ] A per-task LiteLLM key with a $20 budget and a 60-minute TTL. Concurrency caps: 20 across the platform, 5 per team.
- [ ] Pilot review at week 16, covering merged-PR rate, review time, cost per task and incidents.

## Phase 3 — scale-out (from week 16)

- [ ] Team chat/ops agents through the onboarding PR, plus A2A edges.
- [ ] The LLM-judge guardrail through LiteLLM, under the per-tier runtime rules, with a labelled sample set in CI (D49). First use: cross-team A2A edges (D47).
- [ ] Local-agent controls: managed harness config routing through LiteLLM and agentgateway, and a Keycloak client per harness (D48).
- [ ] SaaS-agent controls: OAuth app and agent-feature allowlists in each vendor console, and quarterly grant review (D48).
- [ ] Teams bot and Outlook shared mailboxes, once IT confirms Entra.
- [ ] Coding agents on Bitbucket Data Center.
- [ ] The curated knowledge MCP.
- [ ] Rebuild prod chat/ops agents on kagent 1.x once it reaches GA.
- [ ] Re-evaluate Cursor, OpenShell, Okta for AI Agents and per-user memory.
