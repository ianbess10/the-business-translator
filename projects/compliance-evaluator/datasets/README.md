# Evaluation Datasets

Datasets in this folder test whether the regulatory-intelligence workflow makes operationally correct source, obligation, applicability, control, evidence, ownership and escalation decisions.

## Current dataset

[`baseline-v1.0`](baseline-v1.0/README.md) is the frozen 24-case synthetic baseline:

- 12 South African AML/CFT cases;
- 12 FSCA market-conduct cases;
- separate model-facing inputs and evaluator-only labels;
- 20 required failure-mode tags; and
- validation against the frozen source pack, institution profile, Obligation Schema v1.0 and Control and Evidence Schema v1.0.

The next artefacts are the intentionally simple baseline prompt and executable evaluator.
