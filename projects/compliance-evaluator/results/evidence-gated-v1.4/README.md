# Evidence-Gated Decision Pipeline v1.4 — Regression Results

## Outcome

The frozen v1.4 workflow was executed exactly once against all 24 frozen synthetic regression cases and evaluated exactly once without tuning, repair, retry or rerun.

- end-to-end exact: **21/24 (87.5%)**;
- completed terminal cases: **24/24**;
- quarantined cases: **0**;
- requested and semantically valid model calls: **32/32**;
- retries: **0**; and
- release gates passed: **9/15**.

The workflow therefore **does not pass release** and cannot proceed to holdout validation.

## What worked

- source disposition, obligation outcome, applicability and assurance gate were exact across all 24 cases;
- current control IDs and catalogue-owner routing were exact across all 24 cases;
- all responses passed transport and semantic validation;
- `CON-007`, which stopped v1.3, completed under the canonical evidence contract;
- no case was quarantined;
- no unnecessary escalation occurred;
- escalation precision was **100%**; and
- human review and `not_determined` compliance conclusions were preserved in all cases.

## Remaining decision errors

Three market-conduct assurance cases were not end-to-end exact:

| Case | Primary observed mismatch |
|---|---|
| `CON-008` | Mapping, assurance and remediation were wrong; one mandatory escalation was missed |
| `CON-010` | Partial mapping was not preserved, changing assurance, gap severity and remediation |
| `CON-012` | Evidence condition demoted mapping and changed the routine missing-evidence outcome |

These cases require separate case-level failure analysis. This report does not tune or select a new workflow.

## Escalation performance

| Measure | Result |
|---|---:|
| True positives | 5 |
| False positives | 0 |
| True negatives | 18 |
| False negatives | 1 |
| Precision | 100% |
| Recall | 83.33% |
| Accuracy | 95.83% |

The missed escalation means the mandatory-escalation release gate failed even though unnecessary escalation remained at zero.

## Release decision

Nine of 15 gates passed. Failures were concentrated in:

- detection of all mandatory escalations;
- separation of routine missing evidence;
- exact mapping status for entered assurance;
- exact entered-assurance decisions;
- partial coverage not being promoted or displaced incorrectly; and
- evidence condition not demoting mapping.

Zero quarantine passed as an additional v1.4 gate, but it does not offset the decision-quality failures.

## Evidence boundary

This is evidence from the same 24 frozen synthetic regression cases used throughout workflow development. It is not independent validation, production performance, legal advice or a compliance opinion. v1.4 remains frozen and will not be tuned, rerun or rescored.
