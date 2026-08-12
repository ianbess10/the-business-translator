# Evidence-Gated v1.7 — Independent Holdout Harness v1.0

This separately frozen harness executes the already-frozen v1.7 decision pipeline against 16 unseen synthetic variants: eight source/applicability cases and eight entered-assurance cases.

The provider schemas, prompts, endpoint, model, temperature, request wrapper and deterministic decision runtime are byte-identical to certified v1.7. No new provider certification is required. The holdout inputs and expected decisions are evaluation-separated and frozen before execution.

Exactly one execution and one evaluation are permitted. No retry, repair, tuning, rerun or rescoring is permitted. The result is independent synthetic validation evidence, not production performance.
