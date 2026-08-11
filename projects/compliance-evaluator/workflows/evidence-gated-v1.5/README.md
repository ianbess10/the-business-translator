# Evidence-Gated Decision Pipeline v1.5

## Status

**Rulebook approved; workflow implemented, tested, provider-certified and frozen before regression.** No v1.5 regression execution or score exists.

## Operating design

v1.5 moves mapping authority out of model inference. A human-approved [Coverage and Evidence Rulebook](../../rulebooks/coverage-evidence-v1.0/README.md) decomposes the approved complaints-framework obligation, links controls to mandatory elements and defines typed design and operating-evidence requirements.

Current mapping completeness is calculated deterministically from submitted control membership and approved coverage assertions. Missing authority quarantines the case; the workflow does not infer coverage from control names.

The model performs one bounded task for entered assurance: match each supplied evidence item to an allowed requirement and report its observed state. Deterministic policy derives evidence assessment, mapping outcome, severity, remediation and escalation.

## Integrity boundary

The rulebook was authored from the approved obligation, source locator and frozen control descriptions. Its approval explicitly prohibits benchmark case IDs, evidence IDs, labels and case exceptions. The complementary controls cover distinct mandatory elements; this operating judgment was not altered to reproduce observed regression labels.

## Certification and tests

- rulebook approval, element/control completeness and anti-case-identity checks pass;
- deterministic mapping covers complete and partial control combinations;
- typed evidence tests distinguish design deficiency, missing operating evidence and adverse indicators;
- inherited source schema and prompt exactly match their v1.3 certification hashes;
- the changed nested evidence-observation schema passed one non-benchmark provider certification;
- provider-subset, 24-path routing, append-only ledger, zero-retry quarantine and evaluator self-tests pass; and
- the freeze manifest permits no regression result directory or rerun.

## Future execution

One future authorised regression may use at most 24 model calls: 16 source/support calls and eight evidence-observation calls. Mapping uses zero model calls. No retry, repair, fallback or hidden label access is permitted.

Any result remains synthetic regression evidence, not independent validation or production performance.
