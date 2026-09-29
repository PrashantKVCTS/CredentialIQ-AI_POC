from enum import Enum, IntEnum

class CaseStatus(str, Enum):
    INTAKE = "Intake"
    VERIFYING = "Verifying"
    SANCTION_SCREENING = "SanctionScreening"
    RISK_ASSESSMENT = "RiskAssessment"
    COMMITTEE_REVIEW = "CommitteeReview"
    APPROVED = "Approved"
    ON_HOLD = "OnHold"
    REJECTED = "Rejected"

class RiskClassification(str, Enum):
    CLEAN = "Clean"
    EXCEPTION = "Exception"
    HOLD = "Hold"

class LicenseStatus(str, Enum):
    ACTIVE = "Active"
    EXPIRED = "Expired"
    SUSPENDED = "Suspended"
    UNKNOWN = "Unknown"

class SanctionStatus(str, Enum):
    CLEAR = "Clear"
    MATCH_FOUND = "MatchFound"
    PENDING_REVIEW = "PendingReview"

class LlmProviderType(str, Enum):
    DETERMINISTIC = "Deterministic"
    GEMINI = "Gemini"
