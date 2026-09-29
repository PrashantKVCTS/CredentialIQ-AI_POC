"""Audit service for logging immutable audit trail events."""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.enums import AuditEventType
from app.models.domain import AuditEventModel
from app.repositories.case_repository import CaseRepository


class AuditService:
    """Service for recording audit trail events."""

    def __init__(self, db: Session):
        self.repo = CaseRepository(db)

    def log_event(
        self,
        case_id: str,
        event_type: AuditEventType | str,
        agent_name: str,
        details: dict[str, Any],
    ) -> AuditEventModel:
        """Record an immutable audit event."""
        event_str = event_type.value if isinstance(event_type, AuditEventType) else str(event_type)

        audit_model = AuditEventModel(
            case_id=case_id,
            event_type=event_str,
            agent_name=agent_name,
            timestamp_utc=datetime.utcnow(),
            details_json=details,
        )

        return self.repo.add_audit_event(audit_model)
