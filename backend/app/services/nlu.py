import logging
import re
from typing import Any

from app.schemas import Intent, NLUResult

logger = logging.getLogger(__name__)

DISEASE_KEYWORDS = {
    "dengue": ["dengue", "breakbone", "bone fever"],
    "malaria": ["malaria", "malarial"],
    "covid": ["covid", "corona", "covid-19", "covid19", "sars-cov-2"],
    "chikungunya": ["chikungunya", "chikun"],
    "typhoid": ["typhoid", "enteric fever"],
    "tb": ["tb", "tuberculosis"],
}

INTENT_PATTERNS = [
    (Intent.ASK_SYMPTOMS, [
        r"\b(symptom|sign|indication)s?\b",
        r"\b(how (do|can) (i|you) know)\b",
        r"\b(what (is|are) the)\b.*\b(symptom|sign)s?\b",
    ]),
    (Intent.ASK_PREVENTION, [
        r"\b(prevent|avoid|protect|stop|control)\b",
        r"\b(how (to|can) (prevent|avoid|stop))\b",
    ]),
    (Intent.ASK_VACCINE_SCHEDULE, [
        r"\b(vaccine|vaccination|immuniz|shot)s?\b",
        r"\b(schedule|chart|calendar|when)\b.*\b(vaccine|vaccination|immuniz)s?\b",
    ]),
    (Intent.ASK_OUTBREAK_STATUS, [
        r"\b(outbreak|case|spread|alert)s?\b",
        r"\b(dengue|malaria|chikungunya)\b.*\b(in|at|near)\b",
        r"\b(any|any)\b.*\b(outbreak|case)s?\b",
    ]),
    (Intent.GREET, [
        r"^(hi|hello|hey|vanakkam|namaste|hii)\b",
    ]),
]

AGE_PATTERN = re.compile(r"\b(\d{1,3})\s*(?:month|mo|m)s?\b", re.IGNORECASE)
DISTRICT_PATTERN = re.compile(r"\b(in|at|near|around)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", re.IGNORECASE)
STATE_PATTERN = re.compile(r"\b(in|at|near|around)\s+(Tamil Nadu|Kerala|Karnataka|Maharashtra|Delhi|Gujarat|UP|Uttar Pradesh|Bengal|West Bengal|Punjab|Haryana|Rajasthan|MP|Madhya Pradesh|Odisha|Assam|Jharkhand|Chhattisgarh|Uttarakhand|Himachal|Jammu|Kashmir|Goa|Tripura|Manipur|Meghalaya|Nagaland|Mizoram|Arunachal|Sikkim|Telangana|Andhra|Andhra Pradesh)", re.IGNORECASE)


def extract_entities(text: str) -> dict[str, Any]:
    entities: dict[str, Any] = {}
    text_lower = text.lower()

    # Disease
    for disease, keywords in DISEASE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            entities["disease"] = disease
            break

    # Age months
    age_match = AGE_PATTERN.search(text)
    if age_match:
        entities["age_months"] = int(age_match.group(1))

    # District
    dist_match = DISTRICT_PATTERN.search(text)
    if dist_match:
        entities["district"] = dist_match.group(2).title()

    # State
    state_match = STATE_PATTERN.search(text)
    if state_match:
        entities["state"] = state_match.group(2).title()

    return entities


def classify_intent(text: str) -> NLUResult:
    text_lower = text.lower().strip()

    # Short-circuit greetings
    if any(text_lower.startswith(g) for g in ["hi", "hello", "hey", "vanakkam", "namaste"]):
        return NLUResult(intent=Intent.GREET, confidence=0.95, entities={})

    best_intent = Intent.FALLBACK
    best_score = 0.0

    for intent, patterns in INTENT_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text_lower):
                score = 0.85 + (0.1 if intent != Intent.FALLBACK else 0)
                if score > best_score:
                    best_score = score
                    best_intent = intent

    entities = extract_entities(text)
    return NLUResult(intent=best_intent, confidence=best_score, entities=entities)
