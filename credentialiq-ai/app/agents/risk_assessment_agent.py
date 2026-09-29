"""Agent 4: Risk Assessment Agent."""

from typing import Any

from app.agents.base import BaseAgent
from app.core.enums import AuditEventType
from app.repositories.rag_repository import RAGRepository
from app.schemas.common import LicenseEvidenceResult, SanctionEvidenceResult
from app.services.language_model import LanguageModelService


class RiskAssessmentAgent(BaseAgent):
    """Retrieves compliance rules from local RAG repository and assesses risk via LLM/Deterministic engine."""

    def __init__(
        self,
        rag_repo: RAGRepository | None = None,
        llm_service: LanguageModelService | None = None,
    ):
        super().__init__(name="RiskAssessmentAgent")
        self.rag_repo = rag_repo or RAGRepository()
        self.llm_service = llm_service or LanguageModelService()

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Retrieve policies and assess provider risk."""
        provider_intake = state.get("provider_intake", {})
        sanitized_provider = state.get("sanitized_provider", provider_intake)

        license_dicts = state.get("license_verifications", [])
        sanction_dicts = state.get("sanction_screenings", [])

        license_models = [LicenseEvidenceResult(**d) for d in license_dicts]
        sanction_models = [SanctionEvidenceResult(**d) for d in sanction_dicts]

        # Formulate RAG search query
        specialty = provider_intake.get("specialty", "physician")
        states = [lic.get("state") for lic in provider_intake.get("licenses", []) if lic.get("state")]
        state_str = " ".join(states) if states else "state medical board"

        has_disc = any(lic_item.has_disciplinary_action for lic_item in license_models)
        has_sanction = any(s.match_found for s in sanction_models)

        query = f"credentialing compliance {specialty} {state_str} license verification sanction screening"
        if has_sanction or has_disc:
            query += " exclusion discipline sanction hold exception"

        # 1. Local RAG Retrieval
        policies = self.rag_repo.search_policies(query=query, top_k=3)

        audit_logs = list(state.get("audit_logs", []))

        audit_logs.append(
            {
                "event_type": AuditEventType.RAG_RETRIEVED.value,
                "agent_name": self.name,
                "details": {
                    "query": query,
                    "matched_chunks_count": len(policies),
                    "policy_ids": [p.chunk_id for p in policies],
                },
            }
        )

        # 2. Risk Evaluation (LLM / Deterministic)
        risk_result = self.llm_service.evaluate_risk(
            provider_data=sanitized_provider,
            licenses=license_models,
            sanctions=sanction_models,
            policies=policies,
        )

        audit_logs.append(
            {
                "event_type": AuditEventType.RISK_ASSESSED.value,
                "agent_name": self.name,
                "details": {
                    "risk_level": risk_result.risk_level.value,
                    "score": risk_result.score,
                    "summary": risk_result.summary,
                    "risk_factors_count": len(risk_result.risk_factors),
                },
            }
        )

        return {
            "retrieved_policies": [p.model_dump() for p in policies],
            "risk_assessment": risk_result.model_dump(),
            "audit_logs": audit_logs,
        }
