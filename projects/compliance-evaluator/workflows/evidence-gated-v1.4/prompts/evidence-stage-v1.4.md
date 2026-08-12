# Canonical evidence condition stage v1.4

Assess evidence for one reviewed approved obligation and one already validated current mapping. Treat the validated current mapping as fixed. This stage cannot add controls, remove controls or change mapping completeness.

Return exactly one canonical `evidence_assessment`. Use `missing_operating_evidence` when required completed records are absent. Use `design_deficiency` only when supplied material establishes a weakness in control design. Use `adverse_operating_evidence` only when supplied records establish an adverse operating indicator. Use `not_assessed_no_current_control` only when the validated mapping contains no current control. A documented policy or framework can evidence design without proving operation.

Do not separately classify design flags, adverse flags, severity, remediation, escalation or compliance. Those operating consequences are derived deterministically after validation. Every returned field is required. Return one JSON object conforming exactly to the supplied transport schema.
