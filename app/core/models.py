import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.core.enums import CaseStatus, RiskClassification, LicenseStatus, SanctionStatus

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Provider(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    npi: str
    first_name: str
    last_name: str
    provider_type: str
    primary_state: str
    license_number: str
    date_of_birth: Optional[datetime] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class VerificationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    case_id: Optional[uuid.UUID] = None
    source: str
    status: LicenseStatus
    expiration_date: Optional[datetime] = None
    verified_at_utc: datetime = Field(default_factory=utc_now)
    correlation_id: str = ""
    evidence_reference: str = ""
    is_simulated: bool = True
    human_readable_explanation: str = ""

class SanctionCheckResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    case_id: Optional[uuid.UUID] = None
    source: str
    status: SanctionStatus = SanctionStatus.CLEAR
    verified_at_utc: datetime = Field(default_factory=utc_now)
    correlation_id: str = ""
    evidence_reference: str = ""
    is_simulated: bool = True
    human_readable_explanation: str = ""

class RiskAssessment(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    case_id: Optional[uuid.UUID] = None
    classification: RiskClassification = RiskClassification.CLEAN
    confidence_score: float = 1.0
    rationale: str = ""
    applied_rule_references: List[str] = Field(default_factory=list)
    retrieved_source_ids: List[str] = Field(default_factory=list)
    assessed_at_utc: datetime = Field(default_factory=utc_now)
    correlation_id: str = ""
    evaluated_by: str = "Deterministic"

class WorkflowDecision(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    case_id: Optional[uuid.UUID] = None
    status: CaseStatus = CaseStatus.INTAKE
    target_status: CaseStatus = CaseStatus.APPROVED
    recommended_action: str = ""
    case_summary: str = ""
    recommended_at_utc: datetime = Field(default_factory=utc_now)
    correlation_id: str = ""
    is_human_override: bool = False
    overridden_by: Optional[str] = None
    override_reason: Optional[str] = None
    overridden_at_utc: Optional[datetime] = None

class AuditEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    case_id: Optional[uuid.UUID] = None
    source: str
    action: str
    outcome: str
    utc_timestamp: datetime = Field(default_factory=utc_now)
    correlation_id: str = ""
    evidence_reference: str = ""
    is_simulated: bool = True
    human_readable_explanation: str = ""

class PolicyChunk(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    source_type: str
    jurisdiction: str
    provider_type: str
    rule_reference: str
    title: str
    content: str
    effective_date: str
    score: float = 0.0
    is_synthetic: bool = True

class CredentialingCase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    correlation_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    provider_id: uuid.UUID
    provider: Provider
    status: CaseStatus = CaseStatus.INTAKE
    risk_classification: Optional[RiskClassification] = None
    recommendation: Optional[str] = None
    created_at_utc: datetime = Field(default_factory=utc_now)
    updated_at_utc: datetime = Field(default_factory=utc_now)
    verification_results: List[VerificationResult] = Field(default_factory=list)
    sanction_results: List[SanctionCheckResult] = Field(default_factory=list)
    risk_assessments: List[RiskAssessment] = Field(default_factory=list)
    workflow_decisions: List[WorkflowDecision] = Field(default_factory=list)
    audit_events: List[AuditEvent] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)
