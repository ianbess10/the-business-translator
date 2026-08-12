# Evidence-Gated Decision Pipeline v1.6

## Status

**Implemented, tested, contract-lineage certified and frozen before regression.** No v1.6 regression execution or score exists.

## Operating design

v1.6 retains the approved Coverage and Evidence Rulebook and adds the approved Assurance Composition, Severity and Escalation Policy. Coverage state and evidence condition remain independent terminal facts. Their gap types, actions, routing and escalation roles are unioned deterministically, so partial coverage cannot suppress missing evidence or an adverse operating exception.

The model contracts are unchanged from v1.5:

- non-assurance cases use the inherited source-support contract; and
- entered assurance cases use the inherited bounded evidence-observation contract.

Mapping, assurance composition, severity, remediation and escalation remain deterministic. No mapping model call exists.

## Benchmark authority

Future evaluation uses benchmark authority v1.1, which inherits all v1.0 inputs and undisputed labels while applying the four independently adjudicated dual-axis expectations. The runner cannot load labels or the authority overlay. The evaluator verifies workflow version, dataset-authority version and freeze-manifest identity before writing any score.

## Certification decision

Neither provider-facing schema, prompt, request wrapper, endpoint nor model changed. Their exact hashes are inherited from v1.5 certification lineage, so no new provider call is required or permitted for this version. All changed behavior is deterministic and is tested offline.

## Pre-regression controls

- approved rulebook and assurance policy integrity;
- generic dual-axis, remediation-union and escalation-floor boundaries;
- provider-subset audit for both inherited schemas;
- exact provider-contract lineage hashes;
- 24 input paths and eight entered-assurance paths without label access;
- append-only ledger, quarantine and zero-retry behavior;
- evaluator self-test against benchmark authority v1.1; and
- freeze-manifest verification with no v1.6 result directory.

One later authorised regression may use at most 24 model calls. No retry, repair, fallback, tuning or hidden label access is permitted.

The frozen workflow passed all offline controls. Both provider contracts are byte-identical to their certified predecessors, so certification is inherited with zero new provider calls. Any change to a frozen artefact invalidates this status and requires a separately versioned workflow.
