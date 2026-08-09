# V4 Failure Analysis

**Prompt:** `v4` (`prompts/engineered-v4.md`)  
**Test set:** `trade-exception-test-set-v1.0` (exactly 20 cases)  
**Reference:** `benchmarks/v4-reference.json`  
**Source run:** engineered `20260808T142916Z` / evaluation `20260808T142952Z`  
**Model:** OpenAI `gpt-4o-mini`, temperature `0`

## Measured V4 baseline

| Metric | Score |
|---|---:|
| Classification accuracy | **65%** |
| Missing-information detection | **37.5%** |
| Escalation accuracy | **70%** |
| JSON schema compliance | 100% |
| Unsupported-claim flags | 0 |

These scores are the controlled baseline for V5+. Future prompt versions must be re-run on the **same 20 cases** before claiming improvement.

## Controlled iteration loop

```text
V4 measured on trade-exception-test-set-v1.0
        ↓
Failure analysis (this document)
        ↓
V5 prompt revision
        ↓
Same 20 cases (trade-exception-test-set-v1.0)
        ↓
Measured difference vs V4
```

## Classification failures (7/20)

| Case | Predicted | Expected | Pattern |
|---|---|---|---|
| TX001 | failed_settlement | data_quality | Overweights “settlement” language when the real issue is missing date |
| TX002 | failed_settlement | instruction_issue | Treats invalid account as settlement failure rather than instruction defect |
| TX007 | market_deadline | data_quality | Infers deadline class from “urgent” without an actual deadline |
| TX011 | data_quality | insufficient_information | Under-uses insufficient_information when multiple core fields are absent |
| TX012 | failed_settlement | instruction_issue | SSI/BIC mismatch classified as failed settlement |
| TX016 | other | insufficient_information | Distractor narrative not forced into insufficient_information |
| TX018 | failed_settlement | market_deadline | Holiday/postpone case missed as market deadline |

### V5 design implications
- Strengthen taxonomy disambiguation: `data_quality` vs `failed_settlement` vs `instruction_issue`.
- Require `insufficient_information` when trade identity or core settlement attributes are absent.
- Treat urgency-without-deadline as missing data, not `market_deadline`.

## Missing-information gaps (13/20 incomplete)

Common miss: model returns empty `missing_information` even when the narrative clearly lacks an operational detail.

High-priority misses:
- TX002 valid receiving account
- TX003 / TX013 counterparty or broker confirmation
- TX005 deadline timestamp
- TX008 / TX017 authoritative counterparty identity (name / LEI)
- TX009 valid message reference
- TX010 / TX019 authoritative instruction when contradictions exist
- TX012 correct SSI BIC
- TX015 funding confirmation
- TX016 / TX020 exception facts on thin or distractor narratives

### V5 design implications
- Add explicit “if X is mentioned as absent/invalid/conflicting, emit X in `missing_information`”.
- Prohibit empty `missing_information` when evidence is incomplete or contradictory.
- Give examples of acceptable missing-field labels aligned to the test-set vocabulary.

## Escalation under-firing (6/20)

| Case | Predicted | Expected | Pattern |
|---|---|---|---|
| TX005 | false | true | Market deadline not escalated |
| TX007 | false | true | Ambiguous urgency not escalated |
| TX008 | false | true | Counterparty conflict not escalated |
| TX011 | false | true | Severe information gap not escalated |
| TX018 | false | true | Market holiday / missing new ISD not escalated |
| TX020 | false | true | Empty/referential narrative not escalated |

### V5 design implications
- Make escalation mandatory for: contradictory instructions, identity conflicts, market deadline pressure, and insufficient information.
- Keep non-escalation only for routine, fully evidenced operational follow-ups.

## What must stay fixed for V5 measurement

1. Test set ID: `trade-exception-test-set-v1.0`
2. Case count: 20 (`TX001`–`TX020`)
3. Metrics: same `evaluate.py` definitions
4. Comparable model settings unless the experiment intentionally changes model (record that change separately)
5. Compare with:

```bash
python compare_evals.py \
  --baseline benchmarks/v4-reference.json \
  --candidate results/evaluation/<new_eval_id>.json
```
