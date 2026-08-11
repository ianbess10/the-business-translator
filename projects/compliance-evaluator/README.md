# Regulatory Change & Obligation-to-Control Intelligence

## AI-enabled regulatory change management and obligation-to-control assurance

> **AI is the enabler. Faster, traceable and accountable regulatory implementation is the product.**

## Project status

**Project 2 — Evidence-Gated Decision Pipeline v1.2 frozen and executed once. The provider rejected the frozen source-stage schema before producing predictions, so no scoring was possible and no rerun occurred.**

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

## Controlled decision records

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

The frozen [Obligation Schema v1.0](schemas/obligation-schema-v1.0/README.md) now enforces this source-to-obligation decision record. It rejects draft-as-binding, guidance-as-law, superseded-as-current, unsupported-obligation and approval-without-review states before they reach control mapping.

The frozen [Control and Evidence Schema v1.0](schemas/control-evidence-schema-v1.0/README.md) now connects each approved obligation to profile controls, owners, expected and supplied evidence, assurance gaps, remediation routing, escalation and human closure. It keeps insufficient evidence separate from a potential control gap and prevents an approved obligation from being mistaken for an effective control.

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

The frozen [Regulatory Intelligence Baseline v1.0](datasets/baseline-v1.0/README.md) provides 12 AML/CFT and 12 market-conduct cases with model-facing inputs separated from evaluator-only labels. It covers source gates, applicability, control mapping, evidence sufficiency, ownership, potential gaps and escalation calibration.

## What the intentionally simple baseline revealed

The [simple baseline](baseline/README.md) was frozen before execution and run once against all 24 inputs using `gpt-4o-mini-2024-07-18` at temperature `0`. The model never received the evaluator-only labels, and the prompt was not changed or rerun after results were observed.

All 24 responses satisfied the structured output contract, but only **1 of 24** matched the full expected operational disposition. This is the central baseline finding: **a well-formed AI response can still be operationally wrong.**

The results show a mixed operating profile:

- the approved-obligation assurance gate, human-review boundary and prohibition on compliance conclusions were preserved in all 24 cases;
- control identifiers were selected correctly in all eight cases that legitimately entered assurance;
- source-use disposition was correct in 17 of 24 cases, obligation outcome in 14 of 24 and applicability status in 15 of 24;
- control owners were routed correctly in five of eight entered cases;
- the model identified all three expected potential gaps but added one false positive; and
- escalation calibration failed materially: it missed all six required escalations and introduced two unnecessary escalations.

These are [synthetic benchmark results](results/baseline-v1.0/README.md), not production performance. They created the evidence base for the completed failure analysis and the selected controlled workflow intervention focused on decision consistency, ownership and escalation.

The completed [operational failure analysis](analysis/baseline-v1.0/README.md) found that the model reproduced at least one proposed answer in 21 of 24 cases, leaked assurance activity past the closed gate in 14 of 16 cases and repeated all eight deliberately wrong escalation proposals. The selected next intervention is an [Evidence-Gated Decision Pipeline v1.0](analysis/baseline-v1.0/intervention-design.md): one stage-gated workflow that treats proposals as untrusted claims, enforces source and approval transitions, resolves catalogue owners and derives escalation from explicit policy triggers.

The frozen [Evidence-Gated Decision Pipeline v1.0](workflows/evidence-gated-v1.0/README.md) was executed once across the 24 regression cases and scored once without tuning or rerunning. It improved end-to-end exactness from **1/24 to 15/24**, detected all six mandatory escalations and passed seven of eight hard release gates. One partial mapping was misclassified as a high design deficiency, producing the sole unnecessary escalation. These are [synthetic regression results](results/evidence-gated-v1.0/README.md), not independent validation or production performance.

The completed [v1.0 case-level failure analysis](analysis/evidence-gated-v1.0/README.md) reduces 26 field mismatches across nine cases to three concentrated decision-boundary causes: applicability was conflated with source or obligation reasoning in nine cases, mapping completeness was conflated with evidence or performance in five, and partial coverage was misclassified as a design deficiency in one. The separately versioned [v1.1 decision](analysis/evidence-gated-v1.0/v1.1-decision.md) selects a narrow intervention while retaining the source, approval, owner, escalation and reconciliation controls that passed.

The separate [Evidence-Gated Decision Pipeline v1.1](workflows/evidence-gated-v1.1/README.md) implemented that decision. Reviewed approved obligations bypassed source reinterpretation and retained their accepted applicability; mapping completeness was derived independently from evidence sufficiency and operating performance; and partial coverage took precedence unless explicit evidence supported a design deficiency. Offline tests covered 16 decision-boundary scenarios, all 24 regression input paths, 20 structured-output schema states and a 14-gate evaluator self-test.

