from fastapi import APIRouter
from app.core.dto import SystemInfoResponse

router = APIRouter(prefix="/api/system", tags=["System"])

@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info():
    return SystemInfoResponse()
