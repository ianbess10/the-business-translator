# Governance

### AI may
- classify supplied exception information;
- extract structured facts;
- identify missing information;
- prepare a recommended next action;
- flag escalation.

### AI may not
- release or amend trades;
- cancel transactions;
- approve settlement;
- make investment decisions;
- make final compliance decisions.

### Human authority

A qualified operations professional reviews the output before any consequential action.

### Audit trail

Store prompt version, model version, test-set version (`trade-exception-test-set-v1.0`), input case ID, output, evaluator score and approval status.

Frozen evaluation data lives under `datasets/` and must not be edited in place.
