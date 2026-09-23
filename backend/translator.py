import os

import httpx
from langdetect import detect

AZ_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
AZ_REGION = os.getenv("AZURE_TRANSLATOR_REGION")
ENDPOINT = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"

def detect_lang(text: str):
    try:
        return detect(text)
    except Exception:
        return "en"

def translate(text: str, target: str = "en"):
    if not text or target == "en":
        return text
    if not AZ_KEY:
        # fallback: no real translation available, return original
        return text
    headers = {
        "Ocp-Apim-Subscription-Key": AZ_KEY,
        "Ocp-Apim-Subscription-Region": AZ_REGION,
        "Content-Type": "application/json"
    }
    body = [{"text": text}]
    url = f"{ENDPOINT}&to={target}"
    r = httpx.post(url, headers=headers, json=body, timeout=15)
    try:
        return r.json()[0]["translations"][0]["text"]
    except Exception:
        return text
