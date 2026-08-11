# Evidence-Gated Decision Pipeline v1.3 — Regression Execution Result

## Outcome

The frozen v1.3 workflow was executed exactly once against the 24 frozen synthetic regression cases on 11 August 2026. The run stopped during case 19 when a transport-valid evidence-stage response failed deterministic semantic validation:

```text
ValueError: Design-deficiency assessment and evidence flag must agree
```

The preserved [run state](run-state.json) records:

- status: `failed`;
- completed cases: 18 of 24;
- validated model calls: 21 of 32 expected;
- tuning after observation: `false`; and
- model: `gpt-4o-mini-2024-07-18` at temperature `0`.

The failing response occurred after the mapping stage for the nineteenth case and did not pass the semantic gate. The runner therefore stopped before policy composition for that case.

## Scoring decision

No `predictions.json` was produced because the 24-case run did not complete. The evaluator was not invoked, so there is no v1.3 score, comparison or release-gate result. Reporting a partial or fabricated score would violate the frozen evaluation protocol.

v1.3 will not be tuned, rerun or scored. This is execution evidence showing that provider schema acceptance and offline semantic tests do not guarantee that every generated response will satisfy cross-field business invariants.

## Evidence boundary

This is a failed execution on the existing synthetic regression set. It is not model-quality benchmark evidence, independent validation or production performance. The appropriate next stage is a case-level execution failure analysis followed by a separately versioned workflow decision.
