"""Common Pydantic data schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import LicenseStatus, SanctionStatus


class LicenseInputSchema(BaseModel):
    """License information provided in provider intake."""

    license_number: str = Field(..., description="Medical license number")
    state: str = Field(..., description="Two-letter state postal abbreviation")
    license_type: str = Field(default="MD", description="License type, e.g. MD, DO, RN")
    expiration_date: str | None = Field(None, description="Expiration date YYYY-MM-DD")


class ProviderIntakeSchema(BaseModel):
    """Schema for provider intake information."""

    npi: str = Field(..., min_length=10, max_length=10, description="10-digit National Provider Identifier")
    first_name: str = Field(..., min_length=1, description="First name")
    last_name: str = Field(..., min_length=1, description="Last name")
    date_of_birth: str | None = Field(None, description="Date of birth YYYY-MM-DD")
    ssn: str | None = Field(None, description="Social Security Number")
    taxonomy_code: str | None = Field(None, description="Primary taxonomy specialty code")
    specialty: str = Field(..., description="Medical specialty")
    medical_school: str | None = Field(None, description="Graduating medical school")
    graduation_year: int | None = Field(None, description="Graduation year")
    board_certified: bool = Field(default=True, description="Whether board certified")
    board_name: str | None = Field(None, description="Certifying specialty board")
    licenses: list[LicenseInputSchema] = Field(default_factory=list, description="State licenses")


class EvidenceMetadata(BaseModel):
    """Metadata attached to primary source evidence records."""

    source_system: str
    verified_at_utc: datetime = Field(default_factory=datetime.utcnow)
    is_simulated: bool = True
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    raw_response_snippet: str | None = None


class LicenseEvidenceResult(BaseModel):
    """Primary source verification result for a single license."""

    license_number: str
    state: str
    status: LicenseStatus
    expiration_date: str | None = None
    has_disciplinary_action: bool = False
    disciplinary_details: str | None = None
    metadata: EvidenceMetadata


class SanctionEvidenceResult(BaseModel):
    """Screening result against a single sanction database (OIG, SAM, NPDB)."""

    database_name: str  # e.g., OIG_LEIE, SAM_GOV, NPDB
    status: SanctionStatus
    match_found: bool = False
    exclusion_type: str | None = None
    reinstatement_date: str | None = None
    details: str | None = None
    metadata: EvidenceMetadata


class PolicyChunkMatch(BaseModel):
    """Retrieved policy chunk from local RAG repository."""

    chunk_id: str
    title: str
    category: str
    content: str
    similarity_score: float
    source: str
