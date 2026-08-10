# Evidence-Gated Decision Pipeline v1.2

## Status

**Implemented, tested offline and frozen before regression execution. No v1.2 API call or result exists.**

This is the separately versioned architecture selected by the [v1.1 case-level failure analysis](../../analysis/evidence-gated-v1.1/README.md) and [v1.2 decision record](../../analysis/evidence-gated-v1.1/v1.2-decision.md). It does not modify, tune, rerun or rescore v1.1.

## Operating outcome

v1.2 turns the remaining reasoning boundaries into stage boundaries:

```text
No approved obligation (16 cases)
        ↓
AI source status + statement support
        ↓
Deterministic source, support and applicability policy
        ↓
Assurance gate remains closed

Reviewed approved obligation (8 cases)
        ↓
Bypass source stage and inherit reviewed authority
        ↓
AI current-mapping assessment
  (no evidence status or escalation proposal)
        ↓
Validate current controls and separate remediation candidates
        ↓
AI evidence assessment
  (cannot add controls or change mapping)
        ↓
Deterministic evidence, escalation and reconciliation policy
        ↓
Human review remains mandatory
```

The planned regression contains 16 source/support calls, eight mapping calls and eight evidence calls: **32 calls in total**.

## Selected v1.2 controls

### 1. Source support is independent from legal readiness

The source stage returns both `statement_support` and `legal_readiness`. Staged commencement or pending human approval may keep an obligation at candidate status and keep assurance closed, but cannot by itself turn source-backed wording into an unsupported extension.

### 2. Mapping and evidence have isolated inputs

The mapping stage receives the approved atomic obligation, current submitted mapping and relevant catalogue controls. It does not receive presented-evidence status, evidence-gap claims or escalation proposals.

The evidence stage receives the validated current mapping and presented evidence. It cannot add controls, change mapping membership or decide escalation.

### 3. Current controls and remediation candidates are separate

`current_mapping_control_ids` must be a subset of the submitted mapping. `candidate_additional_control_ids` must be disjoint and cannot enter the final current mapping. Catalogue owner resolution is applied without changing membership.

### 4. Generality measurement is identity-safe

Runtime rule identifiers no longer resemble benchmark case IDs. The evaluator checks the explicit no-override trace, exact rule identity and static runtime isolation; it does not use case-ID substring matching.

## Controls retained from v1.1

- deterministic source transition;
- reviewed approved-obligation authority;
- fact-based applicability;
- catalogue owner resolution;
- evidence and gap taxonomy;
- partial-coverage precedence;
- mandatory escalation rules;
- cross-field reconciliation;
- mandatory human review and `not_determined` compliance conclusion;
- input-only runner isolation from evaluator labels; and
- no mock fallback, overwrite, post-result tuning or rerun.

## Frozen execution design

- Dataset: `SA-REG-BASELINE-001 v1.0`, 24 frozen synthetic regression cases.
- Model: `gpt-4o-mini-2024-07-18`.
- Temperature: `0`.
- Source/support calls: 16.
- Mapping calls: 8.
- Evidence calls: 8.
- Total future API calls: 32.
- Runner label access: prohibited.
- Evaluator label access: only after predictions exist.
- Mock fallback: prohibited.
- Overwrite or rerun: prohibited.
- Post-result tuning: prohibited for this frozen version.

The dated snapshot is retained to isolate workflow change from model change. [Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-4o-mini) records Structured Outputs support and the `gpt-4o-mini-2024-07-18` snapshot.

## Artefacts

### AI stages

- [`prompts/source-support-stage-v1.2.md`](prompts/source-support-stage-v1.2.md)
- [`prompts/mapping-stage-v1.2.md`](prompts/mapping-stage-v1.2.md)
- [`prompts/evidence-stage-v1.2.md`](prompts/evidence-stage-v1.2.md)
- [`schemas/source-support-stage.schema.json`](schemas/source-support-stage.schema.json)
- [`schemas/mapping-stage.schema.json`](schemas/mapping-stage.schema.json)
- [`schemas/evidence-stage.schema.json`](schemas/evidence-stage.schema.json)

### Deterministic controls

- [`policies/source-transition-policy-v1.2.json`](policies/source-transition-policy-v1.2.json)
- [`policies/applicability-policy-v1.2.json`](policies/applicability-policy-v1.2.json)
- [`policies/assurance-decision-policy-v1.2.json`](policies/assurance-decision-policy-v1.2.json)
- [`policies/escalation-policy-v1.2.json`](policies/escalation-policy-v1.2.json)
- [`pipeline.py`](pipeline.py)

### Offline controls

- [`test_stage_schemas.py`](test_stage_schemas.py) — valid and prohibited structured-output states.
- [`test_pipeline.py`](test_pipeline.py) — selected boundary scenarios and all 24 input paths.
- [`test_input_isolation.py`](test_input_isolation.py) — mapping/evidence payload separation and runtime label isolation.
- [`run_regression.py`](run_regression.py) — hash-verified preflight or explicit one-shot execution.
- [`evaluate_regression.py`](evaluate_regression.py) — evaluator-only scoring and corrected release gates.
- `workflow-v1.2.meta.json` — frozen hashes and execution controls.

## Release gates

The 14 operating gates remain mandatory, with the source-support and generality checks strengthened for v1.2:

1. zero assurance-stage leakage;
2. zero prohibited compliance conclusions;
3. exact source boundary and statement-support treatment;
4. exact current-control and catalogue-owner routing;
5. all six mandatory escalations detected;
6. zero unnecessary escalations;
7. routine missing evidence kept distinct;
8. all records reconciled without manual correction;
9. exact applicability with approved-authority routing;
10. exact mapping status across entered assurance;
11. exact assurance outcome, gap, severity and action across entered assurance;
12. partial coverage not promoted to design escalation;
13. evidence condition does not demote mapping; and
14. general policy rules, identity-safe tracing and runtime isolation without case overrides.

## Pre-regression validation

```bash
python3 test_stage_schemas.py
python3 test_pipeline.py
python3 test_input_isolation.py
python3 evaluate_regression.py --self-test
python3 run_regression.py --preflight
```

Preflight verifies every workflow, prompt, schema, policy, input, reviewed obligation, profile, source pack and evaluator hash. It confirms that no result directory exists and makes no API call.

## Regression command — not authorised in this stage

A later explicit instruction may authorise:

```bash
python3 run_regression.py --execute
python3 evaluate_regression.py
```

Do not execute those commands during implementation and freeze. Once a result exists, preserve it exactly and do not tune or rerun v1.2.

## Evidence boundary

Any future v1.2 result on these 24 cases is regression evidence because the cases informed workflow design. It is not independent validation, production performance, legal advice or a compliance determination. A separately authored and frozen unseen holdout is permitted only after every release gate passes.
