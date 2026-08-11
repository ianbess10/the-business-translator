# Evidence-Gated Decision Pipeline v1.5 — Case-Level Failure Analysis

## Executive outcome

Evidence-Gated Decision Pipeline v1.5 completed all 24 frozen synthetic cases in 24/24 permitted calls with zero quarantine, zero retry and no post-observation tuning. It achieved **20/24 end-to-end exact** and passed nine of 15 release gates.

All four non-exact cases are entered market-conduct assurance cases: `CON-006`, `CON-007`, `CON-011` and `CON-012`. They expose two different governance issues that must not be collapsed into prompt tuning.

First, the approved Coverage and Evidence Rulebook treats the obligation to **establish and maintain** a complaints framework as two mandatory elements. `C-CON-006` covers establishment and operation; `C-CON-007` covers maintenance and oversight. A single control is therefore deterministically partial. The frozen labels for all four cases instead treat one submitted control as a complete mapping. That is an authority conflict between the later human-approved rulebook and the earlier benchmark labels—not evidence that deterministic mapping failed.

Second, `CON-011` exposes a real workflow-policy defect. The evidence model correctly identified repeated overdue high-impact complaints as an adverse operating indicator, but partial-coverage precedence suppressed that operating exception and the required escalation. Coverage and operating condition are concurrent assurance dimensions; one must not erase the other.

v1.5 remains frozen. It was not modified, tuned, rerun or rescored.

## Headline evidence

| Measure | Result |
|---|---:|
| End-to-end exact | 20/24 (83.33%) |
| Release gates | 9/15 |
| Completed terminal cases | 24/24 |
| Quarantined cases | 0 |
| Model calls | 24/24 maximum |
| Retry count | 0 |
| Escalation TP / FP / TN / FN | 5 / 0 / 18 / 1 |

All 12 AML/CFT cases were exact. Source use, obligation outcome, applicability, assurance gating, control identity, catalogue owner routing, human review and compliance conclusion were exact across all 24 cases.

## Case-level analysis

### `CON-006` — correct owner correction, disputed mapping authority

The submitted current control is `C-CON-006`. The frozen label expects a complete mapping and mapped-and-evidenced outcome. The approved rulebook determines partial coverage because the maintenance-and-oversight element remains uncovered by the current control set. Both supplied evidence items were correctly observed as complete.

The operational owner correction worked: the workflow used the Complaints Manager rather than the proposed Conduct Risk owner. The mismatch is therefore not owner routing or evidence interpretation. It is a direct conflict between the frozen label and the approved coverage authority.

### `CON-007` — missing operating record preserved, then hidden by a label conflict

The workflow correctly observed that the design framework was present and the operating complaint register was missing. The frozen label expects `C-CON-006` to be completely mapped and therefore expects a routine evidence request. The rulebook determines that `C-CON-006` alone leaves maintenance and oversight uncovered, so partial coverage takes precedence in v1.5.

The evidence observation is correct. The reported end-to-end error arises because the benchmark's complete-mapping premise conflicts with the approved rulebook. A later label-governance decision must determine the authoritative expected state without rewriting the frozen v1.0 dataset.

### `CON-011` — adverse operating exception suppressed

The workflow correctly observed `EV-CON-011` as `adverse_indicator_present`: repeated overdue high-impact complaints with incomplete remediation. The rulebook also consistently determined that `C-CON-006` alone leaves the maintenance-and-oversight element uncovered.

The policy then selected only the partial-coverage path: medium severity, mapping review and no escalation. This suppressed a concurrent high operating exception and caused the sole missed mandatory escalation.

The mapping mismatch remains a benchmark-authority conflict. The missed operating remediation and escalation are a genuine policy defect. An incomplete control set does not make adverse evidence about an operating current control less urgent.

### `CON-012` — missing management information preserved, disputed mapping authority

The workflow correctly observed that the latest customer-outcomes management information was missing. The frozen label expects `C-CON-007` alone to be completely mapped and routes a routine evidence request. The approved rulebook determines partial coverage because establishment and operation remain uncovered without `C-CON-006`.

As in `CON-007`, the evidence fact is correct and the mismatch begins with conflicting mapping authorities. Changing the rulebook calculator to reproduce the label would invalidate its approved two-element coverage model.

## Symptom versus root cause

### Symptom: four mapping-status mismatches

The deterministic calculator performed exactly as the approved rulebook specifies. The root cause is **benchmark authority drift**: the labels predate and conflict with the later approved obligation-element coverage authority.

This is not resolved by changing v1.5 or silently relabelling the existing dataset. It requires an independent human adjudication that cites source, obligation and control-design evidence, followed—only if approved—by a separately versioned benchmark label set.

### Symptom: evidence-request outcomes disappeared in two cases

The evidence model correctly detected the missing records. v1.5 represents a case through one dominant assurance outcome, and partial mapping took precedence.

The deeper design limitation is **single-axis outcome composition**. Coverage condition and evidence condition can coexist and require different owners and actions. A future workflow should preserve both dimensions and route both actions, with a deterministic presentation priority only where the external schema requires one headline outcome.

### Symptom: one mandatory escalation was missed

`CON-011` contained a correctly identified adverse operating indicator. The root cause is **incorrect policy precedence**: partial coverage suppressed adverse operating evidence. High adverse evidence must retain operating remediation and escalation even when mapping is also partial.

### Measurement defect: inherited evaluator version label

The v1.5 evaluator wrapper produced a comparison and report heading labelled `v1.4`, although the run ID, evaluation ID, workflow payload and result location identify v1.5. The one evaluation is valid evidence but its version-label lineage is defective. It must be corrected only in a separately versioned evaluator and never by rescoring v1.5.

## Controls that worked

- deterministic mapping followed the approved rulebook without model inference;
- the bounded evidence model correctly identified complete, missing and adverse evidence states in all four failed cases;
- current control identity and catalogue ownership were exact;
- source, obligation and applicability authority remained exact;
- all 24 cases reached a terminal completed state;
- the append-only ledger preserved all 24 calls;
- no quarantine, retry, repair, fallback or case-specific override occurred;
- no unnecessary escalation occurred; and
- the release gates blocked progression to holdout.

## Selected next-version direction

The separately versioned [v1.6 decision](v1.6-decision.md) selects three controlled interventions:

1. independent adjudication of the rulebook-versus-label conflicts, with any approved changes published only as a new dataset version;
2. dual-axis deterministic assurance composition so mapping coverage and evidence condition remain concurrently visible and actionable; and
3. adverse-evidence precedence that preserves high operating remediation and escalation even when mapping is partial.

It also requires correct workflow-version metadata in the future evaluator. This is a decision record only. v1.6 is not implemented, tested, frozen, executed or scored.

## Evidence boundary

This analysis uses the frozen v1.5 run, predictions, stage ledger, evaluation, v1.0 rulebook and frozen v1.0 labels. It is synthetic regression analysis, not independent validation, production performance, legal advice or a compliance opinion. No v1.5 workflow, result, input, label, rulebook or evaluator artefact was changed.
