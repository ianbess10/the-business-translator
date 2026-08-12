# Assurance Composition, Severity and Escalation Policy v1.0

## Purpose

This approved synthetic policy defines how an AI-assisted obligation-to-control assurance capability must combine two independent operating facts:

- whether the current control set covers the approved obligation; and
- what the supplied evidence says about control design or operation.

The policy prevents one condition from hiding another. It is controlled business authority, not prompt content, workflow code or a benchmark answer key.

## Executive rule

**Preserve every supported assurance condition, route every required action, and apply the highest approved escalation floor.**

A partial mapping does not erase missing evidence. A coverage gap does not suppress an adverse operating exception. Conversely, a missing routine document does not by itself become a high-severity control failure.

## Independent dimensions

### Coverage state

- `complete`: all mandatory obligation elements are covered by current controls;
- `partial`: at least one mandatory element is covered and at least one remains uncovered;
- `absent`: no suitable current control covers a mandatory element; and
- `not_assessable`: approved coverage authority is missing or invalid.

### Evidence condition

- `sufficient`;
- `design_deficiency`;
- `missing_operating_evidence`;
- `adverse_operating_evidence`; and
- `not_assessable`.

Both values must survive into the terminal record. A headline outcome may be derived for compatibility only after gaps, actions, owners and escalation have been retained.

## General consequences

| Condition | Gap | Severity | Action | Escalation floor |
|---|---|---|---|---|
| Complete coverage | None | Not applicable | None | None |
| Partial coverage | Partial coverage | Medium | Mapping review | None |
| Absent coverage | No control | High | Control design change | Workstream compliance authority |
| Missing operating evidence | Operating evidence missing | Unassessed | Evidence request | None |
| Design deficiency | Control design | High | Control design change | Workstream compliance authority |
| Adverse operating evidence | Operating exception | High | Operating remediation | Workstream oversight and compliance authorities |

`not_assessable` is not converted into a policy conclusion. Missing coverage or evidence authority quarantines the case for human review.

## Composition

Actions and gap types are set unions. Routing is resolved independently for each action:

- mapping review → mapping authority owner;
- control design change → current control owner and workstream compliance authority;
- evidence request → evidence owner;
- operating remediation → current control owner and workstream oversight authority.

Severity is derived after all conditions are preserved:

1. any approved high or critical condition sets the corresponding floor;
2. otherwise partial coverage produces medium severity;
3. otherwise missing evidence remains unassessed; and
4. otherwise severity is not applicable.

Escalation is the union of every applicable trigger. A lower-severity condition cannot remove a role or escalation required by a higher-severity condition.

## Workstream escalation roles

- AML/CFT design or no-control gap → AML Compliance Officer;
- AML/CFT adverse operating evidence → AML Compliance Officer and Head of Compliance;
- market-conduct design or no-control gap → Head of Compliance; and
- market-conduct adverse operating evidence → Conduct Risk Officer and Head of Compliance.

These roles are general workstream authorities and reproduce the previously approved escalation policy without case-specific logic.

## Headline compatibility outcomes

Where an external schema requires one headline outcome:

- any assessed design, operating or coverage gap → `potential_control_gap`;
- otherwise missing operating evidence → `insufficient_evidence`;
- otherwise complete coverage plus sufficient evidence → `mapped_and_evidenced`; and
- a not-assessable dimension → quarantine with no policy conclusion.

The headline cannot replace the underlying dimensions.

## Approval

The policy was authored under the synthetic Regulatory Change Lead role, reviewed for challenge by synthetic Independent Assurance and approved by a synthetic Head of Compliance. All identities are fictional portfolio controls.

Approval confirms a general synthetic operating policy only. It is not legal advice, a compliance opinion, production governance or evidence of real institutional approval.

## Implementation boundary

The policy contains no benchmark case IDs, evidence IDs, expected labels or case exceptions. The boundary fixtures use generic combinations that are not regression cases.

No v1.6 workflow, evaluator, provider contract, regression execution or score is created by this policy stage.
