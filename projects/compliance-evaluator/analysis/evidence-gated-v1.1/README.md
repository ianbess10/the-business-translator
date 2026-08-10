# Evidence-Gated Decision Pipeline v1.1 — Case-Level Failure Analysis

## Executive outcome

Evidence-Gated Decision Pipeline v1.1 improved the frozen synthetic regression result from **15 of 24** end-to-end exact decisions in v1.0 to **20 of 24**. It resolved the prior applicability weakness, detected every mandatory escalation, produced no unnecessary escalation and preserved the human-accountability and assurance-entry controls.

It did not meet the release threshold. Four cases were not end-to-end exact and the frozen evaluator reported six failed release gates. One of those reported gate failures is a measurement defect rather than a workflow decision failure: the evaluator treated the legitimate rule identifier `SRC-CON-002` as case-specific because it contains the case ID `CON-002`.

The release conclusion does not change. Even after isolating that evaluator defect, five substantive gates remain failed. v1.1 must remain frozen, must not be tuned or rerun and must not proceed to unseen holdout validation.

This analysis uses the single preserved run in [`results/evidence-gated-v1.1`](../../results/evidence-gated-v1.1/README.md). It does not modify the v1.1 workflow, prompts, policies, schemas, inputs, labels, evaluator or results.

## What v1.1 proved

The intervention materially improved the operating decision chain:

- source-use disposition: 24/24;
- applicability: 24/24;
- assurance-entry gate: 24/24;
- mandatory escalation detection: 6/6;
- unnecessary escalations: 0;
- missed escalations: 0;
- routine missing-evidence treatment: 2/2;
- reconciliation without manual correction: 24/24; and
- prohibited compliance conclusions: 0.

The remaining weakness is concentrated in how the AI stages distinguish source-backed obligation support, current control coverage and evidence sufficiency. It is not a reason to weaken escalation or reopen applicability.

## Root-cause summary

| Root cause | Cases | What happened | Operating consequence |
|---|---:|---|---|
| Source support conflated with legal readiness | 1 | `CON-001` reproduced the supplied obligation wording but was rejected as an unsupported extension because staged commencement and human approval were treated as evidence that the statement itself lacked source support | A valid candidate obligation can be blocked before human approval even when source disposition and applicability are correct |
| Evidence requirement conflated with control coverage | 2 | `CON-007` and `CON-012` treated missing operating records as uncovered obligation elements and therefore demoted complete mappings to partial mappings | Control accountability is understated even though the evidence request and escalation decision remain correct |
| Proposed mapping silently expanded | 1 | `CON-010` added `C-CON-007` from the wider catalogue to the current mapping, turning a partial submitted mapping into a complete and evidenced mapping | The workflow repairs the proposal instead of identifying the missing coverage and routing a mapping review |
| Evaluator rule-identifier collision | 1 | `CON-002` was decision-exact, but `SRC-CON-002` triggered a substring-based case-specific-rule check | A correct general policy rule is reported as benchmark overfitting |

The four decision-error cases contain ten mismatched fields, but most are cascades. The three substantive workflow causes sit upstream of those field-level symptoms.

## Symptom versus root cause

### Symptom: mapping and owner-routing gates failed

The owner catalogue did not assign an incorrect owner. In `CON-010`, the model added an extra control to the current mapping; deterministic catalogue resolution then correctly assigned the owner of that extra control. The failed owner-routing metric is therefore a mapping-membership failure, not an owner-resolution failure.

### Symptom: evidence still demoted mapping

v1.1 added separate mapping and evidence fields to one model response, but `CON-007` and `CON-012` show that field separation did not create decision separation. The same model call received the obligation's evidence requirements, the current mapping and missing evidence, then used the missing evidence to set `coverage_gap_present: true`.

The root cause is shared input and reasoning context. More wording in the same prompt would be tuning the symptom. The stronger operating control is stage-level input isolation.

### Symptom: a partial mapping became complete

`CON-010` correctly identified `C-CON-007` as relevant but placed it inside `supported_control_ids`, even though it was absent from the submitted mapping. The workflow therefore treated a remediation candidate as a current control.

The root cause is that the v1.1 contract has one list for supported controls and no separate field for additional controls that should be considered during remediation.

### Symptom: a general-policy gate failed on an exact case

`CON-002` matched every expected decision and recorded `case_specific_override: false`. The evaluator nevertheless failed the gate because it checked whether the literal case ID appeared anywhere inside an applied rule identifier. `CON-002` is naturally contained in `SRC-CON-002`.

This is an evaluator identity-collision defect. It must be corrected only in a separately versioned evaluator; the frozen v1.1 score and report remain unchanged.

## Case register

| Case | Observed failure | Root cause | What remained protected |
|---|---|---|---|
| `CON-001` | Binding candidate became `unsupported_obligation` | Candidate-statement support was conflated with staged commencement and approval readiness | Source disposition, applicability, closed assurance gate and human review |
| `CON-007` | Complete `C-CON-006` mapping became partial | Missing complaint-register evidence was treated as missing control coverage | Correct control and owner, insufficient-evidence outcome, evidence request and no escalation |
| `CON-010` | `C-CON-007` was added to the submitted `C-CON-006` mapping, producing a complete and evidenced outcome | Current mapping and remediation-candidate controls were not separated | Approved authority, applicability, catalogue owners and no escalation |
| `CON-012` | Complete `C-CON-007` mapping became partial | Missing management information was treated as missing control coverage | Correct evidence request, proportionate routing and no escalation |
| `CON-002` | No decision mismatch; general-policy gate alone failed | Evaluator substring collision between case ID and legitimate rule ID | Every operational decision and the explicit no-override trace |

The complete expected-versus-observed fields, causal stage outputs, policy traces, failed gates and source hashes are preserved in [`failure-analysis.json`](failure-analysis.json).

## v1.2 decision

The selected decision is a separately versioned **Evidence-Gated Decision Pipeline v1.2**, defined in [`v1.2-decision.md`](v1.2-decision.md). It is a design decision only; v1.2 is not implemented, tuned, frozen or executed in this stage.

The selected architecture will:

1. separate candidate-statement support from legal-effect and approval readiness;
2. isolate mapping assessment from evidence assessment as separate model stages with separate inputs;
3. distinguish controls in the submitted current mapping from additional controls proposed for remediation; and
4. replace the evaluator's substring-based overfitting check with an identity-safe generality control.

## Evidence boundary

This is post-run analysis of synthetic regression cases already used during workflow design. It is not independent validation, production performance, legal advice or a compliance opinion. Any future v1.2 result on these 24 cases will also be regression evidence. An unseen holdout is permitted only after a separately implemented and frozen version passes every versioned release gate.
