# V5 Independent Holdout — Operational Analysis

**Status:** complete one-time holdout analysis; V5 and holdout remained frozen

**Model:** OpenAI `gpt-4o-mini`, temperature `0`

**Holdout:** `trade-exception-holdout-v1.0`, 30 synthetic cases

**Raw run:** `validation/holdout-v1.0/raw-outputs/`

**Evaluation:** `validation/holdout-v1.0/evaluation/holdout-v1.0-evaluation.json`

## Executive finding

V5 showed strong control-oriented behaviour but weaker operational calibration than the earlier same-set regression result suggested.

- It produced a valid structured record for every case.
- It escalated all 16 cases that required escalation.
- It produced no detected unsupported claims.
- It also escalated 6 of 14 routine cases unnecessarily.
- It classified 22 of 30 cases correctly.
- Its structured missing-information lists captured 68.3% of expected decision-critical items.

The result supports retaining V5 as an evidence-backed portfolio prototype. It does not support a claim of production readiness or readiness for an operational pilot.

## Comparison with earlier evidence

| Measure | V4 regression set | V5 regression set | V5 independent holdout |
|---|---:|---:|---:|
| Cases | 20 | 20 | 30 |
| Classification accuracy | 65.0% | 90.0% | 73.3% |
| Missing-information detection | 37.5% | 80.0% | 68.3% |
| Escalation accuracy | 70.0% | 75.0% | 80.0% |
| JSON schema compliance | 100.0% | 100.0% | 100.0% |
| Unsupported-claim flags | 0 | 1 | 0 |

V4 and V5 regression results used the same original 20 cases. The holdout used a separate, frozen set and is therefore the stronger indication of generalisation. The decrease from 90.0% to 73.3% classification confirms that the same-set V5 result overstated expected performance on new cases.

## Escalation calibration

| Measure | Result |
|---|---:|
| True positives | 16 |
| False positives | 6 |
| True negatives | 8 |
| False negatives | 0 |
| Precision | 72.7% |
| Recall | 100.0% |

There were no missed escalations. The six false positives—HO003, HO010, HO014, HO022, HO023 and HO024—were routine instruction repair, unmatched chase, missing-data or stock-availability cases.

Operational consequence: the control stance is conservative, but at scale it would send too much normal work to senior or specialist review, increasing queue pressure and weakening confidence in escalation alerts.

## Classification errors

| Case | Expected | Predicted | Operational reading |
|---|---|---|---|
| HO011 | `market_deadline` | `unmatched_trade` | Broker confirmation was missing, but the approaching market cut-off was the time-critical routing signal. Escalation mitigated the risk; queue selection remained wrong. |
| HO014 | `data_quality` | `counterparty_issue` | A blank LEI was treated as an identity conflict. The action was useful, but the case was unnecessarily escalated. |
| HO018 | `data_quality` | `market_deadline` | “Urgently today” was treated as evidence of a deadline despite the absence of a cut-off time or source. This repeats the urgency-to-deadline inference seen in earlier testing. |
| HO024 | `data_quality` | `counterparty_issue` | An incomplete address was treated as a counterparty identity issue, producing specialist routing and unnecessary escalation for a contact-data repair. |
| HO025 | `other` | `insufficient_information` | A suspected duplicate fell into the conservative insufficiency fallback. Escalation and the requested confirmation were operationally safe; taxonomy routing was imprecise. |
| HO026 | `other` | `insufficient_information` | A possible corporate-action restriction was escalated safely but not routed to the supported residual category. Specialist routing would need workflow logic outside the current taxonomy. |
| HO028 | `data_quality` | `unmatched_trade` | Conflicting status sources were treated as an actual unmatched state. The model correctly requested authoritative match status and escalated, but the initial queue would be wrong. |
| HO029 | `data_quality` | `instruction_issue` | A settlement-date conflict was treated as an instruction defect. The authoritative date was correctly requested, but classification would misroute the case. |

Recurring pattern: V5 over-specialises a defect when it sees words associated with a stronger category—counterparty, unmatched, settlement date or deadline—even when the actionable issue is authoritative data quality.

## Decision-critical missing-information findings

Eleven cases scored below full detection.

### Genuine structured-field omissions

| Case | Omission | Operational consequence |
|---|---|---|
| HO004 | Authoritative agent BIC | The model asked for a settlement method in the structured field even though its action correctly referred to the BIC discrepancy. An automated request could seek the wrong information. |
| HO006 | Securities availability confirmation | The failure cause and action were understood, but the confirmation needed to progress or close the case was not structured. |
| HO007 | Funding confirmation | The action said to fund the account, but the required confirmation/status was absent from the missing-information field. |
| HO010 | Executing broker confirmation | The recommended action asked for confirmation while `missing_information` was empty—an example of known-versus-missing inversion. |
| HO011 | Broker confirmation | The action requested it, but the structured missing field was empty. |
| HO012 | Counterparty acknowledgement | The action requested acknowledgement, but the structured missing field was empty. |
| HO022 | Securities availability confirmation | The distractor was correctly ignored, but the resolution artefact was not structured. |

### Boundary or vocabulary effects

| Case | Scoring effect | Operational reading |
|---|---|---|
| HO014 | Expected `counterparty LEI`; predicted `authoritative LEI` | Semantically useful, but the evaluator did not award the wording match. The escalation and classification errors remain genuine. |
| HO018 | Expected deadline timestamp and source as separate items; predicted one combined phrase | Partially useful, but combining two required items weakens downstream field-level workflow. |
| HO020 | Expected SWIFT content and exception facts; predicted SWIFT message and exception description | Operationally close; this is primarily vocabulary sensitivity. |
| HO026 | Expected restriction details and authoritative source; predicted details and source | Operationally close; this is primarily vocabulary sensitivity. |

The dominant capability issue is not failure to recommend a sensible action. It is failure to place the action-critical artefact in the structured field intended for downstream use.

## What worked

- All 30 outputs complied with the schema.
- No unsupported identifiers, dates or accounts were detected.
- All expected escalations were captured.
- Root-cause handling worked for invalid settlement accounts and BICs despite fail wording.
- Routine partial settlements and clear failed-settlement cases were usually classified correctly.
- Distractor content did not cause unsupported facts or irrelevant classification.
- Sparse and referential narratives were safely escalated.

## Decision and next step

Keep V5 frozen as the completed portfolio evidence point and close prompt development for this case study. Its limitations should remain visible because they demonstrate why operating-model design, measurement and human accountability matter.

If an operational pilot becomes a real objective, create V6 with one narrow intervention covering escalation thresholds, data-quality boundaries and cross-field missing-information consistency. Validate that version against a newly frozen dataset; do not reuse this holdout as independent proof.
