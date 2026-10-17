# 0016 — Inspect what agents say to each other, not just whether they may talk

- Status: Accepted (2026-10-12)
- Decisions: D47
- Extends: [0010](0010-a2a-governance.md)

## Context

The edge allowlist (0010) decides whether agent A may call agent B. It never looks at what A sends. That content is checked later, when B puts it into a model prompt, but that check doesn't know which edge the content came over. So we can't write edge-specific rules such as "no customer PII from team-payments agents to agents in other teams."

The AgentFirewall talk (AI governance session, Japan, October 2026) made the same point: a permitted connection doesn't mean every conversation over it should be permitted.

## Decision

- **Where.** An `extProc` policy on the egress `a2a` route sends every A2A exchange to the guardrails adapter. See `a2a-inspection` in `gitops/platform/agentgateway/egress.yaml`.
- **Requests** are held in full and checked before they are forwarded. The task brief is short by design (0010), so the delay is small.
- **Responses** are checked as they stream. Only deterministic rules run on the stream. On a match, the adapter ends the stream with an error.
- **Edge-aware rules.** The adapter receives the caller, the callee, and whether the edge crosses teams.
- **Phase 1:** regex, PII and secret rules on every edge. Fail closed.
- **Phase 3:** the semantic judge, on cross-team edges only, under the runtime rules in [0018](0018-semantic-check-runtime-rules.md).
- **Audit.** Every block goes to the audit tenant and counts toward the guardrail-violation auto-trip ([0015](0015-lifecycle-and-kill-switch.md)).

## Consequences

- Every A2A call gets one more hop. The buffered request adds latency in proportion to the brief's size.
- Because responses stream, part of a response may reach the caller before a later chunk is blocked. The run then fails with an error. That is acceptable for deterministic rules. Calls to T2 agents use the fully buffered mode from 0018 instead.
- The guardrails adapter gains an Envoy ext_proc gRPC endpoint (port 9002).
