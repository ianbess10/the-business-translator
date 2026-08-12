# Synthetic Regulatory Evaluation Dataset — Benchmark Authority v1.1

## Purpose

Version 1.1 is an immutable label-authority overlay on `SA-REG-BASELINE-001` v1.0. It publishes the outcome of the independent synthetic [coverage-versus-label adjudication](../../adjudications/coverage-label-v1.0/README.md) without editing the original inputs or labels.

It exists for future v1.6 development and evaluation only. It is not a retrospective score of v1.5.

## Inheritance

- All 24 frozen v1.0 inputs are inherited unchanged.
- All undisputed v1.0 label fields are inherited unchanged.
- Four entered-assurance cases receive adjudicated dual-axis expectations through `label-authority-overlay.json`.
- The original v1.0 labels remain the authority for the historical v1.5 score.

## Adjudicated cases

The overlay replaces the complete-mapping premise for `CON-006`, `CON-007`, `CON-011` and `CON-012` with partial coverage under rulebook v1.0. It separately preserves sufficient, missing or adverse evidence conditions and all concurrently required remediation actions.

The overlay does not define a v1.6 headline `assurance_outcome`. That output must be designed and tested only after the two authoritative dimensions and their actions are preserved.

## Integrity boundary

This directory contains benchmark authority, not workflow code. It must not be imported by a regression runner. A separately versioned evaluator may load it only after a terminal prediction record exists.

No v1.6 implementation, provider certification, freeze, execution or score is included here.