v1.1 was then executed exactly once and scored exactly once. It improved end-to-end exactness to **20/24**, made source disposition and applicability exact, and produced a perfect escalation confusion matrix: six true positives, zero false positives, 18 true negatives and zero false negatives. It nevertheless failed the release decision because only eight of 14 reported gates passed. These are [synthetic regression results](results/evidence-gated-v1.1/README.md), not independent validation or production performance.

The completed [v1.1 case-level failure analysis](analysis/evidence-gated-v1.1/README.md) separates four decision-error cases from one evaluator measurement defect. It identifies three substantive causes: source support was conflated with legal readiness in one case, missing evidence was conflated with control coverage in two, and a proposed mapping was silently expanded in one. The evaluator also mistook the legitimate rule identifier `SRC-CON-002` for a case-specific override because it used substring matching. The separately versioned [v1.2 decision](analysis/evidence-gated-v1.1/v1.2-decision.md) selected stronger stage and identity boundaries without tuning v1.1.

The separate [Evidence-Gated Decision Pipeline v1.2](workflows/evidence-gated-v1.2/README.md) now implements that decision. It distinguishes source-backed wording from legal readiness, prevents evidence status and escalation proposals from entering mapping assessment, prevents the evidence stage from changing current-control membership, and replaces substring-based generality measurement with exact identity and runtime-isolation checks. Offline validation covers 20 decision-boundary scenarios, all 24 frozen input paths, 32 structured-output examples, isolated payloads for all eight assurance cases and a 14-gate evaluator self-test. The workflow and dependencies are hash-frozen for one future 32-call regression run; no API execution occurred during implementation or freeze.

The [sole v1.2 regression execution](results/evidence-gated-v1.2/README.md) was then started against the 24 frozen cases. The provider rejected the first source-stage request because the frozen Structured Outputs schema used `allOf`, which was not permitted in that response-format context. No prediction was generated, so the evaluator was not invoked and no score is claimed. The failure is preserved exactly as an execution-contract outcome: v1.2 remains unchanged, was not tuned or rerun and cannot proceed to holdout validation.

The completed [v1.2 execution-contract failure analysis](analysis/evidence-gated-v1.2/README.md) establishes that the workflow confused general JSON Schema validity with the provider's supported Structured Outputs subset. Offline tests proved the authored Draft 2020-12 rules but did not certify provider compatibility. The separately versioned [v1.3 decision](analysis/evidence-gated-v1.2/v1.3-decision.md) therefore selects provider-compatible transport schemas, deterministic cross-field semantic validation, a static provider-subset audit and three non-benchmark provider contract-certification calls before freeze. It does not implement or execute v1.3.

The separate [Evidence-Gated Decision Pipeline v1.3](workflows/evidence-gated-v1.3/README.md) implemented that decision without changing v1.2. All three exact provider-compatible schemas passed the offline subset audit and one non-benchmark provider contract-certification request each. Deterministic semantic tests rejected cross-field states that the transport schema intentionally could not express, all 24 frozen paths composed offline, payload isolation remained intact, and the retained evaluator passed its 24/24 and 14/14 self-test.

The [sole v1.3 regression execution](results/evidence-gated-v1.3/README.md) then stopped during case 19 after 18 completed cases and 21 validated model calls. A transport-valid evidence response failed the deterministic semantic gate because its design-deficiency assessment disagreed with its evidence flag. No completed predictions file exists, so the evaluator was not invoked and no score is claimed. v1.3 remains frozen and will not be tuned, rerun or scored.

The completed [v1.3 case-level execution failure analysis](analysis/evidence-gated-v1.3/README.md) identifies the failed case as `CON-007` from the frozen order and call topology. It finds that v1.3 asked the model to express one evidence decision through redundant correlated fields that the provider transport schema could not constrain. It also records an evidence-control gap: the rejected raw stage response and case identity were not checkpointed before validation. The separately versioned [v1.4 decision](analysis/evidence-gated-v1.3/v1.4-decision.md) selects one canonical model-authored evidence classification, deterministic downstream derivation, append-only stage evidence and fail-closed case quarantine without retry. It does not implement or execute v1.4.

