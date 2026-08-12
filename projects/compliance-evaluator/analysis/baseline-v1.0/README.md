# Baseline v1.0 Operational Failure Analysis

## Executive outcome

The simple baseline did not fail because it could not produce structured output. Every response satisfied the JSON contract, the approval gate was selected correctly in all 24 cases, and the model often described the relevant concern in its rationale.

It failed because the workflow did not consistently convert those observations into a controlled operating decision.

Only **1 of 24** cases matched the complete expected disposition. The material risk is therefore not malformed AI output. It is **plausible, well-structured output that could send regulatory work to the wrong stage, owner or escalation route**.

This analysis uses the single frozen run recorded in [`results/baseline-v1.0`](../../results/baseline-v1.0/README.md). The baseline prompt and results remain unchanged, and no case was rerun.

## What the evidence shows

| Operational failure pattern | Evidence | Practical consequence | Priority |
|---|---:|---|---|
| Proposal under test treated as an answer | At least one proposal-anchored decision in 21/24 cases | A plausible analyst or system suggestion can pass through without effective challenge | Critical |
| Assurance activity leaked past the approval gate | 14/16 `not_entered` cases still populated a control, gap, severity or action field | Teams may begin control testing or remediation before an obligation is approved | Critical |
| Escalation followed the proposed answer | All 8 deliberately wrong escalation proposals were reproduced | Six material issues were missed and two routine matters were unnecessarily escalated | Critical |
| Source, obligation or applicability taxonomy was unstable | Source/obligation error in 10 cases; applicability error in 9 | Draft, blocked, superseded or contextual material may enter the wrong regulatory workflow | High |
| Control ownership was not resolved from the authoritative catalogue | Wrong owner in 3/8 entered assurance cases | Work is routed to the wrong accountable function and may be delayed or incorrectly accepted | High |
| Evidence, gap and severity distinctions were inconsistent | At least one error in 6/8 entered assurance cases | Missing evidence can become a gap, adverse operating evidence can be understated, or remediation can be misdirected | High |

These patterns are reproduced in the machine-readable [`failure-analysis.json`](failure-analysis.json). [`analyse_failures.py`](analyse_failures.py) rebuilds the register from the frozen inputs, labels, predictions and evaluation.

## Symptom versus root cause

### Symptom: the final field is wrong

The immediate symptom is a classification mismatch: for example, `escalation_required: false` when escalation was expected.

### Observed behavioural pattern: the proposal is copied

The stronger evidence is that the same error repeats when the input contains a plausible but deliberately wrong proposal:

- source-use proposal anchoring occurred in 6 of 9 source challenge cases;
- obligation-outcome proposal anchoring occurred in 6 of 9 obligation challenge cases;
- applicability proposal anchoring occurred in 5 of 10 applicability challenge cases;
- the proposed control owner was reproduced in 16 of 17 owner challenge cases; and
- the proposed escalation decision was reproduced in all 8 escalation challenge cases.

This is an observed correlation in the synthetic benchmark, not proof of a universal model behaviour. It is nevertheless strong enough to shape the next controlled workflow.

### Inferred workflow root cause

The simple baseline asked one model response to evaluate the source, challenge the proposed obligation, determine applicability, enforce the approval gate, select controls, resolve owners, classify evidence, assign severity and calibrate escalation.

Nothing in that one-step workflow made the proposal explicitly untrusted, forced each decision to be completed in sequence, or prevented later-stage fields from being populated after an earlier gate failed. The structured schema controlled syntax and vocabulary, but not decision dependencies.

The next intervention must therefore change the **decision workflow**, not merely add more explanatory wording to the prompt.

## Decision-critical examples

| Case | What the model understood | What the structured decision did | Operational risk |
|---|---|---|---|
| `AML-003` | Rationale noted unverified commencement | Classified the source as a binding candidate, treated applicability as established and opened control/evidence activity | Premature implementation and missed legal/compliance escalation |
| `AML-011` | Rationale said assurance could not start before approval | Output `assurance_gate: not_entered` but also `mapped_and_evidenced` with a control | Unsupported assurance record |
| `CON-006` | Rationale identified that the proposed owner was wrong | Repeated the wrong owner in the structured control mapping | Misrouted accountability |
| `CON-009` | Rationale stated that supplied evidence met the acceptance criteria | Repeated the proposed gap and escalation | False-positive remediation and management noise |
| `CON-011` | Rationale recognised overdue high-impact complaints and incomplete remediation | Rated the issue medium, labelled evidence missing and did not escalate | Material operating exception understated |

These cases show why narrative quality is not an adequate operating control. Downstream workflow actions will be driven by decision fields, not by whether the prose sounds thoughtful.

## What worked and should be retained

The baseline also provides useful positive evidence:

- the model selected the approval gate correctly in all 24 cases;
- human review remained required in all 24 cases;
- no prohibited compliant/non-compliant conclusion was produced;
- control identifiers were correct in all eight legitimate assurance cases;
- both insufficient-evidence cases were identified without false positives; and
- all three expected potential gaps were surfaced, although one extra gap was introduced.

The next workflow should retain this capability while constraining stage transitions, ownership and escalation.

## Root-cause decision

The selected intervention is a single **Evidence-Gated Decision Pipeline v1.0**, specified in [`intervention-design.md`](intervention-design.md).

It will:

1. treat every proposal as an untrusted claim to accept, amend or reject;
2. make source, obligation, applicability, assurance and escalation decisions in sequence;
3. stop and normalise downstream fields whenever an earlier gate is not passed;
4. resolve control ownership from the frozen catalogue rather than the proposed owner;
5. derive evidence outcome, severity, action and escalation from explicit policy conditions; and
6. reject internally inconsistent outputs before they become operational work.

This is one workflow intervention. It is not a tuned replacement for the preserved simple baseline.

## Evidence boundary

The findings are failure analysis of 24 synthetic regression cases. They are not production performance, legal advice or a compliance opinion. Any improvement on these same cases will be reported as regression evidence. Independent capability evidence requires a separately authored and frozen holdout that is run only after the engineered workflow is frozen.
