# First Release Plan

## Release objective

Demonstrate, with synthetic evidence, whether an AI-assisted workflow can turn an approved South African regulatory source into traceable obligations and map those obligations to controls and evidence without inventing requirements or making compliance decisions.

## Synthetic institution profile

The fictional institution profile is now frozen as `SA-IWM-SYN-001 v1.0`. It covers:

- legal-entity type;
- FIC accountable-institution category assumptions;
- FSCA licence and regulated-activity assumptions;
- products and services;
- customer types;
- distribution channels;
- key AML/CFT and market-conduct processes;
- control-owner roles; and
- explicit exclusions.

See [`profiles/synthetic-investment-wealth-institution-v1.0.md`](profiles/synthetic-investment-wealth-institution-v1.0.md) and the [machine-readable profile](profiles/synthetic-investment-wealth-institution-v1.0.json).

This profile exists only for evaluation. It does not represent a real institution or establish real-world applicability.

## Release 1 use cases

### AML/CFT change case

Given a supplied approved FIC source change and the synthetic institution profile:

1. classify the source and status;
2. extract supported candidate obligations;
3. identify applicability questions;
4. map potential impacts to the synthetic RMCP, processes and controls;
5. identify missing evidence;
6. propose accountable review; and
7. distinguish in-force change from draft readiness work.

### FSCA conduct-assurance case

Given a supplied applicable conduct requirement and synthetic procedure/control pack:

1. identify the customer or market-conduct outcome;
2. map the requirement to the operating process and control;
3. test supplied evidence against the mapping;
4. distinguish potential gap from insufficient evidence;
5. identify ownership and next action; and
6. escalate material uncertainty without declaring non-compliance.

## Baseline dataset

Create 24 synthetic cases:

- 12 AML/CFT;
- 12 FSCA market conduct.

Include:

- binding source correctly mapped;
- guidance mistaken for legislation;
- draft mistaken for an in-force requirement;
- superseded source;
- no applicability to the synthetic profile;
- missing applicability facts;
- correct obligation with wrong control owner;
- plausible but unsupported obligation;
- control description without operating evidence;
- genuine control gap;
- false-positive gap;
- conflicting approved sources;
- partial mapping across multiple controls;
- material issue not escalated; and
- routine evidence request unnecessarily escalated.

## Initial measures

### Regulatory-change quality

- source-status accuracy;
- obligation extraction accuracy;
- source-locator accuracy;
- applicability-question completeness;
- unsupported-obligation rate; and
- change-impact mapping accuracy.

### Obligation-to-control quality

- correct control mapping;
- evidence sufficiency classification;
- potential-gap precision and recall;
- owner-routing accuracy;
- escalation precision and recall; and
- human override rate.

### Operating-value measures

The prototype will define, but not claim, potential movement in:

- time to triage;
- time to impact assessment;
- touches per obligation;
- first-time owner assignment;
- time to disposition; and
- cost per assessed obligation.

## Release gates

The first controlled workflow may advance to an independent synthetic holdout only when:

- every output cites an approved source locator;
- no draft is classified as an in-force obligation;
- unsupported-obligation failures are explicitly measured;
- applicability uncertainty is surfaced rather than guessed;
- human authority is represented in the output and workflow; and
- the regression set and evaluator are frozen.

Production or pilot readiness is outside Release 1.

## Immediate next artefacts

1. ~~synthetic institution profile~~ — complete
2. ~~`source-pack-v1.0` metadata~~ — complete
3. ~~obligation schema~~ — complete
4. ~~control and evidence schema~~ — complete
5. ~~24-case labelled baseline dataset~~ — complete
6. baseline prompt
7. executable evaluator

The existing prompt is not the baseline for these two connected capabilities until it is aligned with the frozen source and institution profiles.
