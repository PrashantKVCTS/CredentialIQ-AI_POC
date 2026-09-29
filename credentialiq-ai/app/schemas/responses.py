"""API Response Schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.enums import CaseStatus, RecommendationType, RiskLevel
from app.schemas.common import (
    LicenseEvidenceResult,
    PolicyChunkMatch,
    SanctionEvidenceResult,
)


class RiskAssessmentResponse(BaseModel):
    """Output summary of risk assessment agent."""

    risk_level: RiskLevel
    score: float = Field(..., ge=0.0, le=100.0)
    summary: str
    risk_factors: list[str] = Field(default_factory=list)
    mitigating_factors: list[str] = Field(default_factory=list)
    applicable_policies: list[PolicyChunkMatch] = Field(default_factory=list)


class WorkflowRecommendationResponse(BaseModel):
    """Output summary of workflow agent."""

    recommendation: RecommendationType
    rationale: str
    action_items: list[str] = Field(default_factory=list)
    requires_committee_approval: bool = False
    next_review_due_date: str | None = None


class AuditEventResponse(BaseModel):
    """Audit event record."""

    id: int
    case_id: str
    event_type: str
    agent_name: str
    timestamp_utc: datetime
    details: dict[str, Any]


class CaseDetailResponse(BaseModel):
    """Complete detail response for a credentialing case."""

    case_id: str
    status: CaseStatus
    created_at_utc: datetime
    updated_at_utc: datetime
    provider_npi: str
    provider_name: str
    sanitized_provider: dict[str, Any]
    license_verifications: list[LicenseEvidenceResult] = Field(default_factory=list)
    sanction_screenings: list[SanctionEvidenceResult] = Field(default_factory=list)
    risk_assessment: RiskAssessmentResponse | None = None
    workflow_recommendation: WorkflowRecommendationResponse | None = None
    disclaimer: str = (
        "CredentialIQ AI POC Legal Disclaimer: POC results are automated recommendations "
        "and do not constitute official credentialing determinations. Final decisions require "
        "qualified human credentialing committee authorization."
    )


class CaseSummaryResponse(BaseModel):
    """Summary record for case listings."""

    case_id: str
    status: CaseStatus
    provider_npi: str
    provider_name: str
    risk_level: RiskLevel | None = None
    recommendation: RecommendationType | None = None
    created_at_utc: datetime


class RAGSearchResponse(BaseModel):
    """Policy RAG search result list."""

    query: str
    total_matches: int
    matches: list[PolicyChunkMatch]
