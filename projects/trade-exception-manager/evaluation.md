# Evaluation

## Controlled comparison protocol

Prompt versions are compared only when they use:

1. the frozen test set `trade-exception-test-set-v1.0` (same 20 cases);
2. the same `evaluate.py` metric definitions;
3. recorded model/provider settings.

```text
V4 → failure analysis → V5 → same 20 cases → measured difference
```

## Measured V4 baseline

Source: actual OpenAI `gpt-4o-mini` run on `trade-exception-test-set-v1.0`.  
Reference file: `benchmarks/v4-reference.json`.

| Metric | V4 engineered |
|---|---:|
| Classification accuracy | **65%** |
| Missing-information detection | **37.5%** |
| Escalation accuracy | **70%** |
| JSON schema compliance | 100% |
| Unsupported-claim flags | 0 |

Failure analysis: `failure-analysis/v4-on-test-set-v1.0.md`.

Compare a later version with:

```bash
python compare_evals.py \
  --baseline benchmarks/v4-reference.json \
  --candidate results/evaluation/<eval_id>.json
```

## Illustrative portfolio table (not run evidence)

| Metric | Baseline | Engineered |
|---|---:|---:|
| Correct regulatory/source identification | 62% | 94% |
| JSON schema compliance | 50% | 98% |
| Unsupported claims | 28% | 2% |
| Required human editing time | 22 min | 6 min |

**Important:** The table above is illustrative only. Public claims about V4/V5 performance must cite measured run artefacts (`benchmarks/` or `results/evaluation/`).

## Executable metrics

`evaluate.py` scores an actual results folder and reports:

- classification accuracy (`exception_type` vs `expected_type`)
- JSON schema compliance (`schema/engineered_output.schema.json`)
- missing-information detection (coverage of `expected_missing_information`)
- escalation accuracy (`escalation_required` vs `expected_escalation`)
- unsupported-claim flags (identifiers/dates/accounts not present in the case input)

Baseline free-text runs contribute unsupported-claim statistics only; structured metrics apply to engineered outputs.

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
