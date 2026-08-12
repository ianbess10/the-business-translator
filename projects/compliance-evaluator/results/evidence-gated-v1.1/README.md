# Evidence-Gated Decision Pipeline v1.1 — Regression Results

> **Evidence boundary:** This is comparison on the same 24 frozen synthetic regression cases used for workflow design. It is not independent validation or production performance.

## Headline comparison

| Measure | Simple baseline | v1.0 | v1.1 | v1.1 vs v1.0 |
|---|---:|---:|---:|---:|
| End-to-end exact | 4.2% | 62.5% | 83.3% | 20.8% |
| Source-use disposition | 70.8% | 100.0% | 100.0% | 0.0% |
| Obligation outcome | 58.3% | 100.0% | 95.8% | -4.2% |
| Applicability status | 62.5% | 62.5% | 100.0% | 37.5% |
| Control and owner mapping | 33.3% | 100.0% | 95.8% | -4.2% |
| Assurance outcome | 91.7% | 91.7% | 95.8% | 4.2% |
| Escalation decision | 66.7% | 95.8% | 100.0% | 4.2% |

## Release gates

| Gate | Result |
|---|---|
| zero assurance stage leakage | PASS |
| zero prohibited compliance conclusions | PASS |
| exact source boundary treatment | PASS |
| exact catalogue owner routing | FAIL |
| all mandatory escalations detected | PASS |
| zero unnecessary escalations | PASS |
| routine missing evidence kept distinct | PASS |
| cross field reconciliation without manual correction | PASS |
| exact applicability and approved authority | PASS |
| exact mapping status for entered assurance | FAIL |
| exact entered assurance decisions | FAIL |
| partial coverage not promoted to design escalation | FAIL |
| evidence condition does not demote mapping | FAIL |
| general policy rules without case overrides | FAIL |

## Escalation confusion matrix

| True positive | False positive | True negative | False negative |
|---:|---:|---:|---:|
| 6 | 0 | 18 | 0 |

## Interpretation

This run must be reported exactly as observed. The frozen v1.1 workflow must not be tuned or rerun after these results are seen. Passing every regression gate permits preparation of a separate unseen holdout; it does not establish production readiness.
