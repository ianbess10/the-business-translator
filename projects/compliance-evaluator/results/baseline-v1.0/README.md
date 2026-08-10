# Simple Baseline v1.0 — Synthetic Benchmark Results

> **Evidence boundary:** These are results from 24 frozen synthetic cases. They are not production performance, legal advice or a compliance conclusion.

## Run control

- Run ID: `baseline-v1.0-329f365a-0b6d-45a3-aae0-14e6da5b7913`
- Model snapshot: `gpt-4o-mini-2024-07-18`
- Temperature: `0`
- Run attempts: one
- Prompt tuning after observation: none
- Scoring: deterministic exact comparison; rationale wording excluded

## Headline results

| Measure | Result |
|---|---:|
| End-to-end exact disposition | 4.2% (1/24) |
| Source-use disposition | 70.8% |
| Obligation outcome | 58.3% |
| Applicability status | 62.5% |
| Approved-obligation gate | 100.0% |
| Control mapping on entered cases | 100.0% |
| Owner routing on entered cases | 62.5% |
| Evidence/gap outcome on entered cases | 87.5% |
| Escalation precision | 0.0% |
| Escalation recall | 0.0% |
| Potential-gap precision | 75.0% |
| Potential-gap recall | 100.0% |
| Prohibited compliance conclusions | 0 |

## Escalation confusion matrix

| True positive | False positive | True negative | False negative |
|---:|---:|---:|---:|
| 0 | 2 | 16 | 6 |

## Cases requiring failure analysis

| Case | Workstream | Mismatched decision fields |
|---|---|---|
| `AML-002` | aml_cft | source_use_disposition, obligation_outcome, applicability_status |
| `AML-003` | aml_cft | source_use_disposition, obligation_outcome, applicability_status, mapping_status, gap_severity, escalation_required, control_ids, control_mappings_with_owner, gap_types, remediation_action_types, escalation_roles |
| `AML-004` | aml_cft | obligation_outcome, applicability_status, mapping_status, control_ids, control_mappings_with_owner |
| `AML-005` | aml_cft | source_use_disposition, obligation_outcome, applicability_status, mapping_status, gap_severity, control_ids, control_mappings_with_owner, gap_types, remediation_action_types |
| `AML-006` | aml_cft | obligation_outcome, applicability_status, mapping_status, control_ids, control_mappings_with_owner |
| `AML-007` | aml_cft | source_use_disposition, obligation_outcome, mapping_status, gap_severity, control_ids, control_mappings_with_owner, gap_types, remediation_action_types |
| `AML-008` | aml_cft | mapping_status, gap_severity, escalation_required, control_ids, control_mappings_with_owner, gap_types, remediation_action_types, escalation_roles |
| `AML-009` | aml_cft | obligation_outcome, applicability_status, mapping_status, control_ids, control_mappings_with_owner |
| `AML-010` | aml_cft | mapping_status, control_ids, control_mappings_with_owner |
| `AML-011` | aml_cft | mapping_status, assurance_outcome, control_ids, control_mappings_with_owner |
| `AML-012` | aml_cft | gap_severity, escalation_required, gap_types, remediation_action_types, escalation_roles |
| `CON-001` | market_conduct | mapping_status, control_ids, control_mappings_with_owner |
| `CON-002` | market_conduct | source_use_disposition, obligation_outcome, applicability_status, mapping_status, control_ids, control_mappings_with_owner |
| `CON-003` | market_conduct | source_use_disposition, obligation_outcome, applicability_status, mapping_status, control_ids, control_mappings_with_owner |
| `CON-004` | market_conduct | source_use_disposition, obligation_outcome, applicability_status, mapping_status, gap_severity, escalation_required, control_ids, control_mappings_with_owner, gap_types, remediation_action_types, escalation_roles |
| `CON-005` | market_conduct | control_mappings_with_owner |
| `CON-006` | market_conduct | control_mappings_with_owner |
| `CON-007` | market_conduct | gap_severity |
| `CON-008` | market_conduct | mapping_status, gap_severity, escalation_required, gap_types, remediation_action_types, escalation_roles |
| `CON-009` | market_conduct | assurance_outcome, gap_severity, escalation_required, control_mappings_with_owner, gap_types, remediation_action_types, escalation_roles |
| `CON-010` | market_conduct | gap_types |
| `CON-011` | market_conduct | gap_severity, escalation_required, gap_types, remediation_action_types, escalation_roles |
| `CON-012` | market_conduct | gap_severity, escalation_required, escalation_roles |

## Interpretation boundary

This is the deliberately simple, pre-engineering baseline. Its errors are preserved for failure analysis. No prompt changes or reruns were made after results were observed.

The next controlled step is to examine the recorded failures by source boundary, obligation decision, applicability, control mapping, evidence, ownership and escalation—then design one traceable workflow intervention against the same frozen regression set.
