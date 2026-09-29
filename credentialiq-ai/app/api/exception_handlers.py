"""FastAPI custom exception handlers."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import CaseNotFoundError, CredentialIQException, InvalidCaseStateError
from app.core.logging import logger


async def credentialiq_exception_handler(
    request: Request, exc: CredentialIQException
) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.error(f"Application Exception ({exc.code}): {exc.message}")

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(exc, CaseNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, InvalidCaseStateError):
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "path": str(request.url),
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global unhandled exception fallback handler."""
    logger.error(f"Unhandled Internal Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred.",
            "path": str(request.url),
        },
    )
