# 0013 — Vendor gate; no Grok Bot; Cursor parked

- Status: Accepted (2026-10-10)
- Decisions: D8, D28

## Decision

**Gate.** An external agent platform is onboarded only if it meets all five of these, set before any demo:

1. Okta SSO + SCIM, and per-agent non-human identities.
2. Calls go through our gateways, or it exports a full audit trail to LGTM.
3. ZDR, data residency, and SOC 2 Type II.
4. A capability we can't build within about 2 quarters.
5. Agents and memory stay portable (MCP / A2A).

**Grok Bot (SpaceX AI):** no, unless we prove we can't build an equivalent.

- It runs in Cursor's cloud as one microVM per user, and would be a second governance plane.
- If Grok models are ever wanted, they go **behind LiteLLM** as a model, not as a platform.

**Cursor:** stays a desktop IDE and is parked for remote agents.

- Its self-hosted workers keep the agent loop, model calls and transcripts in Cursor's cloud, with no path through LiteLLM.
- SpaceX completed its acquisition of Cursor on 2026-08-14.
