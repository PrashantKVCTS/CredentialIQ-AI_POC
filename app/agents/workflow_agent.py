from datetime import datetime, timezone
from app.agents.base import ICredentialingAgent
from app.core.enums import CaseStatus, RiskClassification, LicenseStatus, SanctionStatus
from app.core.models import CredentialingCase, WorkflowDecision, AuditEvent

class WorkflowAgent(ICredentialingAgent):
    @property
    def agent_name(self) -> str:
        return "WorkflowAgent"

    async def process_async(self, case: CredentialingCase) -> CredentialingCase:
        latest_risk = case.risk_assessments[-1] if case.risk_assessments else None
        latest_lic = case.verification_results[-1] if case.verification_results else None
        latest_sanc = case.sanction_results[-1] if case.sanction_results else None

        # Hard safety enforcement rules
        if (latest_sanc and latest_sanc.status == SanctionStatus.MATCH_FOUND) or (latest_lic and latest_lic.status == LicenseStatus.SUSPENDED):
            target_status = CaseStatus.ON_HOLD
            action = "MANDATORY HOLD: Immediate referral to Legal & Compliance Committee. Automatic approval strictly prohibited."
            summary = f"CRITICAL SAFETY ALERT: Provider {case.provider.first_name} {case.provider.last_name} has a recorded Sanction Match or Suspended License. Application placed on HOLD."
        elif latest_risk and latest_risk.classification == RiskClassification.EXCEPTION:
            target_status = CaseStatus.COMMITTEE_REVIEW
            action = "ROUTE TO COMMITTEE REVIEW: License expiration policy exception detected. Escalate to Credentialing Committee."
            summary = f"EXCEPTION RECOMMENDATION: License for {case.provider.first_name} {case.provider.last_name} is expired. Routed for Committee Review."
        else:
            target_status = CaseStatus.APPROVED
            action = "RECOMMEND APPROVAL: Expedited credentialing approval recommended based on clean primary-source verification and zero sanction matches."
            summary = f"APPROVAL RECOMMENDATION: Provider {case.provider.first_name} {case.provider.last_name} passed all verification and screening checks."

        decision = WorkflowDecision(
            case_id=case.id,
            status=case.status,
            target_status=target_status,
            recommended_action=action,
            case_summary=summary,
            recommended_at_utc=datetime.now(timezone.utc),
            correlation_id=case.correlation_id
        )
        case.workflow_decisions.append(decision)
        case.status = target_status
        case.recommendation = action

        audit = AuditEvent(
            case_id=case.id,
            source=self.agent_name,
            action="WorkflowDecision",
            outcome=str(target_status),
            correlation_id=case.correlation_id,
            evidence_reference=f"DECISION-{decision.id.hex[:8]}",
            is_simulated=True,
            human_readable_explanation=f"Workflow Agent determined target case status as [{target_status}]. Recommendation: {action}"
        )
        case.audit_events.append(audit)
        case.updated_at_utc = datetime.now(timezone.utc)
        return case
