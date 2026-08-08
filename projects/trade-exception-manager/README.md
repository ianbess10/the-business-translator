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
- V4: JSON schema and human escalation

See `prompt-iterations.md`.

## Test Set

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

See `test-set.jsonl`.

## Evaluation

The project measures:
- field extraction accuracy;
- classification accuracy;
- missing-data detection;
- JSON schema compliance;
- unsupported claims;
- human editing time.

The headline metrics in the portfolio are **illustrative portfolio test results unless independently validated**.

See `evaluation.md`.

## Human Oversight

The model must not independently release, amend, cancel or settle a transaction. It may prepare an operational recommendation for qualified review.

## Reproducibility

Record:
- model and version;
- system prompt;
- task prompt;
- test-set version;
- temperature/settings;
- evaluation rubric;
- output;
- reviewer decision.

See `governance.md`.
