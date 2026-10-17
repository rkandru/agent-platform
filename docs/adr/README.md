# Architecture decision records

Records 0001–0015 were accepted on 2026-10-10 and 0016–0019 on 2026-10-12. The decision IDs (`Dn`) come from the design review and are indexed in `../architecture.md`. To change a decision, write a new ADR that supersedes the old one; don't edit an accepted record.

| ADR | Title |
| --- | --- |
| [0001](0001-agent-identity-model.md) | Agents have their own identity; humans only narrow it |
| [0002](0002-keycloak-identity-plane.md) | Keycloak is the agent identity plane |
| [0003](0003-chokepoints-and-llm-path.md) | Every agent call passes a chokepoint; agents hold no keys |
| [0004](0004-agentgateway-as-pep.md) | agentgateway is the access-control point in front of kagent |
| [0005](0005-risk-tiers-and-approvals.md) | Risk tiers and argument-bound approval grants |
| [0006](0006-kagent-version-strategy.md) | kagent 0.10 in prod, a kagent 1.x pilot for coding agents |
| [0007](0007-coding-agents.md) | Coding agents: Claude Code + Codex, in-house, PR-only |
| [0008](0008-observability-and-audit.md) | Metadata-only telemetry by default; WORM audit trail |
| [0009](0009-memory-and-context.md) | No long-term memory in v1; curated team knowledge |
| [0010](0010-a2a-governance.md) | Agent-to-agent calls are allowlisted and narrow-only |
| [0011](0011-mcp-and-vendor-oauth.md) | All MCP servers behind the gateway; the broker holds vendor tokens |
| [0012](0012-guardrails.md) | NeMo Guardrails as defence in depth |
| [0013](0013-vendor-gate.md) | Vendor gate; no Grok Bot; Cursor parked |
| [0014](0014-channels-and-intake.md) | kagent UI first; Slack only where needed; one intake service |
| [0015](0015-lifecycle-and-kill-switch.md) | Agent lifecycle gates and kill switches |
| [0016](0016-a2a-content-inspection.md) | Inspect what agents say to each other, not just whether they may talk |
| [0017](0017-agents-we-dont-run.md) | Govern agents we don't run: local and SaaS agents |
| [0018](0018-semantic-check-runtime-rules.md) | Runtime rules for semantic (LLM-judge) checks |
| [0019](0019-agent-activity-map.md) | Agent activity map: who talked to whom, and when |
