# Trade Exception Intelligence — Executive Summary

## The proposition

Trade Exception Intelligence is an AI-assisted capability that helps financial-markets operations teams turn unstructured settlement exceptions into clear, reviewable and appropriately routed actions.

> **AI is the enabler. The operating outcome is the product.**

## The operating challenge

When a transaction leaves straight-through processing, an operations professional must establish what happened, identify the root cause, determine what information is missing, decide what should happen next and judge whether escalation is required.

This interpretation work is necessary but costly. Inconsistent diagnosis can create additional touches, incorrect routing, settlement delay, operational risk and unnecessary senior intervention. Missed escalation can leave time-critical or control-sensitive breaks without appropriate attention.

## The capability

The prototype converts a free-text exception into a structured record containing:

- known facts and supporting evidence;
- the operational exception and actionable root cause;
- decision-critical missing information;
- a recommended next action;
- proposed routing and escalation treatment; and
- an explicit hand-off to an accountable operations professional.

It does not settle, release, amend or cancel transactions. It reduces the interpretation burden before a qualified professional decides and acts.

## The operational lesson

Initial testing showed that technically valid output can still be operationally wrong. An AI can produce perfect structured data while selecting the wrong queue, describing a symptom instead of its cause, omitting the authoritative information required for resolution or escalating routine work.

This means control design must extend beyond output format. The capability must be evaluated against the operational decisions it influences and the consequences of getting them wrong.

## How value should be measured

The production business case should be tested through:

- time to diagnose;
- touches per exception;
- correct first-time routing;
- time to resolution;
- unnecessary and missed escalation rates;
- straight-through-processing and exception rates; and
- cost per exception.

These measures should be accompanied by control indicators such as human overrides, unsupported claims, repeat breaks and performance by exception category.

## Evidence boundary

V5 was tested once against a separately frozen set of 30 synthetic cases after development on the original 20-case regression set. The independent holdout produced:

- 73.3% classification accuracy;
- 68.3% decision-critical missing-information detection;
- 80.0% escalation accuracy;
- 100.0% escalation recall, with no missed escalation;
- 100.0% structured-output compliance; and
- no detected unsupported claims.

The result also produced six unnecessary escalations and several incorrect routing classifications. V5 is therefore retained as the completed portfolio prototype, not presented as production-ready or ready for an operational pilot.

These figures are synthetic benchmark evidence, not production performance or evidence of realised business benefit. Any move toward operational adoption would require a targeted calibration intervention, a new independent validation set and then representative-case testing with expert review and clear authority boundaries.

## What this case study demonstrates

Trade Exception Intelligence demonstrates how domain expertise can translate an AI model into a governed operational capability: begin with the decision, make expert judgement explicit, test operational failure modes, retain human accountability and measure the outcome that matters.

[View the full case study and supporting evidence](README.md).
