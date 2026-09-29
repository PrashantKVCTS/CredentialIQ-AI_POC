"""Security & PII redaction utilities."""

import re
from typing import Any


class PIISanitizer:
    """Utility class to sanitize and redact sensitive PII fields in provider payloads."""

    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b")
    DOB_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b")

    @classmethod
    def redact_ssn(cls, text: str) -> str:
        """Redact Social Security Numbers."""
        if not text:
            return text
        return cls.SSN_PATTERN.sub("[REDACTED-SSN]", text)

    @classmethod
    def redact_dob(cls, text: str) -> str:
        """Redact Date of Birth values."""
        if not text:
            return text
        return cls.DOB_PATTERN.sub("[REDACTED-DOB]", text)

    @classmethod
    def sanitize_provider_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Deep copy and redact sensitive fields from a provider payload."""
        sanitized = data.copy()

        if "ssn" in sanitized and sanitized["ssn"]:
            sanitized["ssn"] = "[REDACTED-SSN]"

        if "date_of_birth" in sanitized and sanitized["date_of_birth"]:
            sanitized["date_of_birth"] = "[REDACTED-DOB]"

        if "dob" in sanitized and sanitized["dob"]:
            sanitized["dob"] = "[REDACTED-DOB]"

        return sanitized
