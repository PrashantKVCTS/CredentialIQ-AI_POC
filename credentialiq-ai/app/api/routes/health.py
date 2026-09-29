"""Health check API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Basic health status")
def health_check():
    """Returns application name and status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
    }


@router.get("/health/ready", summary="Readiness probe")
def readiness_check(db: Session = Depends(get_db)):
    """Verifies database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "unready", "database": str(e)}


@router.get("/health/live", summary="Liveness probe")
def liveness_check():
    """Liveness probe for container/service orchestrators."""
    return {"status": "alive"}
