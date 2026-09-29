"""FastAPI custom middleware."""

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware attaching request correlation IDs and logging execution time."""

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        start_time = time.time()

        request.state.correlation_id = correlation_id

        response = await call_next(request)

        process_time_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time-MS"] = str(process_time_ms)

        logger.info(
            f"[{correlation_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} ({process_time_ms}ms)"
        )

        return response
