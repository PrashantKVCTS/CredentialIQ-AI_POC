from datetime import datetime, timezone
from app.agents.base import ICredentialingAgent
from app.core.enums import CaseStatus
from app.core.models import CredentialingCase, AuditEvent
from app.infrastructure.rag_repository import LocalRagRepository
from app.infrastructure.llm_service import DeterministicLanguageModelService

class RiskAssessmentAgent(ICredentialingAgent):
    def __init__(self, rag_repo: LocalRagRepository, llm_service: DeterministicLanguageModelService):
        self.rag_repo = rag_repo
        self.llm_service = llm_service

    @property
    def agent_name(self) -> str:
        return "RiskAssessmentAgent"

    async def process_async(self, case: CredentialingCase) -> CredentialingCase:
        case.status = CaseStatus.RISK_ASSESSMENT

        query = f"credentialing policy {case.provider.provider_type} license {case.provider.primary_state}"
        policies = await self.rag_repo.retrieve_relevant_policies_async(query, state=case.provider.primary_state, top_k=5)

        risk_assessment = await self.llm_service.evaluate_risk_async(case, policies)
        risk_assessment.case_id = case.id
        case.risk_assessments.append(risk_assessment)
        case.risk_classification = risk_assessment.classification

        audit = AuditEvent(
            case_id=case.id,
            source=self.agent_name,
            action="RiskAssessment",
            outcome=str(risk_assessment.classification),
            correlation_id=case.correlation_id,
            evidence_reference=f"RISK-{risk_assessment.id.hex[:8]}",
            is_simulated=True,
            human_readable_explanation=f"Assessed case risk as [{risk_assessment.classification}] using LLM Service [{self.llm_service.provider_name}]. Rationale: {risk_assessment.rationale}"
        )
        case.audit_events.append(audit)
        case.updated_at_utc = datetime.now(timezone.utc)
        return case
