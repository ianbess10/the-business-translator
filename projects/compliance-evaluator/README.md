# Regulatory Change & Obligation-to-Control Intelligence

## AI-enabled regulatory change management and obligation-to-control assurance

> **AI is the enabler. Faster, traceable and accountable regulatory implementation is the product.**

## Project status

**Project 2 — South African scope, synthetic institution profile and source pack frozen; decision-schema design next.**

This project will test an AI-assisted capability for regulated financial institutions, starting with:

1. South African AML/CFT requirements administered by the Financial Intelligence Centre (FIC); and
2. Financial Sector Conduct Authority (FSCA) market-conduct requirements.

The capability will help teams identify a regulatory change, structure its obligations, map them to affected policies, processes and controls, identify missing evidence, assign accountable review and track the decision through to closure.

It will not decide whether an institution is legally or regulatorily compliant. Qualified compliance, legal, risk, control and business professionals remain accountable for applicability, interpretation, materiality, control adequacy, approval and implementation.

## The operating problem

Regulatory change often arrives as legislation, amendments, standards, directives, guidance, interpretation rulings, regulatory plans or consultation material. These sources do not arrive as an implementation-ready control plan.

A regulated institution must determine:

- what changed and when;
- whether the source is binding, interpretive, planned or still draft;
- which legal entity, licence, product, customer, channel or activity may be affected;
- which obligations are new, amended, clarified, superseded or unchanged;
- which policy, process, system, data field, control, training or management information is impacted;
- whether current control evidence supports the obligation;
- who owns the decision and implementation; and
- which uncertainty or potential gap requires escalation.

This work is fragmented across regulatory change, compliance advisory, legal, policy, operations, technology, risk and control owners. Weak traceability creates duplicated interpretation, delayed implementation, uncertain ownership and difficulty demonstrating how an external requirement became an internal operating response.

## Two connected capabilities

### 1. Regulatory change management

Convert a new or changed approved source into a structured impact assessment:

```text
Authoritative source change
        ↓
Status, effective date and applicability questions
        ↓
Atomic obligations and source locators
        ↓
Impacted business activities and controls
        ↓
Owners, actions, priorities and escalation
        ↓
Human-approved implementation plan
```

### 2. Obligation-to-control assurance

Test whether each approved obligation has an accountable, evidenced operating response:

```text
Approved obligation
        ↓
Mapped policy, process and control
        ↓
Control design and operating evidence
        ↓
Aligned, potential gap, insufficient evidence or source conflict
        ↓
Qualified assurance decision and remediation tracking
```

The second capability closes the loop. Regulatory change is not complete merely because an obligation was recorded; the organisation must be able to show how it is implemented and evidenced.

## Initial South African scope

### AML/CFT

The first workstream will use approved material from the FIC and the official South African legislation portal. Candidate operating domains include:

- enterprise and customer money-laundering, terrorist-financing and proliferation-financing risk assessment;
- risk management and compliance programme governance;
- customer due diligence and beneficial-ownership information;
- ongoing monitoring and enhanced measures;
- record keeping;
- regulatory reporting;
- targeted financial sanctions controls;
- training, oversight and evidence; and
- regulatory returns and supervisory requests.

These are candidate mapping domains, not pre-decided legal obligations. Exact obligation wording, status, commencement and applicability must come from the approved source corpus and human review.

### FSCA market conduct

The second workstream will begin with the FSCA’s statutory market-conduct mandate and the applicable conduct standards, guidance notices, interpretation rulings and financial-sector laws selected for the synthetic institution profile.

Candidate operating domains include:

- product and service governance;
- customer information and disclosure;
- advice, distribution and intermediary controls;
- fair customer outcomes;
- complaints and remediation;
- vulnerable-customer considerations;
- market integrity and conduct controls; and
- management information, oversight and assurance.

The first release will not attempt to create a universal FSCA obligation library. Applicability varies by legal entity, licence, product and sector. The synthetic institution profile and approved instrument list must be fixed before evaluation.

## Source hierarchy and status control

Every source must be classified before its content is used:

