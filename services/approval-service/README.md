# approval-service (D4, D14, D29)

The approval service mints and verifies approval grants for T2 actions. kagent's `requireApproval` and the harness permission prompts are only the user experience; this service is the control.

## Grant format

A JWS signed with an HSM- or Vault-transit-backed key (`kid` is rotated):

```json
{
  "iss": "approval-service",
  "jti": "<uuid, single use>",
  "sub": "<requester kc sub or agent id for autonomous runs>",
  "agent": "team-payments/triage",
  "tool": "mcp-k8s/rollout_restart",
  "args_sha256": "<sha256 of RFC 8785 canonical JSON of the tool arguments>",
  "env": "prod",
  "approvers": ["<kc sub>", "<kc sub>"],
  "exp": "<now + 15 min>"
}
```

## Endpoints

| Method | Path | Caller | Purpose |
| --- | --- | --- | --- |
| POST | `/v1/requests` | intake, kagent HITL bridge | Creates an approval request (tool, args, agent, requester, env) and notifies approvers in the kagent UI, or in Slack for autonomous runs |
| POST | `/v1/requests/{id}/decision` | intake (Slack button), kagent UI | Records approve/deny. Enforces the policy in the next section. Mints the grant when the rule is satisfied |
| gRPC | `envoy.service.auth.v3.Authorization/Check` on :9001 | agentgateway `extAuth` | **Link check**: asks the broker. **Grant check** for T2 tools: verifies signature, `exp`, that `jti` is unused (Redis `SETNX`), the tool and `args_sha256` against the forwarded body, and the agent. Denies with a reason |
| — | `verifier` library (Go / Python) | Self-hosted T2 MCP servers | Same checks, in-process, for servers we own |

## Policy

- T0/T1: no grant needed.
- **T2 in non-prod:** the requester may approve.
- **T2 in prod:** two distinct approvers from the agent's `owner` group (four-eyes). The requester can't be one of them.
- **Autonomous runs:** requests go to the owner team's Slack channel, with a UI deep link.
- **Prod changes to Argo CD-managed state** never get a grant. The agent must open a GitOps PR instead.
- **Every decision** is emitted as an `audit=true` log record, which goes to the Loki audit tenant and the S3 WORM bucket.
