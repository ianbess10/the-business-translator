# Evidence-Gated Decision Pipeline v1.0 — Regression Results

> **Evidence boundary:** This is comparison on the same 24 frozen synthetic regression cases used for workflow design. It is not independent validation or production performance.

## Headline comparison

| Measure | Simple baseline | Evidence-gated | Change |
|---|---:|---:|---:|
| End-to-end exact | 4.2% | 62.5% | 58.3% |
| Source-use disposition | 70.8% | 100.0% | 29.2% |
| Obligation outcome | 58.3% | 100.0% | 41.7% |
| Applicability status | 62.5% | 62.5% | 0.0% |
| Control and owner mapping | 33.3% | 100.0% | 66.7% |
| Assurance outcome | 91.7% | 91.7% | 0.0% |
| Escalation decision | 66.7% | 95.8% | 29.2% |

## Release gates

| Gate | Result |
|---|---|
| zero assurance stage leakage | PASS |
| zero prohibited compliance conclusions | PASS |
| exact source boundary treatment | PASS |
| exact catalogue owner routing | PASS |
| all mandatory escalations detected | PASS |
| zero unnecessary escalations | FAIL |
| routine missing evidence kept distinct | PASS |
| cross field reconciliation without manual correction | PASS |

## Escalation confusion matrix

| True positive | False positive | True negative | False negative |
|---:|---:|---:|---:|
| 6 | 1 | 17 | 0 |

## Interpretation

This run must be reported exactly as observed. The frozen workflow must not be tuned or rerun after these results are seen. Passing the regression gates permits preparation of a separate unseen holdout; it does not establish production readiness.
