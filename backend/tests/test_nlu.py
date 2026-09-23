import os

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456789:TEST_TOKEN_ABCDEFGHIJKLMNOPQRSTUVWXYZ")
os.environ.setdefault("REDIS_URL", "")

from app.services.nlu import Intent, classify_intent, extract_entities


class TestIntentClassification:
    def test_greet(self):
        result = classify_intent("hi")
        assert result.intent == Intent.GREET
        assert result.confidence > 0.9

    def test_greet_vanakkam(self):
        result = classify_intent("vanakkam")
        assert result.intent == Intent.GREET

    def test_ask_symptoms_dengue(self):
        result = classify_intent("what are the symptoms of dengue")
        assert result.intent == Intent.ASK_SYMPTOMS
        assert result.entities.get("disease") == "dengue"

    def test_ask_symptoms_malaria(self):
        result = classify_intent("malaria symptoms")
        assert result.intent == Intent.ASK_SYMPTOMS
        assert result.entities.get("disease") == "malaria"

    def test_ask_prevention(self):
        result = classify_intent("how to prevent dengue")
        assert result.intent == Intent.ASK_PREVENTION
        assert result.entities.get("disease") == "dengue"

    def test_ask_vaccine_schedule(self):
        result = classify_intent("vaccine schedule for 6 months baby")
        assert result.intent == Intent.ASK_VACCINE_SCHEDULE
        assert result.entities.get("age_months") == 6

    def test_ask_outbreak_district(self):
        result = classify_intent("dengue cases in Coimbatore")
        assert result.intent == Intent.ASK_OUTBREAK_STATUS
        assert result.entities.get("disease") == "dengue"
        assert result.entities.get("district") == "Coimbatore"

    def test_ask_outbreak_state(self):
        result = classify_intent("any outbreak in Tamil Nadu")
        assert result.intent == Intent.ASK_OUTBREAK_STATUS
        assert result.entities.get("state") == "Tamil Nadu"

    def test_fallback(self):
        result = classify_intent("asdfghjkl random nonsense")
        assert result.intent == Intent.FALLBACK


class TestEntityExtraction:
    def test_age_extraction(self):
        entities = extract_entities("vaccines at 9 months")
        assert entities.get("age_months") == 9

    def test_disease_extraction(self):
        entities = extract_entities("chikungunya symptoms")
        assert entities.get("disease") == "chikungunya"

    def test_district_extraction(self):
        entities = extract_entities("cases in Chennai")
        assert entities.get("district") == "Chennai"

    def test_state_extraction(self):
        entities = extract_entities("outbreak in Kerala")
        assert entities.get("state") == "Kerala"
