# 0006 — kagent 0.10 in prod, a kagent 1.x pilot for coding agents

- Status: Accepted (2026-10-10)
- Decisions: D24

## Context

kagent 1.0 (alpha11, 2026-10-09) is a rewrite. It has `api.kagent.dev/v1alpha3`, a `Harness` resource that runs `kagent|codex|claude|byo` runtimes, and every agent sandboxed (gVisor or a Kata microVM). agentgateway is built in as a default-deny egress gateway that injects secrets.

The constraints: there is no in-place upgrade from 0.10.x, 1.x needs a new database, and the two lines can't run on the same cluster.

## Decision

- Prod chat/ops agents stay on **kagent 0.10.x** (0.10.3).
- Coding agents run on a **separate pilot cluster with kagent 1.x**.
- When 1.x reaches GA, prod is rebuilt on it. Because agents are code (D6), this is a rebuild, not a migration.

## Fallback

If 1.x isn't stable when the pilot starts, stay on 0.10 and write our own dispatcher on kubernetes-sigs/agent-sandbox (v1beta1 `SandboxTemplate`/`SandboxClaim`, gVisor RuntimeClass).
