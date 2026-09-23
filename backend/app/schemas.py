from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Intent(str, Enum):
    GREET = "greet"
    ASK_SYMPTOMS = "ask_symptoms"
    ASK_PREVENTION = "ask_prevention"
    ASK_VACCINE_SCHEDULE = "ask_vaccine_schedule"
    ASK_OUTBREAK_STATUS = "ask_outbreak_status"
    FALLBACK = "fallback"


class NLUResult(BaseModel):
    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    entities: dict = Field(default_factory=dict)


class WhatsAppIncoming(BaseModel):
    object: str
    entry: list[dict]


class WebhookTextMessage(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    from_number: str = Field(..., alias="from")
    language: str | None = None

    @field_validator("from_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return v.strip().replace(" ", "").replace("-", "")


class WebhookResponse(BaseModel):
    to: str
    reply: str


class KBQuery(BaseModel):
    disease: str = Field(default="fever", min_length=1, max_length=50)

    @field_validator("disease")
    @classmethod
    def normalize(cls, v: str) -> str:
        return v.strip().lower()


class VaccineQuery(BaseModel):
    age_months: int = Field(default=0, ge=0, le=240)


class OutbreakQuery(BaseModel):
    district: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict
