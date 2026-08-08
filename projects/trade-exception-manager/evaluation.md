# Evaluation

## Metrics

| Metric | Baseline | Engineered |
|---|---:|---:|
| Correct regulatory/source identification | 62% | 94% |
| JSON schema compliance | 50% | 98% |
| Unsupported claims | 28% | 2% |
| Required human editing time | 22 min | 6 min |

**Important:** These figures are portfolio benchmark values and should be replaced with run-level evidence when the evaluation is executed against the final test set.

## Scoring

- extraction accuracy: 25
- classification accuracy: 20
- completeness: 15
- schema compliance: 10
- unsupported claims: 15
- human usefulness: 15

Total: 100.

## Evaluation rule

A plausible answer that contains an unsupported fact is a failure, even if the overall narrative appears useful.
