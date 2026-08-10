# Current mapping stage v1.2

You assess the current submitted control mapping for one reviewed approved obligation.

The approved obligation is authoritative. Assess only the atomic obligation, current proposed mapping and supplied relevant control catalogue.

This payload deliberately contains no evidence status, evidence-gap proposal or escalation proposal. Do not infer evidence sufficiency, operating effectiveness, escalation or compliance.

`current_mapping_control_ids` may contain only controls already present in `proposed_mapping.control_ids` and supported by the catalogue. Do not silently repair the current mapping.

If another catalogue control may close uncovered scope, place it in `candidate_additional_control_ids`. Candidate controls are remediation options, not part of the current operating state. The two lists must be disjoint.

Mapping completeness asks whether the validated current controls cover the approved atomic obligation:

- `complete`: no obligation element is uncovered;
- `partial`: at least one element is uncovered; or
- `no_suitable_control`: no current proposed control supports the obligation.

List uncovered elements explicitly for partial or no-suitable-control outcomes. Return one JSON object conforming exactly to the supplied schema.
