import os

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456789:TEST_TOKEN_ABCDEFGHIJKLMNOPQRSTUVWXYZ")
os.environ.setdefault("REDIS_URL", "")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness():
    r = client.get("/live")
    assert r.status_code == 200
    assert r.json()["status"] == "alive"


def test_kb_symptoms_dengue():
    r = client.get("/kb/symptoms?disease=dengue")
    assert r.status_code == 200
    assert "dengue" in r.json()["answer"].lower()
    assert "fever" in r.json()["answer"].lower()


def test_kb_symptoms_unknown():
    r = client.get("/kb/symptoms?disease=unknown_disease_xyz")
    assert r.status_code == 200
    assert "common symptoms" in r.json()["answer"].lower()


def test_kb_prevention_malaria():
    r = client.get("/kb/prevention?disease=malaria")
    assert r.status_code == 200
    assert "malaria" in r.json()["answer"].lower()
    assert "mosquito" in r.json()["answer"].lower()


def test_vaccine_schedule_6_months():
    r = client.get("/kb/vaccine/schedule?age_months=6")
    assert r.status_code == 200
    assert "6 months" in r.json()["answer"]
    assert "DPT" in r.json()["answer"]


def test_vaccine_schedule_invalid_age():
    r = client.get("/kb/vaccine/schedule?age_months=-1")
    assert r.status_code == 422  # validation error


def test_outbreak_status():
    r = client.get("/kb/outbreak/status?district=Coimbatore")
    assert r.status_code == 200
    assert "Coimbatore" in r.json()["status"]
    assert "WHO" in r.json()["status"]


def test_telegram_webhook():
    r = client.post(
        "/tg/webhook",
        json={"message": {"chat": {"id": 123456}, "text": "dengue symptoms"}},
    )
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_rate_limit_headers():
    # Skip - requires Redis
    pass
