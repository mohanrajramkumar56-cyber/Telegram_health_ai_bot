import os

from twilio.rest import Client

SID = os.getenv("TWILIO_SID")
TOK = os.getenv("TWILIO_TOKEN")
FROM = os.getenv("TWILIO_FROM")

_client = None
if SID and TOK:
    _client = Client(SID, TOK)

def send_sms_text(to, text):
    if not _client or not FROM:
        print("Twilio not configured — skipping SMS")
        return
    _client.messages.create(to=to, from_=FROM, body=text[:140])
