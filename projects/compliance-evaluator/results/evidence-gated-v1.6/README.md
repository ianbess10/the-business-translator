# Evidence-Gated Decision Pipeline v1.6 — Regression Results

> Synthetic frozen regression evidence against benchmark authority v1.1; not independent validation or production performance.

## Controlled execution

Frozen v1.6 was executed exactly once across all 24 frozen inputs and its complete terminal-case record was evaluated exactly once. No tuning, repair, retry, rerun or rescoring occurred.

- Terminal cases: **24/24**
- Completed cases: **24**
- Quarantined cases: **0**
- API calls: **24/24 maximum**
- Semantically valid calls: **24**
- Retry count: **0**
- Tuning after observation: **false**
- Model: `gpt-4o-mini-2024-07-18`
- Benchmark authority: **v1.1**

## Result

- End-to-end exact: **23/24 (95.83%)**
- Escalation TP / FP / TN / FN: **6 / 0 / 18 / 0**
- Dual-axis authority gate: **passed**
- Release gates: **5/6 passed**
- Release decision: **failed**

`CON-011`, the material v1.5 policy failure, now preserves both partial coverage and adverse operating evidence. It routes mapping review and operating remediation concurrently and escalates to the Conduct Risk Officer and Head of Compliance.

The sole non-exact case is `CON-008`. v1.6 preserved both its partial-coverage and design-deficiency conditions, producing two gap types and two remediation actions. Benchmark authority v1.1 inherits the original single-gap expectation for this undisputed case, so the evaluator counted `gap_types` and `remediation_action_types` as mismatches. This must be examined in a separately versioned failure analysis; neither the frozen workflow nor the authority record may be changed retrospectively.

## Release boundary

Five gates passed: complete terminal coverage, zero quarantine, exact adjudicated dual-axis authority, all mandatory escalations detected and zero unnecessary escalations. The all-decision-fields-exact gate failed at 23/24, so v1.6 does not proceed to holdout.

The next stage is a case-level v1.6 failure analysis and separately versioned next-workflow decision. v1.6 must not be modified, rerun or rescored.
