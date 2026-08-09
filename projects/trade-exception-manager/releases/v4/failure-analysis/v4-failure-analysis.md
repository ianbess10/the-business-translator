# V4 Failure Analysis — OpenAI Engineered Run

**Status:** analysis only — no prompts, test cases, or model outputs were modified  
**Prompt version under test:** V4 (`engineered-prompt.md` / equivalent engineered system prompt used in the run)  
**Provider / model:** OpenAI `gpt-4o-mini`  
**Engineered run:** `results/engineered/20260808T142916Z/`  
**Evaluation report:** `results/evaluation/20260808T142952Z.json`  
**Test set artefact used for labels/inputs:** `test-set.jsonl` (20 synthetic cases)

## Measured scores (from evaluation report)

| Metric | Score |
|---|---:|
| Classification accuracy | 65% (13/20) |
| Missing-information detection | 37.5% |
| Escalation accuracy | 70% (14/20) |
| JSON schema compliance | 100% (20/20) |
| Unsupported-claim flags | 0 |

---

## A. Incorrectly classified cases (7)

### TX001

1. **Case ID:** TX001  
2. **Synthetic input:** Trade 1001 matched on price but settlement date is absent.  
3. **Expected classification:** `data_quality`  
4. **Actual classification:** `failed_settlement`  
5. **Model evidence/reasoning available in the output:**  
   - known_facts: `Trade 1001 matched on price`  
   - missing_information: `settlement date`  
   - evidence: restates the narrative (`...settlement date is absent`)  
   - recommended_next_action: obtain the missing settlement date  
   - escalation_required: false; confidence: 0.9; severity: high  
6. **Failure category:** Over-classification toward settlement failure when the evidenced defect is missing data.  
7. **Likely root cause:** The model anchors on “settlement” language and treats a blocked/incomplete settlement attribute as a failed settlement event, even while correctly identifying the missing date.  
8. **Potential operational consequence:** Exception routed to settlement-fail workflow instead of data remediation; wrong queue, delayed date capture, unnecessary fail-processing effort.  
9. **Problem appears to arise from:**  
   - **taxonomy ambiguity** (primary): boundary between `data_quality` and `failed_settlement` is thin when settlement is mentioned but no fail event is stated  
   - **prompt ambiguity** (secondary): taxonomy examples do not force “absence of attribute ≠ failed settlement”  
   - not primarily test-label ambiguity: label is consistent with “date absent”  
10. **Recommended intervention:** Add an explicit taxonomy rule: if the only evidenced defect is a missing/invalid field and no fail/unmatch/partial event is stated, classify as `data_quality` (or `insufficient_information` when multiple core fields are absent).

---

### TX002

1. **Case ID:** TX002  
2. **Synthetic input:** Trade 1002 failed because the receiving account is invalid.  
3. **Expected classification:** `instruction_issue`  
4. **Actual classification:** `failed_settlement`  
5. **Model evidence/reasoning available in the output:**  
   - known_facts: full narrative restated  
   - missing_information: `[]`  
   - evidence: `[]`  
   - recommended_next_action: verify/correct receiving account details  
   - escalation_required: false; confidence: 0.9; severity: high  
6. **Failure category:** Cause vs symptom inversion — outcome word “failed” dominates root-cause class.  
7. **Likely root cause:** Lexical primacy of “failed”; instruction/SSI defect is recognized in the action recommendation but not selected as `exception_type`.  
8. **Potential operational consequence:** Treated as a generic settlement fail rather than an SSI/account instruction repair; may miss standing-instruction data fix and repeat fails.  
9. **Problem appears to arise from:**  
   - **taxonomy ambiguity** (primary): `failed_settlement` vs `instruction_issue` when both fail outcome and instruction cause are present  
   - **multiple simultaneous exceptions** (secondary): fail event + invalid account  
   - **model reasoning failure** (secondary): action implies instruction fix, type ignores it  
10. **Recommended intervention:** Priority rule: when a fail is explicitly caused by invalid/mismatched settlement instructions (account, SSI, BIC, method), prefer `instruction_issue` over `failed_settlement`.

---

### TX007

