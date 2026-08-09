# Trade Exception Intelligence

> **AI is the enabler. A faster, safer and more accountable exception-management outcome is the product.**

Trade Exception Intelligence is an AI-assisted operations capability for turning unstructured settlement exceptions into clear, reviewable actions. It is designed to help operations teams diagnose breaks, identify the information needed to resolve them, route work correctly and escalate only when the circumstances warrant it.

The capability supports professional judgement; it does not replace it. A qualified operations professional remains accountable for every decision and action.

[Read the concise executive summary](executive-summary.md).

## The operational problem

Straight-through processing works until a transaction cannot continue without intervention. A settlement instruction may be incomplete, a trade may remain unmatched, counterparty details may conflict, securities or cash may be unavailable, or a market deadline may be approaching.

At that point, the transaction leaves the automated flow and enters exception management. An operations analyst must determine:

- what happened;
- what caused it;
- which information can be trusted;
- what decision-critical information is missing;
- where the exception should be routed;
- what should happen next; and
- whether normal operations handling is sufficient or escalation is required.

Every avoidable manual touch adds time and cost. Incorrect diagnosis or routing can delay settlement, create rework, increase operational risk and distract senior staff with unnecessary escalations. A missed escalation can be more serious still: a time-critical or control-sensitive break may not receive the attention it requires.

## What was built

This project converts a free-text settlement exception into a controlled, structured record for human review. The capability:

1. identifies the exception and the known facts;
2. distinguishes the operational symptom from the actionable root cause;
3. classifies the break into an operational category;
4. identifies missing information needed for the next decision;
5. recommends a practical next action;
6. proposes the appropriate routing and escalation treatment; and
7. presents the result in a consistent format that can support workflow integration and audit.

```text
Exception arrives
        ↓
Diagnose the break and its root cause
        ↓
Identify decision-critical missing information
        ↓
Recommend action, routing and escalation treatment
        ↓
Operations professional reviews, decides and acts
```

The objective is not to allow AI to release, amend, cancel or settle a transaction. The objective is to reduce the manual interpretation required before an experienced professional can make the right decision.

## Why it matters operationally

A well-designed capability could help an operations function:

- shorten the time between exception receipt and an actionable diagnosis;
- reduce repeated reading, interpretation and hand-offs;
- improve first-time routing to the correct queue or specialist;
- make missing-data requests more specific and actionable;
- reserve escalation capacity for genuinely material or time-critical cases;
- create a consistent decision trail for control review; and
- give managers better information about recurring break causes and process weaknesses.

This is not simply a productivity proposition. Better exception intelligence can improve service, capacity, control integrity and the quality of operational decisions at the same time.

## What initial testing revealed

The most important finding was that **structured output can still be operationally wrong**.

An AI response may be complete, readable and technically valid while still:

- routing a data defect as a settlement failure;
- describing the visible symptom instead of the underlying cause;
- recognising a contradiction without asking for the authoritative value;
- treating urgency as evidence of a market deadline; or
- escalating a routine repair that should remain in normal operations.

A valid format is therefore only an entry-level control. Operational usefulness depends on the quality of the diagnosis, the next decision and the escalation judgement.

## Symptom versus root cause

Financial-markets exceptions often contain both an outcome and a cause. A trade may have failed, but the actionable cause may be an invalid receiving account or mismatched standing settlement instruction.

Routing on the symptom sends work toward generic fail management. Routing on the root cause directs it toward instruction repair and helps prevent recurrence. The project therefore tests whether the capability can prioritise the underlying, actionable cause rather than anchor on the most obvious word in the message.

## Decision-critical missing information

Identifying that data is absent is not enough. The capability must identify what is needed to make the next operational decision.

Examples include:

- the valid receiving account, not merely the observation that the supplied account is invalid;
- the authoritative settlement instruction when two sources conflict;
- the confirming counterparty response for an unmatched trade;
- the precise deadline timestamp when urgency or a cut-off is referenced; and
- the trade identifier and exception facts when the message contains too little information to act.

This turns exception analysis into a specific request for resolution evidence, rather than a general description of the problem.

## Escalation calibration

Escalation is a control decision, not a synonym for uncertainty.

Too little escalation can leave a material, deadline-sensitive or unresolved exception without appropriate attention. Too much escalation creates alert fatigue, increases senior-review workload and slows routine repairs.

The capability must therefore distinguish between:

- routine operations work that can follow a standard repair or chase process;
- exceptions needing specialist input or additional authority; and
- genuinely time-critical, control-sensitive or insufficiently evidenced cases requiring escalation.

The benchmark showed why this calibration matters: changes that corrected missed escalations also produced new unnecessary escalations. A safer-looking rule can still create an inefficient operating outcome if it is too broad.

## Tangible business measures

Production value should be judged through operating outcomes, with suitable control and quality measures—not benchmark accuracy alone.

| Measure | What it reveals |
|---|---|
| Time to diagnose | How quickly an exception becomes an actionable case |
| Touches per exception | The amount of manual handling and rework |
| Correct first-time routing | Whether work reaches the right queue or specialist without redirection |
| Time to resolution | End-to-end impact on exception closure and settlement recovery |
| Unnecessary escalation rate | Avoidable senior or specialist intervention and alert fatigue |
| Missed escalation rate | Material cases that did not receive required attention |
| STP / exception rate | Whether insight from recurring breaks contributes to upstream prevention |
| Cost per exception | Combined labour, delay and processing cost of handling a break |

