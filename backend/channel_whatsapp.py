import os

import httpx

PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY = os.getenv("WHATSAPP_VERIFY_TOKEN","myverify")

def verify_webhook(mode, challenge, token):
    if mode == "subscribe" and token == VERIFY:
        return int(challenge)
    return 403

def send_whatsapp_text(to_number: str, text: str):
    if not TOKEN or not PHONE_ID:
        print("WHATSAPP_TOKEN / PHONE_ID not set — skipping send")
        return
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": text[:4000]}}
    resp = httpx.post(url, headers=headers, json=data, timeout=15)
    print("WhatsApp send status:", resp.status_code)
