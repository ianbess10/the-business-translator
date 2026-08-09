# Obligation Schema v1.0

## Outcome

The obligation schema turns an approved source passage into a structured, reviewable candidate obligation without allowing AI to invent legal effect, applicability or approval.

It creates the controlled hand-off between:

```text
Approved source and status
        ↓
Atomic candidate obligation
        ↓
Applicability facts and missing information
        ↓
Potential operating impact and accountable routing
        ↓
Qualified human decision
```

## What every record must answer

| Decision question | Required record content |
|---|---|
| Which source supports this? | Frozen source-pack ID, source ID, document hash and precise locator |
| What is the source allowed to do? | Manifest extraction gates and permitted record use |
| What exactly is required or proposed? | Actor, modality, action, object, trigger, timing, dependencies and evidence needs |
| Is the statement fully supported? | Support status and unsupported-extension flag |
| Is it legally effective? | Normative strength, legal-effect status and effective-date position |
| Does it apply to the synthetic institution? | Profile facts used, missing facts, assumptions and applicability rationale |
| What might change operationally? | Candidate processes, controls, roles and operating artefacts |
| Who must review it? | Proposed owner, required reviewers and escalation rationale |
| Who approved it? | Human-review status, reviewer role, rationale and timestamp |

## Controls enforced by the schema

The schema rejects records that:

- classify a draft as in force;
- promote guidance into a binding obligation;
- use superseded material as current;
- use a strategy as an operational obligation;
- claim a binding obligation when the source-pack extraction gate blocks it;
- claim applicability while still listing missing applicability facts;
- approve a record without completed human review;
- omit a precise source locator; or
- label an unsupported or extended statement as a supported obligation.

## Lifecycle

1. `generated_candidate` - AI-assisted preparation; human review remains pending.
2. `human_reviewed` - a qualified reviewer has assessed the record but has not necessarily approved it.
3. `approved` - a qualified reviewer accepted or amended the record and supplied a decision rationale and timestamp.
4. `rejected` - the candidate was not accepted as an obligation record.
5. `superseded` - an approved record has been replaced while its history remains auditable.

AI cannot set a valid `approved` record without the required human-review evidence.

## Files

- [`obligation-record.schema.json`](obligation-record.schema.json) - JSON Schema Draft 2020-12 definition.
- [`examples/valid/binding-candidate.json`](examples/valid/binding-candidate.json) - amendment-specific conduct obligation candidate.
- [`examples/valid/guidance-context.json`](examples/valid/guidance-context.json) - current guidance kept non-binding.
- [`examples/valid/draft-watchlist.json`](examples/valid/draft-watchlist.json) - proposed requirement kept out of the in-force workflow.
- [`validate_examples.py`](validate_examples.py) - validates structure, source-pack alignment and prohibited-state tests.
- [`obligation-schema-v1.0.meta.json`](obligation-schema-v1.0.meta.json) - freeze metadata and schema hash.

## Validation

Install `jsonschema` and run:

```bash
python3 validate_examples.py
```

The validator checks all valid examples against the schema and frozen source manifest. It then applies prohibited mutations to prove that draft-as-binding, blocked-source, missing-applicability, unsupported-obligation and approval-without-review states fail.

## Boundary

This schema structures evidence and decisions. It does not determine legal applicability, approve an interpretation, assess a real institution or replace qualified legal and compliance judgement.
