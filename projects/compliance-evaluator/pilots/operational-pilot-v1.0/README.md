# Operational Pilot v1.0

## Status

**Designed and implementation-ready; execution is blocked pending named institutional approvals and approved pilot data.**

This is a separately governed shadow-mode pilot for Regulatory Change & Obligation-to-Control Intelligence. It does not modify frozen v1.7, its regression evidence, or its holdout evidence.

The pilot tests whether the capability improves real operating work—not whether it can reproduce a synthetic benchmark. AI output is advisory and cannot update an obligation register, assign final ownership, open or close a finding, declare compliance, or initiate remediation without authorised human action.

## Pilot objective

Determine whether AI-assisted preparation can reduce time and avoidable hand-offs while preserving or improving decision quality, traceability, escalation calibration and professional accountability.

## Operating scope

- Shadow mode alongside the current regulatory-change process.
- One approved South African legal entity and defined licence/product perimeter.
- Approved FIC AML/CFT and FSCA market-conduct sources only.
- Minimum 40 consecutive eligible work items: 20 AML/CFT and 20 market-conduct.
- At least 16 source/applicability items and 16 obligation-to-control assurance items; the balance may reflect actual intake.
- No personal customer data, transaction data, employee performance data or privileged legal advice.
- No direct integration to production registers, workflow tools or control systems.

## Required approval gates

Pilot execution is prohibited until every gate in `approval-gates.json` is approved by a named human with authority to approve that domain. Repository authors, synthetic identities and benchmark approvals cannot satisfy these gates.

## Human decision model

1. An authorised analyst completes the normal current-process decision without seeing AI output.
2. The frozen pilot workflow prepares a separate advisory assessment.
3. A qualified reviewer compares both records against the approved source and institution facts.
4. The reviewer records the accepted decision, disagreements, corrections and rationale.
5. Only the institution's existing authorised process may create or update operational records.

Legal interpretation, applicability, materiality, control adequacy, finding approval, remediation approval and closure remain human decisions.

## Evidence and measurement

Every work item must produce one immutable pilot record conforming to `pilot-record.schema.json`. The record captures current-process effort, AI-assisted effort, accepted decision, corrections, routing, escalation, reviewer identity, source locators and incidents.

The primary comparison is current process versus AI-assisted preparation:

| Measure | Pilot calculation |
|---|---|
| Time to reviewable assessment | Median analyst minutes before qualified review |
| Touches per work item | Count of people or queues handling the item before accepted disposition |
| Correct first-time routing | Initial owner accepted without reassignment |
| Decision-field agreement | AI advisory fields matching the reviewer-accepted decision |
| Evidence completeness | Mandatory evidence fields accepted without supplementation |
| Unnecessary escalation rate | AI escalation not supported by the accepted decision |
| Missed escalation rate | Required accepted escalation absent from AI advice |
| Time to accepted disposition | Elapsed working time from intake to reviewer decision |
| Cost per work item | Recorded effort multiplied by approved role-cost assumptions |

## Success gates

The pilot may be recommended for a controlled next phase only when all are true:

- 100% human review and source traceability;
- zero compliance declarations or unauthorised operational actions;
- zero missed material escalations;
- no unresolved critical incident or data-governance breach;
- at least 90% correct first-time routing;
- at least 95% exact agreement on mandatory decision fields;
- at least 20% median reduction in preparation time;
- at least 15% reduction in touches per work item; and
- independent assurance accepts the evidence and limitations.

Passing these gates does not authorise production deployment. It permits a separately approved controlled-live decision only.

## Stop conditions

Immediately stop new processing and preserve evidence if any of the following occurs:

- confidential, privileged or prohibited data enters the workflow;
- an AI output is used as an unreviewed operational decision;
- a material escalation is missed;
- source identity or version cannot be verified;
- the workflow accesses benchmark labels or evaluation authority at runtime;
- provider, model, prompt, schema, policy or rulebook identity differs from the approved manifest;
- an integrity, security or auditability control fails; or
- the accountable pilot executive directs suspension.

## Current execution decision

`go-no-go.json` records **NO-GO for execution** until institutional authority, data approval, named participants, an approved source corpus and the operating baseline are supplied. The pilot design may be reviewed and approved without processing data.
