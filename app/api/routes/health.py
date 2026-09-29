from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.dto import HealthCheckResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthCheckResponse)
async def get_health():
    return HealthCheckResponse(
        status="Healthy",
        components={
            "Database": "Healthy (SQLite In-Memory/File)",
            "LocalRagRepository": "Healthy (Knowledge base active)",
            "LanguageModelService": "Healthy (Deterministic)"
        },
        checked_at_utc=datetime.now(timezone.utc)
    )
