# Evidence-Gated Decision Pipeline v1.5 — Regression Results

> Synthetic frozen regression evidence; not independent validation or production performance.

## Controlled execution

Frozen v1.5 was executed exactly once against all 24 frozen cases and its complete terminal-case record was evaluated exactly once. No tuning, repair, retry, rerun or rescoring occurred.

- Terminal cases: **24/24**
- Completed cases: **24**
- Quarantined cases: **0**
- API calls: **24/24 maximum**
- Retry count: **0**
- Tuning after observation: **false**
- Model: `gpt-4o-mini-2024-07-18`

## Result

- End-to-end exact: **20/24 (83.33%)**
- AML/CFT: **12/12 (100%)**
- Market conduct: **8/12 (66.67%)**
- Release gates passed: **9/15**
- Release decision: **failed**

Source use, obligation outcome, applicability, the assurance gate, control identity and owner routing were exact across all 24 cases. Escalation precision was **100%** with no unnecessary escalations, but recall was **83.33%** because one mandatory escalation was missed.

The four non-exact cases were `CON-006`, `CON-007`, `CON-011` and `CON-012`. Their mismatches are concentrated in deterministic mapping completeness and its downstream assurance, gap and remediation decisions. `CON-011` also missed the required escalation. These differences must remain visible until a separately versioned failure analysis determines whether they represent workflow defects, benchmark-label conflict with the approved rulebook, or both.

## Evidence integrity

The generated comparison and report heading retain the inherited evaluator's `v1.4` lineage label. The scored payload, run state and evaluation identity all identify workflow v1.5. This metadata defect was preserved after the one evaluation and was not repaired through rescoring.

The next stage is a case-level v1.5 failure analysis and a separately versioned next-workflow decision. v1.5 must not be modified, rerun or rescored.
