# Evidence-Gated Decision Pipeline v1.0 — Case-Level Failure Analysis

## Executive outcome

Evidence-Gated Decision Pipeline v1.0 materially improved the synthetic regression result from **1 of 24** end-to-end exact decisions to **15 of 24**. It also detected all six mandatory escalations, preserved every assurance-entry boundary, resolved all catalogue owners correctly and produced no prohibited compliance conclusion.

It did not meet the release threshold. Nine cases were not end-to-end exact and one of the eight hard release gates failed because `CON-010` was unnecessarily escalated.

The decisive finding is that the escalation rule itself did not fail. The workflow first misclassified a partial control mapping as a high design deficiency; the deterministic escalation policy then correctly escalated the wrong upstream classification. The v1.1 response should therefore correct the decision boundaries before escalation, not weaken escalation sensitivity.

This analysis uses the single frozen run in [`results/evidence-gated-v1.0`](../../results/evidence-gated-v1.0/README.md). It did not modify or rerun v1.0.

## Root-cause summary

| Root cause | Cases | What happened | Operating consequence |
|---|---:|---|---|
| Applicability dimension conflation | 9 | Source authority, legal effect or proposal wording changed applicability even though applicability is a separate institution-and-obligation decision | Correct source and control decisions can still be routed under the wrong applicability state |
| Mapping and evidence dimension conflation | 5 | Complete control mappings were marked partial because evidence was missing, control performance was adverse or commencement reasoning leaked into assurance | Valid accountability relationships are understated and downstream gap treatment can be distorted |
| Partial coverage misclassified as design deficiency | 1 | Incomplete coverage by an existing control became a high design gap rather than a medium partial-coverage issue | The only unnecessary escalation was created |

Across the nine failed cases there were 26 mismatched fields, but those fields do not represent 26 independent problems. Most were deterministic cascades from the three upstream boundary errors above.

## Symptom versus root cause

### Symptom: one unnecessary escalation

`CON-010` ended with `escalation_required: true` and routing to the Head of Compliance, when a mapping review without management escalation was expected.

### Root cause: the wrong gap entered the escalation policy

The AI stage correctly recognised that only part of the obligation was covered. It then labelled that condition `design_deficiency`. The evidence policy converted that label into a high `control_design` gap, and the escalation policy correctly applied its mandatory high-design-gap trigger.

Reducing the escalation rule would risk missing genuine high-severity design gaps. The correct intervention is to distinguish:

- **partial coverage** — an existing control covers only part of the obligation; and
- **design deficiency** — supplied evidence shows the control design itself is inadequate.

## Case register

| Case | Observed failure | Root cause | What remained protected |
|---|---|---|---|
| `AML-011` | Guidance context was labelled out of scope rather than applicable context with assurance closed | Applicability was inferred from non-binding legal effect | Guidance boundary, closed assurance gate and no escalation |
| `CON-005` | Applicable, fully mapped and evidenced record became uncertain, partial and a medium potential gap | Approved applicability was reopened; mapping was influenced by commencement reasoning | Correct source, obligation, controls, owners and no escalation |
| `CON-006` | Complete single-control mapping with sufficient evidence became a medium partial-coverage gap | Approved applicability was reopened; mapping and evidence dimensions were mixed | Correct control, owner and no escalation |
| `CON-007` | Complete mapping with missing operating evidence was marked partial | Missing evidence was allowed to change mapping completeness | Correct evidence request, unassessed severity and no escalation |
| `CON-008` | Only applicability was wrong | Approved applicability was reopened | Genuine high design gap and mandatory escalation were correct |
| `CON-009` | Only applicability was wrong | Approved applicability was reopened | Complete mapping, sufficient evidence, no gap and no escalation |
| `CON-010` | Partial coverage became a high design gap and unnecessary escalation | Partial coverage was misclassified as design deficiency; approved applicability was reopened | Correct control and owner |
| `CON-011` | Correct mapping was marked partial because operating evidence was adverse | Control performance was allowed to change mapping completeness; approved applicability was reopened | High operating exception and both escalation roles were correct |
| `CON-012` | Correct mapping was marked partial because routine evidence was absent | Evidence completeness was allowed to change mapping completeness; approved applicability was reopened | Evidence request remained distinct from a gap and was not escalated |

The complete expected-versus-observed record, stage outputs, policy trace, causal fields and source hashes are preserved in [`failure-analysis.json`](failure-analysis.json). [`analyse_failures.py`](analyse_failures.py) rebuilds that register from the frozen inputs, labels, predictions and evaluation.

## Latent source-stage observation

The source/obligation AI stage classified all eight failed market-conduct assurance cases as a `final_change_event`, while the authoritative policy correctly normalised the final source disposition to `binding_candidate` and the obligation outcome to `candidate_binding_obligation`.

That deterministic control worked: both final fields were correct in all 24 cases. Applicability remained model-assessed, however, so the same source-stage reasoning leaked into the final applicability field. v1.1 should retain the successful authoritative source control and close the remaining applicability path.

## What worked and must be retained

- source-use disposition: 24/24;
- obligation outcome: 24/24;
- assurance-entry gate: 24/24 with zero downstream leakage;
- control identifiers and catalogue owners: 24/24 overall and 8/8 entered assurance cases;
- mandatory escalations: 6/6, with zero missed escalation;
- routine missing-evidence treatment: 2/2;
- prohibited compliance conclusions: 0; and
- cross-field reconciliation: 24/24 without manual correction.

These controls are not candidates for relaxation merely because end-to-end exactness was 62.5%.

## v1.1 decision

The selected decision is to build a narrowly scoped, separately versioned **Evidence-Gated Decision Pipeline v1.1**. The change is defined in [`v1.1-decision.md`](v1.1-decision.md).

v1.1 will:

1. establish an approved-obligation authority boundary for applicability;
2. make mapping completeness independent from evidence sufficiency and control performance;
3. give partial-coverage treatment precedence over design-deficiency treatment when the evidence does not establish a design flaw; and
4. retain the existing source, approval, owner, evidence, escalation and reconciliation controls that passed.

## Evidence boundary

This is post-run analysis of 24 synthetic regression cases used during workflow design. It is not independent validation, production performance, legal advice or a compliance opinion. Any v1.1 improvement on these cases must still be reported only as regression evidence. An unseen holdout can be authored and frozen only after v1.1 is implemented, frozen and assessed against its release gates.
