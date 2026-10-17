# 0015 — Agent lifecycle gates and kill switches

- Status: Accepted (2026-10-10)
- Decisions: D6, D33, D39, D40

## Decision

**Lifecycle:**

1. **Onboarding PR** in `gitops/teams/<group>/agents/`. Kyverno enforces the owner, audience, tier, tools and data-class labels. A T2 tool or a content-capture opt-in needs security CODEOWNERS approval.
2. **Evals.** A task-eval suite and garak run in non-prod; then Argo CD promotes the agent.
3. **Quarterly re-certification** by the owner.
4. **Auto-disable** after 90 days with no owner or no use.
5. **Agent registry** generated from the CRDs, used as audit evidence.

Only Argo CD may write Agents, ModelConfigs and RemoteMCPServers (Kyverno).

**Skills** are pulled from Artifactory as OCI (`spec.skills.refs`). They are unsigned in v1. Restrict who can publish to the skills repo.

**Kill switches** (runbook `docs/runbooks/kill-switch.md`):

1. Deny the agent at agentgateway (`kill-switch-agents`).
2. Block its LiteLLM spend.
3. Disable its Keycloak client.
4. Scale it to zero.

There is also a global freeze (`kill-switch-global-freeze`).

**Auto-trips** suspend the agent and page its owner when any of these happens:

- a budget overrun;
- a tool-call rate spike;
- repeated guardrail violations;
- repeated approval denials;
- an A2A loop.

**Quarterly drill**, with a target of under 1 minute.
