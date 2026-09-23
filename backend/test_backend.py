from fastapi.testclient import TestClient

from app import app
from translator import detect_lang, translate

client = TestClient(app)

# Test translator
print('detect_lang("hello"):', detect_lang('hello'))
print('detect_lang("vanakkam"):', detect_lang('vanakkam'))
print('detect_lang("I have fever and headache"):', detect_lang('I have fever and headache'))
print('translate("hello", "ta"):', translate('hello', 'ta'))  # No Azure key, should fallback

# Test vaccine_service
from vaccine_service import get_vaccine_text

print('get_vaccine_text(6):', get_vaccine_text(6))

# Test outbreak_service (without emoji issue)
from outbreak_service import _latest, fetch_who

fetch_who()
print('WHO entries fetched:', len(_latest['who']))

# Test kb endpoints
r = client.get('/kb/symptoms?disease=dengue')
print('GET /kb/symptoms?disease=dengue:', r.status_code, r.json())

r = client.get('/kb/prevention?disease=malaria')
print('GET /kb/prevention?disease=malaria:', r.status_code, r.json())

r = client.get('/vaccine/schedule?age_months=6')
print('GET /vaccine/schedule?age_months=6:', r.status_code, r.text)

r = client.get('/outbreak/status?district=Coimbatore')
print('GET /outbreak/status?district=Coimbatore:', r.status_code, r.json())

# Test WhatsApp webhook verify
r = client.get('/wa/webhook?hub_mode=subscribe&hub_challenge=12345&hub_verify_token=myverify')
print('GET /wa/webhook verify:', r.status_code, r.text)

print("\nAll backend unit tests passed!")
