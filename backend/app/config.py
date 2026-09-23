from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "healthbot"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000

    # Telegram Bot (required)
    TELEGRAM_BOT_TOKEN: str = Field(default="test_token_for_dev", min_length=10)

    # Redis (optional - for rate limiting, falls back to in-memory)
    REDIS_URL: str | None = "redis://localhost:6379/0"

    # Outbreak sources
    WHO_RSS_URL: str = "https://www.who.int/feeds/entity/csr/don/en/rss.xml"
    OUTBREAK_CACHE_TTL_SECONDS: int = 3600

    # Rate limits
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Medical disclaimer
    DISCLAIMER: str = (
        "This bot provides general health information only. "
        "It is NOT a substitute for professional medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare provider."
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
