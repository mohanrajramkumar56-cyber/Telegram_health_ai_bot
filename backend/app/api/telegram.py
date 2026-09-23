import logging

import httpx
from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.services.kb import get_prevention, get_symptoms, get_vaccine_schedule
from app.services.nlu import classify_intent
from app.services.outbreaks import format_outbreak_response
from app.services.translator import detect_lang, translate

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


async def process_message(text: str, chat_id: int) -> str:
    """Core message processing pipeline."""
    lang = detect_lang(text)
    text_en = translate(text, "en") if lang != "en" else text

    nlu = classify_intent(text_en)
    entities = nlu.entities
    disease = entities.get("disease", "fever")

    if nlu.intent == "ask_symptoms":
        reply_en = get_symptoms(disease)
    elif nlu.intent == "ask_prevention":
        reply_en = get_prevention(disease)
    elif nlu.intent == "ask_vaccine_schedule":
        age = entities.get("age_months", 0)
        reply_en = get_vaccine_schedule(age)
    elif nlu.intent == "ask_outbreak_status":
        reply_en = format_outbreak_response(
            entities.get("district"), entities.get("state")
        )
    elif nlu.intent == "greet":
        reply_en = "Vanakkam! I can help with symptoms, prevention, vaccines & local alerts."
    else:
        reply_en = "Try: 'dengue symptoms', 'prevent malaria', 'vaccines at 6 months', 'outbreak in Coimbatore'."

    return translate(reply_en, lang) if lang != "en" else reply_en


async def send_telegram_message(chat_id: int, text: str) -> bool:
    """Send message via Telegram Bot API."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text[:4000],
                    "parse_mode": "HTML"
                }
            )
            resp.raise_for_status()
            logger.info("Telegram message sent to %s: %s", chat_id, resp.status_code)
            return True
    except Exception as e:
        logger.error("Telegram send failed: %s", e)
        return False


@router.post("/tg/webhook")
async def tg_webhook(request: Request):
    """Handle incoming Telegram updates."""
    try:
        update = await request.json()

        # Handle message or edited_message
        message = update.get("message") or update.get("edited_message")
        if not message or "text" not in message:
            return {"ok": True}

        chat_id = message["chat"]["id"]
        text = message["text"]

        # Process and reply
        reply = await process_message(text, chat_id)
        await send_telegram_message(chat_id, reply)

        return {"ok": True}
    except Exception as e:
        logger.exception("Telegram webhook error: %s", e)
        return {"ok": True}  # Always return 200 to Telegram


@router.get("/tg/set_webhook")
async def set_webhook(url: str):
    """Set Telegram webhook URL."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook",
                json={"url": url, "allowed_updates": ["message", "edited_message"]}
            )
            return resp.json()
    except Exception as e:
        logger.error("Set webhook failed: %s", e)
        raise HTTPException(500, str(e))


@router.get("/tg/webhook_info")
async def webhook_info():
    """Get current webhook info."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getWebhookInfo"
        )
        return resp.json()


# Dev-only simplified endpoint for testing
@router.post("/dev/webhook")
async def dev_webhook(request: Request):
    """Dev endpoint: accepts simple JSON like {'text': '...', 'chat_id': 123}"""
    try:
        body = await request.json()
        text = body.get("text", "")
        chat_id = body.get("chat_id", 123456)
        if text:
            reply = await process_message(text, chat_id)
            return {"chat_id": chat_id, "reply": reply}
        return {"error": "No text provided"}
    except Exception as e:
        logger.exception("Dev webhook error: %s", e)
        return {"error": str(e)}
