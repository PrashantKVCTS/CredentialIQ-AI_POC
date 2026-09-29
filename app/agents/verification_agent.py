import uuid
from datetime import datetime, timezone
from app.agents.base import ICredentialingAgent
from app.core.enums import CaseStatus
from app.core.models import CredentialingCase, AuditEvent

class CredentialVerificationAgent(ICredentialingAgent):
    @property
    def agent_name(self) -> str:
        return "CredentialVerificationAgent"

    async def process_async(self, case: CredentialingCase) -> CredentialingCase:
        if not case.provider or not case.provider.npi or len(case.provider.npi) != 10:
            raise ValueError(f"Invalid NPI: {case.provider.npi if case.provider else 'None'}. Must be a 10-digit numeric NPI.")

        case.status = CaseStatus.INTAKE
        case.updated_at_utc = datetime.now(timezone.utc)

        audit = AuditEvent(
            case_id=case.id,
            source=self.agent_name,
            action="IntakeValidation",
            outcome="Success",
            correlation_id=case.correlation_id,
            evidence_reference=f"INTAKE-{uuid.uuid4().hex[:8]}",
            is_simulated=True,
            human_readable_explanation=f"Validated provider intake payload for {case.provider.first_name} {case.provider.last_name} (NPI: {case.provider.npi})."
        )
        case.audit_events.append(audit)
        return case
