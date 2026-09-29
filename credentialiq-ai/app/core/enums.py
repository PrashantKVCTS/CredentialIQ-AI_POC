"""Domain enumerations for CredentialIQ AI POC."""

from enum import Enum


class CaseStatus(str, Enum):
    """Lifecycle status of a credentialing case."""

    DRAFT = "Draft"
    IN_PROGRESS = "InProgress"
    CLEAN = "Clean"
    EXCEPTION = "Exception"
    HOLD = "Hold"
    APPROVED = "Approved"
    DENIED = "Denied"
    OVERRIDDEN = "Overridden"


class RiskLevel(str, Enum):
    """Assessed risk level for a provider."""

    CLEAN = "Clean"
    EXCEPTION = "Exception"
    HOLD = "Hold"


class RecommendationType(str, Enum):
    """Final workflow recommendation."""

    AUTO_APPROVE = "AutoApprove"
    COMMITTEE_REVIEW = "CommitteeReview"
    DENY = "Deny"
    ADDITIONAL_INFO_REQUIRED = "AdditionalInfoRequired"


class LicenseStatus(str, Enum):
    """Primary source medical license status."""

    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    EXPIRED = "Expired"
    REVOKED = "Revoked"
    NOT_FOUND = "NotFound"


class SanctionStatus(str, Enum):
    """Sanction screening status."""

    CLEAR = "Clear"
    MATCH_FOUND = "MatchFound"
    POTENTIAL_MATCH = "PotentialMatch"


class AuditEventType(str, Enum):
    """Types of audit trail events recorded."""

    INTAKE_RECEIVED = "IntakeReceived"
    INTAKE_VERIFIED = "IntakeVerified"
    LICENSE_VERIFIED = "LicenseVerified"
    SANCTION_SCREENED = "SanctionScreened"
    RAG_RETRIEVED = "RAGRetrieved"
    RISK_ASSESSED = "RiskAssessed"
    WORKFLOW_RECOMMENDED = "WorkflowRecommended"
    CASE_PERSISTED = "CasePersisted"
    HUMAN_OVERRIDE = "HumanOverride"
    ERROR_ENCOUNTERED = "ErrorEncountered"
