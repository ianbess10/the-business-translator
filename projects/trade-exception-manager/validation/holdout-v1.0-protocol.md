# V5 Independent Operational Holdout Protocol

## Purpose

Determine whether the frozen V5 capability generalises to 30 previously unused synthetic settlement exceptions without further prompt tuning.

This is a one-time prototype validation. It is not production performance and does not demonstrate realised business benefit.

## Frozen inputs

- Prompt: `engineered-prompt-v5.md`
- Holdout: `datasets/trade-exception-holdout-v1.0.jsonl`
- Model: OpenAI `gpt-4o-mini`
- Temperature: `0`
- Runs: one complete run
- Schema: `schema/engineered_output.schema.json`

Freeze hashes:

| Artefact | SHA-256 |
|---|---|
| V5 prompt | `b09dd331458639ecae180e9174f76ed9bec9faece909fb6b9327cf440dfa9854` |
| Holdout JSONL | `d158010cea68c5a9e09a262edf926134fa6ac2567afe49ad9cb3bbb1e976a610` |
| Output schema | `b95916dab2cd91e1d0ebb79c67381fd2716d9630caff0fd40d3f2bdcc2a30a1d` |

The prompt and holdout must not be altered after the holdout metadata hash is recorded. If execution fails for a technical reason before complete outputs are produced, record the failure and rerun only after documenting why it did not constitute an evaluable run.

## Operational questions

1. Did the capability identify the actionable root cause rather than the visible symptom?
2. Did it request the authoritative information required for the next decision?
3. Did routine repairs remain in normal operations handling?
4. Did time-critical, contradictory or genuinely insufficient cases escalate?
5. Were any unsupported facts introduced?

## Measures

Report:

- classification accuracy;
- missing-information detection;
- JSON schema compliance;
- unsupported-claim flags;
- escalation accuracy, precision and recall;
- escalation true positives, false positives, true negatives and false negatives; and
- case-level operational consequences for every error.

The primary residual-risk assessment is the balance between missed escalations and unnecessary escalations. Aggregate accuracy alone is insufficient.

## Execution

From `projects/trade-exception-manager`, configure `.env` with a valid API key and:

```dotenv
MODEL_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0
PROMPT_VERSION=v5
TEST_SET_PATH=datasets/trade-exception-holdout-v1.0.jsonl
RUN_LABEL=holdout-v1
```

Then run exactly once:

```bash
python run_engineered.py --prompt-version v5
python evaluate.py --variant engineered
```

Capture the generated run directory and evaluation report in the final analysis.

## Decision rule

- **Retain V5 and close prompt development:** no systematic operational weakness appears, missed escalation risk is acceptable for a human-reviewed prototype, and errors can be managed through workflow controls.
- **Make one targeted intervention:** a repeated failure pattern affects routing, decision-critical evidence or escalation treatment across multiple cases.
- **Do not progress toward operational pilot:** unsupported claims, material missed escalations or inconsistent decisions indicate that the capability is not ready for representative-case testing.

Whatever the result, do not tune V5 on this holdout and then claim the revised version passed an independent test. A revised capability requires a new, separately frozen holdout.

## Current status

**Prepared and frozen; genuine model run pending.** The offline mock-provider wiring check completed successfully but is not validation evidence and its scores must not be published as V5 performance.
