# 0014 — kagent UI first; Slack only where needed; one intake service

- Status: Accepted (2026-10-10)
- Decisions: D22, D26, D27, D35

## Decision

- **The kagent UI** (behind agw-inbound) is the default chat and approval surface.
- **Slack** is used only for:
  - agents a team binds to a channel in Git;
  - notifications;
  - approvals for autonomous runs, with a UI deep link.
- **One channel-agnostic intake service** replaces the single Slack adapter: Slack Socket Mode, GitHub and Jira webhooks, a queue, routing, approval buttons and account linking.
- **GitHub and Jira Cloud** reach us through a hardened, webhook-only public ingress (HMAC verification, source-IP allowlist, enqueue only).
- **Teams and Outlook** come in phase 3, after IT confirms the Entra setup.
  - Teams uses a bot.
  - Outlook uses app-only Graph, limited to shared mailboxes via Exchange RBAC for Applications.
  - Sending email is T2.
