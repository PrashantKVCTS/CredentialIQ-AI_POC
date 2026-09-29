import pytest
import uuid
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.models import Provider, CredentialingCase
from app.core.enums import CaseStatus, RiskClassification, LicenseStatus, SanctionStatus
from app.infrastructure.connectors import MockStateBoardConnector, MockSanctionConnector
from app.infrastructure.rag_repository import LocalRagRepository
from app.infrastructure.llm_service import DeterministicLanguageModelService, GeminiLanguageModelService
from app.agents.verification_agent import CredentialVerificationAgent
from app.agents.license_agent import LicenseVerificationAgent
from app.agents.sanction_agent import SanctionCheckAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.workflow_agent import WorkflowAgent
from app.agents.orchestrator import CredentialingOrchestrator
from app.infrastructure.repository import CredentialingCaseRepository

@pytest.mark.asyncio
async def test_credential_verification_agent_valid_npi():
    agent = CredentialVerificationAgent()
    provider = Provider(npi="1234567890", first_name="Jane", last_name="Doe", provider_type="MD", primary_state="CA", license_number="C123")
    case = CredentialingCase(provider_id=provider.id, provider=provider)
    
    processed = await agent.process_async(case)
    assert processed.status == CaseStatus.INTAKE
    assert len(processed.audit_events) == 1

@pytest.mark.asyncio
async def test_license_verification_agent_expired_license():
    connector = MockStateBoardConnector()
    agent = LicenseVerificationAgent(connector)
    provider = Provider(npi="9876543210", first_name="Robert", last_name="Smith", provider_type="MD", primary_state="CA", license_number="EXP-998877")
    case = CredentialingCase(provider_id=provider.id, provider=provider)

    processed = await agent.process_async(case)
    assert len(processed.verification_results) == 1
    assert processed.verification_results[0].status == LicenseStatus.EXPIRED

@pytest.mark.asyncio
async def test_sanction_check_agent_clear():
    connector = MockSanctionConnector()
    agent = SanctionCheckAgent(connector)
    provider = Provider(npi="1234567890", first_name="Jane", last_name="Doe", provider_type="MD", primary_state="CA", license_number="C123")
    case = CredentialingCase(provider_id=provider.id, provider=provider)

    processed = await agent.process_async(case)
    assert len(processed.sanction_results) == 1
    assert processed.sanction_results[0].status == SanctionStatus.CLEAR

@pytest.mark.asyncio
async def test_workflow_agent_mandatory_hold_on_suspended_license():
    agent = WorkflowAgent()
    provider = Provider(npi="5556667778", first_name="Arthur", last_name="Pendelton", provider_type="NP", primary_state="NY", license_number="SUSP-112233")
    case = CredentialingCase(provider_id=provider.id, provider=provider)
    
    lic_agent = LicenseVerificationAgent(MockStateBoardConnector())
    case = await lic_agent.process_async(case)
    
    processed = await agent.process_async(case)
    assert processed.status == CaseStatus.ON_HOLD
    assert "MANDATORY HOLD" in processed.recommendation

@pytest.mark.asyncio
async def test_full_orchestrator_clean_provider():
    repo = CredentialingCaseRepository()
    rag_repo = LocalRagRepository(knowledge_dir="knowledge")
    llm_service = DeterministicLanguageModelService()
    
    agents = [
        CredentialVerificationAgent(),
        LicenseVerificationAgent(MockStateBoardConnector()),
        SanctionCheckAgent(MockSanctionConnector()),
        RiskAssessmentAgent(rag_repo, llm_service),
        WorkflowAgent()
    ]
    orchestrator = CredentialingOrchestrator(agents, repo)

    provider = Provider(npi="1234567890", first_name="Jane", last_name="Doe", provider_type="Medical Doctor", primary_state="CA", license_number="C12345")
    case = CredentialingCase(provider_id=provider.id, provider=provider)

    result = await orchestrator.run_pipeline_async(case)
    assert result.status == CaseStatus.APPROVED
    assert result.risk_classification == RiskClassification.CLEAN
    assert len(result.audit_events) == 5

@pytest.mark.asyncio
async def test_api_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Healthy"

@pytest.mark.asyncio
async def test_api_system_info_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["applicationName"] == "CredentialIQ AI" or data["application_name"] == "CredentialIQ AI"

@pytest.mark.asyncio
async def test_api_create_case_clean_provider():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "npi": "1234567890",
            "firstName": "Jane",
            "lastName": "Doe",
            "providerType": "Medical Doctor",
            "primaryState": "CA",
            "licenseNumber": "C12345"
        }
        response = await ac.post("/api/credentialingcases", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Approved"
    assert data.get("riskClassification") == "Clean" or data.get("risk_classification") == "Clean"
