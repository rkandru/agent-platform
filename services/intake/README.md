# intake (D16, D22, D26, D27, D35)

The intake service is the channel-agnostic front door. It replaces the current single Slack adapter. It runs in namespace `agent-platform`, with stateless replicas, a queue (NATS JetStream or Redis Streams), and Postgres for thread↔`contextId` mapping and task records.

## Channels

| Channel | Transport | Phase |
| --- | --- | --- |
| Slack | One Slack app, Socket Mode (outbound only, up to 10 connections) | 1 |
| GitHub Cloud | GitHub App webhooks through the hardened webhook ingress (HMAC `X-Hub-Signature-256`, source IPs from `api.github.com/meta`) | 2 |
| Jira Cloud | Jira webhooks through the same ingress (shared secret / JWT, Atlassian IP ranges) | 2 |
| Teams | Bot Framework, after IT confirms Entra | 3 |

## Routing (Slack)

1. **Channel binding.** `gitops/teams/<team>/channels.yaml` maps channel IDs to agents.
2. **Explicit addressing.** `/agent <name> <text>`, or `@platform <name>: <text>`.
3. **Concierge (optional, per channel).** A router agent hands off over A2A, using allowlisted edges (D21).

The gateway authorizes every call, so a mis-route is a UX bug, not a security hole.

## Coding-agent triggers (phase 2)

| Event | Who may trigger | Action |
| --- | --- | --- |
| New issue labelled `bug` / new Jira Bug | Anyone (automatic) | **Read-only triage.** The agent comments with an analysis, the likely files and a repro attempt. It has no write tools |
| Label `agent:claude` / `agent:codex`, or a `/agent fix` comment | Users with **write** access to the repo (checked through the GitHub API) | Starts a coding task on the kagent 1.x pilot, using the matching `Harness` |
| Jira label `agent-fix` or a transition | Members of the project role `Developers` | Same. The repo comes from the Jira component → repo map in `gitops/teams/<team>/repos.yaml` |
| Slack `/agent code <repo> <text>` | Linked users in a bound channel who have write access to the repo | Same |

For each coding task, intake does the following:

1. **Credentials.** It mints a LiteLLM key (`max_budget: 20`, `duration: 60m`, `metadata.task_id`) and a GitHub App installation token scoped to the one repo (`permissions: contents/pull_requests/issues: write`, 1-hour expiry).
2. **Concurrency.** It enforces a limit of 20 concurrent tasks across the platform and 5 per team.
3. **Status.** It posts status back to the origin with its own app credentials.

## Approvals

- kagent's `INPUT_REQUIRED` approval prompts (via the `A2A-Extensions: https://kagent.dev/extensions/hitl/v1` header) render as Block Kit approve/deny buttons.
- Decisions are forwarded to approval-service, which enforces the four-eyes rule.

## Account linking

- Unlinked Slack users get a DM with the credential broker's `/connect/keycloak` link (D12).
- Slack users are mapped to Keycloak users by email. Slack SSO is through Okta, and its emails match AD.
