# Regulatory Intelligence Baseline v1.0

## Outcome

This dataset creates the first controlled benchmark for Project 2. It tests whether an AI-assisted workflow can move a regulatory issue to the correct operational disposition without inventing legal effect, applicability, control evidence or approval.

The benchmark follows the decision chain:

```text
Approved source pack
        ↓
Source status and permitted use
        ↓
Obligation and applicability decision
        ↓
Approved-obligation gate
        ↓
Control, owner and evidence assessment
        ↓
Gap, remediation and escalation decision
        ↓
Human accountability retained
```

## Dataset design

The 24 cases are evenly divided:

- 12 South African AML/CFT cases; and
- 12 FSCA market-conduct cases.

Inputs and expected labels are stored separately. A baseline run receives only the files under [`inputs`](inputs). The evaluator loads the files under [`labels`](labels) after predictions are produced. This prevents the expected answer from leaking into the model task.

Every case remains synthetic. No real customer, transaction, employee or institution data is included.

## What the cases test

The benchmark covers:

- binding, guidance, draft, superseded, strategy, unofficial-compilation and blocked-source boundaries;
- unverified commencement and missing applicability facts;
- out-of-scope profile activity and unsupported obligation extensions;
- control assurance attempted before human obligation approval;
- correct and partial control mapping;
- correct control-owner routing;
- control descriptions without operating evidence;
- insufficient evidence versus a genuine potential control gap;
- false-positive gaps;
- source conflict;
- missed material escalation; and
- unnecessary escalation of routine evidence requests.

See the [coverage matrix](coverage-matrix.md) for the case-by-case design.

## Important AML/CFT boundary

The frozen source pack does not currently permit binding-obligation extraction from any AML/CFT source:

- the original Act source and unofficial compilation are blocked for binding extraction;
- Guidance Note 7B is guidance only;
- Guidance Note 7A is superseded;
- Directive 10 has unverified Gazette commencement; and
- Directive 12 is a draft.

The AML/CFT cases therefore test source, applicability, unsupported-extension and premature-assurance controls. They do not invent an approved AML/CFT obligation merely to create a control-mapping example.

The FSCA amendment source permits a binding candidate with human review and staged-date control. Eight market-conduct cases therefore exercise the approved-obligation-to-control assurance workflow.

## Record structure

[`baseline-record.schema.json`](baseline-record.schema.json) defines two record types:

- `case_input` — the source facts, institution facts, proposed interpretation, proposed mapping and review question supplied to the baseline workflow; and
- `case_label` — the expected operational disposition held by the evaluator.

Labels use the controlled vocabularies from both frozen decision schemas and add only the `not_applicable` sentinel required when control assurance must not be entered.

## Initial measures enabled

The dataset supports calculation of:

- source-status and permitted-use accuracy;
- obligation-outcome accuracy;
- applicability-status accuracy;
- approved-obligation gate accuracy;
- control-mapping accuracy;
- control-owner routing accuracy;
- evidence-sufficiency accuracy;
- potential-gap precision and recall;
- escalation precision and recall; and
- prohibited compliance-conclusion rate.

Metrics are not production performance. They will become baseline evidence only after an intentionally simple workflow is run against the frozen inputs.

## Files

- [`inputs/aml-cft.json`](inputs/aml-cft.json) — 12 model-facing AML/CFT cases.
- [`inputs/market-conduct.json`](inputs/market-conduct.json) — 12 model-facing market-conduct cases.
- [`labels/aml-cft.json`](labels/aml-cft.json) — evaluator-only AML/CFT labels.
- [`labels/market-conduct.json`](labels/market-conduct.json) — evaluator-only market-conduct labels.
- [`baseline-record.schema.json`](baseline-record.schema.json) — input and label contract.
- [`validate_dataset.py`](validate_dataset.py) — structural, frozen-input, vocabulary, coverage and prohibited-state validation.
- [`coverage-matrix.md`](coverage-matrix.md) — case intent and expected operating disposition.
- [`baseline-v1.0.meta.json`](baseline-v1.0.meta.json) — freeze metadata and file hashes.

## Validation

Install `jsonschema` and run:

```bash
python3 validate_dataset.py
```

The validator confirms:

- exactly 24 paired input and label records;
- a 12/12 workstream balance;
- alignment with all four frozen project inputs;
- eight approved-obligation control-assurance cases;
- all 20 required coverage tags; and
- rejection of 12 prohibited dataset states.

## Freeze rule

Do not tune the dataset after observing baseline performance. Corrections to a demonstrably defective case require a new dataset version with a documented change. Workflow improvements must be tested against this frozen version before any separate holdout is created.

## Boundary

This is synthetic evaluation evidence. It is not legal advice, production assurance, a compliance determination or a representation of any institution's control environment.
