# V4 → V5 Interventions

**Source freeze:** `releases/v4/`  
**Failure analysis:** `releases/v4/failure-analysis/v4-failure-analysis.md`  
**V4 prompt (immutable):** `releases/v4/prompt/engineered-v4.md`  
**V5 prompt (new):** `engineered-prompt-v5.md`  
**Test set (unchanged):** `trade-exception-test-set-v1.0` / `test-set.jsonl`  
**Status:** interventions authored; V5 not yet executed

Every V5 change below maps to an observed V4 failure. No schema, evaluator, provider, test-set or V4 result changes are included.

---

## Intervention catalogue

### I1 — Explicit classification definitions

| Field | Detail |
|---|---|
| **Observed V4 failure** | Taxonomy boundary errors: TX001 (`failed_settlement` vs `data_quality`), TX007 (`market_deadline` vs `data_quality`), TX011 (`data_quality` vs `insufficient_information`), TX018 (`failed_settlement` vs `market_deadline`) |
| **Operational risk** | Wrong queue / wrong remediation path; deadline chase when only data is missing; fail-processing when calendar/ISD work is needed |
| **V5 intervention** | Section “Explicit classification definitions” with use/do-not-use criteria for every `exception_type` |
| **Expected measurable effect** | Fewer boundary misclasses on single-defect and holiday/urgency cases |
| **Metric affected** | Classification accuracy |

### I2 — Root-cause classification over downstream symptom

| Field | Detail |
|---|---|
| **Observed V4 failure** | TX002, TX012: “failed” wording dominated despite instruction/SSI root cause; next action repaired SSI/account while type stayed `failed_settlement` |
| **Operational risk** | Repeat settlement fails; SSI/account master data not corrected; symptom recycling |
| **V5 intervention** | Section “Root-cause over downstream symptom”; require `recommended_next_action` to align with root-cause `exception_type` |
| **Expected measurable effect** | TX002/TX012 shift to `instruction_issue`; reduce fail-vs-instruction inversions |
| **Metric affected** | Classification accuracy |

### I3 — Classification precedence for dual-cue cases

| Field | Detail |
|---|---|
| **Observed V4 failure** | Dual-cue cases resolved to outcome class: TX002/TX012 (fail + instruction), TX018 (postponed + market holiday) |
| **Operational risk** | Higher-value root cause ignored when narrative contains both symptom and cause |
| **V5 intervention** | Ordered precedence list (`insufficient_information` → … → `failed_settlement` → `data_quality` → `other`) |
| **Expected measurable effect** | Stable choice when multiple cues co-occur; measurable lift on dual-cue cases |
| **Metric affected** | Classification accuracy |

### I4 — Known facts vs decision-critical missing vs irrelevant absence

| Field | Detail |
|---|---|
| **Observed V4 failure** | Missing-information score 37.5%; empty `missing_information` on TX002–TX003, TX005, TX008–TX010, TX012–TX013, TX015–TX017, TX019; TX016 empty/empty; TX020 partial paraphrase |
| **Operational risk** | Ops receive a narrative of the defect without a structured ask for the authoritative artefact needed to act |
| **V5 intervention** | Section defining `known_facts`, decision-critical `missing_information`, and irrelevant absences; mandatory mapping from invalid/outstanding/conflict/absent cues to missing artefacts |
| **Expected measurable effect** | Higher coverage of expected missing labels; fewer empty missing lists when defects are evidenced |
| **Metric affected** | Missing-information detection |

### I5 — Explicit escalation rules

| Field | Detail |
|---|---|
| **Observed V4 failure** | Escalation false negatives on TX005, TX007, TX008, TX011, TX018, TX020; high severity often paired with `escalation_required=false` |
| **Operational risk** | Material ambiguity, identity conflict, deadline pressure or insufficiency handled as routine follow-up |
| **V5 intervention** | Mandatory escalation triggers (insufficiency, contradictions, counterparty conflict, market deadline/holiday ISD gap, material ambiguity, multi-field absence) + severity/escalation consistency rule |
| **Expected measurable effect** | Reduce false-negative escalations on the six V4 misses without relying on qualitative wording alone |
| **Metric affected** | Escalation accuracy |

### I6 — Cross-field consistency validation before output

| Field | Detail |
|---|---|
| **Observed V4 failure** | Internal inconsistencies: TX007 type vs missing deadline; TX002/TX012 type vs next action; high severity + non-escalation; empty facts without insufficiency |
| **Operational risk** | Structured JSON looks complete but fields disagree, creating reviewer confusion and wrong routing |
| **V5 intervention** | Mandatory pre-output consistency checklist (evidence support, type↔action alignment, missing-list obligations, escalation rules, deadline/fail guards) |
| **Expected measurable effect** | Fewer self-contradictory records; secondary lift across classification, missing-info and escalation |
| **Metric affected** | Classification accuracy; missing-information detection; escalation accuracy |

### I7 — Prohibit same information as both known and missing

