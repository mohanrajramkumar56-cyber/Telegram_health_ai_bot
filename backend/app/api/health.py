from fastapi import APIRouter

from app.config import get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/live", response_model=HealthResponse)
async def liveness():
    return HealthResponse(
        status="alive", version="1.0.0", services={"redis": "unknown", "who": "unknown"}
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness():
    # Check Redis
    redis_status = "unknown"
    try:
        import redis.asyncio as redis
        r = redis.Redis.from_url(settings.REDIS_URL)
        await r.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "down"

    # Check WHO RSS (quick)
    who_status = "unknown"
    try:
        import feedparser
        d = feedparser.parse(str(settings.WHO_RSS_URL))
        who_status = "ok" if d.entries else "empty"
    except Exception:
        who_status = "down"

    return HealthResponse(
        status="ready" if redis_status == "ok" else "degraded",
        version="1.0.0",
        services={"redis": redis_status, "who": who_status},
    )
