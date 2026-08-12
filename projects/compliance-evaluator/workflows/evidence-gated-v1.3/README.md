# Evidence-Gated Decision Pipeline v1.3

## Status

**Implemented, tested, provider-certified and frozen before regression.** No v1.3 benchmark execution or result exists. Regression requires a separate explicit instruction and must occur exactly once.

v1.3 is a separate workflow. It does not alter, rerun or score v1.2; the preserved v1.2 provider-contract failure remains evidence.

## What changed

v1.3 corrects the execution contract without relaxing the operational controls selected in v1.2:

- each model-facing schema uses an explicit conservative subset of OpenAI Structured Outputs;
- release-critical cross-field rules are enforced by deterministic semantic validators after transport validation and before policy composition;
- a recursive allowlist audit rejects unsupported or unknown schema keywords before any benchmark run;
- mapping inputs remain isolated from evidence and escalation proposals;
- evidence output cannot change current-control membership; and
- the regression runner is locked to the exact certified schema, prompt, model and endpoint hashes.

The deterministic source, applicability, assurance, ownership, escalation and reconciliation policies remain the frozen v1.2 policy layer. This keeps v1.3 focused on the failed provider boundary.

## Provider certification

Three generic sentinel calls were made on 11 August 2026 using `gpt-4o-mini-2024-07-18`, temperature `0`, the Chat Completions endpoint and strict Structured Outputs:

| Contract | Calls | Provider accepted | Transport valid | Semantic valid |
|---|---:|---:|---:|---:|
| Source/support | 1 | Yes | Yes | Yes |
| Mapping | 1 | Yes | Yes | Yes |
| Evidence | 1 | Yes | Yes | Yes |

The [certification record](certification/contract-certification-v1.3.json) preserves response IDs, timestamps, usage and hashes. These were **three non-benchmark development contract calls**: no frozen regression input, evaluator label or expected benchmark decision was used, and no model-quality score is claimed.

## Offline release evidence

- provider-subset audit: three valid schemas and 12 prohibited contract states;
- semantic boundaries: three valid states, 23 invalid states and three transport-valid semantic rejections;
- full-path smoke composition: all 24 frozen input paths;
- payload isolation: all eight mapping and evidence paths;
- evaluator self-test: 24/24 exact and 14/14 release gates; and
- certification permission gate: valid evidence accepted; missing, failed, incomplete, stale and wrong-model states rejected.

## Frozen execution protocol

The next authorised stage is one 24-case regression execution: 16 source/support calls, eight mapping calls and eight evidence calls, for 32 model calls in total. The runner refuses to start if certification is missing, failed or stale, if a frozen artefact hash changes, or if a v1.3 result directory already exists.

```bash
python run_regression.py --preflight
python run_regression.py --execute
python evaluate_regression.py
```

There is no mock, JSON-mode, alternate-model or alternate-endpoint fallback. Provider rejection, refusal or runtime failure is preserved as the outcome. Any future score is synthetic regression evidence, not independent validation or production performance.
