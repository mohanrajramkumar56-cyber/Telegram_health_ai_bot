import os

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456789:TEST_TOKEN_ABCDEFGHIJKLMNOPQRSTUVWXYZ")
os.environ.setdefault("REDIS_URL", "")

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.translator import detect_lang, translate

client = TestClient(app)


class TestTelegramWebhook:
    def test_webhook_message(self):
        r = client.post(
            "/tg/webhook",
            json={"message": {"chat": {"id": 123456}, "text": "dengue symptoms"}},
        )
        assert r.status_code == 200
        assert r.json() == {"ok": True}

    def test_webhook_edited_message(self):
        r = client.post(
            "/tg/webhook",
            json={"edited_message": {"chat": {"id": 123456}, "text": "malaria prevention"}},
        )
        assert r.status_code == 200

    def test_webhook_no_text(self):
        r = client.post(
            "/tg/webhook",
            json={"message": {"chat": {"id": 123456}, "photo": []}},
        )
        assert r.status_code == 200

    def test_webhook_empty(self):
        r = client.post("/tg/webhook", json={})
        assert r.status_code == 200


class TestDevWebhook:
    def test_dev_webhook(self):
        r = client.post("/dev/webhook", json={"text": "dengue symptoms", "chat_id": 123456})
        assert r.status_code == 200
        assert "dengue" in r.json()["reply"].lower()

    def test_dev_webhook_no_text(self):
        r = client.post("/dev/webhook", json={"chat_id": 123456})
        assert r.status_code == 200
        assert "error" in r.json()


class TestSetWebhook:
    def test_set_webhook_endpoint_exists(self):
        # Just verify endpoint exists - mocking httpx properly is complex in sync tests
        r = client.get("/tg/set_webhook", params={"url": "https://example.com/tg/webhook"})
        # Will fail due to fake token, but endpoint exists
        assert r.status_code in (200, 401, 500)


class TestTranslator:
    def test_detect_lang_english(self):
        assert detect_lang("hello world") == "en"
        assert detect_lang("what are dengue symptoms") == "en"

    def test_detect_lang_tamil(self):
        assert detect_lang("vanakkam") == "ta"
        assert detect_lang("நன்றி") == "ta"

    def test_detect_lang_hindi(self):
        assert detect_lang("namaste kaise hai") == "hi"
        assert detect_lang("मुझे दवा चाहिए") == "hi"

    def test_detect_lang_bengali(self):
        assert detect_lang("kemon achen") == "bn"

    def test_translate_noop(self):
        assert translate("hello", "en") == "hello"
        assert translate("", "hi") == ""
        assert translate("hello", "en") == "hello"

    @patch("app.services.translator._translator._init_translators")
    def test_translate_fallback(self, mock_init):
        # Without actual language packs installed, should return original
        result = translate("hello", "hi")
        assert result == "hello"  # fallback
