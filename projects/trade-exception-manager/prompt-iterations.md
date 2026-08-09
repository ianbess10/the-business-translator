# Prompt Iterations

## Controlled experiment rule

All engineered prompt versions from **V4 onward** are measured against the frozen set:

**`trade-exception-test-set-v1.0`** (exactly the same 20 cases).

```text
V4
65% classification
37.5% missing information
70% escalation
        ↓
Failure analysis
        ↓
V5
        ↓
Same 20 cases
        ↓
Measured difference
```

Do not change the cases when iterating the prompt. If the cases must change, publish a new test-set version and restart the baseline.

## Version history

## V0 — Open-ended
Goal: establish baseline behaviour.

## V1 — Role + context
Added explicit post-trade operations role and business context.

## V2 — Structured extraction
Added fixed fields and exception taxonomy.

## V3 — Evidence discipline
Added known-fact/inference/missing-information separation and prohibition on invented facts.

## V4 — Controlled workflow
Added JSON schema requirements, escalation rules and explicit decision boundaries.

Frozen release bundle: **`releases/v4/`**

```text
releases/v4
├── prompt
├── test-set-v1.0
├── raw-outputs
├── evaluation
└── failure-analysis
```

Canonical freeze paths:
- Prompt: `releases/v4/prompt/engineered-v4.md`
- Test set: `releases/v4/test-set-v1.0/trade-exception-test-set-v1.0.jsonl`
- Raw outputs: `releases/v4/raw-outputs/engineered/20260808T142916Z/`
- Evaluation: `releases/v4/evaluation/20260808T142952Z.json`
- Failure analysis: `releases/v4/failure-analysis/v4-failure-analysis.md`
- Manifest: `releases/v4/MANIFEST.json`

Working copy `engineered-prompt.md` is intentionally outside the freeze and was not modified for this freeze.

Measured on OpenAI `gpt-4o-mini` (temperature 0):

| Metric | V4 |
|---|---:|
| Classification | 65% |
| Missing information | 37.5% |
| Escalation | 70% |
| JSON schema compliance | 100% |

## V5 — Next revision (planned)

Input: V4 failure analysis on the same 20 cases.  
Method:

1. Revise prompt into `prompts/engineered-v5.md`
2. Set `PROMPT_VERSION=v5`
3. Run on `trade-exception-test-set-v1.0` only
4. Evaluate
5. Compare with `compare_evals.py --baseline benchmarks/v4-reference.json`

```bash
export PROMPT_VERSION=v5
python run_engineered.py
python evaluate.py --variant engineered
python compare_evals.py \
  --baseline benchmarks/v4-reference.json \
  --candidate results/evaluation/<eval_id>.json
```

### Learning

The largest improvement to date came from converting an open-ended generation task into a constrained information-transformation task.

Further gains must be evidenced as measured deltas on the frozen 20-case set, not narrative claims.
