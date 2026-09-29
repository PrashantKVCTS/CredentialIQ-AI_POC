"""Agent 3: Sanction Check Agent."""

from typing import Any

from app.agents.base import BaseAgent
from app.core.enums import AuditEventType
from app.services.evidence_service import EvidenceService


class SanctionCheckAgent(BaseAgent):
    """Screens providers against federal and state exclusion databases (OIG LEIE, SAM.gov, NPDB)."""

    def __init__(self, evidence_service: EvidenceService | None = None):
        super().__init__(name="SanctionCheckAgent")
        self.evidence_service = evidence_service or EvidenceService()

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Perform sanction and exclusion screening."""
        provider_intake = state.get("provider_intake", {})
        npi = state.get("provider_npi", provider_intake.get("npi", ""))
        first_name = provider_intake.get("first_name", "")
        last_name = provider_intake.get("last_name", "")

        screenings = self.evidence_service.screen_sanctions(npi, first_name, last_name)

        has_sanction_match = any(s.match_found for s in screenings)

        audit_details = {
            "databases_screened": [s.database_name for s in screenings],
            "sanction_match_found": has_sanction_match,
            "match_count": sum(1 for s in screenings if s.match_found),
        }

        audit_logs = list(state.get("audit_logs", []))
        audit_logs.append(
            {
                "event_type": AuditEventType.SANCTION_SCREENED.value,
                "agent_name": self.name,
                "details": audit_details,
            }
        )

        return {
            "sanction_screenings": [s.model_dump() for s in screenings],
            "has_sanction_match": has_sanction_match,
            "audit_logs": audit_logs,
        }