1. **Case ID:** TX007  
2. **Synthetic input:** Narrative says settlement is urgent but gives no deadline.  
3. **Expected classification:** `data_quality`  
4. **Actual classification:** `market_deadline`  
5. **Model evidence/reasoning available in the output:**  
   - known_facts: `Settlement is urgent`  
   - missing_information: `Deadline for settlement`  
   - evidence: urgency stated, deadline not provided  
   - recommended_next_action: clarify the deadline  
   - escalation_required: false; confidence: 0.8; severity: high  
6. **Failure category:** Inferring a market-deadline exception from urgency language without an actual deadline event.  
7. **Likely root cause:** Semantic leap from “urgent” → deadline taxonomy, despite the model itself recording that no deadline exists.  
8. **Potential operational consequence:** False deadline escalation path; ops may chase market cut-off processes that are not evidenced, while the real need is to obtain timing data.  
9. **Problem appears to arise from:**  
   - **model reasoning failure** (primary): contradicts its own missing-deadline finding  
   - **taxonomy ambiguity** (secondary): `market_deadline` vs `data_quality` for urgency-without-deadline  
   - **prompt ambiguity** (secondary): insufficient negative examples for “urgent ≠ deadline miss”  
10. **Recommended intervention:** Hard rule: `market_deadline` requires an evidenced missed/approaching market deadline or holiday/cut-off event; urgency without a timepoint is `data_quality` / missing deadline.

---

### TX011

1. **Case ID:** TX011  
2. **Synthetic input:** Trade 1011 has no ISIN, quantity or settlement date in the free-text note.  
3. **Expected classification:** `insufficient_information`  
4. **Actual classification:** `data_quality`  
5. **Model evidence/reasoning available in the output:**  
   - known_facts: `Trade 1011 has been identified.`  
   - missing_information: `ISIN`, `quantity`, `settlement date` (good detection)  
   - evidence: free-text note indicates those fields are missing  
   - recommended_next_action: obtain the missing fields  
   - escalation_required: false; confidence: 0.9; severity: high  
6. **Failure category:** Underuse of `insufficient_information` when multiple core attributes are absent.  
7. **Likely root cause:** Model treats multi-field absence as ordinary data-quality remediation rather than “cannot proceed / insufficient to classify operationally.”  
8. **Potential operational consequence:** Case stays in normal data-fix queue instead of insufficient-info / enrich-before-action handling; overconfidence (0.9) despite sparse facts.  
9. **Problem appears to arise from:**  
   - **taxonomy ambiguity** (primary): `data_quality` vs `insufficient_information` overlap  
   - **prompt ambiguity** (secondary): when to choose insufficient_information is under-specified relative to multi-field absence  
   - **test-label ambiguity** (minor): both labels are defensible; expected label encodes a stricter “cannot analyse” stance  
10. **Recommended intervention:** Define a threshold rule: if two or more core trade attributes (e.g. ISIN, quantity, settlement date) are absent, use `insufficient_information` and escalate.

---

### TX012

1. **Case ID:** TX012  
2. **Synthetic input:** Trade 1012 failed settlement; SSI BIC does not match the standing instruction file.  
3. **Expected classification:** `instruction_issue`  
4. **Actual classification:** `failed_settlement`  
5. **Model evidence/reasoning available in the output:**  
   - known_facts: fail stated; SSI BIC mismatch stated  
   - missing_information: `[]`  
   - evidence: `Trade 1012`, `SSI BIC mismatch`  
   - recommended_next_action: review/correct SSI BIC in standing instruction file  
   - escalation_required: false; confidence: 0.9; severity: high  
6. **Failure category:** Same cause-vs-symptom pattern as TX002.  
7. **Likely root cause:** “Failed settlement” phrase selected as type despite explicit SSI root cause and SSI-corrective next action.  
8. **Potential operational consequence:** Fail recycling without durable SSI master-data correction; repeat settlement breaks.  
9. **Problem appears to arise from:**  
   - **taxonomy ambiguity** / **multiple simultaneous exceptions** (primary)  
   - **model reasoning failure** (secondary): action and type disagree  
10. **Recommended intervention:** Same priority rule as TX002; optionally require `exception_type` to reflect the actionable root cause named in `recommended_next_action`.

---

### TX016

