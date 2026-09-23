import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4())[:8])
        request.state.correlation_id = correlation_id

        logger = logging.getLogger("healthbot.request")
        start = time.perf_counter()

        logger.info(
            "Request started",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )

        try:
            response: Response = await call_next(request)
        except Exception as e:
            logger.exception(
                "Request failed",
                extra={"correlation_id": correlation_id, "error": str(e)},
            )
            raise

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "Request completed",
            extra={
                "correlation_id": correlation_id,
                "status": response.status_code,
                "duration_ms": round(duration, 2),
            },
        )
        response.headers["X-Correlation-ID"] = correlation_id
        return response
