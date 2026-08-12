# Evidence-Gated Decision Pipeline v1.4

## Status

**Implemented, tested, provider-certified and frozen before regression.** No v1.4 regression execution or result exists. A future run requires separate explicit authorisation and may occur exactly once.

v1.4 is a separate workflow. It does not modify, rerun or score v1.3.

## Operational correction

v1.3 asked the model to represent one evidence decision through several correlated fields. A contradiction stopped the sole regression on `CON-007`. v1.4 removes that avoidable ambiguity.

The model now returns one canonical `evidence_assessment`. Deterministic policy derives:

- design-deficiency and adverse-indicator audit flags;
- assurance outcome;
- gap type and severity;
- remediation routing; and
- escalation.

The model no longer authors separate deficiency flags or an unused severity recommendation. This reduces the semantic state space without weakening the operational control.

## Execution evidence and quarantine

Every provider response is written to an append-only stage ledger before semantic validation or policy composition. The record includes case, stage, request ordinal, provider metadata, parsed response, validation results, error and zero retry count.

If a stage fails, that case is quarantined for mandatory human review. It receives no policy conclusion and no retry, repair or fallback. The same one-time batch continues to later frozen cases so a single malformed response cannot conceal the remaining workflow behaviour.

The evaluator requires one terminal record per case. A quarantine:

- counts as an end-to-end error;
- blocks release;
- is excluded from decision-field and escalation denominators because no decision exists; and
- is reported separately with the reduced denominator disclosed.

## Provider certification

The source/support and mapping schema, prompt, model and endpoint hashes are byte-identical to their accepted v1.3 contracts. The one changed evidence contract received one new generic non-benchmark certification using `gpt-4o-mini-2024-07-18`, temperature `0`, Chat Completions and strict Structured Outputs.

The changed schema passed provider acceptance, transport validation and canonical semantic validation. Certification used no regression input, evaluator label or expected benchmark decision and is not model-quality evidence.

## Offline release evidence

- all three schemas pass the conservative provider-subset audit;
- all six evidence classifications derive deterministic operational adapter fields;
- redundant evidence fields are absent and three invalid canonical states are rejected;
- stage evidence is checkpointed before semantic blocking;
- semantic failure produces zero-retry quarantine and later-case continuation;
- all 24 frozen paths compose through canonical evidence;
- all eight assurance payload pairs remain isolated;
- the quarantine-aware evaluator accepts 24/24 perfect terminal records and blocks release when one case is quarantined; and
- missing, failed or stale certification cannot unlock regression.

## Frozen future protocol

One future batch may make at most 32 calls: 16 source/support, eight mapping and up to eight evidence calls. A mapping quarantine skips that case's evidence call. No case is retried.

```bash
python run_regression.py --preflight
python run_regression.py --execute
python evaluate_regression.py
```

There is no mock, automatic repair, JSON-mode, alternate-model or alternate-endpoint fallback. Any future outcome remains synthetic regression evidence, not independent validation or production performance.
