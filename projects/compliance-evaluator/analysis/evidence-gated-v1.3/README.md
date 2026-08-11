# Evidence-Gated Decision Pipeline v1.3 — Execution Failure Analysis

## Executive outcome

Evidence-Gated Decision Pipeline v1.3 passed its offline tests, three provider contract certifications and frozen preflight, then stopped during its sole authorised regression execution when the evidence-stage response for the nineteenth case failed a deterministic cross-field rule.

The failed case is **`CON-007` — Control description without operating evidence**. Its operating question is whether a documented complaints control can be treated as having operated effectively when the complaint register is missing. The response passed the provider transport schema but represented design deficiency inconsistently across two separate fields:

```text
ValueError: Design-deficiency assessment and evidence flag must agree
```

This is a **post-inference semantic-contract failure**, not a provider-schema failure and not a scored model-quality result. Eighteen cases completed, 21 model calls passed transport and semantic validation, and the next evidence response failed before policy composition. No completed prediction set exists, so v1.3 was not scored.

v1.3 remains frozen. It was not modified, tuned, rerun or scored.

## Case-level reconstruction

The frozen execution order and call topology identify the failure boundary:

| Execution position | Case | Stage calls | Cumulative validated calls | Outcome |
|---:|---|---|---:|---|
| 1–16 | `AML-001`–`AML-012`, `CON-001`–`CON-004` | One source/support call each | 16 | Completed |
| 17 | `CON-005` | Mapping and evidence | 18 | Completed |
| 18 | `CON-006` | Mapping and evidence | 20 | Completed |
| 19 | `CON-007` | Mapping passed; evidence response failed semantic validation | 21 | Failed before case composition |

The identification of `CON-007` is a deterministic reconstruction from the frozen input order, runner branch logic and preserved counters. The run state does not itself store the failed case ID.

`CON-007` supplied a documented complaints framework but marked the completed complaint register as missing. The evidence prompt instructed the model to use `missing_operating_evidence` when required completed records were absent and to use `design_deficiency` only for supplied design weaknesses.

The raw failing response was not persisted. It is therefore not possible to determine from preserved evidence whether the model returned:

- `evidence_assessment: design_deficiency` with `design_deficiency_evidence_present: false`; or
- a different assessment with `design_deficiency_evidence_present: true`.

No claim is made about the unseen field values or the response's benchmark correctness.

## Symptom versus root cause

### Symptom: two evidence fields disagreed

The deterministic validator correctly rejected the contradiction. Weakening or removing that validator would allow an internally inconsistent operational decision to enter policy composition.

The deeper design problem is that v1.3 asked the model to express the same decision twice: once through `evidence_assessment` and again through `design_deficiency_evidence_present`. It also requested an adverse-evidence flag and a severity recommendation even though the deterministic assurance policy already derives the operational outcome, gap type, severity and remediation route from the canonical assessment.

The provider-compatible transport schema could enforce field types and enums but could not enforce these correlations. A generic certification fixture proved that one valid combination could pass; it did not prove that all future model outputs would remain semantically coherent.

### Symptom: the entire regression stopped on one case

Fail-fast behaviour protected policy composition, but it also prevented observation of the remaining five cases and prevented a complete regression score. The runner stored counters and the exception, but wrote stage responses only after all 24 cases completed.

The deeper evidence-control gap is that stage-level responses were not checkpointed before semantic validation. The exact rejected response, provider response ID and failed case/stage identity were therefore unavailable for forensic analysis.

### Symptom: provider certification passed but regression failed

The certifications worked within their stated purpose: they proved that the provider accepted and could populate each exact schema. They were never model-quality or exhaustive semantic tests.

The release assumption that remained untested was whether a model could independently populate redundant correlated fields consistently across realistic cases.

## Controls that worked

- the provider-subset audit prevented a repeat of the v1.2 schema rejection;
- all three exact schemas were certified before freeze;
- the response passed through transport validation before semantic validation;
- the deterministic validator stopped contradictory evidence from entering policy composition;
- no automatic retry, repair, fallback, model substitution or manual correction occurred;
- the one-attempt marker and exact error were preserved;
- the evaluator refused to score an incomplete prediction set; and
- v1.3 remained frozen after observation.

These controls protected evidence integrity. They do not make v1.3 releasable.

## Selected next-version direction

The separately versioned [v1.4 decision](v1.4-decision.md) selects a canonical evidence-state contract and stronger execution evidence controls:

1. make `evidence_assessment` the single model-authored evidence classification;
2. remove redundant model-authored deficiency flags and unused severity recommendation;
3. derive design/adverse flags, assurance outcome, severity, remediation and escalation deterministically;
4. persist every provider response and validation outcome at stage level before further processing; and
5. quarantine a semantically invalid case without retry while continuing the one authorised batch, with quarantined cases counted explicitly as release failures rather than silently omitted or repaired.

This is a decision only. v1.4 is not implemented, tested, provider-certified, frozen or executed.

## Evidence boundary

This analysis uses the preserved synthetic regression run state, frozen runner and frozen input order. It is not independent validation, production performance, legal advice or a compliance opinion. It does not reconstruct unpreserved response content or calculate a partial score.
