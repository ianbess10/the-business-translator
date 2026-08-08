# Example Failure — Unsupported Inference

## Input

"The settlement date is not present in the supplied message."

## Bad output

"Settlement will occur on the next market business day."

## Failure

The model inferred a settlement date that was not provided.

## Business consequence

An operational user could treat an unsupported assumption as a confirmed fact.

## Intervention

Add explicit rules:
- never infer dates;
- return missing_information;
- escalate when the missing field is decision-critical.

## Remaining risk

A human reviewer remains necessary for consequential settlement actions.
