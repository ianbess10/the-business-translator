# Coverage Rulebook versus Benchmark Labels — Independent Adjudication v1.0

## Decision

The approved Coverage and Evidence Rulebook is the authoritative coverage source for `CON-006`, `CON-007`, `CON-011` and `CON-012`.

Each case submits only one of the two complementary complaints controls. Each current mapping is therefore **partial**:

- `C-CON-006` covers establishment and operation but not maintenance and oversight; and
- `C-CON-007` covers maintenance and oversight but not establishment and operation.

The four complete-mapping expectations in frozen dataset v1.0 are not supported by the approved two-element coverage authority. They remain preserved as historical benchmark evidence and are not edited.

This is a synthetic governance adjudication for an educational portfolio. The reviewer identity and approval are fictional controls used to demonstrate separation of duties; they are not a real legal, regulatory or production-control opinion.

## Review independence

The adjudication is recorded under the synthetic **Compliance Monitoring Lead** role (`SYN-CML-001`), separate from:

- workflow implementation and evaluation;
- the original benchmark-label authoring function;
- the Complaints Manager and Conduct Risk control owners; and
- the Head of Compliance role that approved rulebook v1.0.

The reviewer assessed only the source obligation, approved obligation record, frozen control catalogue, approved rulebook and original label rationales. Frozen v1.5 predictions and scores were used to identify the disputed cases but not as authority for the determination.

## Authority hierarchy applied

1. source-supported atomic obligation;
2. approved obligation-element decomposition;
3. frozen control-design descriptions;
4. human-approved coverage assertions;
5. benchmark label rationale.

Benchmark labels measure a workflow; they cannot override approved business authority.

## Case determinations

| Case | Submitted current control | Coverage determination | Evidence condition | Required actions | Escalation |
|---|---|---|---|---|---|
| `CON-006` | `C-CON-006` | Partial | Sufficient | Mapping review | No |
| `CON-007` | `C-CON-006` | Partial | Missing operating evidence | Mapping review and evidence request | No |
| `CON-011` | `C-CON-006` | Partial | Adverse operating evidence | Mapping review and operating remediation | Conduct Risk Officer and Head of Compliance |
| `CON-012` | `C-CON-007` | Partial | Missing operating evidence | Mapping review and evidence request | No |

### `CON-006`

The original label correctly identifies `C-CON-006` and its Complaints Manager owner, but overstates that single control as complete coverage. `OEL-CON-MAINTAIN-001` remains uncovered. The supplied design and operating evidence is sufficient for the element that `C-CON-006` performs; that evidence does not expand control coverage.

### `CON-007`

The missing complaint register is a valid operating-evidence condition for `C-CON-006`. It coexists with partial coverage. The proportionate response is both a mapping review for the uncovered maintenance element and a routine evidence request, with no escalation absent adverse evidence.

### `CON-011`

The submitted control set remains partial, but the supplied register contains repeated overdue high-impact complaints and incomplete remediation. The adverse operating condition is high severity and requires operating remediation plus escalation to the Conduct Risk Officer and Head of Compliance. Partial coverage cannot suppress that consequence.

The escalation determination is approved here as a synthetic adjudication outcome. Before v1.6 freeze it must be expressed in separately versioned general policy authority, without case IDs or benchmark wording.

### `CON-012`

`C-CON-007` covers maintenance and oversight but not establishment and operation. The missing monthly customer-outcomes report is a routine missing-evidence condition. Both a mapping review and evidence request are required, with no escalation because no adverse condition is presented.

## Publication decision

The original dataset remains `SA-REG-BASELINE-001` v1.0 and is immutable. The approved determinations are published as [benchmark authority overlay v1.1](../../datasets/baseline-v1.1/README.md), which inherits all undisputed v1.0 labels and replaces only the four adjudicated expectations with dual-axis coverage and evidence states.

The overlay is for future v1.6 implementation and evaluation. It must not be applied retrospectively to v1.5, and no revised v1.5 score may be produced.

## Outcome

**Approved as synthetic benchmark authority. Pre-implementation adjudication is complete. v1.6 remains unimplemented, untested, unfrozen, unexecuted and unscored.**