| Status | Permitted use |
|---|---|
| Enacted legislation or in-force regulatory instrument | Candidate binding obligation, subject to applicability and human interpretation |
| Official guidance or interpretation | Interpretive context; never silently promoted to legislation |
| Regulatory strategy or plan | Change horizon and prioritisation; not a binding obligation by itself |
| Consultation or draft | Watchlist and readiness assessment only |
| Superseded or withdrawn | Historical trace only; excluded from current obligation conclusions |
| Unverified or secondary source | Discovery aid only; excluded from assessment evidence |

See the [official source register](source-register.md) and frozen [South African Regulatory Source Pack v1.0](source-packs/source-pack-v1.0/README.md), verified on 9 August 2026.

## Decision record to be built

For every candidate obligation, the capability should prepare:

- source authority, title, version and status;
- effective or relevant date;
- source locator and supported obligation statement;
- applicability conditions and unresolved applicability questions;
- change type: new, amended, clarified, superseded or unchanged;
- impacted entity, product, process, policy, system, data and control;
- mapped control owner and evidence;
- assurance status;
- missing evidence or source conflict;
- proposed action, priority and escalation;
- model confidence and limitations; and
- reviewer decision, rationale and timestamp.

## Assessment taxonomy

Use operationally explicit outcomes:

- `mapped_and_evidenced` — a supported mapping and sufficient supplied evidence exist;
- `potential_control_gap` — the supplied material indicates a potentially missing or inadequate operating response;
- `insufficient_evidence` — a decision cannot be supported from the supplied evidence;
- `source_conflict` — approved sources or versions conflict;
- `applicability_uncertain` — the requirement may depend on entity, licence, product or activity facts not supplied;
- `draft_or_watchlist` — the source is not an in-force obligation source;
- `superseded` — the source is not current; and
- `out_of_scope` — the source or requirement is outside the approved corpus or institution profile.

No `compliant` or `non_compliant` outcome is permitted.

## Tangible business measures

| Measure | What it reveals |
|---|---|
| Time from source publication to triage | Regulatory horizon-scanning responsiveness |
| Time to initial impact assessment | Speed from approved source to reviewable operating view |
| Obligations mapped per review cycle | Analyst capacity and throughput |
| Correct first-time owner assignment | Avoidable reassignment and hand-offs |
| Obligation-to-control mapping completeness | Traceability across the operating model |
| Evidence completeness | Whether findings are decision-ready |
| False-positive gap rate | Unnecessary investigation and remediation effort |
| Missed material-obligation or gap rate | Control risk not surfaced for review |
| Time to agreed disposition | Speed from finding to accepted action or documented closure |
| Overdue implementation actions | Ownership and execution effectiveness |
| Cost per assessed source or obligation | End-to-end analysis and review effort |

No benefit will be claimed until measured against a defined operating baseline.

## Human accountability

The capability may prepare analysis and recommendations. It must not:

- determine legal applicability without reviewed institution facts;
- declare compliance or non-compliance;
- invent or extend an obligation beyond the approved source;
- treat a draft or plan as an in-force obligation;
- determine legal interpretation or materiality;
- approve control adequacy or a remediation plan;
- assign final accountability without owner acceptance; or
- close an obligation or finding without authorised human review.

## First release

The first release will use the frozen [Synthetic South African Investment & Wealth Institution](profiles/synthetic-investment-wealth-institution-v1.0.md) and controlled source excerpts. It will test both workflows without exposing real customer, transaction, employee or institution data.

The immediate build sequence is:

1. ~~freeze the synthetic institution and applicability profile;~~ **complete**
2. ~~freeze a small approved-source pack with explicit status metadata;~~ **complete**
3. define the obligation, control and evidence schemas;
4. create a labelled baseline set spanning AML/CFT and market conduct;
5. run an intentionally simple baseline;
6. analyse obligation, mapping, evidence, ownership and escalation failures;
7. introduce one controlled workflow design;
8. retest on the frozen regression set; and
9. validate once against a separate holdout.

See the [operating model](operating-model.md) and [first-release plan](first-release-plan.md).

The existing [engineered prompt](engineered-prompt.md) is an early technical artefact. It remains subordinate to this operating charter and is not a validated capability.

## Evidence boundary

This repository is an educational portfolio prototype. Source links and statuses must be re-verified before every evaluation run. Nothing in this project is legal advice, a compliance opinion or a representation of an institution’s regulatory position.
