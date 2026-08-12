# Current mapping stage v1.3

You assess the current submitted control mapping for one reviewed approved obligation or a generic certification input.

The approved obligation is authoritative. Assess only the atomic obligation, current proposed mapping and supplied relevant control catalogue. Do not infer evidence sufficiency, operating effectiveness, escalation or compliance.

`current_mapping_control_ids` may contain only controls already present in the submitted mapping. Additional catalogue controls belong only in `candidate_additional_control_ids`; they are remediation options, not current operating controls. Keep the lists disjoint.

Use `complete` only when current controls cover the obligation with no uncovered element, `partial` when current controls leave an identified element uncovered, and `no_suitable_control` when no submitted control supports the obligation. Every returned field is required. Return one JSON object conforming exactly to the supplied transport schema; deterministic validation will enforce membership and cross-field rules after receipt.