Additional safeguards should track unsupported claims, human overrides, repeat exceptions and differences in performance by exception type, market and workflow.

## What this demonstrates about AI-enabled operations transformation

This case study demonstrates a repeatable transformation discipline:

- begin with the operating problem and the decision that must improve;
- translate expert judgement into explicit workflow, taxonomy and control rules;
- test plausible failure modes, not just presentation quality;
- learn from errors at the level of operational consequence;
- retain human accountability at the point of action; and
- measure the resulting operating outcome.

The work is not the endless optimisation of a prompt. It is the design of an operational capability that combines process knowledge, AI, evaluation, workflow controls and accountable human judgement.

## Executive-level proposition

Trade Exception Intelligence provides a practical route from unstructured exception traffic to faster, more consistent and better-controlled operations decisions.

Its value proposition is:

> **Reduce the interpretation burden on operations teams, improve the quality and speed of routing and resolution, and strengthen control by making the facts, missing evidence, next action and escalation decision explicit.**

The production case would be proven through controlled piloting against live operating measures, not assumed from synthetic test performance.

---

# Supporting technical and benchmark evidence

The material below documents how the prototype was built and tested. It supports the executive case; it is not the product proposition.

## Evidence status and limitations

All cases in the current benchmark are synthetic. V4 and V5 were evaluated on the **same frozen set of 20 cases** using OpenAI `gpt-4o-mini` at temperature `0`.

These results demonstrate comparative behaviour within a controlled prototype benchmark. They are **not production performance**, do not establish business benefits and should not be extrapolated to live volumes, markets or control environments. Production claims would require representative historical or controlled live cases, independent review and measurement against an operational baseline.

## Measured V4 and V5 benchmark results

| Metric | V4 | V5 | Change |
|---|---:|---:|---:|
| Classification accuracy | 65% | **90%** | +25 percentage points |
| Missing-information detection | 37.5% | **80%** | +42.5 percentage points |
| Escalation accuracy | 70% | **75%** | +5 percentage points |
| JSON schema compliance | 100% | 100% | No change |
| Unsupported-claim flags | 0 | 1 | +1 flag |

V5 materially improved classification and missing-information detection. Escalation accuracy improved only modestly: all six V4 missed escalations were corrected, but five new unnecessary escalations appeared. The remaining classification errors were over-conservative choices of `insufficient_information` instead of `data_quality` for single-gap cases.

See the [V5 evaluation analysis](results/analysis/v5-evaluation-analysis.md), [V4 failure analysis](failure-analysis/v4-on-test-set-v1.0.md) and [controlled evaluation protocol](evaluation.md).

## Development and evaluation progression

- V0: open-ended analysis
- V1: explicit role and task
- V2: structured fields and taxonomy
- V3: evidence and uncertainty controls
- V4: structured schema and human escalation, measured as the frozen comparison baseline
- V5: decision-control changes derived from V4 failure analysis and retested on the same cases

```text
V4 benchmark
      ↓
Operational failure analysis
      ↓
V5 decision-control intervention
      ↓
Same frozen 20 synthetic cases
      ↓
Measured comparison and residual-risk analysis
```

The frozen V4 bundle is in [`releases/v4/`](releases/v4/). The V4-to-V5 intervention map is in [`methodology/v4-to-v5-interventions.md`](methodology/v4-to-v5-interventions.md).

## Test set and controls

The frozen `trade-exception-test-set-v1.0` contains 20 synthetic cases covering missing settlement dates, counterparty and instruction conflicts, unmatched and partial trades, settlement failures, market deadlines, contradictory or malformed messages, sparse narratives and distractors.

Each case has expected labels for exception type, escalation and missing information. The model must distinguish known facts from inference, expose uncertainty and return a structured record. It may recommend an action but cannot independently release, amend, cancel or settle a transaction.

Key artefacts:

- [frozen test-set metadata](datasets/trade-exception-test-set-v1.0.meta.json)
- [V4 prompt](prompts/engineered-v4.md)
- [V5 prompt](engineered-prompt-v5.md)
- [output schema](schema/engineered_output.schema.json)
- [governance controls](governance.md)
- [prompt iteration record](prompt-iterations.md)

## Reproducing the benchmark

Requirements: Python 3.10+.

```bash
cd projects/trade-exception-manager
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

The default offline mock provider checks workflow wiring only. It is not evidence of LLM or production performance. For a recorded OpenAI run, configure the provider and model in `.env`, then run:

```bash
python run_baseline.py
python run_engineered.py
python evaluate.py --variant both
```

To compare a later prompt run with frozen V4:

```bash
python compare_evals.py \
  --baseline releases/v4/evaluation/v4-reference.json \
  --candidate results/evaluation/<eval_id>.json
```

Record the model and version, prompt version, test-set version, temperature and settings, evaluation rubric, raw output and reviewer decision for every run.

## Technical project layout

```text
baseline-prompt.md
engineered-prompt.md
engineered-prompt-v5.md
evaluation.md
governance.md
prompt-iterations.md
datasets/
prompts/
releases/v4/
failure-analysis/
methodology/
schema/
src/
results/
run_baseline.py
run_engineered.py
evaluate.py
compare_evals.py
```
