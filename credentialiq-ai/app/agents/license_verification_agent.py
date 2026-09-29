"""Agent 2: License Verification Agent."""

from typing import Any

from app.agents.base import BaseAgent
from app.core.enums import AuditEventType
from app.services.evidence_service import EvidenceService


class LicenseVerificationAgent(BaseAgent):
    """Executes primary source state medical board license verification."""

    def __init__(self, evidence_service: EvidenceService | None = None):
        super().__init__(name="LicenseVerificationAgent")
        self.evidence_service = evidence_service or EvidenceService()

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Verify provider's state medical licenses against primary sources."""
        provider_intake = state.get("provider_intake", {})
        provider_npi = state.get("provider_npi", provider_intake.get("npi", ""))
        licenses = provider_intake.get("licenses", [])

        # Execute primary source checks
        verifications = self.evidence_service.verify_licenses(licenses, provider_npi)

        # Audit event
        audit_details = {
            "verified_licenses_count": len(verifications),
            "license_statuses": [
                {
                    "state": v.state,
                    "number": v.license_number,
                    "status": v.status.value,
                    "has_disciplinary": v.has_disciplinary_action,
                }
                for v in verifications
            ],
            "primary_source_simulated": True,
        }

        audit_logs = list(state.get("audit_logs", []))
        audit_logs.append(
            {
                "event_type": AuditEventType.LICENSE_VERIFIED.value,
                "agent_name": self.name,
                "details": audit_details,
            }
        )

        return {
            "license_verifications": [v.model_dump() for v in verifications],
            "audit_logs": audit_logs,
        }
