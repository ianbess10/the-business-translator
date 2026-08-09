# South African Regulatory Source Pack v1.0

## Purpose

This pack freezes the source metadata for the first synthetic evaluation of Regulatory Change & Obligation-to-Control Intelligence.

It is designed to test whether an AI-assisted workflow can correctly distinguish:

- legislation from guidance;
- an original instrument from its amendment chain;
- a final-issued instrument from a verified in-force instrument;
- current guidance from superseded guidance;
- a consultation draft from a binding requirement; and
- a regulatory strategy from an operational obligation.

## Pack identity

| Field | Value |
|---|---|
| Pack ID | `SA-REG-SOURCE-PACK-001` |
| Version | `1.0` |
| Status | frozen for schema and synthetic-baseline design |
| Verified | 9 August 2026 |
| Institution profile | `SA-IWM-SYN-001 v1.0` |
| Scope | South African AML/CFT and FSCA market conduct |
| Sources | 10 |

The [machine-readable manifest](manifest.json) is the authoritative pack record. The [freeze metadata](source-pack-v1.0.meta.json) records its integrity hash.

## Status-controlled inventory

| Source | Status in this pack | Permitted use |
|---|---|---|
| FIC Act 38 of 2001 | in force with amendments; supplied PDF is as enacted | Statutory anchor and amendment-control test; no current-obligation extraction from the as-enacted PDF |
| 2024 FIC Act booklet | official FIC publication explicitly labelled unofficial | Locator discovery and comparison only |
| Guidance Note 7B | current official guidance | Interpretive statements labelled as guidance; never promoted to legislation |
| Revised Guidance Note 7A | superseded by Guidance Note 7B | Historical and supersession test only |
| Directive 10 of 2026 | final issued; Gazette commencement not independently verified | Change-event and commencement-control test; no in-force conclusion |
| Draft Directive 12 | consultation draft | Watchlist and readiness test only |
| FAIS Act 37 of 2002 | in force with amendments; supplied PDF is as enacted | Statutory anchor and amendment-control test; no current-obligation extraction from the as-enacted PDF |
| General Code, Board Notice 80 of 2003 | in force as amended; supplied PDF is the original | Base-instrument and amendment-chain test; not a standalone current text |
| General Code Amendment, Government Notice 706 of 2020 | in force with staged commencement | Amendment-specific candidate obligations, subject to the commencement table and human interpretation |
| FSCA Regulatory Strategy 2025-2028 | regulatory strategy | Horizon and supervisory context only |

## Material control decisions

### Directive 10

The instrument is signed and dated 31 July 2026, but clause 7 states that it takes effect on publication in the Government Gazette. That Gazette publication was not independently verified during this freeze. Its machine status is therefore `final_issued_commencement_unverified`, and the evaluator must not call it in force.

### Draft Directive 12

The notice records the deadline as "Monday, 21 August 2026". The calendar date 21 August 2026 is a Friday. The pack preserves the source text, flags the weekday/date conflict and requires human resolution. It does not silently correct the regulator's notice.

### Guidance Note 7B

The version statement says Guidance Note 7B replaces Revised Guidance Note 7A, Guidance Note 7A and Guidance Note 7 from publication. All three predecessors are excluded from current interpretive use.

### Original Acts and base code

The Government source PDFs for the FIC Act, FAIS Act and Board Notice 80 are not consolidated current texts. They remain useful authority and lineage anchors, but a current obligation cannot be claimed from them without an approved amendment chain or reviewed consolidated source.

## Run-time admission gate

Before an evaluation uses a source:

1. retrieve it from the recorded official URL;
2. verify the SHA-256 hash against `manifest.json`;
3. confirm that the source status has not changed since 9 August 2026;
4. apply the source's permitted-use and extraction rules;
5. cite a precise source locator in every generated statement; and
6. route any date, version, applicability or source conflict to a qualified human reviewer.

A hash mismatch, unavailable source, later publication or changed status invalidates the frozen run until a new pack version is approved.

## Boundary

This pack is an evaluation artefact. It is not legal advice, a complete regulatory inventory or evidence of a real institution's compliance position. No external PDF is redistributed in this repository.
