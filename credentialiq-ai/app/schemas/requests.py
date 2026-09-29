"""API Request Schemas."""


from pydantic import BaseModel, Field

from app.schemas.common import ProviderIntakeSchema


class CaseProcessRequest(BaseModel):
    """Payload to initiate a new credentialing case processing pipeline."""

    provider: ProviderIntakeSchema
    notes: str | None = Field(None, description="Optional intake notes or context")


class CaseOverrideRequest(BaseModel):
    """Payload to apply a human reviewer override to a case."""

    reviewer_id: str = Field(..., min_length=1, description="ID or username of human reviewer")
    override_decision: str = Field(
        ..., description="Approved, Denied, or Hold"
    )
    rationale: str = Field(..., min_length=10, description="Detailed justification for human override")
