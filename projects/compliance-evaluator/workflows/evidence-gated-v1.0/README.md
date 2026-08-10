# Evidence-Gated Decision Pipeline v1.0

## Status

**Implemented for pre-regression freeze. No regression API call or result exists yet.**

This workflow is the single controlled intervention selected from the [simple-baseline failure analysis](../../analysis/baseline-v1.0/README.md). It does not modify the simple baseline prompt, dataset, predictions or evaluation.

## Operating outcome

The pipeline converts a one-step AI disposition into two bounded AI assessments surrounded by deterministic operating controls:

```text
Frozen input case
      ↓
AI stage 1: source, obligation and applicability facts
      ↓
Authoritative source-transition policy
      ↓
Deterministic approved-obligation gate
      ↓ entered cases only
AI stage 2: control mapping and evidence facts
      ↓
Catalogue owner resolution + evidence decision policy
      ↓
Deterministic escalation policy
      ↓
Cross-field reconciliation
      ↓
Structured decision for human review
```

The proposal under test remains visible to each relevant AI stage, but is explicitly treated as an untrusted claim. The deterministic layer never uses the proposal to derive source status, approval, catalogue ownership, evidence disposition or escalation.

## Deliberate control changes

| Baseline weakness | Workflow control |
|---|---|
| Proposed answer copied | Prompts require accept/amend/reject; policy decisions ignore proposed values |
| Assurance leaked past closed gate | Closed gate deterministically clears every downstream assurance field |
| Source taxonomy instability | Frozen source-transition table controls permitted source and obligation dispositions |
| Wrong owner repeated | Control IDs resolve to owners from the frozen institution catalogue |
| Missing evidence confused with gaps | Evidence decision table fixes outcome, gap, severity and action combinations |
| Escalation copied or guessed | Escalation is derived only from explicit policy triggers |
| Plausible but inconsistent JSON | Reconciliation rejects cross-field and catalogue violations |

## Frozen execution design

- Dataset: `SA-REG-BASELINE-001 v1.0`, 24 frozen synthetic regression cases.
- Model: `gpt-4o-mini-2024-07-18`.
- Temperature: `0`.
- Source/obligation stage calls: 24.
- Control/evidence stage calls: 8, only where a supplied upstream obligation is approved.
- Total future API calls: 32.
- Runner access: input files, source pack, institution profile, prompts, policies and schemas only.
- Label access: evaluator only, after predictions exist.
- Mock fallback: prohibited.
- Overwrite or rerun: prohibited.
- Post-result tuning: prohibited for this frozen version.

The dated model snapshot is retained to make the engineered regression directly comparable with the simple baseline. OpenAI documents that GPT-4o mini supports Structured Outputs and that snapshots lock a specific model version.

## Artefacts

### AI stages

- [`prompts/source-obligation-stage-v1.0.md`](prompts/source-obligation-stage-v1.0.md)
- [`prompts/control-evidence-stage-v1.0.md`](prompts/control-evidence-stage-v1.0.md)
- [`schemas/source-obligation-stage.schema.json`](schemas/source-obligation-stage.schema.json)
- [`schemas/control-evidence-stage.schema.json`](schemas/control-evidence-stage.schema.json)

### Deterministic controls

- [`policies/source-transition-policy-v1.0.json`](policies/source-transition-policy-v1.0.json)
- [`policies/evidence-decision-policy-v1.0.json`](policies/evidence-decision-policy-v1.0.json)
- [`policies/escalation-policy-v1.0.json`](policies/escalation-policy-v1.0.json)
- [`pipeline.py`](pipeline.py) — composition, catalogue owner resolution and reconciliation.
- [`test_pipeline.py`](test_pipeline.py) — seven offline control scenarios plus all 24 input paths; no labels or API calls.

### Execution and evaluation

- [`run_regression.py`](run_regression.py) — explicit `--preflight` or `--execute`; runner never loads labels.
- [`evaluate_regression.py`](evaluate_regression.py) — evaluator-only labels, baseline comparison and eight release gates.
- `workflow-v1.0.meta.json` — pre-regression hashes and execution controls.

## Release gates

The evaluator will require:

1. zero assurance-stage leakage across 16 closed-gate cases;
2. zero prohibited compliance conclusions;
3. exact treatment of draft, superseded, strategy, blocked and conflicting sources;
4. exact catalogue owner routing across eight entered cases;
5. all six mandatory escalations detected;
6. zero unnecessary escalations across 18 non-escalation cases;
7. routine missing evidence kept distinct from a potential control gap; and
8. all 24 records reconciled without manual correction.

Component and end-to-end metrics are still reported even when these hard gates pass.

## Pre-regression validation

Install the same local dependencies used by the baseline and run:

```bash
python3 test_pipeline.py
python3 evaluate_regression.py --self-test
python3 run_regression.py --preflight
```

Preflight verifies every frozen prompt, schema, policy, code file, input, profile, source pack and evaluator hash. It makes no API call.

## Regression command — not yet executed

After this workflow is committed and confirmed frozen, the authorised one-run command is:

```bash
python3 run_regression.py --execute
python3 evaluate_regression.py
```

Do not execute those commands during the implementation/freeze stage. Once results exist, preserve them exactly and proceed to analysis without changing or rerunning this workflow version.

## Evidence boundary

Any future result on the existing 24 cases is regression evidence because these cases informed the workflow design. It is not independent validation, production performance, legal advice or a compliance determination. A separately authored, hashed and frozen holdout is required after the regression gate decision.
