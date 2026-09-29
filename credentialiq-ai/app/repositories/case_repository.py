"""Case repository for SQLite persistence."""


from sqlalchemy.orm import Session

from app.models.domain import AuditEventModel, CaseModel


class CaseRepository:
    """Repository handling persistence for cases and audit events."""

    def __init__(self, db: Session):
        self.db = db

    def save_case(self, case_model: CaseModel) -> CaseModel:
        """Create or update a case in the database."""
        existing = self.db.query(CaseModel).filter(CaseModel.case_id == case_model.case_id).first()
        if existing:
            existing.status = case_model.status
            existing.sanitized_intake_json = case_model.sanitized_intake_json
            existing.license_verifications_json = case_model.license_verifications_json
            existing.sanction_screenings_json = case_model.sanction_screenings_json
            existing.risk_assessment_json = case_model.risk_assessment_json
            existing.workflow_recommendation_json = case_model.workflow_recommendation_json
            existing.override_json = case_model.override_json
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(case_model)
            self.db.commit()
            self.db.refresh(case_model)
            return case_model

    def get_case(self, case_id: str) -> CaseModel | None:
        """Fetch a case by ID."""
        return self.db.query(CaseModel).filter(CaseModel.case_id == case_id).first()

    def list_cases(self, limit: int = 100, offset: int = 0) -> list[CaseModel]:
        """List cases ordered by creation time descending."""
        return (
            self.db.query(CaseModel)
            .order_by(CaseModel.created_at_utc.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def add_audit_event(self, audit_event: AuditEventModel) -> AuditEventModel:
        """Add an audit event to a case."""
        self.db.add(audit_event)
        self.db.commit()
        self.db.refresh(audit_event)
        return audit_event

    def get_audit_trail(self, case_id: str) -> list[AuditEventModel]:
        """Retrieve all audit events for a case."""
        return (
            self.db.query(AuditEventModel)
            .filter(AuditEventModel.case_id == case_id)
            .order_by(AuditEventModel.timestamp_utc.asc())
            .all()
        )
