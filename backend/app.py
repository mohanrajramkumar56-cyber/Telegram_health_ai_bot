import json
import os
from pathlib import Path

import feedparser
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from outbreak_service import start_alert_scheduler
from translator import detect_lang, translate

load_dotenv()
BASE = Path(__file__).resolve().parent
KB = json.loads(Path(BASE / "kb" / "faq_health.json").read_text(encoding="utf-8"))
VACC = json.loads(Path(BASE / "kb" / "vaccine_schedule_india.json").read_text(encoding="utf-8"))

RASA_URL = os.getenv("RASA_URL", "http://localhost:5005/webhooks/rest/webhook")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "myverify")

app = FastAPI()
start_alert_scheduler()

# Simple health KB endpoints used by Rasa actions
@app.get("/kb/symptoms")
def kb_symptoms(disease: str = "fever"):
    d = KB.get((disease or "").lower())
    if not d:
        return {"answer": "Common symptoms: fever, cough, fatigue. Ask a specific disease like dengue."}
    return {"answer": f"Symptoms of {disease.title()}: " + ", ".join(d["symptoms"]) }

@app.get("/kb/prevention")
def kb_prev(disease: str = "fever"):
    d = KB.get((disease or "").lower())
    if not d:
        return {"answer": "General prevention: hand hygiene, safe water, vector control."}
    return {"answer": f"Prevention for {disease.title()}: " + ", ".join(d["prevention"]) }

@app.get("/vaccine/schedule")
def vaccine_schedule(age_months: int = 0):
    age = int(age_months)
    closest = min(VACC, key=lambda x: abs(x["age_months"] - age))
    lines = [f"Vaccines at ~{closest['age_months']} months:"]
    for v in closest["vaccines"]:
        lines.append(f"- {v['name']} ({v['dose']})")
    return JSONResponse("\n".join(lines), media_type="text/plain")

@app.get("/outbreak/status")
def outbreak_status(district: str = None, state: str = None):
    WHO_RSS = "https://www.who.int/feeds/entity/csr/don/en/rss.xml"
    d = feedparser.parse(WHO_RSS)
    entries = [e.title for e in d.entries[:3]]
    loc = district or state or "your area"
    lines = [f"Outbreak updates for {loc}:", *["• " + t for t in entries]]
    return {"status": "\n".join(lines)}

# Minimal WhatsApp webhook simulator for Meta verification
@app.get("/wa/webhook")
def wa_verify(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    return 403

@app.post("/wa/webhook")
async def wa_incoming(req: Request):
    payload = await req.json()
    # This endpoint is written to handle WhatsApp Cloud API payloads. For local testing you can POST
    # simple JSON like: {"text":"dengue symptoms","from":"919876543210"}
    if payload.get("text") and payload.get("from"):
        text = payload["text"]
        from_num = payload["from"]
        lang = detect_lang(text)
        text_en = translate(text, target="en") if lang != "en" else text
        # Send to Rasa REST webhook
        import httpx
        async with httpx.AsyncClient() as c:
            r = await c.post(RASA_URL, json={"sender": from_num, "message": text_en})
            replies = [m.get("text") for m in r.json() if m.get("text")]
        final = translate("\n".join(replies), target=lang) if lang != "en" else "\n".join(replies)
        # For simplicity, return response instead of sending via Meta
        return {"to": from_num, "reply": final}
    return {"status": "no-action"}
