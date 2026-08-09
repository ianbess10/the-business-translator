# Obligation-to-Control Operating Model

## Outcome

Create an auditable chain from an approved regulatory source to an accountable operating response:

```text
Source
  → Change
    → Obligation
      → Applicability
        → Business impact
          → Policy / process / system / data
            → Control
              → Evidence
                → Finding
                  → Owner and action
                    → Human decision
```

The chain must remain navigable in both directions. A reviewer should be able to start with an obligation and find its controls and evidence, or start with a control and identify every obligation it supports.

## Stage 1: source intake and authority

Capture:

- authority and jurisdiction;
- instrument title, type and status;
- official URL and version;
- publication, commencement and transition dates;
- amendment, supersession and withdrawal position; and
- whether the source is admitted to the approved corpus.

Control: draft, strategy, plan, guidance and binding instruments remain visibly distinct.

## Stage 2: change identification

Compare the approved source version with the previous approved version and identify:

- new text;
- amended text;
- repealed or superseded text;
- clarifications;
- changed dates or thresholds; and
- unchanged context needed to understand the change.

Control: the model must not infer a legal change merely because wording differs. Human review confirms significance.

## Stage 3: obligation structuring

Convert source text into reviewable candidate obligations:

- actor;
- required or prohibited activity;
- object or outcome;
- trigger or condition;
- timing or frequency;
- evidence or reporting requirement;
- exception or dependency; and
- source locator.

Control: every obligation statement must be traceable to supplied source text. Unsupported extensions fail evaluation.

## Stage 4: applicability assessment

Identify the institution facts required to decide applicability:

- legal entity and accountable-institution category;
- licence and regulated activity;
- product or service;
- customer and counterparty type;
- distribution channel;
- jurisdiction and geographic exposure;
- transaction or relationship characteristics; and
- effective or transition date.

Control: missing applicability facts produce `applicability_uncertain`, not a guessed conclusion.

## Stage 5: operating impact

Map the candidate obligation to:

- governance and policy;
- process and procedure;
- technology and workflow;
- customer or transaction data;
- preventive, detective and corrective controls;
- reporting and management information;
- training and competence;
- third parties and outsourcing; and
- records and assurance evidence.

Control: impact mapping is a review proposal until accepted by the accountable owner.

## Stage 6: control and evidence assurance

For every mapping, assess the supplied evidence:

- control objective;
- control description;
- owner and operator;
- frequency or trigger;
- system or manual execution;
- design evidence;
- operating evidence;
- exceptions and remediation; and
- testing or assurance evidence.

Control: a control description without operating evidence cannot automatically be treated as evidenced.

## Stage 7: finding and routing

Use the project taxonomy:

- `mapped_and_evidenced`;
- `potential_control_gap`;
- `insufficient_evidence`;
- `source_conflict`;
- `applicability_uncertain`;
- `draft_or_watchlist`;
- `superseded`; or
- `out_of_scope`.

Route to the appropriate role:

- regulatory change lead;
- compliance advisory;
- legal;
- AML compliance officer or MLRO-equivalent role;
- conduct-risk or customer-outcomes owner;
- policy owner;
- process or operations owner;
- control owner;
- technology or data owner; or
- independent assurance.

Control: the model proposes routing. Accountable functions accept or change ownership.

## Stage 8: decision and closure

Record:

- reviewer decision;
- accepted interpretation and applicability;
- agreed controls and evidence;
- remediation action and due date;
- accepted risk or formal exception where authorised;
- implementation evidence;
- assurance outcome; and
- closure authority and timestamp.

Control: AI cannot approve, accept risk or close an obligation or finding.

## Minimum audit trail

Every record must preserve:

- source and version used;
- model and workflow version;
- source excerpt and locator;
- generated obligation and mapping;
- confidence and limitations;
- human changes;
- final reviewer decision;
- ownership changes;
- timestamps; and
- linked evidence.

The project should measure human overrides as a source of learning, not conceal them as model failure.
