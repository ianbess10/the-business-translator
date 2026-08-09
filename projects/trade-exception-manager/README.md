# Trade Exception Intelligence

## Business Problem

Post-trade communications can contain information required to resolve settlement exceptions, but relevant facts may be distributed across free text, message references and operational commentary.

The portfolio prototype demonstrates whether an LLM can:
1. identify the exception;
2. extract relevant attributes;
3. classify the issue;
4. identify missing information;
5. recommend a next operational action;
6. return a controlled structured record.

## Operational Consequence

Poor extraction or classification can create rework, delay settlement, increase operational risk and reduce straight-through-processing.

## Users and Context

Primary user: post-trade operations specialist.

Domain context: securities settlement, financial messaging and exception management.

The prototype uses synthetic examples and is not connected to production systems.

## Baseline

Baseline prompt:

> Analyse this settlement exception and tell me what happened and what should be done.

Typical failure modes:
- inconsistent field extraction;
- prose instead of structured data;
- unsupported assumptions;
- failure to distinguish known facts from inference;
- missing escalation conditions.

See `baseline-prompt.md`.

## Prompt Strategy

The engineered version separates:
- role;
- business context;
- task;
- classification taxonomy;
- evidence rules;
- uncertainty handling;
- output schema;
- escalation conditions.

See `engineered-prompt.md`.

## Prompt Iterations

- V0: open-ended analysis
- V1: explicit role and task
- V2: structured fields and taxonomy
- V3: evidence and uncertainty controls
- V4: JSON schema and human escalation (**measured baseline on frozen 20 cases**)
- V5+: revise from failure analysis, re-test on the **same** 20 cases, measure the delta

```text
V4 (65% / 37.5% / 70%) → failure analysis → V5 → same 20 cases → measured difference
```

Frozen V4 bundle: `releases/v4/` (prompt, test-set-v1.0, raw outputs, evaluation, failure analysis).  
See `prompt-iterations.md` and `releases/v4/README.md`.

## Test Set

Frozen release: **`trade-exception-test-set-v1.0`**

- File: `datasets/trade-exception-test-set-v1.0.jsonl`
- Metadata: `datasets/trade-exception-test-set-v1.0.meta.json`
- Compatibility copy: `test-set.jsonl` (same 20 cases; runners default to the frozen dataset path)

Twenty synthetic cases cover:
- missing settlement date;
- incorrect counterparty details;
- unmatched trade;
- partial settlement;
- failed settlement;
- market deadline;
- ambiguous narrative;
- contradictory instructions;
- malformed message reference;
- insufficient information;
- deliberate distractors.

Each case includes evaluation labels:
- `expected_type`
- `expected_escalation`
- `expected_missing_information`

Do not edit the frozen v1.0 file in place. Publish a new version if the cases change.

## Evaluation

The project measures:
- classification accuracy;
- JSON schema compliance;
- missing-information detection;
- escalation accuracy;
- unsupported-claim flags;
- field extraction / human usefulness (manual review notes in `evaluation.md`).

**Do not present performance figures as validated results unless they were produced by an actual local run of `evaluate.py`.**  
The table in `evaluation.md` remains illustrative portfolio benchmarking only.

See `evaluation.md` and `results/evaluation/`.

## Human Oversight

The model must not independently release, amend, cancel or settle a transaction. It may prepare an operational recommendation for qualified review.

## Reproducibility

Record:
- model and version;
- system prompt;
- task prompt;
- test-set version (`trade-exception-test-set-v1.0`);
- temperature/settings;
- evaluation rubric;
- output;
- reviewer decision.

See `governance.md`.

---

## Setup

Requirements: Python 3.10+.

```bash
cd projects/trade-exception-manager
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure `.env`:

| Variable | Purpose |
|---|---|
| `MODEL_PROVIDER` | `mock` (default, offline) or `openai` |
| `OPENAI_API_KEY` | Required only for `openai` |
| `OPENAI_MODEL` | Defaults to `gpt-4o-mini` |
| `OPENAI_BASE_URL` | Optional OpenAI-compatible endpoint |
| `OPENAI_TEMPERATURE` | Defaults to `0` |
| `RUN_LABEL` | Optional suffix for run IDs |
| `TEST_SET_PATH` | Optional override; defaults to frozen `datasets/trade-exception-test-set-v1.0.jsonl` |
| `PROMPT_VERSION` | Prompt version label (`v4` default; use `v5` for next revision) |
| `ENGINEERED_PROMPT_PATH` | Optional prompt file override; default `prompts/engineered-<version>.md` |

API keys are read from the environment only. They are never hard-coded.

Provider logic lives under `src/providers/` so additional vendors can be added without changing runners.

## Execution

From `projects/trade-exception-manager` with the virtualenv active:

```bash
# 1) Baseline free-text run (writes results/baseline/<run_id>/)
python run_baseline.py

# 2) Engineered structured run + per-case schema validation
python run_engineered.py

# 3) Score the latest runs
python evaluate.py --variant both

# 4) Measure difference vs frozen V4 baseline (after a later prompt version run)
python compare_evals.py \
  --baseline releases/v4/evaluation/v4-reference.json \
  --candidate results/evaluation/<eval_id>.json
```

Useful options:

```bash
python run_engineered.py --case-id TX001 --case-id TX010
python evaluate.py --variant engineered
python evaluate.py --variant engineered --run-dir <run_id_or_path>

# Next prompt version on the exact same frozen cases
export PROMPT_VERSION=v5
# create prompts/engineered-v5.md first
python run_engineered.py
python evaluate.py --variant engineered
python compare_evals.py --candidate results/evaluation/<eval_id>.json
```

Outputs:
- `results/baseline/<run_id>/*.json` — baseline responses
- `results/engineered/<run_id>/*.json` — engineered responses, parsed JSON, schema errors
- `results/evaluation/<run_id>.json` — metric report from an actual run

### Offline mock provider

`MODEL_PROVIDER=mock` uses a deterministic rules stub. It is for workflow reproducibility and wiring checks. Mock scores are real run outputs for that stub, not claims about production LLM performance.

### OpenAI provider

```bash
# in .env
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0
```

Then rerun `run_baseline.py`, `run_engineered.py`, and `evaluate.py`.

## Project layout

```text
baseline-prompt.md
engineered-prompt.md
evaluation.md
governance.md
prompt-iterations.md
datasets/trade-exception-test-set-v1.0.jsonl
datasets/trade-exception-test-set-v1.0.meta.json
prompts/engineered-v4.md
benchmarks/v4-reference.json
failure-analysis/v4-on-test-set-v1.0.md
test-set.jsonl        # compatibility copy of v1.0
schema/engineered_output.schema.json
run_baseline.py
run_engineered.py
evaluate.py
compare_evals.py
src/
  providers/          # mock + openai isolation
  runners/
  evaluate.py
  compare.py
results/              # generated run artefacts
```