1. **Case ID:** TX016  
2. **Synthetic input:** Please resolve immediately. Also the weather in London was rainy today.  
3. **Expected classification:** `insufficient_information`  
4. **Actual classification:** `other`  
5. **Model evidence/reasoning available in the output:**  
   - known_facts: `[]`  
   - missing_information: `[]`  
   - evidence: `Request to resolve immediately`  
   - recommended_next_action: investigate the request for immediate resolution  
   - escalation_required: true; confidence: 0.7; severity: high  
6. **Failure category:** Distractor / non-operational narrative not forced into insufficient-information.  
7. **Likely root cause:** Model recognizes emptiness (empty known_facts) but selects residual class `other` and fails to emit required missing fields (trade id / exception details). Weather distractor is ignored (good) but not converted into an explicit insufficiency record.  
8. **Potential operational consequence:** Vague “investigate urgently” work with no structured ask-back; escalated noise without actionable missing-data list.  
9. **Problem appears to arise from:**  
   - **prompt ambiguity** (primary): weak requirement to prefer `insufficient_information` when no trade exception facts exist  
   - **model reasoning failure** (secondary): empty facts but empty missing_information  
   - **insufficient context** (secondary): no trade record supplied beyond free text  
10. **Recommended intervention:** If no trade identifier and no exception mechanism are present, force `insufficient_information`, populate missing_information with trade identifier + exception details, and escalate.

---

### TX018

1. **Case ID:** TX018  
2. **Synthetic input:** Trade 1018 settlement postponed after market holiday; new intended settlement date not provided.  
3. **Expected classification:** `market_deadline`  
4. **Actual classification:** `failed_settlement`  
5. **Model evidence/reasoning available in the output:**  
   - known_facts: postponed after market holiday  
   - missing_information: `New intended settlement date`  
   - evidence: postponement due to market holiday  
   - recommended_next_action: obtain new intended settlement date  
   - escalation_required: false; confidence: 0.8; severity: medium  
6. **Failure category:** Market calendar / ISD postponement misread as settlement failure.  
7. **Likely root cause:** “Settlement postponed” interpreted as fail-like outcome; market-holiday cue underweighted relative to expected `market_deadline` label.  
8. **Potential operational consequence:** Wrong fail-processing path; missed market-calendar / ISD amendment handling; delayed new ISD chase may be under-prioritised (no escalation).  
9. **Problem appears to arise from:**  
   - **taxonomy ambiguity** (primary): postponed-for-holiday vs failed settlement  
   - **test-label ambiguity** (secondary): case also contains a missing-date `data_quality` element; `market_deadline` is a modelling choice  
   - **model reasoning failure** (secondary): holiday evidence present but type ignores it  
10. **Recommended intervention:** Map market holiday / cut-off / missed deadline language to `market_deadline`; keep missing new ISD in `missing_information` (which the model already did).

---

## B. Missing-information detection failures

Metric definition: coverage of each case’s `expected_missing_information` labels by model `missing_information` (partial credit per case). Aggregate score: **37.5%**.

### Case-by-case (score &lt; 1.0)

| Case | Expected missing | Predicted missing | Score | Notes |
|---|---|---|---:|---|
| TX002 | valid receiving account | _(empty)_ | 0.0 | Invalid account stated as known fact; not reframed as missing valid account |
| TX003 | counterparty confirmation | _(empty)_ | 0.0 | “Confirmation outstanding” placed in known_facts, not missing_information |
| TX005 | deadline timestamp | _(empty)_ | 0.0 | Deadline miss asserted; precise timestamp not requested |
| TX008 | confirmed counterparty name | _(empty)_ | 0.0 | Conflict stated; authoritative value not listed as missing |
| TX009 | valid message reference | _(empty)_ | 0.0 | Malformed reference known; valid replacement not listed as missing |
| TX010 | authoritative settlement account | _(empty)_ | 0.0 | Contradiction known; authoritative choice not listed as missing |
| TX012 | correct SSI BIC | _(empty)_ | 0.0 | Mismatch known; correct BIC not listed as missing |
| TX013 | affirming broker response | _(empty)_ | 0.0 | “No affirming broker response” in known_facts only |
| TX015 | funding confirmation | _(empty)_ | 0.0 | Funding failure known; confirmation artefact not requested |
| TX016 | trade identifier; exception details | _(empty)_ | 0.0 | Empty known_facts but also empty missing_information |
| TX017 | authoritative LEI | _(empty)_ | 0.0 | LEI conflict known; authoritative LEI not listed as missing |
| TX019 | authoritative settlement method | _(empty)_ | 0.0 | Contradictory methods known; authoritative method not listed as missing |
| TX020 | exception facts; previous email content | Details of trade 1020; Context of the previous email | 0.5 | Partial semantic match; “exception facts” not matched by scorer |

