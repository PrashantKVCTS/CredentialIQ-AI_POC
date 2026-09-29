"""Integration tests for 5-agent LangGraph orchestrator."""

from app.core.enums import CaseStatus
from app.orchestration.orchestrator import CredentialingOrchestrator


def test_orchestrator_clean_case(db_session, sample_clean_provider):
    orchestrator = CredentialingOrchestrator(db_session)
    case_model = orchestrator.process_case(sample_clean_provider)

    assert case_model.case_id is not None
    assert case_model.status == CaseStatus.CLEAN.value
    assert case_model.risk_assessment_json["risk_level"] == "Clean"
    assert case_model.workflow_recommendation_json["recommendation"] == "AutoApprove"
    assert len(case_model.audit_events) >= 5


def test_orchestrator_hold_case(db_session, sample_hold_provider):
    orchestrator = CredentialingOrchestrator(db_session)
    case_model = orchestrator.process_case(sample_hold_provider)

    assert case_model.status == CaseStatus.HOLD.value
    assert case_model.risk_assessment_json["risk_level"] == "Hold"
    assert case_model.workflow_recommendation_json["recommendation"] == "Deny"
