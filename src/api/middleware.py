"""
Custom middleware for request logging and error handling.
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.services.audit_logger import audit_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all incoming requests with timing information."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        # Log incoming request
        audit_logger.info(
            f"[{request_id}] → {request.method} {request.url.path} "
            f"| Client: {request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = (time.perf_counter() - start_time) * 1000
            audit_logger.error(
                f"[{request_id}] ✗ {request.method} {request.url.path} "
                f"| Error: {str(exc)} | {process_time:.2f}ms"
            )
            raise

        process_time = (time.perf_counter() - start_time) * 1000

        # Log response
        audit_logger.info(
            f"[{request_id}] ← {request.method} {request.url.path} "
            f"| Status: {response.status_code} | {process_time:.2f}ms"
        )

        # Add timing header
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        response.headers["X-Request-Id"] = request_id

        return response
