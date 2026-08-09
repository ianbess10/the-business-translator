from __future__ import annotations

import json
import re
from typing import Any

from src.providers.base import GenerationRequest, GenerationResult, ModelProvider

TYPE_RULES: list[tuple[str, list[str]]] = [
    ("partial_settlement", ["partially settled", "partial settlement", "remaining quantity"]),
    ("failed_settlement", ["failed settlement", "failed because", "insufficient securities", "cash funding"]),
    ("unmatched_trade", ["unmatched", "allegement", "confirmation outstanding"]),
    ("market_deadline", ["deadline", "market holiday", "cut-off", "missed market"]),
    ("counterparty_issue", ["counterparty", "lei"]),
    ("instruction_issue", ["receiving account", "settlement account", "ssi", "instruction", "deliver free", "delivery versus payment"]),
    ("data_quality", ["absent", "malformed", "no deadline", "settlement date is absent"]),
    ("insufficient_information", ["see previous email", "weather", "no isin", "no attached facts", "gives no"]),
]


class MockProvider(ModelProvider):
    """Deterministic local provider for reproducible offline runs."""

    name = "mock"

    def generate(self, request: GenerationRequest) -> GenerationResult:
        if request.expect_json:
            payload = self._engineered_payload(request.user_prompt)
            text = json.dumps(payload, ensure_ascii=False, indent=2)
        else:
            text = self._baseline_text(request.user_prompt)
        return GenerationResult(text=text, provider=self.name, model="mock-rules-v1")

    def _baseline_text(self, user_prompt: str) -> str:
        message = self._extract_message(user_prompt)
        exception_type = self._classify(message)
        return (
            f"It looks like a {exception_type.replace('_', ' ')} issue. "
            f"Based on the note ({message}), operations should investigate and resolve. "
            "A settlement date of 2026-01-15 may apply and account ACCT-999911 may need updating."
        )

    def _engineered_payload(self, user_prompt: str) -> dict[str, Any]:
        case_id = self._extract_case_id(user_prompt)
        message = self._extract_message(user_prompt)
        exception_type = self._classify(message)
        missing = self._missing_information(message, exception_type)
        escalate = self._should_escalate(message, exception_type, missing)
        known_facts = [message.strip()] if message.strip() else []
        evidence = [f"Source narrative: {message.strip()}"] if message.strip() else []

        # Deliberately imperfect offline stub: useful for wiring checks, not claimed accuracy.
        if "weather" in message.lower():
            known_facts.append("London weather was rainy")

        return {
            "case_id": case_id or "UNKNOWN",
            "exception_type": exception_type,
            "severity": "high" if escalate else "medium",
            "known_facts": known_facts,
            "missing_information": missing,
            "evidence": evidence,
            "recommended_next_action": (
                "Escalate to a qualified operations reviewer before any settlement action."
                if escalate
                else "Request the missing operational details and re-evaluate after update."
                if missing
                else "Prepare a structured exception record for human review."
            ),
            "escalation_required": escalate,
            "confidence": 0.55 if missing or escalate else 0.7,
        }

    def _extract_case_id(self, user_prompt: str) -> str | None:
        match = re.search(r"case_id:\s*([A-Za-z0-9_-]+)", user_prompt, flags=re.IGNORECASE)
        return match.group(1) if match else None

    def _extract_message(self, user_prompt: str) -> str:
        match = re.search(
            r"Exception narrative:\s*(.*?)(?:\n\n|\Z)",
            user_prompt,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if match:
            return match.group(1).strip()
        return user_prompt.strip()

    def _classify(self, message: str) -> str:
        lower = message.lower()
        for exception_type, keywords in TYPE_RULES:
            if any(keyword in lower for keyword in keywords):
                return exception_type
        if len(lower.split()) < 8:
            return "insufficient_information"
        return "other"

    def _missing_information(self, message: str, exception_type: str) -> list[str]:
        lower = message.lower()
        missing: list[str] = []
        if "settlement date is absent" in lower or "settlement date not provided" in lower:
            missing.append("settlement date")
        if "no deadline" in lower or "gives no deadline" in lower:
            missing.append("deadline")
        if "malformed" in lower:
            missing.append("valid message reference")
        if "invalid" in lower and "account" in lower:
            missing.append("valid receiving account")
        if "confirmation outstanding" in lower or "no affirming broker response" in lower:
            missing.append("counterparty confirmation")
        if "different settlement accounts" in lower:
            missing.append("authoritative settlement account")
        if "lei" in lower and "does not match" in lower:
            missing.append("authoritative LEI")
        if "no isin" in lower:
            missing.extend(["ISIN", "quantity", "settlement date"])
        if "see previous email" in lower or "weather" in lower:
            missing.extend(["trade identifier", "exception details"])
        if "new intended settlement date not provided" in lower:
            missing.append("new intended settlement date")
        if "deliver free" in lower and "delivery versus payment" in lower:
            missing.append("authoritative settlement method")
        if "cash funding" in lower:
            missing.append("funding confirmation")
        if "ssi" in lower:
            missing.append("correct SSI BIC")
        if exception_type == "insufficient_information" and not missing:
            missing.append("exception facts")
        # Deduplicate while preserving order
        seen: set[str] = set()
        ordered: list[str] = []
        for item in missing:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                ordered.append(item)
        return ordered

    def _should_escalate(self, message: str, exception_type: str, missing: list[str]) -> bool:
        lower = message.lower()
        if exception_type in {"insufficient_information", "market_deadline", "counterparty_issue"}:
            return True
        if any(token in lower for token in ("contradict", "differs", "different", "does not match", "urgent", "malformed")):
            return True
        if "two instructions" in lower or ("instruction a" in lower and "instruction b" in lower):
            return True
        return len(missing) >= 2
