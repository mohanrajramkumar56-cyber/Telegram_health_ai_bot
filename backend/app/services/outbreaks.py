import logging
from datetime import datetime
from threading import Lock
from typing import Any

import feedparser

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_WHO_CACHE: dict[str, Any] = {"data": [], "fetched_at": None}
_CACHE_LOCK = Lock()


def _fetch_who_rss() -> list[dict[str, str]]:
    try:
        d = feedparser.parse(str(settings.WHO_RSS_URL))
        entries = [
            {"title": e.title, "link": e.link, "published": getattr(e, "published", "")}
            for e in d.entries[:10]
        ]
        logger.info("WHO RSS fetched %d entries", len(entries))
        return entries
    except Exception as e:
        logger.warning("WHO RSS fetch failed: %s", e)
        return []


def get_outbreak_data(force_refresh: bool = False) -> list[dict[str, str]]:
    global _WHO_CACHE
    with _CACHE_LOCK:
        now = datetime.utcnow()
        fetched_at = _WHO_CACHE.get("fetched_at")
        if not force_refresh and fetched_at and isinstance(fetched_at, datetime):
            age = (now - fetched_at).total_seconds()
            if age < settings.OUTBREAK_CACHE_TTL_SECONDS and _WHO_CACHE["data"]:
                return _WHO_CACHE["data"]  # type: ignore[no-any-return]

        data = _fetch_who_rss()
        _WHO_CACHE = {"data": data, "fetched_at": now}
        return data


def format_outbreak_response(district: str | None, state: str | None) -> str:
    entries = get_outbreak_data()
    loc = district or state or "your area"
    lines = [f"Outbreak updates for {loc}:", "• WHO global DONs (latest):"]
    for e in entries[:3]:
        lines.append(f"  - {e['title']}")
    lines.append("\n" + settings.DISCLAIMER)
    return "\n".join(lines)
