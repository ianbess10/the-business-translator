# Executive Summary — Regulatory Change & Obligation-to-Control Intelligence

## The operating challenge

Regulatory sources do not arrive as implementation-ready operating plans. Institutions must determine what changed, what applies, which obligations require action, how those obligations connect to controls and evidence, who owns the response, and what needs escalation. Fragmented hand-offs create delay, duplicated interpretation, uncertain ownership and weak auditability.

## What was built

An AI-assisted, evidence-gated decision pipeline that converts controlled source material into structured, reviewable regulatory-change and obligation-to-control decisions. AI prepares bounded analysis; approved rules determine coverage, severity, routing and escalation; qualified professionals remain accountable for interpretation, materiality, control adequacy, approval and closure.

## Why it matters

The capability is designed to improve:

- time from source publication to triage;
- time to initial impact assessment;
- correct first-time owner assignment;
- obligation-to-control mapping completeness;
- evidence completeness;
- false-positive and missed-gap rates;
- time to agreed disposition;
- overdue-action management; and
- cost per assessed source or obligation.

## What the build demonstrated

The initial baseline showed that structured AI output can still be operationally wrong: only 1 of 24 synthetic cases was fully correct, despite all responses conforming to the output format. Successive frozen versions exposed and addressed proposal anchoring, gate leakage, provider-contract failure, incomplete checkpointing, weak coverage authority, evidence conflation and escalation suppression.

The final v1.7 capability passed:

- **24/24** frozen regression cases, with zero quarantines, missed escalations or unnecessary escalations; and
- **16/16** separately frozen unseen synthetic holdout cases, again with zero quarantines, missed escalations or unnecessary escalations.

Every execution and evaluation occurred exactly once without tuning, retry, rerun or rescoring. These results are synthetic validation evidence, not production performance or a compliance conclusion.

## Executive conclusion

The project demonstrates that trustworthy AI-enabled regulatory operations depend less on increasingly elaborate prompts than on explicit business authority, evidence requirements, decision boundaries, accountable routing, controlled escalation and human approval.

> **AI is the enabler. Faster, traceable and accountable regulatory implementation is the product.**

The benchmark build is complete. The next step, if pursued, is a separately governed operational pilot using approved real-world sources and representative institution facts, measured against the operating baseline above.
