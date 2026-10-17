# 0017 — Govern agents we don't run: local and SaaS agents

- Status: Accepted (2026-10-12)
- Decisions: D48
- Extends: [0013](0013-vendor-gate.md), [0015](0015-lifecycle-and-kill-switch.md)

## Context

The AgentSecOps talk (AI governance session, Japan, October 2026) defined an agent as anything that makes decisions and takes actions. A2A is just one way agents interact. It named three kinds: A2A agents, SaaS agents and local agents.

Our controls cover the agents we run (kagent agents and coding sandboxes). Two kinds sit outside them:

- **Local agents:** Claude Code, Codex and Cursor on engineers' laptops. They act with the engineer's full permissions, which is the risk security raised.
- **SaaS agents:** agents built into vendor products, such as Atlassian Rovo, GitHub Copilot, Slack AI, Microsoft 365 Copilot, and any Grok Bot trial. They act through OAuth grants inside the vendor's platform.

## Decision

**Phase 1: inventory.** The agent registry lists all three kinds. Each entry has an owner and a review date.

| Kind | Source of the inventory |
| --- | --- |
| Platform | Agent CRDs (as today) |
| Local | LiteLLM key owners and the client name each request reports |
| SaaS | Vendor admin consoles (Atlassian, GitHub, Slack, Okta): agent features that are switched on, and OAuth apps with agent capabilities |

**Phase 3: controls for local agents.**

- Model calls go only through LiteLLM, with per-user keys.
- A centrally managed harness configuration points model and MCP traffic at LiteLLM and agentgateway, and allowlists MCP servers. Claude Code supports admin-managed settings; Codex and Cursor still need checking.
- Each harness gets its own Keycloak public client, for example `local-claude-code`, used through browser login. Its tokens name the harness in `azp`. The gateway then treats those calls as agent calls: tool allowlists apply, and T2 tools need an approval grant even though a human is at the keyboard.

**Phase 3: controls for SaaS agents.**

- In each vendor's admin console (Atlassian, GitHub, Slack, M365), only approved OAuth apps and agent features are switched on.
- Their grants are reviewed quarterly, together with agent recertification (0015).
- Any new SaaS agent goes through the vendor gate (0013).

**Out of scope:** blocking local agents outright. Endpoint controls belong to IT.

## Consequences

- The registry becomes more than a dump of the CRDs. It needs a collector for each source.
- Local agents still act as the human. The intersection rule doesn't apply to them. The `azp` marker only lets us add agent-style limits on top of the human's own rights.
