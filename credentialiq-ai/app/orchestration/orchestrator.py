"""Orchestrator coordinating pipeline execution, persistence, and audit logging."""

import uuid

from sqlalchemy.orm import Session

from app.core.enums import AuditEventType, CaseStatus
from app.models.domain import CaseModel
from app.orchestration.graph import build_credentialing_graph
from app.orchestration.state import CredentialingState
from app.repositories.case_repository import CaseRepository
from app.services.audit_service import AuditService


class CredentialingOrchestrator:
    """Orchestrates 5-agent credentialing pipeline and handles persistence."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = CaseRepository(db)
        self.audit_service = AuditService(db)
        self.graph = build_credentialing_graph()

    def process_case(
        self, raw_provider_data: dict, case_id: str | None = None
    ) -> CaseModel:
        """Run provider intake through full 5-agent workflow and persist case."""
        c_id = case_id or str(uuid.uuid4())

        initial_state: CredentialingState = {
            "case_id": c_id,
            "raw_provider_data": raw_provider_data,
            "audit_logs": [
                {
                    "event_type": AuditEventType.INTAKE_RECEIVED.value,
                    "agent_name": "Orchestrator",
                    "details": {"case_id": c_id},
                }
            ],
        }

        # Execute compiled LangGraph workflow
        final_state: CredentialingState = self.graph.invoke(initial_state)

        status_str = final_state.get("final_status", CaseStatus.IN_PROGRESS.value)

        # Build CaseModel entity
        case_model = CaseModel(
            case_id=c_id,
            status=status_str,
            provider_npi=final_state.get("provider_npi", raw_provider_data.get("npi", "0000000000")),
            provider_name=final_state.get(
                "provider_name",
                f"{raw_provider_data.get('first_name', '')} {raw_provider_data.get('last_name', '')}",
            ),
            raw_intake_json=raw_provider_data,
            sanitized_intake_json=final_state.get("sanitized_provider", {}),
            license_verifications_json=final_state.get("license_verifications", []),
            sanction_screenings_json=final_state.get("sanction_screenings", []),
            risk_assessment_json=final_state.get("risk_assessment"),
            workflow_recommendation_json=final_state.get("workflow_recommendation"),
            override_json=None,
        )

        saved_case = self.repo.save_case(case_model)

        # Save all audit events
        for log in final_state.get("audit_logs", []):
            self.audit_service.log_event(
                case_id=c_id,
                event_type=log.get("event_type", AuditEventType.CASE_PERSISTED),
                agent_name=log.get("agent_name", "Orchestrator"),
                details=log.get("details", {}),
            )

        self.audit_service.log_event(
            case_id=c_id,
            event_type=AuditEventType.CASE_PERSISTED,
            agent_name="Orchestrator",
            details={"status": saved_case.status, "case_id": c_id},
        )

        return saved_case
