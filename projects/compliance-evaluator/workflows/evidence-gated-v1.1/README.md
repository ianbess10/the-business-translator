# Evidence-Gated Decision Pipeline v1.1

## Status

**Implemented and frozen before regression execution. No v1.1 API call or result exists.**

This is the separately versioned intervention selected by the [v1.0 case-level failure analysis](../../analysis/evidence-gated-v1.0/README.md) and [v1.1 decision record](../../analysis/evidence-gated-v1.0/v1.1-decision.md). It does not modify or rerun v1.0.

## Operating outcome

v1.1 keeps regulatory-change assessment and approved obligation assurance as two distinct operating paths:

```text
No approved obligation (16 cases)
        ↓
AI source / obligation assessment
        ↓
Source + applicability policy
        ↓
Assurance gate remains closed

Reviewed approved obligation (8 cases)
        ↓
Bypass source / obligation model stage
        ↓
Inherit reviewed source, obligation and applicability
        ↓
AI control coverage + evidence assessment
        ↓
Mapping normalisation + evidence policy
        ↓
Escalation policy + reconciliation + human review
```

The planned regression therefore contains 16 source-stage calls and eight assurance-stage calls: **24 calls in total**, down from 32 in v1.0.

## Selected v1.1 controls

### 1. Approved-obligation authority boundary

An entered assurance record must resolve to the supplied approved-obligation fixture, including accepted human review. The runner does not call the source/obligation model for those cases. Source disposition, obligation outcome and applicability are inherited from the reviewed record.

The pipeline rejects:

- an approved case with a source-stage model output;
- a missing or mismatched obligation fixture;
- an obligation without approved lifecycle status;
- an obligation without accepted human review; or
- an approved source, obligation or applicability state outside the policy allow-list.

### 2. Applicability independent from legal effect

Non-approved regulatory-change cases continue through source assessment, but final applicability is derived from explicit institution and missing facts:

- an explicit profile exclusion produces `out_of_scope`;
- a material missing applicability fact produces `applicability_uncertain`;
- a supporting institution fact produces `applicable_candidate`; and
- fixed source-policy modes retain `not_assessed` or `applicability_uncertain`.

Guidance can therefore remain relevant to an institution without being promoted to a binding obligation.

### 3. Mapping independent from evidence and performance

The control-stage schema now returns two explicit boundary facts:

- `coverage_gap_present`; and
- `design_deficiency_evidence_present`.

Deterministic mapping normalisation uses supported controls and coverage only. Missing evidence and adverse operating performance cannot demote an otherwise complete mapping.

### 4. Partial-coverage precedence

Partial coverage becomes a medium `partial_coverage` issue with a mapping review unless supplied evidence supports an actual design deficiency. A high `control_design` gap and its mandatory escalation remain available for genuine design evidence.

## Controls retained from v1.0

- authoritative source-transition policy;
- approved-obligation assurance gate;
- catalogue owner resolution;
- distinct sufficient, missing-evidence, design-gap and operating-exception outcomes;
- mandatory escalation triggers and accountable roles;
- cross-field reconciliation;
- mandatory human review and `not_determined` compliance conclusion;
- input-only runner isolation from evaluator labels;
- no mock fallback, overwrite, post-result tuning or rerun.

## Frozen execution design

- Dataset: `SA-REG-BASELINE-001 v1.0`, 24 frozen synthetic regression cases.
- Model: `gpt-4o-mini-2024-07-18`.
- Temperature: `0`.
- Source/obligation calls: 16, only where no approved obligation is supplied.
- Control/evidence calls: 8, only for supplied approved obligations.
- Total future API calls: 24.
- Runner label access: prohibited.
- Evaluator label access: only after predictions exist.
- Mock fallback: prohibited.
- Overwrite or rerun: prohibited.
- Post-result tuning: prohibited for this frozen version.

The dated model snapshot is retained to isolate the workflow change from model change. [Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-4o-mini) records Structured Outputs support and the `gpt-4o-mini-2024-07-18` snapshot.

## Artefacts

### AI stages

- [`prompts/source-obligation-stage-v1.1.md`](prompts/source-obligation-stage-v1.1.md)
- [`prompts/control-evidence-stage-v1.1.md`](prompts/control-evidence-stage-v1.1.md)
- [`schemas/source-obligation-stage.schema.json`](schemas/source-obligation-stage.schema.json)
- [`schemas/control-evidence-stage.schema.json`](schemas/control-evidence-stage.schema.json)

### Deterministic controls

- [`policies/source-transition-policy-v1.1.json`](policies/source-transition-policy-v1.1.json)
- [`policies/applicability-policy-v1.1.json`](policies/applicability-policy-v1.1.json)
- [`policies/evidence-decision-policy-v1.1.json`](policies/evidence-decision-policy-v1.1.json)
- [`policies/escalation-policy-v1.1.json`](policies/escalation-policy-v1.1.json)
- [`pipeline.py`](pipeline.py)

### Offline controls

- [`test_pipeline.py`](test_pipeline.py) — 16 decision-boundary scenarios plus all 24 input paths.
- [`test_stage_schemas.py`](test_stage_schemas.py) — valid and prohibited structured-output states.
- [`run_regression.py`](run_regression.py) — hash-verified preflight or explicit one-shot execution.
- [`evaluate_regression.py`](evaluate_regression.py) — evaluator-only scoring, v1.0 comparison and release gates.
- `workflow-v1.1.meta.json` — frozen hashes and execution controls.

## Release gates

The original eight gates remain mandatory:

1. zero assurance-stage leakage;
2. zero prohibited compliance conclusions;
3. exact source-boundary treatment;
4. exact catalogue-owner routing;
5. all six mandatory escalations detected;
6. zero unnecessary escalations;
7. routine missing evidence kept distinct; and
8. all records reconciled without manual correction.

v1.1 adds six diagnostic gates:

9. exact applicability with approved-authority routing;
10. exact mapping status across entered assurance;
11. exact assurance outcome, gap, severity and action across entered assurance;
12. partial coverage not promoted to design escalation;
13. evidence condition does not demote mapping completeness; and
14. general policy rules with no case-specific overrides.

## Pre-regression validation

Using the frozen local dependencies:

```bash
python3 test_stage_schemas.py
python3 test_pipeline.py
python3 evaluate_regression.py --self-test
python3 run_regression.py --preflight
```

Preflight verifies every workflow, prompt, schema, policy, input, approved-obligation fixture, profile, source pack and evaluator hash. It confirms that no result directory exists and makes no API call.

## Regression command — not authorised in this stage

After this pre-regression state is committed and confirmed frozen, a later explicit instruction may authorise:

```bash
python3 run_regression.py --execute
python3 evaluate_regression.py
```

Do not execute those commands during implementation and freeze. Once a result exists, preserve it exactly and do not tune or rerun v1.1.

## Evidence boundary

Any future v1.1 result on these 24 cases is regression evidence because the cases informed workflow design. It is not independent validation, production performance, legal advice or a compliance determination. A separately authored and frozen unseen holdout is permitted only after every release gate passes.
