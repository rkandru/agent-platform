# 0008 — Metadata-only telemetry by default; WORM audit trail

- Status: Accepted (2026-10-10)
- Decisions: D9, D19, D32

## Decision

One OpenTelemetry Collector routes to three LGTM tenants:

| Tenant | What it holds | Retention | Access |
| --- | --- | --- | --- |
| ops | Everything, with `gen_ai` content and tool arguments/results stripped. kagent always records these in spans, so this stripping is mandatory | Standard | Engineering |
| content | Unredacted spans, only for agents annotated `platform.example.com/capture-content: "true"` (security CODEOWNERS approval); coding transcripts | 30 days | On-call + the agent's owner |
| audit | Gateway access logs, approval, intake and broker events | 13 months in Loki, plus a copy in S3 with **Object Lock (compliance mode, 13 months)** | Security + platform |

## Consequences

- The redaction rules must track the attribute names kagent and the harnesses emit. Acceptance test 7 checks this.
- The S3 Object Lock bucket can't be shortened or deleted early. Set retention deliberately.
