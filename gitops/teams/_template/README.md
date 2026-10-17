# Team template

Copy this folder to `gitops/teams/<ad-group>/`. The folder name must be the AD group name (D41). Argo CD then creates the namespace `team-<ad-group>`, labelled for Cilium default-deny and Kyverno.

Every Agent needs the following. Kyverno rejects an Agent that is missing any of them.

| Key | Kind | Example | Purpose |
| --- | --- | --- | --- |
| `platform.example.com/owner` | label | `payments-eng` | Owner group. It approves T2 actions and re-certifies the agent quarterly (D14, D40) |
| `platform.example.com/audience` | label | `payments-eng` | The only group allowed to invoke the agent (D25) |
| `platform.example.com/risk-tier` | label | `T1` | The highest tier among the agent's tools. T2 needs security review |
| `platform.example.com/tools` | annotation | `{"mcp-grafana":["query_loki_logs"]}` | Tool allowlist rendered into the gateway (D13) |
| `platform.example.com/a2a-edges` | annotation | `["team-sre/k8s-agent"]` | Agents this one may call. The called team must approve the edge (D21) |
| `platform.example.com/data-classes` | annotation | `internal` | Recorded in the agent registry (D40) |
| `platform.example.com/capture-content` | annotation (optional) | `"true"` | Opts the agent into full prompt capture for 30 days. Needs security CODEOWNERS approval (D19) |

Before you merge, CI runs `tools/render_agent_policies.py`, `kyverno test` and the agent eval suite.
