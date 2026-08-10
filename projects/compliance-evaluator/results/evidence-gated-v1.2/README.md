# Evidence-Gated Decision Pipeline v1.2 — Regression Execution Outcome

> **Evidence boundary:** This is the preserved outcome of the sole authorised v1.2 execution attempt against the 24 frozen synthetic regression cases. It is not independent validation or production performance.

## Outcome

The frozen v1.2 runner was started exactly once on 10 August 2026 using `gpt-4o-mini-2024-07-18` at temperature `0`.

The provider rejected the first source-stage request before generating a model response:

```text
Invalid schema for response_format 'source_support_stage_v1_2':
In context=(), 'allOf' is not permitted.
```

The preserved [`run-state.json`](run-state.json) records:

| Measure | Preserved outcome |
|---|---:|
| Run status | `failed` |
| Expected API calls | 32 |
| Successfully completed API calls | 0 |
| Completed cases | 0 of 24 |
| Predictions produced | 0 |
| Tuning after observation | `false` |

## Scoring disposition

No `predictions.json` exists, so no operational decision can be compared with the evaluator-only labels. The evaluator was not invoked and no score, field metric, confusion matrix or release-gate result is claimed.

Treating the provider rejection as `0/24` would be misleading: it is an execution-contract failure, not 24 observed model decisions. Re-running after changing the frozen schema would also violate the one-run protocol.

## Release decision

v1.2 does not pass the regression release boundary and cannot proceed to unseen holdout validation. The workflow, prompts, schemas, policies and frozen metadata remain unchanged. Any correction to the provider-compatible Structured Outputs contract must be analysed and implemented only in a separately versioned workflow.
