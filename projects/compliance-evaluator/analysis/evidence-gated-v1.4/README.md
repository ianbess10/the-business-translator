# Evidence-Gated Decision Pipeline v1.4 — Case-Level Failure Analysis

## Executive outcome

Evidence-Gated Decision Pipeline v1.4 completed all 24 frozen synthetic cases with 32/32 transport- and semantic-valid model calls, zero quarantine and zero retry. It achieved **21/24 end-to-end exact** and passed nine of 15 release gates.

The three failed cases are concentrated in one operational decision boundary: **the workflow lacks an approved obligation-to-control coverage authority**. The mapping stage received an atomic obligation, submitted control IDs and short catalogue names, then inferred whether each control completely covered the obligation.

That inference was wrong in both directions:

- `C-CON-006` was treated as complete in `CON-008` and `CON-010`, where the frozen expected mapping is partial; and
- `C-CON-007` was treated as partial in `CON-012`, where the frozen expected mapping is complete.

The downstream assurance policy behaved consistently with those mapping outputs. The primary failure is therefore not escalation logic or cross-field reconciliation. It is insufficient business meaning at the mapping boundary.

A second error affected `CON-008`: a supplied procedure missing governance fields was classified as missing operating evidence instead of a design deficiency. This exposes the same data-contract weakness on the evidence side: required design attributes and operating records are described in prose rather than represented as approved, typed assurance requirements.

v1.4 remains frozen. It was not modified, tuned, rerun or rescored.

## Headline evidence

| Measure | Result |
|---|---:|
| End-to-end exact | 21/24 (87.5%) |
| Release gates | 9/15 |
| Completed terminal cases | 24/24 |
| Quarantined cases | 0 |
| Model calls passing transport and semantics | 32/32 |
| Escalation TP / FP / TN / FN | 5 / 0 / 18 / 1 |

Source use, obligation outcome, applicability, assurance gating, current control identity, owner routing, human review and compliance conclusion were exact across all cases.

## Case-level analysis

### `CON-008` — potential complaints-framework design gap

Expected:

- `C-CON-006` is a partial mapping;
- the supplied procedure lacks approval, ownership and review-cycle design attributes;
- assurance outcome is a high potential design gap; and
- escalation to Head of Compliance is required.

Observed:

- mapping stage returned `complete` for `C-CON-006` while also identifying `C-CON-007` as an additional candidate;
- evidence stage returned `missing_operating_evidence`; and
- policy produced an unassessed evidence request with no escalation.

The mapping output is internally permitted but operationally weak: identifying a relevant additional control while claiming no uncovered obligation element provides no authoritative coverage explanation. The evidence output then treated absent governance design fields as though completed operating records were merely missing.

This case caused the sole false-negative escalation.

### `CON-010` — partial mapping across complaint controls

Expected:

- `C-CON-006` covers complaint handling but not the ongoing framework-oversight element;
- mapping is partial;
- the gap is partial coverage with medium severity; and
- mapping review is required without escalation.

Observed:

- mapping stage returned `complete` for `C-CON-006` and listed `C-CON-007` only as a candidate;
- evidence stage correctly found the presented framework and register sufficient; and
- policy returned mapped and evidenced with no gap.

This is the cleanest proof that the failure sits upstream of evidence. Even correct evidence classification cannot compensate for an incorrect coverage decision.

### `CON-012` — routine missing management-information evidence

Expected:

- `C-CON-007` is the complete current mapping;
- the latest monthly report is missing;
- assurance outcome is insufficient evidence;
- a routine evidence request is proportionate; and
- escalation is not required.

Observed:

- mapping stage returned `partial` for `C-CON-007` and proposed `C-CON-006` as an additional candidate;
- evidence stage correctly returned `missing_operating_evidence`; but
- deterministic partial-coverage precedence converted the final outcome to a medium mapping gap.

The evidence stage did not demote mapping. The incorrect mapping output caused the policy to take the partial-coverage path, as designed. This distinction matters because changing evidence precedence would treat the symptom and weaken the established mapping/evidence boundary.

## Symptom versus root cause

### Symptom: mapping completeness was wrong in three cases

Prompt tuning could emphasize control names or relevant candidates, but the stage still lacks a reviewed record of which atomic obligation elements each control covers. The model is being asked to create an assurance conclusion from descriptive names such as “complaint classification, escalation and remediation” and “customer-outcomes management-information review.”

The root cause is an **authority gap**: approved obligation records identify affected controls, but do not contain approved coverage assertions at obligation-element level.

### Symptom: `CON-008` missed a design deficiency

The evidence prompt distinguishes design deficiency from missing operating evidence, but the evidence input does not provide a typed checklist of required design attributes and operating artefacts.

The root cause is an **assurance-requirement gap**: prose descriptions are being used where the operating model needs approved evidence requirements with requirement type, expected attributes and failure classification.

### Symptom: one escalation was missed

Escalation policy correctly escalates high potential control gaps. It received an unassessed missing-evidence outcome because the mapping and evidence classifications were wrong.

The root cause is upstream decision meaning, not escalation calibration. Adding a case-specific escalation trigger would obscure that causal chain.

## Controls that worked

- the canonical evidence contract removed the v1.3 semantic contradiction;
- `CON-007` completed successfully;
- every stage response was checkpointed before validation and composition;
- mapping and evidence inputs remained isolated;
- current controls were never replaced by remediation candidates;
- catalogue owners were exact;
- deterministic policy reconciled every accepted stage output without manual correction;
- no quarantine, retry, repair, fallback or case-specific override occurred;
- zero unnecessary escalations were produced; and
- the evaluator preserved all 15 release gates and blocked holdout progression.

## Selected next-version direction

The separately versioned [v1.5 decision](v1.5-decision.md) selects an **Approved Coverage and Evidence Rulebook**:

1. decompose each approved obligation into reviewed obligation elements;
2. link each relevant control to those elements using human-approved coverage assertions;
3. define typed design and operating-evidence requirements with explicit failure classifications;
4. make the model extract bounded facts rather than decide mapping completeness or assurance consequences from prose; and
5. derive mapping, evidence outcome, remediation and escalation deterministically from the approved rulebook and extracted facts.

This is a decision record only. v1.5 is not implemented, tested, certified, frozen or executed.

## Evidence boundary

This analysis uses the frozen v1.4 regression inputs, predictions, stage ledger, labels and evaluation. It is synthetic regression analysis, not independent validation, production performance, legal advice or a compliance opinion. No label or result artefact was changed.
