# Regulatory Change & Control Intelligence

> **AI is the enabler. Faster, evidence-backed and accountable regulatory impact assessment is the product.**

## Project status

**Next portfolio project — charter established.**

This project will test an AI-assisted capability for translating supplied regulatory or control requirements into a structured view of impacted procedures, controls, evidence gaps, accountable owners and review priorities.

It will not determine whether an organisation is legally or regulatorily compliant. Qualified compliance, legal, risk and business professionals remain accountable for interpretation, materiality, approval and action.

## The operational problem

Regulatory and control requirements must be interpreted, mapped to the operating model and supported by evidence. In practice, this work is often distributed across policy teams, compliance specialists, control owners and operations managers.

The challenge is not simply finding relevant text. Teams must determine:

- what the requirement actually requires;
- which process, procedure, system or control may be affected;
- whether the current procedure contains sufficient evidence of alignment;
- where evidence is missing, contradictory or outdated;
- who should own the review or remediation; and
- which findings require escalation.

Manual comparison can be slow and inconsistent. Poor traceability can create duplicated analysis, delayed implementation, unclear ownership and difficulty demonstrating how a requirement was translated into an operating response.

## The capability to be built

The prototype will compare an approved source requirement with supplied procedure and control material, then prepare a review record containing:

1. the requirement and its source reference;
2. the potentially affected operating activity or control;
3. the relevant procedure evidence;
4. an assessment of alignment, potential gap, insufficient evidence or source conflict;
5. the evidence or authoritative information still required;
6. a proposed owner and next review action;
7. an escalation recommendation; and
8. a complete evidence trail for qualified human review.

```text
Approved requirement
        +
Procedure and control evidence
        ↓
Requirement and impact mapping
        ↓
Evidence-backed alignment assessment
        ↓
Gap, uncertainty or source conflict
        ↓
Owner, next action and escalation treatment
        ↓
Qualified compliance and business review
```

## Operating outcome

The intended outcome is not an AI-generated compliance verdict. It is a faster and more consistent path from a supplied requirement to an accountable, evidence-backed operating decision.

Potential benefits to test include:

- shorter time to complete an initial impact assessment;
- clearer linkage from requirement to procedure, control and owner;
- fewer repeated evidence requests and hand-offs;
- better first-time assignment of review actions;
- earlier identification of missing or conflicting evidence; and
- a more auditable trail from regulatory source to operating response.

## Tangible business measures

| Measure | What it reveals |
|---|---|
| Time to initial impact assessment | Speed from approved source receipt to a reviewable operating view |
| Requirements mapped per review cycle | Analyst capacity and throughput |
| Correct first-time owner assignment | Avoidable reassignment and hand-offs |
| Evidence completeness | Whether findings are decision-ready |
| False-positive potential-gap rate | Unnecessary investigation and remediation effort |
| Missed-gap rate | Material weaknesses not surfaced for review |
| Time to agreed disposition | Speed from finding to accepted action or documented closure |
| Overdue remediation actions | Effectiveness of ownership and follow-through |
| Cost per assessed requirement | End-to-end analysis and review effort |

No benefit will be claimed until measured against a defined operating baseline.

## First validation question

Can the capability distinguish among:

- genuine procedure/control alignment;
- a potential control gap;
- insufficient evidence;
- conflicting approved sources; and
- a requirement outside the supplied approved corpus?

The evaluation must test evidence quality and operating consequence, not merely whether the output looks well structured.

## Initial test scenarios

- clearly aligned procedure and control;
- obvious missing control step;
- ambiguous procedure wording;
- outdated or superseded source;
- conflicting requirements;
- missing supporting evidence;
- plausible false positive;
- unsupported inference beyond the approved corpus;
- correct requirement but wrong operating owner; and
- material issue incorrectly treated as routine.

## Human accountability

The capability may prepare analysis and recommendations. It must not:

- declare the organisation compliant or non-compliant;
- invent regulatory obligations;
- determine legal interpretation or materiality;
- approve a control or remediation plan; or
- close a finding without authorised human review.

## Delivery sequence

1. Define the operating decision and approved-source boundary.
2. Establish the assessment taxonomy and human authority model.
3. Create a small synthetic baseline set with explicit operational labels.
4. Run an intentionally simple baseline.
5. Analyse evidence, routing and escalation failures.
6. Introduce one controlled workflow design.
7. Retest on the frozen regression set.
8. Validate once on a separate holdout.
9. Package results as synthetic evidence, with production claims reserved for a controlled pilot.

The existing [engineered prompt](engineered-prompt.md) is an early technical artefact. It will remain subordinate to this operating charter and must not be treated as a validated capability.
