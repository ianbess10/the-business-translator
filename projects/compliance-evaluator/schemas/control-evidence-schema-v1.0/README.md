# Control and Evidence Schema v1.0

## Outcome

This schema connects an approved regulatory obligation to the institution's operating controls, accountable owners, expected evidence, assurance gaps and remediation routing.

It creates the controlled hand-off from interpretation to implementation assurance:

```text
Human-approved obligation
        ↓
Affected process and control mapping
        ↓
Control owner, operator and control design
        ↓
Expected evidence and supplied evidence
        ↓
Evidenced mapping, insufficient evidence or potential gap
        ↓
Accountable review, remediation and authorised closure
```

Approval of an obligation does not prove that its controls are adequate or operating. The control-and-evidence assessment requires a separate human decision.

## What every record must answer

| Operational question | Required record content |
|---|---|
| Is the upstream obligation authorised for assessment? | Approved lifecycle status, obligation hash and human approval reference |
| Which parts of the operating model are affected? | Frozen profile, process IDs and mapping coverage |
| Which controls address the obligation? | Catalogue control ID, name, owner, type, objective and mapping rationale |
| Who owns and operates each control? | Catalogue owner, operator, assessment owner and required reviewers |
| What evidence should exist? | Evidence type, assurance purpose, acceptance criteria, period and evidence owner |
| What evidence was actually supplied? | Evidence reference, status, location, integrity hash, period and limitations |
| Is the material decision-ready? | Design, operating and testing-evidence assessment |
| Is there a gap or merely missing evidence? | Separate outcome, gap type, evidence basis and non-compliance boundary |
| What must happen next? | Linked remediation action, accountable owner, due date, priority and escalation |
| Who can approve or close it? | Named reviewer, rationale, closure authority, evidence and timestamp |

## Operational outcomes

- `mapped_and_evidenced` — approved controls are mapped and the required supplied evidence supports the defined assessment scope.
- `insufficient_evidence` — the control mapping may be sound, but the supplied material cannot support an assurance decision.
- `potential_control_gap` — the supplied material indicates a potentially missing or inadequate control response that requires human confirmation.

Every outcome carries `compliance_conclusion: not_determined`. The schema does not permit compliant or non-compliant conclusions.

## Controls enforced

The schema and connected validator reject records that:

- send an unapproved obligation into control assurance;
- alter the frozen obligation or institution-profile hash;
- map an unknown control or change its catalogue owner, name or type;
- treat a control description as operating evidence;
- classify missing evidence as mapped and evidenced;
- let an AI-generated assessment approve itself or confirm a gap;
- omit escalation for a high or critical potential gap;
- reference evidence whose hash does not match the supplied artefact;
- route remediation to a gap that does not exist; or
- close an assessment without authority and closure evidence.

## Human decision lifecycle

1. `generated_assessment` — AI-assisted proposal; gaps and actions remain potential or proposed.
2. `human_reviewed` — an authorised person has reviewed the assessment without necessarily approving it.
3. `approved_assessment` — a named reviewer accepted or amended the mapping, evidence outcome and routing.
4. `closed` — an authorised closer supplied closure rationale and evidence; all remediation actions are closed or rejected.
5. `superseded` — the record has been replaced but remains auditable.

AI cannot approve the assessment, confirm a gap, accept risk or close remediation.

## Synthetic examples

- [`mapped-and-evidenced.json`](examples/valid/mapped-and-evidenced.json) — the approved complaints-framework obligation maps to two profile controls with hashed design and operating evidence.
- [`insufficient-evidence.json`](examples/valid/insufficient-evidence.json) — design evidence is available but the operating records are missing, producing a routine evidence request rather than a control-failure conclusion.
- [`potential-control-gap.json`](examples/valid/potential-control-gap.json) — a partial design indicates a potential ownership and review gap, triggering elevated review and escalation.

The examples are synthetic schema evidence, not production performance or an assessment of a real institution.

## Files

- [`control-evidence-assessment.schema.json`](control-evidence-assessment.schema.json) — JSON Schema Draft 2020-12 definition.
- [`fixtures/approved-obligation.json`](fixtures/approved-obligation.json) — human-approved upstream obligation validated against Obligation Schema v1.0.
- [`fixtures/evidence`](fixtures/evidence) — four small synthetic evidence artefacts with verified hashes.
- [`validate_examples.py`](validate_examples.py) — validates both schemas, frozen inputs, profile mappings, evidence integrity and prohibited states.
- [`control-evidence-schema-v1.0.meta.json`](control-evidence-schema-v1.0.meta.json) — freeze metadata and schema hash.

## Validation

Install `jsonschema` and run:

```bash
python3 validate_examples.py
```

The validator accepts three operational scenarios and rejects thirteen prohibited states.

## Boundary

This schema structures control-assurance evidence and human decisions. It does not provide legal advice, determine compliance, prove the effectiveness of a real control, accept risk or replace compliance, business-control or independent-assurance judgement.
