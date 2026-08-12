# Evidence-Gated Decision Pipeline v1.6 — Case-Level Failure Analysis

## Executive outcome

Evidence-Gated Decision Pipeline v1.6 completed all 24 frozen synthetic cases in 24/24 calls with zero quarantine, zero retry and no post-observation tuning. It achieved **23/24 end-to-end exact**, passed five of six release gates and produced a perfect escalation matrix of six true positives, zero false positives, 18 true negatives and zero false negatives.

The sole non-exact case is `CON-008`. Its two mismatched fields—`gap_types` and `remediation_action_types`—do not reveal a workflow decision failure. They reveal an incomplete benchmark-authority migration.

v1.6 correctly preserved two concurrent conditions:

- partial coverage, because `C-CON-006` does not cover the mandatory maintenance-and-oversight element; and
- design deficiency, because the supplied procedure lacks the approved governance attributes.

Approved composition policy therefore requires both `partial_coverage` and `control_design`, with both `mapping_review` and `control_design_change`. Benchmark authority v1.1 adjudicated four other cases but inherited `CON-008` from the original single-condition label, which contains only `control_design` and `mapping_review`.

v1.6 remains frozen. It was not modified, tuned, rerun or rescored.

## Headline evidence

| Measure | Result |
|---|---:|
| End-to-end exact | 23/24 (95.83%) |
| Release gates | 5/6 |
| Completed terminal cases | 24/24 |
| Quarantined cases | 0 |
| Model calls | 24/24 maximum |
| Retry count | 0 |
| Escalation TP / FP / TN / FN | 6 / 0 / 18 / 0 |

The exact dual-axis authority gate passed for every case covered by authority overlay v1.1. The failed all-fields gate arises solely from the inherited `CON-008` expectation.

## Case-level analysis

### `CON-008` — concurrent coverage and design conditions

The submitted current control is `C-CON-006`. The approved rulebook determines partial coverage because `OEL-CON-MAINTAIN-001` remains uncovered and identifies `C-CON-007` as the relevant additional candidate.

The evidence model assigned the supplied procedure to `ER-CON-DESIGN-001` and returned `present_deficient`, citing the missing governance fields. Deterministic policy derived `design_deficiency`.

The approved composition policy then produced:

- coverage state: `partial`;
- evidence condition: `design_deficiency`;
- gaps: `partial_coverage` and `control_design`;
- severity: `high`;
- actions: `mapping_review` and `control_design_change`;
- mapping-review routing: Conduct Risk Officer;
- design-change routing: Complaints Manager and Head of Compliance; and
- escalation: Head of Compliance.

This output follows the general policy exactly. It does not contain a case-specific override and is supported independently by the rulebook and evidence requirement.

The inherited v1.0 label already expects partial mapping and a high design gap, but it collapses the two concurrent conditions into one gap and one action. Benchmark authority v1.1 did not adjudicate or normalize this case because its scope was limited to four complete-mapping disputes. The score therefore compares a dual-axis workflow with a partially migrated authority set.

## Symptom versus root cause

### Symptom: one case has two field mismatches

The workflow returned additional `partial_coverage` and `control_design_change` values. Removing them would violate approved composition policy and recreate the suppression behavior v1.6 was designed to eliminate.

### Root cause: incomplete authority migration

Benchmark authority v1.1 overlays only `CON-006`, `CON-007`, `CON-011` and `CON-012`. Other entered-assurance cases inherit single-axis v1.0 labels even where the approved rulebook and composition policy establish concurrent states.

The root cause is therefore **authority-scope incompleteness**, not workflow quality. A patch for `CON-008` alone would repeat the same narrow migration pattern. The correct response is an independent, complete audit of all eight entered-assurance cases under the approved rulebook and composition policy.

### Measurement consequence

The observed 23/24 score remains the valid and immutable v1.6 result against authority v1.1. No alternative score may be claimed. A future authority version may support a later workflow evaluation, but cannot retrospectively rescore v1.6.

## Controls that worked

- all provider responses passed transport and semantic validation;
- deterministic mapping followed the approved rulebook;
- bounded evidence observation correctly identified the deficient design evidence;
- concurrent coverage and evidence conditions were retained;
- both remediation actions and accountable routes were preserved;
- high design severity and escalation were correct;
- all six mandatory escalations were detected with no unnecessary escalation;
- workflow, dataset and authority identities were correct;
- the runner had no access to labels or authority overlays;
- no quarantine, retry, repair, fallback or case-specific override occurred; and
- the failed release gate blocked holdout progression.

## Selected next-version direction

The separately versioned [v1.7 decision](v1.7-decision.md) selects an **authority-completeness intervention before implementation**:

1. independently adjudicate all eight entered-assurance cases under the approved rulebook and composition policy;
2. publish a complete, self-contained dual-axis benchmark authority rather than another sparse patch;
3. require evaluator completeness checks so no entered case silently falls back to a legacy single-axis expectation; and
4. retain the v1.6 runtime architecture unless the completed authority audit identifies a genuine workflow defect.

This is a decision record only. No adjudication, authority v1.2, v1.7 workflow, execution or score is created here.

## Evidence boundary

This analysis uses frozen v1.6 predictions, stage ledger, evaluation and comparison; benchmark authority v1.1; original v1.0 labels; rulebook v1.0; and composition policy v1.0. It is synthetic regression analysis, not independent validation, production performance, legal advice or a compliance opinion. No frozen artefact was changed.
