# Decision Schemas

Schemas in this folder define the controlled records passed between the regulatory-change, impact-assessment and obligation-to-control workflows.

## Current schemas

[`obligation-schema-v1.0`](obligation-schema-v1.0/README.md) defines a traceable candidate-obligation record against:

- institution profile `SA-IWM-SYN-001 v1.0`; and
- source pack `SA-REG-SOURCE-PACK-001 v1.0`.

[`control-evidence-schema-v1.0`](control-evidence-schema-v1.0/README.md) consumes a human-approved obligation and connects it to:

- frozen profile processes and controls;
- accountable control owners and operators;
- expected and supplied evidence;
- evidence sufficiency and potential assurance gaps;
- remediation ownership and escalation; and
- separate human approval and closure authority.

The connected schemas now serve as immutable decision contracts for the frozen [24-case labelled baseline dataset](../datasets/baseline-v1.0/README.md). The next artefacts are the intentionally simple baseline prompt and executable evaluator.
