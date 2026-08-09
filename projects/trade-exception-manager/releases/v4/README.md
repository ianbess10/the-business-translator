# Trade Exception Intelligence — V4 Freeze

**Status:** frozen  
**Freeze ID:** `trade-exception-v4`  
**Prompt version:** `v4`  
**Test set:** `trade-exception-test-set-v1.0` (20 cases)  
**Model:** OpenAI `gpt-4o-mini`, temperature `0`

```text
V4
├── prompt
├── test-set-v1.0
├── raw-outputs
├── evaluation
└── failure-analysis
```

## Contents

| Artefact | Path |
|---|---|
| Prompt | `prompt/engineered-v4.md` |
| Test set | `test-set-v1.0/trade-exception-test-set-v1.0.jsonl` |
| Raw outputs (engineered) | `raw-outputs/engineered/20260808T142916Z/` |
| Raw outputs (baseline companion) | `raw-outputs/baseline/20260808T142741Z/` |
| Evaluation | `evaluation/20260808T142952Z.json` |
| Evaluation summary | `evaluation/v4-reference.json` |
| Failure analysis | `failure-analysis/v4-failure-analysis.md` |
| Checksums / inventory | `MANIFEST.json` |

## Measured headline metrics

| Metric | Score |
|---|---:|
| Classification | 65% |
| Missing information | 37.5% |
| Escalation | 70% |
| JSON schema compliance | 100% |

## Immutability rules

1. Do **not** edit files under `releases/v4/` in place.
2. Do **not** modify root `engineered-prompt.md` as part of this freeze (working copy stays separate).
3. Future work is **V5+** against the **same** `test-set-v1.0`.
4. Compare with:

```bash
python compare_evals.py \
  --baseline releases/v4/evaluation/v4-reference.json \
  --candidate results/evaluation/<new_eval_id>.json
```