The separate [Evidence-Gated Decision Pipeline v1.4](workflows/evidence-gated-v1.4/README.md) now implements that decision without changing v1.3. The evidence model authors one canonical assessment; deterministic policy derives flags, assurance outcome, severity, remediation and escalation. Every stage response is checkpointed before semantic validation. An invalid case is quarantined without retry or policy conclusion while the same one-time batch continues, and quarantine-aware evaluation counts it as an end-to-end error and blocks release. All offline boundaries pass, the unchanged source and mapping contracts retain exact v1.3 certification lineage, the one changed evidence contract passed one non-benchmark provider certification, and the exact workflow is hash-frozen before regression. No v1.4 regression execution or score exists.

The [sole v1.4 regression](results/evidence-gated-v1.4/README.md) then completed all 24 terminal cases with 32/32 transport- and semantic-valid calls, zero quarantine and zero retry. It was evaluated exactly once and achieved **21/24 end-to-end exact**, with nine of 15 release gates passing. Source, applicability, current-control ownership and unnecessary-escalation controls were exact, but three entered market-conduct cases retained mapping and assurance errors, including one missed mandatory escalation. v1.4 therefore fails release, remains frozen and will not be tuned, rerun or rescored.

The completed [v1.4 case-level failure analysis](analysis/evidence-gated-v1.4/README.md) finds that all three errors begin with model-authored mapping completeness based on thin control descriptions rather than approved obligation-element coverage. `C-CON-006` was overstated twice and `C-CON-007` understated once. `CON-008` also exposed the absence of typed design and operating-evidence requirements. The separately versioned [v1.5 decision](analysis/evidence-gated-v1.4/v1.5-decision.md) therefore selects a human-approved Coverage and Evidence Rulebook, deterministic mapping completeness and bounded model extraction of evidence observations. It is a business-data and decision-authority intervention, not prompt tuning, and does not implement or execute v1.5.

The immediate build sequence is:

1. ~~freeze the synthetic institution and applicability profile;~~ **complete**
2. ~~freeze a small approved-source pack with explicit status metadata;~~ **complete**
3. ~~define the obligation schema;~~ **complete**
4. ~~define the control and evidence schema;~~ **complete**
5. ~~create a labelled baseline set spanning AML/CFT and market conduct;~~ **complete**
6. ~~define and run an intentionally simple baseline;~~ **complete**
7. ~~analyse obligation, mapping, evidence, ownership and escalation failures;~~ **complete**
8. ~~implement and freeze the Evidence-Gated Decision Pipeline v1.0;~~ **complete**
9. ~~run and score v1.0 once on the frozen regression set without tuning;~~ **complete**
10. ~~complete the v1.0 case-level failure analysis;~~ **complete**
11. ~~make a separately versioned v1.1 intervention decision;~~ **complete**
12. ~~implement, test and freeze v1.1 without changing v1.0;~~ **complete**
13. ~~run and score v1.1 once as regression evidence;~~ **complete**
14. ~~complete the v1.1 case-level failure analysis;~~ **complete**
15. ~~make a separately versioned v1.2 architecture decision;~~ **complete**
16. ~~implement, test and freeze v1.2 without changing or rerunning v1.1;~~ **complete**
17. **v1.2 execution attempted once; provider schema rejection preserved; no predictions existed to score;** **closed without rerun**
18. ~~complete the v1.2 execution-contract failure analysis and make a separately versioned v1.3 decision;~~ **complete**
19. ~~implement, test and provider-certify v1.3 separately before freeze;~~ **complete**
20. **v1.3 executed once; semantic-gate failure preserved; no complete predictions existed to score;** **closed without rerun**
21. ~~complete the v1.3 execution failure analysis and make a separately versioned v1.4 decision;~~ **complete**
22. ~~implement, test, certify and freeze v1.4 separately without modifying v1.3;~~ **complete**
23. ~~execute frozen v1.4 once and evaluate its complete terminal-case record once;~~ **complete — 21/24 exact, 9/15 gates, release failed**
24. ~~complete the v1.4 case-level failure analysis and make a separately versioned v1.5 decision;~~ **complete**
25. **author and approve the v1.5 Coverage and Evidence Rulebook, then implement, test, certify and freeze v1.5 separately;** **next**
26. only after a future frozen version passes every release gate, author and freeze a separate unseen holdout.

See the [operating model](operating-model.md) and [first-release plan](first-release-plan.md).

The existing [engineered prompt](engineered-prompt.md) is an early technical artefact. It remains subordinate to this operating charter and is not a validated capability.

## Evidence boundary

This repository is an educational portfolio prototype. Source links and statuses must be re-verified before every evaluation run. Nothing in this project is legal advice, a compliance opinion or a representation of an institution’s regulatory position.
