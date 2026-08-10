# Baseline v1.0 Coverage Matrix

## AML/CFT cases

| Case | Decision tested | Expected operating disposition |
|---|---|---|
| `AML-001` | Current official guidance | Guidance context; no control assurance |
| `AML-002` | Superseded guidance | Historical trace only |
| `AML-003` | Final directive with unverified commencement | Final change event; applicability uncertain; escalate |
| `AML-004` | Draft treated as in force | Draft watchlist only |
| `AML-005` | Original Act without amendment chain | Binding extraction blocked |
| `AML-006` | Unofficial compilation treated as law | Locator discovery only; binding extraction blocked |
| `AML-007` | Guidance promoted to mandatory rule | Guidance context; remove unsupported legal-strength extension |
| `AML-008` | Missing Schedule 1 classification | Applicability uncertain; escalate |
| `AML-009` | Explicitly excluded virtual-asset service | Out of institution scope |
| `AML-010` | Unsupported daily screening frequency | Retain guidance context; remove unsupported frequency |
| `AML-011` | Control assessment before obligation approval | Do not enter control assurance |
| `AML-012` | Material uncertainty silently deferred | Escalate commencement and applicability questions |

## Market-conduct cases

| Case | Decision tested | Expected operating disposition |
|---|---|---|
| `CON-001` | Supported binding candidate not yet approved | Candidate obligation; do not enter assurance yet |
| `CON-002` | Standalone base Code | Block until amendment chain is applied |
| `CON-003` | Regulatory strategy treated as binding | Strategy context only |
| `CON-004` | Unreconciled base and amendment texts | Source conflict; compliance and legal escalation |
| `CON-005` | Correct mapping with sufficient evidence | Mapped and evidenced |
| `CON-006` | Correct control, wrong owner | Correct owner to Complaints Manager |
| `CON-007` | Design description, no operating records | Insufficient evidence; routine evidence request |
| `CON-008` | Missing ownership and review design | High potential design gap; escalate |
| `CON-009` | Complete evidence but gap proposed | Reject false-positive gap |
| `CON-010` | Complaint operation mapped, oversight omitted | Partial mapping; mapping review |
| `CON-011` | Repeated material operating exceptions | High potential operating gap; remediate and escalate |
| `CON-012` | Missing routine monthly evidence | Insufficient evidence; request without escalation |

## Coverage balance

| Dimension | Count |
|---|---:|
| Total cases | 24 |
| AML/CFT | 12 |
| Market conduct | 12 |
| Cases entering control assurance | 8 |
| Cases blocked before control assurance | 16 |
| `mapped_and_evidenced` labels | 3 |
| `insufficient_evidence` labels | 2 |
| `potential_control_gap` labels | 3 |
| Required failure-mode tags | 20 |
