# 0010 — Agent-to-agent calls are allowlisted and narrow-only

- Status: Accepted (2026-10-10)
- Decisions: D21

## Decision

- **Allowed edges.** An Agent's `platform.example.com/a2a-edges` annotation lists the agents it may call. These edges are rendered into a `Require` policy on the egress A2A route. A cross-team edge needs approval from the team that owns the agent being called (CODEOWNERS on that team's folder).
- **Narrow-only hops.** Each hop exchanges the token again, and the result can only be narrower or equal. The `act` chain records the path.
- **Task-scoped context.** The caller passes a task brief plus artifact references, with access scoped to the task. It never passes its full history or memory.

## Open

The depth cap of 3 needs a hop counter, either a header propagated by the runtime or the `act` chain length. Neither kagent 0.10 nor agentgateway enforces this today. SPIKE in phase 3, before cross-team edges are allowed.
