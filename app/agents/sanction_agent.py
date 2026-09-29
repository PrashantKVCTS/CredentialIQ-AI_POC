from datetime import datetime, timezone
from app.agents.base import ICredentialingAgent
from app.core.enums import CaseStatus
from app.core.models import CredentialingCase, AuditEvent
from app.infrastructure.connectors import MockSanctionConnector

class SanctionCheckAgent(ICredentialingAgent):
    def __init__(self, connector: MockSanctionConnector):
        self.connector = connector

    @property
    def agent_name(self) -> str:
        return "SanctionCheckAgent"

    async def process_async(self, case: CredentialingCase) -> CredentialingCase:
        case.status = CaseStatus.SANCTION_SCREENING
        result = await self.connector.check_sanctions_async(case.provider, case.correlation_id)
        result.case_id = case.id
        case.sanction_results.append(result)

        audit = AuditEvent(
            case_id=case.id,
            source=self.agent_name,
            action="SanctionCheck",
            outcome=str(result.status),
            correlation_id=case.correlation_id,
            evidence_reference=result.evidence_reference,
            is_simulated=result.is_simulated,
            human_readable_explanation=result.human_readable_explanation
        )
        case.audit_events.append(audit)
        case.updated_at_utc = datetime.now(timezone.utc)
        return case
