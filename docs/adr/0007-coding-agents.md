# 0007 — Coding agents: Claude Code + Codex, in-house, PR-only

- Status: Accepted (2026-10-10)
- Decisions: D7, D15, D16, D18, D37, D41

## Decision

**Residency:** strictly in-house. Clones, execution and secrets stay on our cluster, and models are reached only through LiteLLM.

- Only the **Claude Code CLI** (`ANTHROPIC_BASE_URL` → LiteLLM) and the **Codex CLI** (`[model_providers]` with `wire_api="responses"` → LiteLLM) meet this when run in our pods.
- Excluded: Cursor self-hosted agents, Claude Code self-hosted environments and Codex cloud, because all of them keep the agent loop on the vendor's side.

**Triggers:**

- Every new bug report gets **read-only triage** automatically.
- Code changes need an explicit trigger from a user with write access: a GitHub label or comment, a Jira label or transition, or a Slack command in a bound channel.

**Sandbox:** gVisor, with egress only to LiteLLM (through the gateway), the git host and Artifactory. No prod secrets.

**Git identity:**

- **One GitHub App per harness.** Each task gets an installation token scoped to one repo that expires after 1 hour.
- **Rulesets** block the Apps from pushing to the default branch, approving PRs or merging.
- **Attribution:** commits carry `Co-authored-by` for the requester.

**CI secrets:** they come from Vault via GitHub OIDC, and the roles **must be bound to protected refs**.

**Pilot:**

- One team of 10–20 engineers, on 3–5 repos.
- At most 20 concurrent tasks across the platform, and 5 per team.
- Each task is capped at 60 minutes and $20.

**Harness hardening:**

- **Claude Code** runs in headless mode with `--bare`, which skips repo-defined hooks and MCP servers. Managed settings add:
  - `allowedProviders: ["customEndpoint"]`
  - `allowManagedHooksOnly`
  - `allowManagedMcpServersOnly`
  - `disableBypassPermissionsMode`
- **Codex** runs with `codex exec --json`, inside the gVisor pod.

## Consequences

- The issue, ticket or Slack text is untrusted input. Auto-triage has no write tools.
- Bitbucket DC comes later; it needs project access tokens instead of a GitHub App.
- Cursor stays an IDE (D28).
