# V5 Evaluation Analysis

**Status:** measured run analysis — no prompts, test cases, schema or evaluator modified in this step  
**Prompt version:** V5 (`engineered-prompt-v5.md`)  
**Test set:** `trade-exception-test-set-v1.0` (same 20 cases as V4 freeze)  
**Provider / model:** OpenAI `gpt-4o-mini`, temperature `0`  
**Engineered run:** `results/engineered/20260809T075928Z/`  
**Evaluation report:** `results/evaluation/20260809T080010Z.json`  
**V4 baseline:** `releases/v4/evaluation/v4-reference.json`  
**Intervention map:** `methodology/v4-to-v5-interventions.md`

> Note: the evaluation JSON top-level `prompt_version` field reflects evaluator process defaults (`v4`) in this report; the engineered **run meta** correctly records `prompt_version=v5` and `prompt_file=engineered-prompt-v5.md`. Analysis below trusts run meta + outputs.

---

## 1. Headline results vs frozen V4

| Metric | V4 | V5 | Δ |
|---|---:|---:|---:|
| Classification accuracy | 65% | **90%** | **+25 pp** |
| Missing-information detection | 37.5% | **80%** | **+42.5 pp** |
| Escalation accuracy | 70% | **75%** | **+5 pp** |
| JSON schema compliance | 100% | 100% | 0 |
| Unsupported-claim flags (total) | 0 | 1 | +1 |
| Unsupported-claim rate | 0.00 | 0.05 | +0.05 |

**Interpretation:** V5 delivered large gains where V4 was weakest (classification boundaries and missing-information structuring). Escalation improved only modestly because false-negative under-escalation was largely fixed, then partly replaced by false-positive over-escalation.

---

## 2. Did the intended interventions work?

| Intervention | Intent | Observed effect |
|---|---|---|
| I1 Explicit definitions | Reduce taxonomy boundary errors | Mostly yes — TX011/TX016/TX018 corrected; TX001/TX007 still wrong but shifted toward insufficiency rather than fail/deadline |
| I2 Root-cause over symptom | Prefer instruction/SSI over “failed” | Yes — TX002, TX012 now `instruction_issue` |
| I3 Dual-cue precedence | Stabilise fail+cause / holiday cases | Yes — TX002/TX012/TX018 fixed |
| I4 Decision-critical missing info | Raise missing-info coverage | Strong yes — 37.5% → 80%; 9 prior miss cases fully fixed |
| I5 Explicit escalation triggers | Fix false-negative escalations | Partially — all 6 V4 under-escalations fixed, but 5 new over-escalations appeared |
| I6 Cross-field consistency | Reduce self-contradiction | Improved type↔action alignment on instruction cases; remaining issues are rule over-firing |
| I7 Known ≠ missing | Stop known/missing inversion | Largely yes on conflict/outstanding cases |
| I8 Evidence supports type | Block unsupported inference | TX007 no longer falsely `market_deadline`; residual issue is over-use of insufficiency |
| I9 Insufficiency fallback | Prefer insufficiency over guess/`other` | Yes for TX016/TX011; over-applied on TX001/TX007 |

---

## 3. Classification: fixed, remaining, new

### Fixed vs V4 (5)

| Case | V4 | V5 | Comment |
|---|---|---|---|
| TX002 | `failed_settlement` | `instruction_issue` | Root-cause precedence worked |
| TX011 | `data_quality` | `insufficient_information` | Multi-field absence rule worked |
| TX012 | `failed_settlement` | `instruction_issue` | SSI root-cause precedence worked |
| TX016 | `other` | `insufficient_information` | Fallback worked |
| TX018 | `failed_settlement` | `market_deadline` | Holiday/deadline mapping worked |

### Remaining (2) — no new classification misses

#### TX001
- **Input:** Trade 1001 matched on price but settlement date is absent.  
- **Expected:** `data_quality`  
- **Actual:** `insufficient_information`  
- **Output signals:** missing `settlement date`; evidence restates narrative; escalates.  
- **Failure mode:** Over-trigger of insufficiency fallback on a **single** clear field defect.  
- **Likely cause:** V5 insufficiency criteria / conservative fallback dominate the `data_quality` definition.  
- **Operational consequence:** Case may enter enrich/escalate path instead of routine data-quality remediation.  
- **Origin:** prompt rule over-breadth (insufficiency), not model invention.

