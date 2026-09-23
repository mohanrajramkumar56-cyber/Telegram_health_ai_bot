import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, kb, telegram
from app.config import get_settings
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.services.outbreaks import get_outbreak_data

settings = get_settings()

# Configure JSON logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger = logging.getLogger("healthbot.startup")
    logger.info("Starting HealthBot...")
    get_outbreak_data()  # Prime cache
    logger.info("Cache primed, ready")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="HealthBot API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENV != "production" else None,
    redoc_url=None,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENV != "production" else [],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(kb.router, prefix="/kb", tags=["knowledge-base"])
app.include_router(telegram.router, tags=["telegram"])