### Recurring missing-information patterns

1. **Known-vs-missing inversion (dominant):** The model often records that something is wrong/outstanding/mismatched in `known_facts`, then leaves `missing_information` empty. It describes the defect but does not emit the remediation artefact still needed (valid account, authoritative LEI, correct BIC, etc.).
2. **Conflict without authority ask:** TX008, TX010, TX017, TX019 state contradictions but do not ask for the authoritative value.
3. **Outcome completeness illusion:** When a fail/unmatch is narrated “completely,” the model assumes information is sufficient even though confirmatory artefacts are still missing (TX003, TX013, TX015).
4. **Vocabulary mismatch (scoring + prompt):** TX020 is conceptually close (`previous email` context) but label wording differs (`exception facts` / `previous email content`). Some misses may be partly evaluation-surface mismatch, not total misunderstanding.
5. **True emptiness failure:** TX016 is the clearest reasoning failure: no facts and no missing fields.

### Origins (missing-information)

| Origin | Role |
|---|---|
| Prompt ambiguity | Strong — prompt requires distinguishing missing_information but does not force “defect implies missing authoritative value” |
| Taxonomy ambiguity | Moderate — interacts with classification, less central here |
| Test-label ambiguity | Moderate — expected strings are specific; model paraphrases or omits |
| Insufficient context | Low/moderate — many cases are self-contained; labels expect operational artefacts not named verbatim |
| Model reasoning failure | Strong — especially empty missing lists despite clear gaps |
| Multiple simultaneous exceptions | Moderate — fail+instruction cases omit instruction artefact asks |

### Recommended intervention themes (not implemented)

- Require `missing_information` whenever narrative contains absent/invalid/outstanding/conflicting attributes.
- For conflicts, always ask for the authoritative value.
- Prohibit empty `missing_information` when `known_facts` is empty or when evidence mentions absence/mismatch.

---

## C. Escalation accuracy failures

Expected vs actual `escalation_required` mismatches: **6/20** (accuracy 70%). All observed errors are **false negatives** (expected true, predicted false). No false-positive escalations in this failure set.

| Case | Expected | Actual | Actual type | Model next action (summary) | Pattern |
|---|---|---|---|---|---|
| TX005 | true | false | market_deadline | Investigate missed deadline / corrective actions | Deadline pressure not escalated |
| TX007 | true | false | market_deadline | Clarify deadline | Ambiguity handled as routine clarify |
| TX008 | true | false | counterparty_issue | Verify/update counterparty name | Identity conflict not escalated |
| TX011 | true | false | data_quality | Obtain ISIN/qty/date | Multi-field gap treated as normal chase |
| TX018 | true | false | failed_settlement | Obtain new ISD | Holiday postponement + missing ISD not escalated |
| TX020 | true | false | insufficient_information | Request additional information | Explicit insufficiency without escalation |

### Recurring escalation patterns

1. **Under-escalation bias:** Every escalation miss is a miss toward `false`. V4 is conservative about human escalation.
2. **Action without authority gate:** Model often proposes a sensible next step (verify, obtain, clarify) but keeps `escalation_required=false`, treating human-needed judgment as ordinary ops follow-up.
3. **Severity ≠ escalation:** Several misses have severity `high` yet escalation false (TX005, TX007, TX011, TX020) — severity and escalation are decoupled in practice.
4. **Coupling to classification errors:** TX007, TX011, TX018 are also classification failures; wrong type may be steering non-escalation paths.
5. **Prompt rule under-applied:** Engineered rules say escalate on contradictory instructions, material ambiguity, or outside taxonomy — model escalates some contradictions (e.g. TX010/TX019 true) but not identity conflicts (TX008) or insufficiency (TX011/TX020).

### Origins (escalation)

| Origin | Role |
|---|---|
| Prompt ambiguity | Strong — escalation conditions are qualitative; no mandatory triggers for deadline / identity conflict / insufficiency |
| Taxonomy ambiguity | Moderate — wrong class can imply wrong escalation path |
| Test-label ambiguity | Moderate — expected escalation is assertive for market/identity/insufficiency cases |
| Insufficient context | Low |
| Model reasoning failure | Moderate — high severity + escalate-false inconsistency |
| Multiple simultaneous exceptions | Low/moderate |

