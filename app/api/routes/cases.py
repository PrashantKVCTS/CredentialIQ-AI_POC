import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from app.core.dto import (
    CreateCredentialingCaseRequest, CredentialingCaseResponse,
    EvidenceAuditResponse, ManualOverrideRequest
)
from app.core.models import CredentialingCase, Provider, AuditEvent, WorkflowDecision
from app.core.enums import CaseStatus
from app.infrastructure.repository import CredentialingCaseRepository
from app.infrastructure.connectors import MockStateBoardConnector, MockSanctionConnector
from app.infrastructure.rag_repository import LocalRagRepository
from app.infrastructure.llm_service import DeterministicLanguageModelService
from app.agents.verification_agent import CredentialVerificationAgent
from app.agents.license_agent import LicenseVerificationAgent
from app.agents.sanction_agent import SanctionCheckAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.workflow_agent import WorkflowAgent
from app.agents.orchestrator import CredentialingOrchestrator

router = APIRouter(prefix="/api/credentialingcases", tags=["Credentialing Cases"])

# Dependencies
repository = CredentialingCaseRepository()
rag_repo = LocalRagRepository(knowledge_dir="knowledge")
llm_service = DeterministicLanguageModelService()

def build_orchestrator() -> CredentialingOrchestrator:
    state_connector = MockStateBoardConnector()
    sanction_connector = MockSanctionConnector()
    
    agents = [
        CredentialVerificationAgent(),
        LicenseVerificationAgent(state_connector),
        SanctionCheckAgent(sanction_connector),
        RiskAssessmentAgent(rag_repo, llm_service),
        WorkflowAgent()
    ]
    return CredentialingOrchestrator(agents, repository)

def to_case_response(case: CredentialingCase) -> CredentialingCaseResponse:
    latest_lic = case.verification_results[-1] if case.verification_results else None
    latest_sanc = case.sanction_results[-1] if case.sanction_results else None
    latest_risk = case.risk_assessments[-1] if case.risk_assessments else None
    latest_wf = case.workflow_decisions[-1] if case.workflow_decisions else None

    return CredentialingCaseResponse(
        id=case.id,
        correlation_id=case.correlation_id,
        provider_id=case.provider_id,
        provider=case.provider,
        status=case.status,
        risk_classification=case.risk_classification,
        recommendation=case.recommendation,
        created_at_utc=case.created_at_utc,
        updated_at_utc=case.updated_at_utc,
        latest_verification_result=latest_lic,
        latest_sanction_result=latest_sanc,
        latest_risk_assessment=latest_risk,
        latest_workflow_decision=latest_wf
    )

@router.post("", response_model=CredentialingCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(request: CreateCredentialingCaseRequest):
    provider_id = uuid.uuid4()
    provider = Provider(
        id=provider_id,
        npi=request.npi,
        first_name=request.first_name,
        last_name=request.last_name,
        provider_type=request.provider_type,
        primary_state=request.primary_state,
        license_number=request.license_number,
        date_of_birth=request.date_of_birth,
        email=request.email,
        phone=request.phone,
        address=request.address
    )

    case = CredentialingCase(
        provider_id=provider_id,
        provider=provider
    )

    orchestrator = build_orchestrator()
    processed_case = await orchestrator.run_pipeline_async(case)
    return to_case_response(processed_case)

@router.get("/{case_id}", response_model=CredentialingCaseResponse)
async def get_case(case_id: uuid.UUID):
    case = await repository.get_case_by_id_async(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Credentialing case {case_id} not found.")
    return to_case_response(case)

@router.get("/{case_id}/evidence", response_model=EvidenceAuditResponse)
async def get_evidence(case_id: uuid.UUID):
    case = await repository.get_case_by_id_async(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Credentialing case {case_id} not found.")

    return EvidenceAuditResponse(
        case_id=case.id,
        correlation_id=case.correlation_id,
        verification_results=case.verification_results,
        sanction_results=case.sanction_results,
        risk_assessments=case.risk_assessments,
        workflow_decisions=case.workflow_decisions,
        audit_events=case.audit_events
    )

@router.post("/{case_id}/override", response_model=CredentialingCaseResponse)
async def post_override(case_id: uuid.UUID, request: ManualOverrideRequest):
    case = await repository.get_case_by_id_async(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Credentialing case {case_id} not found.")

    old_status = case.status
    case.status = request.target_status
    case.updated_at_utc = datetime.now(timezone.utc)

    override_decision = WorkflowDecision(
        case_id=case.id,
        status=old_status,
        target_status=request.target_status,
        recommended_action=f"MANUAL OVERRIDE by {request.reviewer_name}: {request.reason}",
        case_summary=f"Case status changed from [{old_status}] to [{request.target_status}] by Authorized Reviewer.",
        recommended_at_utc=datetime.now(timezone.utc),
        correlation_id=case.correlation_id,
        is_human_override=True,
        overridden_by=request.reviewer_name,
        override_reason=request.reason,
        overridden_at_utc=datetime.now(timezone.utc)
    )
    case.workflow_decisions.append(override_decision)

    audit = AuditEvent(
        case_id=case.id,
        source="HumanReviewer",
        action="ManualOverride",
        outcome=str(request.target_status),
        correlation_id=case.correlation_id,
        evidence_reference=f"OVERRIDE-{override_decision.id.hex[:8]}",
        is_simulated=False,
        human_readable_explanation=f"Authorized reviewer [{request.reviewer_name}] manually set status to [{request.target_status}]. Reason: {request.reason}"
    )
    case.audit_events.append(audit)
    await repository.save_case_async(case)
    return to_case_response(case)
