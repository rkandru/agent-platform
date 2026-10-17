#!/usr/bin/env python3
"""Render gateway ACLs, MCP tool allowlists and Keycloak clients from Agent CR labels (D6, D21, D25).

Input: `kubectl get agents.kagent.dev -A -o json` (or the same shape built in CI from gitops/teams/*/agents).
Output: YAML/JSON files under gitops/platform/agentgateway/generated/ and gitops/platform/keycloak/generated/.

Agent metadata contract (enforced by Kyverno, gitops/platform/kyverno/policies/require-agent-metadata.yaml):
  labels:
    platform.example.com/owner:     <AD group>            # who owns + approves
    platform.example.com/audience:  <AD group>            # who may invoke
    platform.example.com/risk-tier: T0|T1|T2              # highest tier among its tools
  annotations:
    platform.example.com/tools:     '{"mcp-grafana": ["query_loki_logs"], "mcp-atlassian": ["getJiraIssue"]}'
    platform.example.com/a2a-edges: '["team-sre/k8s-agent"]'   # agents this agent may call
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GW_OUT = ROOT / "gitops/platform/agentgateway/generated"
KC_OUT = ROOT / "gitops/platform/keycloak/generated"
L = "platform.example.com/"
WORKLOAD = 'source.unverifiedWorkload.namespace + "/" + source.unverifiedWorkload.serviceAccount'


def path_is(prefix):
    """Exact agent path or a sub-path; avoids `triage` also matching `triage-v2`."""
    return f'(request.path == "{prefix}" || request.path.startsWith("{prefix}/"))'


def cel_list(items):
    return "[" + ", ".join(json.dumps(i) for i in items) + "]"


def policy(name, target_kind, target_name, body):
    return {
        "apiVersion": "agentgateway.dev/v1alpha1",
        "kind": "AgentgatewayPolicy",
        "metadata": {"name": name, "namespace": "agentgateway-system",
                     "labels": {L + "generated": "true"}},
        "spec": {"targetRefs": [{"group": "gateway.networking.k8s.io", "kind": target_kind, "name": target_name}],
                 **body},
    }


def main():
    agents = json.load(sys.stdin)["items"]
    inbound_deny, tool_allow, edges = [], {}, []
    for a in agents:
        md = a["metadata"]
        ns, name = md["namespace"], md["name"]
        labels, ann = md.get("labels", {}), md.get("annotations", {})
        audience = labels[L + "audience"]
        sa = a["spec"].get("declarative", {}).get("deployment", {}).get("serviceAccountName", name)
        ident = f"{ns}/{sa}"
        # D25: deny invoking this agent unless the caller is in its audience group.
        inbound_deny.append(
            f'{path_is(f"/api/a2a/{ns}/{name}")} && !({json.dumps(audience)} in jwt.groups)')
        # D13: per-agent tool allowlist per MCP backend.
        for backend, tools in json.loads(ann.get(L + "tools", "{}")).items():
            tool_allow.setdefault(backend, []).append(
                f"{WORKLOAD} == {json.dumps(ident)} && mcp.tool.name in {cel_list(tools)}")
        # D21: A2A edges this agent may call.
        for callee in json.loads(ann.get(L + "a2a-edges", "[]")):
            edges.append(f'({WORKLOAD} == {json.dumps(ident)} && {path_is("/api/a2a/" + callee)})')
        # D11: one Keycloak client per agent.
        tmpl = json.loads((ROOT / "gitops/platform/keycloak/agent-client-template.json").read_text())
        tmpl.pop("_comment", None)
        raw = json.dumps(tmpl).replace("team-TEAM:AGENT", f"{ns}:{sa}").replace("team-TEAM/AGENT", f"{ns}/{name}") \
            .replace("TEAM-AGENT", f"{ns.removeprefix('team-')}-{name}").replace("TEAM/AGENT", f"{ns}/{name}") \
            .replace("owner=TEAM", "owner=" + labels[L + "owner"]).replace("tier=T1", "tier=" + labels[L + "risk-tier"])
        KC_OUT.mkdir(parents=True, exist_ok=True)
        (KC_OUT / f"client-{ns}-{name}.json").write_text(json.dumps(json.loads(raw), indent=2) + "\n")

    docs = []
    if inbound_deny:
        docs.append(policy("inbound-agent-acl", "HTTPRoute", "kagent-api",
                           {"traffic": {"authorization": {"action": "Deny",
                                                          "policy": {"matchExpressions": inbound_deny}}}}))
    for backend, rules in sorted(tool_allow.items()):
        # The kagent controller may list (not call) tools so it can populate discoveredTools.
        rules = ['source.unverifiedWorkload.namespace == "kagent" && mcp.methodName == "tools/list"'] + rules
        docs.append(policy(f"tools-{backend}", "HTTPRoute", backend,
                           {"backend": {"mcp": {"authorization": {"action": "Allow",
                                                                  "policy": {"matchExpressions": rules}}}}}))
    # A2A route: allow only declared edges (anything else is denied by Require semantics).
    docs.append(policy("a2a-edges", "HTTPRoute", "a2a",
                       {"traffic": {"authorization": {"action": "Require",
                                                      "policy": {"matchExpressions": [" || ".join(edges) or "false"]}}}}))
    GW_OUT.mkdir(parents=True, exist_ok=True)
    # JSON is valid YAML; Argo CD applies it as-is.
    (GW_OUT / "agent-policies.yaml").write_text("\n---\n".join(json.dumps(d, indent=2) for d in docs) + "\n")


if __name__ == "__main__":
    main()
