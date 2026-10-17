# 0009 — No long-term memory in v1; curated team knowledge

- Status: Accepted (2026-10-10)
- Decisions: D10, D31

## Decision

- **Sessions** are kept in kagent's Postgres for 90 days. kagent 0.10.3's built-in `database.postgres.sessionRetentionDays: 90` deletes idle sessions, so no custom job is needed.
- **Context compaction** is on (`declarative.context.compaction`).
- **kagent long-term memory is off.** It is per agent *and per user*, needs pgvector, and is the main path for cross-user leaks and memory poisoning.
- **Team knowledge** comes from a curated, read-only knowledge MCP built from runbooks and ADRs in Git or Confluence. Changes go through PRs.
- **Untrusted content stays out of memory.** Tool output is never written to memory automatically.

## Revisit

Per-user memory in phase 3, with retention, deletion and poisoning controls.
