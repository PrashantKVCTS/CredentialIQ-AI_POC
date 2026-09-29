"""API routes module."""

from app.api.routes.cases import router as cases_router
from app.api.routes.health import router as health_router
from app.api.routes.system import router as system_router

__all__ = ["health_router", "system_router", "cases_router"]
