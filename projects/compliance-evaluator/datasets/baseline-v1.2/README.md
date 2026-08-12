# Benchmark Authority v1.2

Version 1.2 is the complete, self-contained dual-axis authority for all eight frozen benchmark cases that enter control assurance. It supersedes evaluator fallback to baseline v1.0 labels and the partial v1.1 overlay for future workflow versions.

It does not alter the 24 frozen inputs, source-stage labels, rulebook, composition policy, or prior results. It is approved synthetic benchmark authority and is not production performance.

Required integrity controls:

- exactly eight unique entered-case records;
- exact identity match to `CON-005`–`CON-012`;
- explicit coverage and evidence conditions for every record;
- concurrent gaps and actions composed from the approved policy;
- no runtime access to this evaluation-only authority;
- fail closed on missing, duplicate, extra or invalid authority;
- no retrospective rescoring of v1.6 or earlier evidence.
