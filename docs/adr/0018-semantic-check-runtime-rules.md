# 0018 — Runtime rules for semantic (LLM-judge) checks

- Status: Accepted (2026-10-12)
- Decisions: D49
- Extends: [0012](0012-guardrails.md)

## Context

Some controls are about meaning and intent, which rules can't express. A model-based judge can check those. But a judge:

- isn't fully reproducible;
- misses some violations;
- flags some clean traffic;
- has to cope with streamed responses, where judging chunk by chunk misses meaning and waiting for the whole response adds delay.

The AgentFirewall talk (AI governance session, Japan, October 2026) summed it up: "semantic inspection is not just a model call; it is a runtime control design problem."

## Decision

**Rules by default.** A judge check is added only for a control that can't be written as a rule. Each judge check names the control it serves.

**When the judge runs depends on the tier:**

| Tier | When the judge runs | If the judge is down or times out | When it flags something |
| --- | --- | --- | --- |
| T0 (reads) | After the call, asynchronously | Allow, and alert | Alert; counts toward the auto-trip |
| T1 (reversible writes); cross-team A2A (0016) | On the request, before it is forwarded. On the response, after it is delivered | Allow, and alert | Block the request. Alert on the response |
| T2 (irreversible or prod) | On the request, before the approval prompt. On the full buffered response | Block | The verdict is shown to the human approver as advice. The approver may override, with a written reason |

- **Timeout.** A synchronous check that takes longer than 3 seconds counts as "down". Tune this from pilot data.
- **Audit.** Every verdict goes to the audit tenant with:
  - the control ID and policy version;
  - the judge model and its version;
  - the SHA-256 of the input;
  - the verdict and score;
  - the latency;
  - any override, with who made it and why.

  The input itself goes to the content tenant only if the agent has opted in to content capture.
- **Model.** A small approved model through LiteLLM, with its version pinned and temperature 0. Changing the model or a prompt is a PR that must pass the eval set.
- **Measuring accuracy.** A labelled set of violating and clean samples runs in CI next to garak. Precision and recall are tracked per control, and a regression blocks the change. False positives are reviewed monthly.

## Consequences

- T2 calls get slower, but they already wait for a human.
- Someone has to maintain the labelled set. Each control's owner adds samples whenever the judge gets one wrong.
