# Intentionally Simple Baseline v1.0

## Purpose

This baseline establishes the unengineered starting point for the Regulatory Change & Obligation-to-Control Intelligence case study. It is deliberately compact: one fixed instruction, one structured prediction contract and one deterministic scorer.

The objective is not to maximise a benchmark score. It is to expose where a general AI model produces a plausible-looking answer that is operationally wrong across source status, obligation decisions, applicability, control mapping, evidence, ownership or escalation.

## Frozen run design

- Dataset: `SA-REG-BASELINE-001 v1.0`, 24 synthetic cases.
- Model: `gpt-4o-mini-2024-07-18` snapshot.
- Temperature: `0`.
- Model access: frozen input files only; evaluator labels are never loaded by the runner.
- Output: strict structured prediction contract.
- Run rule: one API request per case in one baseline run.
- Tuning rule: no prompt changes or rerun after observing results.
- Evidence boundary: synthetic benchmark evidence, not production performance.

## Files

- [`baseline-prompt-v1.0.md`](baseline-prompt-v1.0.md) — intentionally simple instruction.
- [`baseline-prediction.schema.json`](baseline-prediction.schema.json) — machine-enforced output contract.
- [`run_baseline.py`](run_baseline.py) — input-only, one-run API runner.
- [`evaluate_baseline.py`](evaluate_baseline.py) — deterministic scorer with exact-match and calibration measures.
- `baseline-v1.0.meta.json` — frozen hashes and model settings.
- [`../results/baseline-v1.0`](../results/baseline-v1.0) — immutable run evidence after execution.

## Measures

The evaluator reports:

- end-to-end exact operational disposition;
- source-use, obligation-outcome, applicability and assurance-gate accuracy;
- entered-case control mapping and owner-routing accuracy;
- evidence/gap outcome accuracy;
- potential-gap precision and recall;
- insufficient-evidence precision and recall;
- escalation precision, recall and confusion matrix;
- prohibited compliance-conclusion count; and
- case- and failure-tag-level mismatches for analysis.

Rationale wording is retained but excluded from exact-match scoring because the controlled decisions, not prose similarity, are the benchmark target.

## Reproduction safeguards

The runner verifies the frozen prompt, schema, evaluator and input hashes before it calls the API. It refuses to run without a real OpenAI credential and has no mock fallback. It also refuses to overwrite a run marker or completed predictions.

The scorer may be checked offline before execution:

```bash
python3 evaluate_baseline.py --self-test
python3 run_baseline.py --preflight
```

After the real run, execute the scorer once:

```bash
python3 evaluate_baseline.py
```

Do not alter this baseline to improve the observed result. Any later workflow intervention belongs in a separately versioned engineered workflow and must be compared against these preserved results.
