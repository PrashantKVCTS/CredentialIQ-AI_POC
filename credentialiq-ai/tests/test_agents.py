"""Unit tests for individual credentialing agents."""

from app.agents.credential_verification_agent import CredentialVerificationAgent
from app.agents.license_verification_agent import LicenseVerificationAgent
from app.agents.workflow_agent import WorkflowAgent
from app.core.enums import RecommendationType, RiskLevel


def test_credential_verification_agent(sample_clean_provider):
    agent = CredentialVerificationAgent()
    state = {"raw_provider_data": sample_clean_provider, "audit_logs": []}

    out = agent.execute(state)

    assert out["provider_npi"] == "1234567890"
    assert out["sanitized_provider"]["ssn"] == "[REDACTED-SSN]"
    assert len(out["audit_logs"]) == 1


def test_license_verification_agent(sample_clean_provider):
    agent = LicenseVerificationAgent()
    state = {
        "provider_intake": sample_clean_provider,
        "provider_npi": sample_clean_provider["npi"],
        "audit_logs": [],
    }

    out = agent.execute(state)

    assert len(out["license_verifications"]) == 1
    assert out["license_verifications"][0]["status"] == "Active"


def test_workflow_agent_clean():
    agent = WorkflowAgent()
    state = {
        "risk_assessment": {"risk_level": RiskLevel.CLEAN.value},
        "audit_logs": [],
    }

    out = agent.execute(state)

    rec = out["workflow_recommendation"]
    assert rec["recommendation"] == RecommendationType.AUTO_APPROVE.value
    assert rec["requires_committee_approval"] is False


def test_workflow_agent_hold():
    agent = WorkflowAgent()
    state = {
        "risk_assessment": {"risk_level": RiskLevel.HOLD.value},
        "audit_logs": [],
    }

    out = agent.execute(state)

    rec = out["workflow_recommendation"]
    assert rec["recommendation"] == RecommendationType.DENY.value
    assert rec["requires_committee_approval"] is True
