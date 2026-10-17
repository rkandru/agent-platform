# Runbook: stopping an agent

- **Owners:** platform on-call and security (D39).
- **Target:** calls blocked within 1 minute of step 1.
- **Order:** steps 1 and 2 stop a misbehaving agent; steps 3 and 4 make sure it stays stopped.

## 0. Identify the agent

- Find the agent's namespace, its ServiceAccount, and its id `<namespace>/<serviceaccount>`. Look in the Grafana audit tenant (`{service_name="agentgateway"} | json | agent_id="<id>"`) or in the alert that paged you.
- Note its Keycloak client `agent-<team>-<name>`, which is in the existing AD-backed realm `platform`.

## 1. Deny at agentgateway (fastest)

Argo CD self-heals `platform-agentgateway`, so turn off auto-sync first. Then add the agent to the deny list in `AgentgatewayPolicy/kill-switch-agents`:

```bash
argocd app set platform-agentgateway --sync-policy none
kubectl -n agentgateway-system edit agentgatewaypolicy kill-switch-agents
#   matchExpressions:
#     - 'source.unverifiedWorkload.namespace + "/" + source.unverifiedWorkload.serviceAccount in ["__none__/__none__", "team-x/agent-y"]'
```

The gateway rejects every LLM, MCP and A2A call from that workload within seconds.

Within 24 hours, commit the same change to `gitops/platform/agentgateway/kill-switch.yaml` and re-enable auto-sync.

## 2. Block its model spend

kagent 0.10 agents are tracked in LiteLLM as end-users keyed by `x-agent-id`:

```bash
curl -sS -X POST "$LITELLM_URL/customer/block" -H "Authorization: Bearer $LITELLM_ADMIN_KEY" \
  -H 'Content-Type: application/json' -d '{"user_ids":["<namespace>/<serviceaccount>"]}'
```

For a coding task, block its per-task key with `POST /key/block` and `{"key":"<key>"}`. The key also expires on its own at its 60-minute TTL.

## 3. Disable the Keycloak client

Keycloak admin console → realm `platform` → Clients → `agent-<team>-<name>` → Enabled: off. Or:

```bash
kcadm.sh update clients/<client-uuid> -r platform -s enabled=false
```

## 4. Scale to zero / suspend

```bash
# kagent 0.10 declarative agent
kubectl -n <namespace> scale deployment <agent-name> --replicas=0
# coding task on the kagent 1.x pilot
kubectl -n <namespace> delete sandboxclaim <task-id>
```

Argo CD will try to restore the agent. Disable auto-sync for `team-<group>` until the postmortem is done.

## Global freeze

Use this when several agents are misbehaving, or the cause is unknown.

1. In `AgentgatewayPolicy/kill-switch-global-freeze`, change the match expression from `"false"` to `"true"`. Every agent egress call is then denied.
2. Pause intake: `kubectl -n agent-platform scale deployment intake --replicas=0`. GitHub and Jira retry webhook deliveries.
3. Announce the freeze in `#agent-platform-incidents`.

## Automatic trips

The kill-switch controller performs step 1 automatically and pages the agent's owner when any of these happens:

- a LiteLLM budget is exceeded;
- the tool-call rate is above the threshold;
- 3 or more guardrail violations occur within 10 minutes;
- 3 or more approval denials occur within 1 hour;
- A2A depth or loop is violated.

## After the incident

- Audit records are under S3 Object Lock and can't be deleted.
- Open a postmortem. Re-enable the agent only through a Git PR approved by the owner and security.
- Run a drill each quarter. The drill result is SOC 2 evidence.
