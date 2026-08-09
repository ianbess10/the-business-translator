# V5 Independent Operational Holdout — Result

**Status:** complete

**Decision:** retain V5 as the frozen portfolio prototype; do not present it as ready for production or a controlled operational pilot

**Run:** `20260809T174850Z_holdout-v1`

**Evaluation:** `20260809T175010Z_holdout-v1`

**Model:** OpenAI `gpt-4o-mini`, temperature `0`

**Cases:** 30 frozen synthetic holdout cases

**Prompt changes before or during run:** none

## Headline result

| Measure | Result |
|---|---:|
| Classification accuracy | 73.3% (22/30) |
| Decision-critical missing-information detection | 68.3% |
| Escalation accuracy | 80.0% (24/30) |
| Escalation precision | 72.7% |
| Escalation recall | 100.0% |
| JSON schema compliance | 100.0% (30/30) |
| Unsupported-claim flags | 0 |

Escalation outcomes:

| | Expected escalation | Expected normal handling |
|---|---:|---:|
| Model escalated | 16 true positives | 6 false positives |
| Model did not escalate | 0 false negatives | 8 true negatives |

## Operational interpretation

The strongest result is risk containment: V5 escalated every case labelled as requiring escalation, returned valid structured records for every case and introduced no detected unsupported facts.

The principal weakness is operating efficiency. Six routine cases were unnecessarily escalated. This would increase review workload and create alert fatigue if the capability were introduced without further calibration.

Classification performance also revealed routing-boundary problems. V5 sometimes treated a missing counterparty field as a counterparty identity issue, a settlement-date conflict as an instruction issue, a match-status conflict as an unmatched trade and urgency without a precise deadline as a market-deadline case. Two specialist cases were conservatively classified as insufficient information rather than `other`.

Several missing-information misses were field-placement or vocabulary failures rather than complete operational misunderstandings. In some cases the recommended action correctly requested the missing artefact while the structured `missing_information` list remained empty. That is still material: downstream workflow automation cannot safely rely on information that appears only in prose.

## Decision

V5 is retained unchanged as the final portfolio prototype because the holdout provides more value as independent evidence than as another tuning set. The result demonstrates both meaningful capability and the limits of apparently well-structured AI output.

V5 is **not ready to support an operational pilot without further work**. If the project proceeds toward piloting, the next intervention should be narrowly focused on:

1. keeping routine instruction repairs, unmatched chases and stock/funding investigations out of escalation unless an explicit material trigger exists;
2. separating missing data from identity, instruction and match-status conflicts for correct first-time routing; and
3. requiring every action-critical request in `recommended_next_action` to appear explicitly in `missing_information`.

Any V6 developed from these findings must be validated on a new frozen holdout. Reusing this dataset as proof of independent validation would invalidate the claim.

## Evidence

- [Case-level operational analysis](../../results/analysis/v5-holdout-analysis.md)
- [Machine-readable evaluation](evaluation/holdout-v1.0-evaluation.json)
- [Raw model outputs](raw-outputs/)
- [Frozen protocol](../holdout-v1.0-protocol.md)
- [Manifest](MANIFEST.json)

These figures are synthetic benchmark evidence. They are not production performance and do not demonstrate time, cost, STP or risk benefits.