### Recommended intervention themes (not implemented)

- Mandatory escalation triggers: market deadline miss/holiday ISD gap; counterparty identity/LEI conflict; insufficient_information; unresolved contradictory instructions.
- Consistency check: if severity is high/critical OR missing_information is non-empty for authoritative conflicts, default escalation true unless explicitly routine.

---

## D. Cross-cutting recurring patterns

1. **Symptom over root cause in `exception_type`**  
   “Failed” wording dominates TX002/TX012/TX018-style cases even when the actionable defect is instruction, SSI, or market calendar.

2. **Defect described, artefact not requested**  
   Strongest systemic issue: missing-information score 37.5%. The model narrates problems as known facts and under-populates `missing_information`.

3. **Conservative escalation**  
   All escalation errors are false negatives. The model prefers “ops can just follow up” over “needs qualified review now.”

4. **Internal inconsistency inside single outputs**  
   Examples: TX007 classifies `market_deadline` while listing deadline as missing; TX002/TX012 recommend instruction repairs while typing `failed_settlement`; TX016 has empty facts and empty missing list; high severity with false escalation.

5. **Overlap zones in the taxonomy**  
   Hottest boundaries:  
   - `failed_settlement` vs `instruction_issue`  
   - `data_quality` vs `insufficient_information`  
   - `data_quality` vs `market_deadline`  
   - postponement/holiday vs `failed_settlement`

6. **Schema success does not equal operational quality**  
   100% JSON compliance with material classification/missing/escalation errors — structure is solved; decision quality is not.

7. **No unsupported-claim problem in this run**  
   Fabrication is not the failing mode here; under-structuring and mis-typing are.

---

## E. Root-cause summary (ranked)

Ranked by importance for explaining V4’s measured gaps on this frozen 20-case run:

### 1. Prompt under-specification of decision rules (highest impact)
The V4 prompt defines fields and taxonomy but does not encode hard priority/escalation/missing-information rules that the failures require.  
**Explains:** missing-information collapse, escalation false negatives, several taxonomy boundary errors.

### 2. Taxonomy boundary ambiguity (very high impact)
Overlapping classes—especially fail-vs-instruction and data-quality-vs-insufficient/deadline—invite unstable choices when narratives contain both an outcome and a cause.  
**Explains:** TX001, TX002, TX007, TX011, TX012, TX018.

### 3. Model reasoning failures / local inconsistency (high impact)
Even with usable evidence in the same JSON object, the model sometimes chooses a conflicting type, omits obvious missing artefacts, or pairs high severity with no escalation.  
**Explains:** TX007 self-contradiction; TX016 empty/empty; severity–escalation mismatches.

### 4. Known-fact vs missing-information conceptual mix-up (high impact on the 37.5% metric)
Outstanding/invalid/conflicting items are treated as fully known facts rather than as signals that an authoritative value is still missing.  
**Explains:** most missing-information failures (TX003, TX008–TX010, TX012–TX013, TX015, TX017, TX019, etc.).

### 5. Multiple simultaneous exception cues (moderate–high)
Cases that state both a fail outcome and an instruction/market cause are resolved toward the outcome class.  
**Explains:** TX002, TX012, partly TX018.

### 6. Test-label / expected-string strictness (moderate)
Some disagreements are partly evaluative: `data_quality` vs `insufficient_information`, or paraphrase mismatches on missing-info labels (TX020). Labels are usable, but a few boundaries are intrinsically tight.  
**Explains:** portion of TX011/TX018/TX020 gap; not the main story.

### 7. Insufficient supplied context (lower for this set)
Most failures occur on self-contained synthetic narratives; lack of external trade records is material mainly for distractor/thin cases (TX016, TX020).

---

## F. What this analysis is not

- Not a prompt rewrite  
- Not a test-set relabel  
- Not a model rerun  
- Not an optimisation pass  

Next step (later): use this ranked root-cause list to design V5 interventions, then re-measure on the **same** 20 cases (`trade-exception-test-set-v1.0` / `test-set.jsonl`) and compute deltas against the V4 baseline.
