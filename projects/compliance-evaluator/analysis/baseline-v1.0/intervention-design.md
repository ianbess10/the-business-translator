# Evidence-Gated Decision Pipeline v1.0

## Decision record

**Selected intervention:** replace the one-step disposition with one stage-gated workflow that combines bounded AI analysis with deterministic transition, ownership and escalation controls.

**Why this intervention:** the baseline generally recognised relevant facts but did not reliably challenge the proposal under test, enforce dependencies between fields, resolve authoritative owners or apply escalation policy. Adding examples to the same one-step prompt would not by itself prevent logically inconsistent operating states.

**Status:** design selected from baseline failure analysis; implementation and regression execution not yet started.

## Operating principle

> A proposal is a claim to test, not evidence to accept.

The workflow must keep three things separate:

- **facts** — supplied source, institution, obligation, control and evidence records;
- **proposal** — a potentially wrong disposition included to test professional challenge; and
- **decision** — the workflow's traceable disposition after applying approved rules.

## Stage sequence

```text
1. Source authority and status
              ↓ pass
2. Obligation support and applicability
              ↓ human-approved obligation only
3. Assurance-entry gate
              ↓ entered
4. Control, catalogue owner and evidence
              ↓
5. Gap, severity, action and escalation
              ↓
6. Cross-field reconciliation and human review
```

Each stage receives only the facts and decisions required for that stage. Later-stage outputs cannot override an earlier-stage stop.

## Stage controls

### 1. Source authority and status

Classify the source before considering the candidate statement.

| Source state | Permitted disposition | Downstream boundary |
|---|---|---|
| Current binding candidate | Candidate obligation assessment | May proceed to applicability |
| Final change with unverified commencement | Pending-commencement change event | Escalate material timing/applicability uncertainty; no assurance |
| Guidance | Guidance context | No binding obligation or assurance |
| Draft | Watchlist/readiness only | No in-force obligation or assurance |
| Superseded | Historical trace only | Stop |
| Strategy | Horizon context only | Stop |
| Blocked or conflicting source | Blocked/source-conflict disposition | Stop; escalate conflict where required |

The proposal under test must not influence this classification.

### 2. Obligation support and applicability

Test whether the candidate statement is supported without extending frequency, scope, deadline or legal effect. Applicability can be assessed only from the frozen institution facts.

Missing commencement, legal-entity, licence, activity or classification facts produce `applicability_uncertain` or `not_assessed`; they must not be silently converted into an applicable candidate.

### 3. Assurance-entry gate

The only permitted entry condition is:

```text
upstream_obligation.supplied = true
AND upstream_obligation.status = approved
```

If the condition is false, the workflow deterministically sets:

- `assurance_gate = not_entered`;
- `mapping_status = not_applicable`;
- `control_mappings = []`;
- `assurance_outcome = not_applicable`;
- `gap_types = []`;
- `gap_severity = not_applicable`; and
- `remediation_action_types = []`.

AI output cannot override this normalisation.

### 4. Control, owner and evidence

When assurance is entered:

- control identifiers must resolve against the frozen institution catalogue;
- the owner returned for each control must equal the catalogue owner;
- the proposed owner is used only as a challenge input;
- control description or design evidence does not prove operation;
- missing operating evidence produces `insufficient_evidence`; and
- adverse operating records are evaluated as potential operating exceptions, not treated as merely absent evidence.

### 5. Gap, severity, action and escalation

The workflow derives these fields from policy triggers rather than from the proposed answer.

| Trigger | Required treatment |
|---|---|
| Final change with material commencement and applicability uncertainty | Escalate to accountable compliance and legal roles |
| Unresolved source conflict affecting the current obligation | Block approval and escalate to compliance and legal roles |
| High-severity potential design gap | Escalate to the accountable compliance owner |
| High-severity operating exception with incomplete remediation | Escalate to conduct risk and compliance owners |
| Missing routine evidence with no adverse indicator | Evidence request; severity unassessed; no management escalation |
| Complete accepted evidence with no adverse indicator | No gap, remediation or escalation |

Escalation roles must come from the policy route for the trigger, not from the proposal.

### 6. Cross-field reconciliation and human review

Before release, a deterministic validator rejects or normalises:

- assurance fields populated when the gate is not entered;
- control owners that conflict with the catalogue;
- `mapped_and_evidenced` with a gap or missing required evidence;
- `insufficient_evidence` without an evidence request;
- high-severity potential gaps without escalation;
- escalation without an approved trigger or accountable role;
- no escalation when a mandatory trigger exists; and
- any compliance conclusion other than `not_determined`.

Human review remains required for every final record.

## Regression acceptance gates

Testing on the existing 24 cases is regression evidence, not independent validation. The engineered workflow must meet these hard operating gates before a holdout is authored:

1. zero assurance-stage leakage across all 16 `not_entered` cases;
2. zero prohibited compliance conclusions;
3. exact source boundary treatment for draft, superseded, strategy, blocked and conflicting sources;
4. exact catalogue owner routing in all eight entered assurance cases;
5. all six mandatory escalations detected;
6. zero unnecessary escalations in the 18 non-escalation cases;
7. routine missing evidence remains distinct from a confirmed or potential control gap; and
8. every output passes cross-field reconciliation without post-run manual correction.

End-to-end and component metrics will still be reported in full. These gates are not permission to suppress other errors.

## Change-control boundary

- Do not modify the simple baseline prompt or its preserved results.
- Implement this intervention as a separately versioned workflow.
- Use general source, control and escalation policies; do not encode case IDs or expected labels.
- Run the engineered workflow against the frozen regression set only after its prompt, rules, schemas and evaluator changes are committed.
- Analyse regression results without tuning or rerunning that frozen version.
- Create and freeze a separate unseen holdout only after the regression release gate is satisfied.

## Next implementation artefacts

1. stage-specific decision schemas;
2. authoritative source-transition table;
3. catalogue owner resolver;
4. evidence/gap/severity decision table;
5. escalation policy table;
6. deterministic cross-field validator;
7. orchestration runner that never loads labels; and
8. regression evaluation adapter that preserves baseline-versus-engineered comparison.
