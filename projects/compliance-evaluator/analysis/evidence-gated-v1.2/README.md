# Evidence-Gated Decision Pipeline v1.2 — Execution-Contract Failure Analysis

## Executive outcome

Evidence-Gated Decision Pipeline v1.2 did not reach model inference. Its sole authorised regression execution attempt was rejected by the provider before the first response was generated because the frozen source-stage Structured Outputs schema used the unsupported root composition keyword `allOf`. [Official OpenAI Structured Outputs documentation](https://developers.openai.com/api/docs/guides/structured-outputs) states that the feature supports a subset of JSON Schema and explicitly lists `allOf`, `if` and `then` among unsupported composition keywords.

This is an **execution-contract failure**, not a model-decision failure. No case completed, no prediction exists and no operational accuracy, escalation or release-gate metric can be calculated. Treating the outcome as `0/24` would wrongly convert an unavailable measurement into 24 observed decision errors.

The release conclusion is nevertheless decisive: v1.2 failed the regression release boundary and cannot proceed to holdout validation. It remains frozen, was not modified or rerun, and was not scored.

This analysis uses the single preserved [`run-state.json`](../../results/evidence-gated-v1.2/run-state.json). It does not modify the v1.2 workflow, prompts, schemas, policies, runner, evaluator, inputs, labels or result evidence.

## What happened

The frozen runner passed its local preflight for all 24 inputs and then started run `evidence-gated-v1.2-a9972172-5cb7-4d7f-89ad-0011586d37db` using `gpt-4o-mini-2024-07-18` at temperature `0`.

The first source/support request returned HTTP 400:

```text
Invalid schema for response_format 'source_support_stage_v1_2':
In context=(), 'allOf' is not permitted.
```

The audit marker records zero successfully completed API calls, zero completed cases, no tuning after observation and final status `failed`. No `predictions.json`, evaluation or comparison artefact exists.

## Root-cause summary

| Layer | Finding | Consequence |
|---|---|---|
| Immediate trigger | The source/support response schema used root-level `allOf` with `if` and `then` conditions | The provider rejected the request before inference |
| Contract mismatch | Offline validation checked general JSON Schema validity, while strict Structured Outputs accepts only a provider-supported subset | A locally valid schema was incorrectly treated as executable |
| Preflight gap | Preflight verified hashes, files, case counts and local schema construction but did not audit provider-subset keywords or certify schemas against the pinned endpoint | Release-blocking compatibility remained undetected until the regression attempt |
| Control-placement issue | Cross-field business invariants were encoded inside the model transport schema | Business validation became dependent on unsupported provider composition features |

## Schema exposure register

The first error proves only the source-stage rejection. It does not prove how the provider would have treated later schemas because execution stopped immediately.

| Schema | Observed or latent exposure | Classification |
|---|---|---|
| Source/support | Uses `allOf`, `if`, `then`, `const`, `uniqueItems` and length/cardinality constraints | `allOf`, `if` and `then` are confirmed unsupported by the provider response and official contract; the request was rejected |
| Mapping | Uses `allOf`, `if`, `then`, `const`, `uniqueItems` and length/cardinality constraints | Contains the same confirmed-unsupported composition design, but was never submitted |
| Evidence | Uses simple required properties and `minLength` | Never submitted; compatibility was not certified and must not be inferred from local validation alone |

`uniqueItems` is not relied upon in the next decision because it is not listed in the documented supported property set. This analysis does not claim the provider independently rejected that keyword.

## Symptom versus root cause

### Symptom: the API rejected `allOf`

Removing that single keyword would address the reported message but not the control failure. The mapping schema repeats the same composition pattern, and the release process still lacks a provider-parity gate.

The root cause is broader: the workflow equated full JSON Schema validity with strict Structured Outputs compatibility.

### Symptom: offline schema tests passed

The tests correctly proved that valid examples satisfied, and invalid examples violated, the authored Draft 2020-12 schemas. They did not prove that the provider accepts every keyword in those schemas.

The tests were therefore useful but incomplete. The missing control was a second validation layer for the actual provider subset and endpoint.

### Symptom: no score exists

The evaluator did not fail. It correctly requires completed predictions. With no model decisions, there is no numerator, denominator, field comparison or escalation confusion matrix to calculate.

The root cause sits before inference and before evaluation. A fabricated zero score or forced evaluator invocation would obscure that causal boundary.

## Controls that worked

The failure also demonstrates that several governance controls operated as intended:

- frozen artefact hashes were verified before execution;
- the runner created a one-attempt audit marker before the provider request;
- the exact provider error and timestamps were preserved;
- no mock, JSON-mode fallback or alternative model was substituted;
- no prediction or score was fabricated;
- no schema change or rerun occurred after observation;
- evaluator-only labels remained outside the runner; and
- holdout preparation remained blocked.

These controls made the failure visible and attributable. They do not make the workflow releasable.

## Next-version decision

The selected response is a separately versioned **Evidence-Gated Decision Pipeline v1.3**, defined in [`v1.3-decision.md`](v1.3-decision.md). It is a decision record only; v1.3 is not implemented, tested, certified, frozen or executed in this stage.

The selected architecture will:

1. use only the documented Structured Outputs subset for model-facing transport schemas;
2. move conditional and cross-field business invariants into deterministic post-response validators;
3. add a static provider-subset audit to offline tests and runner preflight;
4. require one pre-freeze provider contract-certification request per stage using non-benchmark sentinel inputs; and
5. prevent regression execution unless the certification evidence matches the exact schemas, model snapshot and endpoint configuration being frozen.

The three-stage v1.2 operating architecture, prompts, deterministic policies, evaluator gates and 24-case regression design remain the baseline for the future version. This is a contract-layer correction, not evidence to change the business decision logic.

## Evidence boundary

This is post-attempt analysis of a synthetic regression workflow. It is not an observed model-performance result, independent validation, production performance, legal advice or a compliance opinion. The v1.2 attempt is closed. Any future regression must use a separately implemented and frozen version.
