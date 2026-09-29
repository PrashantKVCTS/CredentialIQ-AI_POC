import uuid
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.core.enums import CaseStatus, RiskClassification
from app.core.models import (
    Provider, VerificationResult, SanctionCheckResult,
    RiskAssessment, WorkflowDecision, AuditEvent
)

from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class CreateCredentialingCaseRequest(CamelModel):
    npi: str = Field(..., min_length=10, max_length=10)
    first_name: str
    last_name: str
    provider_type: str
    primary_state: str
    license_number: str
    date_of_birth: Optional[datetime] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CredentialingCaseResponse(CamelModel):
    id: uuid.UUID
    correlation_id: str
    provider_id: uuid.UUID
    provider: Provider
    status: CaseStatus
    risk_classification: Optional[RiskClassification] = None
    recommendation: Optional[str] = None
    created_at_utc: datetime
    updated_at_utc: datetime
    latest_verification_result: Optional[VerificationResult] = None
    latest_sanction_result: Optional[SanctionCheckResult] = None
    latest_risk_assessment: Optional[RiskAssessment] = None
    latest_workflow_decision: Optional[WorkflowDecision] = None
    disclaimer: str = "POC Disclaimer: CredentialIQ AI recommendations are simulated for demonstration purposes only and require review and authorization by a qualified human credentialing committee before any official action."

class EvidenceAuditResponse(CamelModel):
    case_id: uuid.UUID
    correlation_id: str
    verification_results: List[VerificationResult]
    sanction_results: List[SanctionCheckResult]
    risk_assessments: List[RiskAssessment]
    workflow_decisions: List[WorkflowDecision]
    audit_events: List[AuditEvent]

class ManualOverrideRequest(CamelModel):
    target_status: CaseStatus
    reviewer_name: str
    reason: str

class SystemInfoResponse(CamelModel):
    application_name: str = "CredentialIQ AI"
    version: str = "1.0.0-poc"
    environment: str = "Production"
    llm_provider: str = "Deterministic"
    connector_mode: str = "MockPrimarySource"
    synthetic_data_enabled: bool = True
    disclaimer: str = "CredentialIQ AI Proof of Concept - Local Profile. Results require authorized human review."

class HealthCheckResponse(CamelModel):
    status: str = "Healthy"
    components: Dict[str, str] = Field(default_factory=dict)
    checked_at_utc: datetime
