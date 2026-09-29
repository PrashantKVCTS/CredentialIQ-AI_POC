"""SQLAlchemy domain models for persistence."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class CaseModel(Base):
    """Database entity representing a provider credentialing case."""

    __tablename__ = "cases"

    case_id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Draft")
    provider_npi: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    provider_name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at_utc: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # JSON stored data
    raw_intake_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    sanitized_intake_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    license_verifications_json: Mapped[list] = mapped_column(JSON, default=list)
    sanction_screenings_json: Mapped[list] = mapped_column(JSON, default=list)
    risk_assessment_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    workflow_recommendation_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    override_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    audit_events: Mapped[list["AuditEventModel"]] = relationship(
        "AuditEventModel", back_populates="case", cascade="all, delete-orphan"
    )


class AuditEventModel(Base):
    """Database entity representing immutable audit log events."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict)

    case: Mapped["CaseModel"] = relationship("CaseModel", back_populates="audit_events")
