# Evidence-Gated Decision Pipeline v1.7

## Status

**Implemented, tested, contract-lineage certified and frozen before regression.** No v1.7 regression execution or score exists.

## Operating design

v1.7 retains the byte-identical v1.6 runtime and adds a complete evaluator-authority control. Coverage state and evidence condition remain independent terminal facts. Their gap types, actions, routing and escalation roles are unioned deterministically, so partial coverage cannot suppress missing evidence or an adverse operating exception.

The model contracts are unchanged from v1.5:

- non-assurance cases use the inherited source-support contract; and
- entered assurance cases use the inherited bounded evidence-observation contract.

Mapping, assurance composition, severity, remediation and escalation remain deterministic. No mapping model call exists.

## Benchmark authority

Evaluation uses complete benchmark authority v1.2 for all eight entered-assurance cases. No entered case may fall back to a legacy label. The evaluator fails closed on missing, duplicate, extra or invalid authority and verifies workflow version, dataset-authority version and freeze-manifest identity before writing any score. The runner cannot load labels or evaluation authority.

## Certification decision

Neither provider-facing schema, prompt, request wrapper, endpoint nor model changed. Their exact hashes are inherited from v1.5 certification lineage, so no new provider call is required or permitted for this version. All changed behavior is deterministic and is tested offline.

## Pre-regression controls

- approved rulebook and assurance policy integrity;
- generic dual-axis, remediation-union and escalation-floor boundaries;
- provider-subset audit for both inherited schemas;
- exact provider-contract lineage hashes;
- 24 input paths and eight entered-assurance paths without label access;
- append-only ledger, quarantine and zero-retry behavior;
- evaluator self-test against complete benchmark authority v1.2;
- missing, duplicate, extra and invalid authority boundary tests; and
- freeze-manifest verification with no v1.7 result directory.

One later authorised regression may use at most 24 model calls. No retry, repair, fallback, tuning or hidden label access is permitted.

The frozen workflow passed all offline controls. Both provider contracts are byte-identical to their certified predecessors, so certification is inherited with zero new provider calls. Any change to a frozen artefact invalidates this status and requires a separately versioned workflow.
