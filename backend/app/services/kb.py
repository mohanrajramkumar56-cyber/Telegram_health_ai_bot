import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
BASE = Path(__file__).resolve().parent.parent.parent

_KB_CACHE: dict[str, Any] = {}
_VACC_CACHE: list[dict[str, Any]] = []


@lru_cache(maxsize=1)
def _load_kb() -> dict[str, Any]:
    global _KB_CACHE
    if not _KB_CACHE:
        path = BASE / "kb" / "faq_health.json"
        _KB_CACHE = json.loads(path.read_text(encoding="utf-8"))
        logger.info("KB loaded: %d diseases", len(_KB_CACHE))
    return _KB_CACHE


@lru_cache(maxsize=1)
def _load_vaccines() -> list[dict[str, Any]]:
    global _VACC_CACHE
    if not _VACC_CACHE:
        path = BASE / "kb" / "vaccine_schedule_india.json"
        _VACC_CACHE = json.loads(path.read_text(encoding="utf-8"))
        logger.info("Vaccine schedule loaded: %d age points", len(_VACC_CACHE))
    return _VACC_CACHE


def get_symptoms(disease: str) -> str:
    kb = _load_kb()
    d = kb.get(disease.lower())
    if not d:
        return "Common symptoms: fever, cough, fatigue. Ask a specific disease like dengue."
    return f"Symptoms of {disease.title()}: " + ", ".join(d["symptoms"])


def get_prevention(disease: str) -> str:
    kb = _load_kb()
    d = kb.get(disease.lower())
    if not d:
        return "General prevention: hand hygiene, safe water, vector control."
    return f"Prevention for {disease.title()}: " + ", ".join(d["prevention"])


def get_vaccine_schedule(age_months: int) -> str:
    vacc = _load_vaccines()
    age = int(age_months)
    closest = min(vacc, key=lambda x: abs(x["age_months"] - age))
    lines = [f"Vaccines at ~{closest['age_months']} months:"]
    for v in closest["vaccines"]:
        lines.append(f"- {v['name']} ({v['dose']})")
    return "\n".join(lines)
