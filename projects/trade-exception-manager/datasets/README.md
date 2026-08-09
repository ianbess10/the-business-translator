# Datasets

## trade-exception-test-set-v1.0

Frozen synthetic evaluation set for Trade Exception Intelligence.

| Field | Value |
|---|---|
| ID | `trade-exception-test-set-v1.0` |
| Status | frozen |
| Cases | 20 |
| File | `trade-exception-test-set-v1.0.jsonl` |
| Metadata | `trade-exception-test-set-v1.0.meta.json` |

Do not edit the frozen JSONL in place. Publish a new version (for example `v1.1`) if cases change.

## trade-exception-holdout-v1.0

Frozen 30-case synthetic holdout for a one-time independent operational validation of V5.

| Field | Value |
|---|---|
| ID | `trade-exception-holdout-v1.0` |
| Status | frozen |
| Cases | 30 |
| File | `trade-exception-holdout-v1.0.jsonl` |
| Metadata | `trade-exception-holdout-v1.0.meta.json` |

The holdout is separate from the original 20-case regression set. It must not be used to revise V5 before the one-time run, and the result must not be presented as production performance.