#### TX007
- **Input:** Narrative says settlement is urgent but gives no deadline.  
- **Expected:** `data_quality`  
- **Actual:** `insufficient_information`  
- **Output signals:** missing `deadline timestamp`; escalates; correctly avoids `market_deadline`.  
- **Failure mode:** Right avoidance of unsupported deadline class; wrong final label vs expected single-field data-quality.  
- **Likely cause:** Material-ambiguity → insufficiency path is stronger than “urgent without deadline = data_quality”.  
- **Operational consequence:** Higher-touch escalation for a clarify-deadline task.  
- **Origin:** prompt precedence / fallback tension with test label.

**Pattern:** Remaining classification errors are **not** the old fail/deadline symptom errors. They are over-conservative insufficiency substitutions for single-gap `data_quality` cases.

---

## 4. Missing-information detection

Aggregate: **80%** (was 37.5%).

### Fixed vs V4 (9)
TX002, TX003, TX008, TX009, TX010, TX012, TX013, TX016, TX017 — previously empty or inverted missing lists now emit decision-critical artefacts (valid account, confirmations, authoritative identity/SSI values, etc.).

### Remaining incomplete (4)

| Case | Expected missing | Predicted | Score | Diagnosis |
|---|---|---|---:|---|
| TX005 | deadline timestamp | `[]` | 0.0 | Correct `market_deadline` + escalate, but does not ask for precise timestamp once miss is asserted |
| TX015 | funding confirmation | `[]` | 0.0 | Treats cash-not-available fail as informationally complete |
| TX019 | authoritative settlement method | `[]` | 0.0 | Correct contradiction class + escalate, but omits authoritative-method ask |
| TX020 | exception facts; previous email content | `trade identifier`, `exception details` | 0.0 | Semantically close; vocabulary mismatch vs expected labels (also saw partial-credit issues in V4) |

### Patterns
1. **Conflict/outstanding artefact asks largely solved** (biggest V4 gap).  
2. **Residual misses are either:**  
   - outcome-complete illusion (TX005, TX015), or  
   - contradiction without explicit authority ask (TX019), or  
   - label paraphrasing (TX020).  
3. No new missing-info regressions vs V4 incomplete set.

---

## 5. Escalation accuracy

Aggregate: **75%** (was 70%).

### V4 under-escalations: all fixed
TX005, TX007, TX008, TX011, TX018, TX020 now escalate when expected.

### New over-escalations (5) — expected false, predicted true

| Case | Type | Why V5 likely escalated | Expected label stance |
|---|---|---|---|
| TX001 | `insufficient_information` | Insufficiency rule forces escalate | Routine single-field data gap → no escalate |
| TX002 | `instruction_issue` | Invalid account / high severity path | Routine instruction repair → no escalate |
| TX003 | `unmatched_trade` | Outstanding confirmation treated as escalate | Standard unmatched chase → no escalate |
| TX012 | `instruction_issue` | SSI mismatch / high severity | Routine SSI correction → no escalate |
| TX013 | `unmatched_trade` | Missing affirming broker response | Standard unmatched chase → no escalate |

### Pattern
V5 corrected the V4 **under-escalation bias** by introducing an **over-escalation bias** on otherwise class-correct routine cases. Net escalation accuracy only +5 pp because gains and new false positives nearly offset.

This is the main V5 trade-off: safer human gating vs alert fatigue / unnecessary senior review.

---

## 6. Unsupported claims

- **Total flags:** 1 (TX017: `lei counterparty`)  
- V4 had 0.  
- Likely a tokenisation/false-positive from claim scanner on LEI/counterparty wording rather than a fabricated identifier (classification and missing-info for TX017 are otherwise correct).  
- Not a systemic fabrication regression, but worth monitoring.

---

## 7. Case scoreboard (V5)

