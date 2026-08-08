# Regulatory Compliance Evaluator

## Business Problem

Operating procedures need to remain aligned with defined regulatory and control requirements. Manual comparison can be time-consuming and inconsistent.

The prototype asks whether AI can identify **potential** control gaps and provide evidence for qualified human review.

## Operating Principle

The system does not determine whether an organisation is legally or regulatorily compliant.

It identifies potential gaps against a supplied reference framework.

## Workflow

```text
Regulatory / control source
        +
Operating procedure
        ↓
AI comparison
        ↓
Control mapping
        ↓
Potential gap
        ↓
Evidence
        ↓
Human compliance review
```

## Difficult Test Cases

- compliant procedure;
- obvious gap;
- ambiguous language;
- outdated source;
- conflicting requirements;
- missing evidence;
- false positive;
- source outside the approved corpus.

## Evaluation

Key metrics:
- correct control mapping;
- evidence accuracy;
- unsupported claims;
- false-positive rate;
- escalation accuracy.

## Human Oversight

No regulatory, legal or compliance decision is finalised by the model.
