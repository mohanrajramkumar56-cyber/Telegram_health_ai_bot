import logging
import time
from collections import defaultdict
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# In-memory fallback (used when Redis unavailable or disabled)
_request_counts: dict[str, list[float]] = defaultdict(list)
_redis_client: Any = None


async def _get_redis():
    global _redis_client
    if not settings.REDIS_URL:
        return None
    if _redis_client is None:
        try:
            import redis.asyncio as redis
            _redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            await _redis_client.ping()
            logger.info("Redis connected for rate limiting")
        except Exception as e:
            logger.warning("Redis unavailable, using in-memory rate limiting: %s", e)
            _redis_client = None
    return _redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app, max_requests: int | None = None, window_seconds: int | None = None
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS

    async def dispatch(self, request: Request, call_next) -> JSONResponse | Any:
        # Skip rate limiting for health checks and Telegram webhook
        if request.url.path.startswith("/health") or request.url.path.startswith("/tg"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{request.url.path}"
        now = time.time()

        # Try Redis first
        r = await _get_redis()
        if r:
            try:
                pipe = r.pipeline()
                pipe.zremrangebyscore(key, 0, now - self.window_seconds)
                pipe.zcard(key)
                pipe.zadd(key, {str(now): now})
                pipe.expire(key, self.window_seconds)
                results = await pipe.execute()
                current = results[1]

                if current >= self.max_requests:
                    logger.warning("Rate limit exceeded: %s %s", client_ip, request.url.path)
                    return JSONResponse(
                        {"error": "Rate limit exceeded. Please slow down."},
                        status_code=429,
                        headers={"Retry-After": str(self.window_seconds)},
                    )

                response = await call_next(request)
                response.headers["X-RateLimit-Limit"] = str(self.max_requests)
                response.headers["X-RateLimit-Remaining"] = str(max(0, self.max_requests - current))
                return response
            except Exception as e:
                logger.warning("Redis rate limiter error, falling back to memory: %s", e)

        # In-memory fallback
        _request_counts[key] = [t for t in _request_counts[key] if now - t < self.window_seconds]
        current = len(_request_counts[key])

        if current >= self.max_requests:
            return JSONResponse(
                {"error": "Rate limit exceeded. Please slow down."},
                status_code=429,
                headers={"Retry-After": str(self.window_seconds)},
            )

        _request_counts[key].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.max_requests - current))
        return response
