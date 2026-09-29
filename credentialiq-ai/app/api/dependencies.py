"""FastAPI dependency injection utilities."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.repositories.case_repository import CaseRepository
from app.repositories.rag_repository import RAGRepository
from app.services.audit_service import AuditService


def get_case_repository(db: Session = Depends(get_db)) -> CaseRepository:
    """Dependency providing CaseRepository instance."""
    return CaseRepository(db)


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Dependency providing AuditService instance."""
    return AuditService(db)


# Global singleton instance for RAG repository to avoid re-indexing on every API call
_rag_repo_instance: RAGRepository | None = None


def get_rag_repository() -> RAGRepository:
    """Dependency providing global RAGRepository instance."""
    global _rag_repo_instance
    if _rag_repo_instance is None:
        _rag_repo_instance = RAGRepository()
    return _rag_repo_instance
