# Benchmarks

Frozen measured baselines for prompt-version comparison.

## V4 reference

- File: `v4-reference.json`
- Prompt: `v4` / `prompts/engineered-v4.md`
- Test set: `trade-exception-test-set-v1.0` (20 cases)
- Headline metrics:
  - classification **65%**
  - missing information **37.5%**
  - escalation **70%**

Use this file as `--baseline` for `compare_evals.py` when measuring V5+.
