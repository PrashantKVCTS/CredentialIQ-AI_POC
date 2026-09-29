import uuid
from datetime import datetime, timezone
from app.agents.base import ICredentialingAgent
from app.core.enums import CaseStatus
from app.core.models import CredentialingCase, AuditEvent
from app.infrastructure.connectors import MockStateBoardConnector

class LicenseVerificationAgent(ICredentialingAgent):
    def __init__(self, connector: MockStateBoardConnector):
        self.connector = connector

    @property
    def agent_name(self) -> str:
        return "LicenseVerificationAgent"

    async def process_async(self, case: CredentialingCase) -> CredentialingCase:
        case.status = CaseStatus.VERIFYING
        result = await self.connector.verify_license_async(case.provider, case.correlation_id)
        result.case_id = case.id
        case.verification_results.append(result)

        audit = AuditEvent(
            case_id=case.id,
            source=self.agent_name,
            action="LicenseVerification",
            outcome=str(result.status),
            correlation_id=case.correlation_id,
            evidence_reference=result.evidence_reference,
            is_simulated=result.is_simulated,
            human_readable_explanation=result.human_readable_explanation
        )
        case.audit_events.append(audit)
        case.updated_at_utc = datetime.now(timezone.utc)
        return case
