"""Case management and processing endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_audit_service, get_case_repository
from app.core.enums import AuditEventType, CaseStatus
from app.core.exceptions import CaseNotFoundError
from app.models.database import get_db
from app.orchestration.orchestrator import CredentialingOrchestrator
from app.repositories.case_repository import CaseRepository
from app.schemas.requests import CaseOverrideRequest, CaseProcessRequest
from app.schemas.responses import (
    AuditEventResponse,
    CaseDetailResponse,
    CaseSummaryResponse,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/v1/cases", tags=["Cases"])


@router.post(
    "/process",
    response_model=CaseDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process a new credentialing case",
)
def process_case(request: CaseProcessRequest, db: Session = Depends(get_db)):
    """Initiates 5-agent credentialing pipeline for a provider intake."""
    orchestrator = CredentialingOrchestrator(db)
    provider_dict = request.provider.model_dump()

    saved_case = orchestrator.process_case(raw_provider_data=provider_dict)

    return _format_case_detail_response(saved_case)


@router.get("/{case_id}", response_model=CaseDetailResponse, summary="Get case details by ID")
def get_case(case_id: str, repo: CaseRepository = Depends(get_case_repository)):
    """Fetch complete case record."""
    case_model = repo.get_case(case_id)
    if not case_model:
        raise CaseNotFoundError(case_id)

    return _format_case_detail_response(case_model)


@router.get("", response_model=list[CaseSummaryResponse], summary="List credentialing cases")
def list_cases(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    repo: CaseRepository = Depends(get_case_repository),
):
    """List credentialing cases."""
    cases = repo.list_cases(limit=limit, offset=offset)
    summaries = []
    for c in cases:
        risk_level = None
        if c.risk_assessment_json:
            risk_level = c.risk_assessment_json.get("risk_level")

        rec = None
        if c.workflow_recommendation_json:
            rec = c.workflow_recommendation_json.get("recommendation")

        summaries.append(
            CaseSummaryResponse(
                case_id=c.case_id,
                status=CaseStatus(c.status),
                provider_npi=c.provider_npi,
                provider_name=c.provider_name,
                risk_level=risk_level,
                recommendation=rec,
                created_at_utc=c.created_at_utc,
            )
        )
    return summaries


@router.post(
    "/{case_id}/override",
    response_model=CaseDetailResponse,
    summary="Human reviewer decision override",
)
def override_case(
    case_id: str,
    request: CaseOverrideRequest,
    repo: CaseRepository = Depends(get_case_repository),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Allows a human reviewer to override the automated agent decision."""
    case_model = repo.get_case(case_id)
    if not case_model:
        raise CaseNotFoundError(case_id)

    override_data = {
        "reviewer_id": request.reviewer_id,
        "override_decision": request.override_decision,
        "rationale": request.rationale,
        "timestamp_utc": datetime.utcnow().isoformat(),
    }

    case_model.status = CaseStatus.OVERRIDDEN.value
    case_model.override_json = override_data

    updated_case = repo.save_case(case_model)

    audit_service.log_event(
        case_id=case_id,
        event_type=AuditEventType.HUMAN_OVERRIDE,
        agent_name=f"HumanReviewer_{request.reviewer_id}",
        details=override_data,
    )

    return _format_case_detail_response(updated_case)


@router.get(
    "/{case_id}/audit-trail",
    response_model=list[AuditEventResponse],
    summary="Get case audit event trail",
)
def get_audit_trail(
    case_id: str,
    repo: CaseRepository = Depends(get_case_repository),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Retrieve complete immutable audit trail for a case."""
    case_model = repo.get_case(case_id)
    if not case_model:
        raise CaseNotFoundError(case_id)

    events = audit_service.repo.get_audit_trail(case_id)
    return [
        AuditEventResponse(
            id=e.id,
            case_id=e.case_id,
            event_type=e.event_type,
            agent_name=e.agent_name,
            timestamp_utc=e.timestamp_utc,
            details=e.details_json,
        )
        for e in events
    ]


def _format_case_detail_response(c) -> CaseDetailResponse:
    """Format SQLAlchemy CaseModel into CaseDetailResponse Pydantic schema."""
    return CaseDetailResponse(
        case_id=c.case_id,
        status=CaseStatus(c.status),
        created_at_utc=c.created_at_utc,
        updated_at_utc=c.updated_at_utc,
        provider_npi=c.provider_npi,
        provider_name=c.provider_name,
        sanitized_provider=c.sanitized_intake_json or {},
        license_verifications=c.license_verifications_json or [],
        sanction_screenings=c.sanction_screenings_json or [],
        risk_assessment=c.risk_assessment_json,
        workflow_recommendation=c.workflow_recommendation_json,
    )
