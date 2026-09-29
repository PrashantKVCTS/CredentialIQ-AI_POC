"""LangGraph state definition for credentialing pipeline."""

from typing import Any, TypedDict


class CredentialingState(TypedDict, total=False):
    """State object passed through LangGraph agent workflow nodes."""

    case_id: str
    raw_provider_data: dict[str, Any]
    provider_intake: dict[str, Any]
    sanitized_provider: dict[str, Any]
    provider_npi: str
    provider_name: str
    license_verifications: list[dict[str, Any]]
    sanction_screenings: list[dict[str, Any]]
    has_sanction_match: bool
    retrieved_policies: list[dict[str, Any]]
    risk_assessment: dict[str, Any]
    workflow_recommendation: dict[str, Any]
    final_status: str
    audit_logs: list[dict[str, Any]]
    error: str | None