| Field | Detail |
|---|---|
| **Observed V4 failure** | Known-vs-missing inversion pattern: defect placed only in `known_facts` (e.g. “confirmation outstanding”, “SSI mismatch”) with empty missing list |
| **Operational risk** | Defect acknowledged but authoritative replacement not requested |
| **V5 intervention** | Explicit prohibition + required pattern: known = evidenced defect/outcome; missing = authoritative value still required |
| **Expected measurable effect** | Cleaner separation and more complete missing lists on conflict/outstanding cases |
| **Metric affected** | Missing-information detection |

### I8 — Evidence must support exception_type

| Field | Detail |
|---|---|
| **Observed V4 failure** | TX007 inferred `market_deadline` without deadline event evidence; TX001/TX018 chose fail/deadline classes not justified as root cause; TX016 used `other` with no exception mechanism |
| **Operational risk** | Unsupported inference drives wrong workflow |
| **V5 intervention** | Require evidence items that justify `exception_type`; discard unsupported candidate types |
| **Expected measurable effect** | Lower unsupported type selection; especially urgency≠deadline and symptom≠cause errors |
| **Metric affected** | Classification accuracy; unsupported-claim discipline (qualitative; flags already 0 in V4) |

### I9 — Fallback to insufficient_information + escalation

| Field | Detail |
|---|---|
| **Observed V4 failure** | TX016 → `other` with empty missing list; TX011 under-used insufficiency; TX020 insufficiency without escalation |
| **Operational risk** | Speculative residual class or normal data-fix path when enrichment/escalation is required |
| **V5 intervention** | Hard fallback criteria for insufficiency + mandatory escalation; prefer insufficiency over speculative `other` |
| **Expected measurable effect** | TX016/TX011/TX020 align to insufficiency/escalation expectations |
| **Metric affected** | Classification accuracy; escalation accuracy; missing-information detection |

---

## Requirement → intervention map

| Required V5 capability | Intervention IDs | Primary V4 failures addressed |
|---|---|---|
| 1. Explicit classification definitions | I1 | TX001, TX007, TX011, TX018 |
| 2. Root-cause over symptom | I2 | TX002, TX012 |
| 3. Dual-cue precedence | I3 | TX002, TX012, TX018 |
| 4. Known / decision-critical missing / irrelevant absence | I4 | Missing-info cohort (13 cases) |
| 5. Explicit escalation rules | I5 | TX005, TX007, TX008, TX011, TX018, TX020 |
| 6. Cross-field consistency validation | I6 | TX002, TX007, TX012, TX016 + severity/escalation mismatches |
| 7. No same item as known and missing | I7 | Known-vs-missing inversion pattern |
| 8. Evidence must support exception_type | I8 | TX001, TX007, TX016, TX018 |
| 9. Fallback to insufficiency/escalation | I9 | TX011, TX016, TX020 |

---

## Case-level expectation (for later measurement only)

Not executed yet. When V5 is run on the same 20 cases, these are the intended directional effects:

| Case | V4 error mode | V5 intended correction | Metrics |
|---|---|---|---|
| TX001 | `failed_settlement` | `data_quality` | classification |
| TX002 | `failed_settlement` + empty missing | `instruction_issue` + missing valid account | classification, missing-info |
| TX003 | empty missing | missing counterparty confirmation | missing-info |
| TX005 | no escalation; empty missing | escalate; missing deadline timestamp | escalation, missing-info |
| TX007 | `market_deadline`; no escalation | `data_quality`; escalate; missing deadline | classification, escalation, missing-info |
| TX008 | no escalation; empty missing | escalate; missing confirmed counterparty name | escalation, missing-info |
| TX009 | empty missing | missing valid message reference | missing-info |
| TX010 | empty missing | missing authoritative settlement account | missing-info |
| TX011 | `data_quality`; no escalation | `insufficient_information`; escalate | classification, escalation |
| TX012 | `failed_settlement`; empty missing | `instruction_issue` + missing correct SSI BIC | classification, missing-info |
| TX013 | empty missing | missing affirming broker response | missing-info |
| TX015 | empty missing | missing funding confirmation | missing-info |
| TX016 | `other`; empty missing | `insufficient_information` + missing trade id/details; escalate | classification, missing-info, escalation |
| TX017 | empty missing | missing authoritative LEI | missing-info |
| TX018 | `failed_settlement`; no escalation | `market_deadline` + missing new ISD; escalate | classification, escalation, missing-info |
| TX019 | empty missing | missing authoritative settlement method | missing-info |
| TX020 | no escalation; partial missing labels | escalate; missing exception facts / previous email content | escalation, missing-info |

---

## Non-changes (explicit)

- `engineered-prompt.md` — not modified  
- `test-set.jsonl` / frozen test-set-v1.0 — not modified  
- `releases/v4/**` — not modified  
- `evaluate.py` / scoring logic — not modified  
- `schema/engineered_output.schema.json` — not modified  
- provider configuration — not modified  

## How to select V5 later (no run performed now)

```bash
# default remains V4
python run_engineered.py

# select V5 when ready to measure
python run_engineered.py --prompt-version v5
# or: PROMPT_VERSION=v5 python run_engineered.py
```
