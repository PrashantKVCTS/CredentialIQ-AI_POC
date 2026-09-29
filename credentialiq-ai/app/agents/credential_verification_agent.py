"""Agent 1: Credential Verification Agent."""

from typing import Any

from app.agents.base import BaseAgent
from app.core.enums import AuditEventType
from app.core.security import PIISanitizer
from app.schemas.common import ProviderIntakeSchema


class CredentialVerificationAgent(BaseAgent):
    """Validates provider intake schema, normalizes fields, and redacts sensitive PII."""

    def __init__(self):
        super().__init__(name="CredentialVerificationAgent")

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Validate intake data, sanitize PII, update state."""
        raw_provider = state.get("raw_provider_data", {})

        # Validate with Pydantic schema
        intake_model = ProviderIntakeSchema(**raw_provider)

        # Sanitize PII
        sanitized_dict = PIISanitizer.sanitize_provider_data(intake_model.model_dump())

        # Audit details
        audit_details = {
            "npi": intake_model.npi,
            "provider_name": f"{intake_model.first_name} {intake_model.last_name}",
            "specialty": intake_model.specialty,
            "license_count": len(intake_model.licenses),
            "pii_redacted": True,
        }

        audit_logs = list(state.get("audit_logs", []))
        audit_logs.append(
            {
                "event_type": AuditEventType.INTAKE_VERIFIED.value,
                "agent_name": self.name,
                "details": audit_details,
            }
        )

        return {
            "provider_intake": intake_model.model_dump(),
            "sanitized_provider": sanitized_dict,
            "provider_npi": intake_model.npi,
            "provider_name": f"{intake_model.first_name} {intake_model.last_name}",
            "audit_logs": audit_logs,
        }
