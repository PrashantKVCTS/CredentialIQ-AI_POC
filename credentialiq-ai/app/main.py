"""FastAPI application entrypoint for CredentialIQ AI POC."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import credentialiq_exception_handler, global_exception_handler
from app.api.middleware import RequestCorrelationMiddleware
from app.api.routes import cases_router, health_router, system_router
from app.core.config import settings
from app.core.exceptions import CredentialIQException
from app.core.logging import logger
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown events."""
    logger.info("Initializing CredentialIQ AI database schema...")
    init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("CredentialIQ AI application shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic Healthcare Provider Credentialing & Compliance Proof of Concept",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(RequestCorrelationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(CredentialIQException, credentialiq_exception_handler)  # type: ignore
app.add_exception_handler(Exception, global_exception_handler)

# Include Routers
app.add_api_route("/", lambda: {"message": f"Welcome to {settings.APP_NAME}", "docs": "/docs"})
app.include_router(health_router)
app.include_router(system_router)
app.include_router(cases_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
