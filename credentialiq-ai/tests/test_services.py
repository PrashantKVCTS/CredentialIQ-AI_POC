"""Unit tests for services including security PII redaction and deterministic LLM."""

from app.core.enums import LicenseStatus, RiskLevel, SanctionStatus
from app.core.security import PIISanitizer
from app.schemas.common import EvidenceMetadata, LicenseEvidenceResult, SanctionEvidenceResult
from app.services.deterministic_language_model import DeterministicLanguageModelService


def test_pii_sanitizer():
    raw_data = {
        "npi": "1234567890",
        "ssn": "999-00-1234",
        "date_of_birth": "1980-05-14",
        "first_name": "Eleanor",
    }
    sanitized = PIISanitizer.sanitize_provider_data(raw_data)

    assert sanitized["ssn"] == "[REDACTED-SSN]"
    assert sanitized["date_of_birth"] == "[REDACTED-DOB]"
    assert sanitized["first_name"] == "Eleanor"


def test_deterministic_llm_clean():
    service = DeterministicLanguageModelService()
    lic = LicenseEvidenceResult(
        license_number="C123456",
        state="CA",
        status=LicenseStatus.ACTIVE,
        has_disciplinary_action=False,
        metadata=EvidenceMetadata(source_system="Mock"),
    )
    sanc = SanctionEvidenceResult(
        database_name="OIG_LEIE",
        status=SanctionStatus.CLEAR,
        match_found=False,
        metadata=EvidenceMetadata(source_system="Mock"),
    )

    res = service.evaluate_risk({}, [lic], [sanc], [])
    assert res.risk_level == RiskLevel.CLEAN
    assert res.score < 15.0


def test_deterministic_llm_hold():
    service = DeterministicLanguageModelService()
    lic = LicenseEvidenceResult(
        license_number="FL33333",
        state="FL",
        status=LicenseStatus.SUSPENDED,
        has_disciplinary_action=True,
        metadata=EvidenceMetadata(source_system="Mock"),
    )
    sanc = SanctionEvidenceResult(
        database_name="OIG_LEIE",
        status=SanctionStatus.MATCH_FOUND,
        match_found=True,
        metadata=EvidenceMetadata(source_system="Mock"),
    )

    res = service.evaluate_risk({}, [lic], [sanc], [])
    assert res.risk_level == RiskLevel.HOLD
    assert res.score >= 90.0
