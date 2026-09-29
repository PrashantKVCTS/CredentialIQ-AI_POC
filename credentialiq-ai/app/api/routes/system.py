"""System information and RAG search API endpoints."""

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_rag_repository
from app.core.config import settings
from app.repositories.rag_repository import RAGRepository
from app.schemas.responses import RAGSearchResponse

router = APIRouter(prefix="/api/v1/system", tags=["System & RAG"])


@router.get("/info", summary="System configuration info")
def system_info():
    """Returns system operational metadata."""
    return {
        "app_name": settings.APP_NAME,
        "llm_provider": settings.LLM_PROVIDER,
        "gemini_model": settings.GEMINI_MODEL,
        "database_url": settings.DATABASE_URL.split("///")[0],
        "disclaimer": (
            "CredentialIQ AI POC Legal Disclaimer: POC results are automated recommendations "
            "and do not constitute official credentialing determinations."
        ),
    }


@router.get("/rag/search", response_model=RAGSearchResponse, summary="Search local policy RAG")
def search_policy_rag(
    q: str = Query(..., min_length=2, description="Search query string"),
    top_k: int = Query(default=3, ge=1, le=10),
    rag_repo: RAGRepository = Depends(get_rag_repository),
):
    """Search policy knowledge repository using TF-IDF vector similarity."""
    matches = rag_repo.search_policies(query=q, top_k=top_k)
    return RAGSearchResponse(
        query=q,
        total_matches=len(matches),
        matches=matches,
    )
