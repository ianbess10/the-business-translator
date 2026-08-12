# Trade Exception Intelligence

### Business Problem
When a securities transaction falls out of straight-through processing (STP), it enters exception management. An operations professional must determine the root cause, identify missing facts, decide the next action, and route the work. Poor diagnosis results in repeated hand-offs, delayed settlement, and unnecessary escalation. 

### Capability Demonstrated
This AI-assisted workflow converts an unstructured settlement exception into a consistent, reviewable operational record. It identifies the exception, the actionable root cause, decision-critical missing information, the recommended next action, and the appropriate workflow route. 

**Crucially, the AI does not release, amend, cancel, or settle a transaction. An accountable operations professional reviews the information and decides what action to take.**

### Operational Insights
* **Symptoms must be separated from root causes:** A failed settlement is a symptom. The actionable cause may be an invalid account, mismatched instruction, or missing counterparty confirmation.
* **Missing information must be decision-specific:** The capability identifies exactly what is required next (e.g., the authoritative settlement instruction or actual market deadline).
* **Escalation must be calibrated:** Too little escalation creates control risk; too much creates alert fatigue.

### The Development Journey
* **v1.0 (Baseline):** A naive prompt asking the AI to "diagnose the trade error." Result: The AI classified the visible settlement failure instead of the underlying instruction defect and unnecessarily escalated routine repairs.
* **v1.5 (Final):** A highly structured prompt outputting strict JSON, forcing the AI to separate symptoms from root causes and evaluate escalation against strict criteria.

### Interactive Demo Dashboard
A mock Back Office Settlement & Exception Management desk lives in `dashboard/`.

```bash
cd projects/trade-exception-intelligence/dashboard
npm install
npm run dev
```