| Case | Class OK | Predicted | Expected | Missing score | Escalation OK | Notes |
|---|---|---|---|---:|---|---|
| TX001 | No | insufficient_information | data_quality | 1.0 | No (over) | Over-fallback |
| TX002 | Yes | instruction_issue | instruction_issue | 1.0 | No (over) | Class/missing win |
| TX003 | Yes | unmatched_trade | unmatched_trade | 1.0 | No (over) | Missing win |
| TX004 | Yes | partial_settlement | partial_settlement | 1.0 | Yes | Stable |
| TX005 | Yes | market_deadline | market_deadline | 0.0 | Yes | Missing timestamp gap |
| TX006 | Yes | failed_settlement | failed_settlement | 1.0 | Yes | Stable |
| TX007 | No | insufficient_information | data_quality | 1.0 | Yes | Avoided false deadline |
| TX008 | Yes | counterparty_issue | counterparty_issue | 1.0 | Yes | Fixed V4 miss+esc |
| TX009 | Yes | data_quality | data_quality | 1.0 | Yes | Fixed missing |
| TX010 | Yes | instruction_issue | instruction_issue | 1.0 | Yes | Fixed missing |
| TX011 | Yes | insufficient_information | insufficient_information | 1.0 | Yes | Fixed class+esc |
| TX012 | Yes | instruction_issue | instruction_issue | 1.0 | No (over) | Class/missing win |
| TX013 | Yes | unmatched_trade | unmatched_trade | 1.0 | No (over) | Missing win |
| TX014 | Yes | partial_settlement | partial_settlement | 1.0 | Yes | Stable |
| TX015 | Yes | failed_settlement | failed_settlement | 0.0 | Yes | Missing funding conf |
| TX016 | Yes | insufficient_information | insufficient_information | 1.0 | Yes | Fixed distractor |
| TX017 | Yes | counterparty_issue | counterparty_issue | 1.0 | Yes | 1 claim flag |
| TX018 | Yes | market_deadline | market_deadline | 1.0 | Yes | Fixed class+esc |
| TX019 | Yes | instruction_issue | instruction_issue | 0.0 | Yes | Missing authority method |
| TX020 | Yes | insufficient_information | insufficient_information | 0.0 | Yes | Label paraphrase miss |

---

## 8. Root-cause summary for remaining V5 gaps (ranked)

1. **Insufficiency / escalation over-firing (highest residual risk)**  
   Rules that fixed V4 under-escalation and unsupported inference now escalate (and sometimes reclassify) routine single-defect or standard chase cases (TX001/TX002/TX003/TX012/TX013; class impact on TX001/TX007).

2. **Authority-ask still incomplete on a minority of contradictions/outcomes**  
   TX019 omits authoritative settlement method; TX005/TX015 omit confirmatory artefacts after an outcome is stated.

3. **Expected-label vocabulary mismatch**  
   TX020 predicts useful missing fields (`trade identifier`, `exception details`) that do not match expected strings (`exception facts`, `previous email content`).

4. **Minor claim-scanner noise**  
   TX017 single unsupported-claim flag; not evidence of broad hallucination.

---

## 9. What V5 proves on the frozen set

On **exactly the same 20 cases**:

- Decision-control interventions produced **large, measured** gains in classification (+25 pp) and missing-information detection (+42.5 pp).  
- Schema quality remained perfect.  
- Escalation quality improved slightly, but the error type flipped from under- to over-escalation.  
- Remaining classification misses are a narrower, more conservative failure mode than V4’s symptom/root-cause inversions.

## 10. Implications for any later V6 (analysis only — not implemented)

If a next version is warranted, evidence points to:

1. Tighten insufficiency: single missing field with clear trade context → `data_quality`, not `insufficient_information` (TX001/TX007).  
2. Narrow mandatory escalation: keep triggers for identity conflict, true insufficiency, market-deadline pressure, unresolved contradictions; exclude routine unmatched confirmation chase / simple SSI repair unless severity/criticality thresholds say otherwise.  
3. Keep authority-ask rule but add explicit examples for settlement-method conflicts and post-outcome confirmations (TX019/TX015/TX005).  
4. Optionally align missing-info phrasing examples with test-set vocabulary for thin narratives (TX020), without changing the frozen labels.

No V6 prompt was created in this analysis step.
