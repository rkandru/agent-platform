# 0019 — Agent activity map: who talked to whom, and when

- Status: Accepted (2026-10-12)
- Decisions: D50
- Extends: [0008](0008-observability-and-audit.md), [0015](0015-lifecycle-and-kill-switch.md)

## Context

The AgentSecOps talk (AI governance session, Japan, October 2026) framed agent governance as visualization, traceability and control. We had traceability and control. Security also wants to see which agents talk to which tools and agents, and when.

## Decision

All of these are Grafana dashboards on the existing LGTM stack:

- **Live map.** A Grafana node-graph panel shows agent → tool → agent calls. Its edges come from gateway access logs and metrics, with an added `caller_agent` field (see the spike result below).
- **Interaction log.** A Loki panel on the gateway access logs in the audit tenant shows, for each call: time, calling agent, user, target (agent, MCP server and tool, or model), result and latency.
- **Declared vs used.** This panel compares the A2A edges and tool allowlists declared in the registry with the ones actually used in the last 30 days. Any edge or tool unused for 30 days is flagged to its owner for removal at recertification.
- **Registry view.** One dashboard lists every agent, of all three kinds in [0017](0017-agents-we-dont-run.md). For each, it shows the owner, tier, tools, edges, budget use and last activity.

**Spike result (2026-10-12),** checked in the agentgateway v1.6.0 source:

- Tempo service graphs can't separate agents. Every agent's calls pass through the same gateway node, so the graph shows kagent → gateway → upstream. We use the fallback: edges from the gateway's logs and metrics.
- Access logs already carry `mcp.target`, `mcp.method.name`, `gen_ai.tool.name`, `a2a.method`, `a2a.task.state`, `jwt.sub`, `http.status`, `duration` and `trace.id`. We add `caller_agent` and `target_backend` as CEL fields (`frontend.accessLog.attributes.add`), and `caller_agent` as a metric label (`frontend.metrics.attributes.add`, up to 16 labels).
- The full recipe is in the published doc's agentgateway tab.

## Consequences

The `caller_agent` metric label adds one Prometheus series per agent and target. Keep metric labels to agent, target and result.
