from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import httpx, os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

class ActionSymptoms(Action):
    def name(self):
        return "action_symptoms"
    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        disease = next(tracker.get_latest_entity_values("disease"), None) or "fever"
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{BACKEND}/kb/symptoms", params={"disease": disease}, timeout=20)
        dispatcher.utter_message(text=r.json().get("answer", "Sorry, no info."))
        return []

class ActionPrevention(Action):
    def name(self):
        return "action_prevention"
    async def run(self, dispatcher, tracker, domain):
        disease = next(tracker.get_latest_entity_values("disease"), None) or "fever"
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{BACKEND}/kb/prevention", params={"disease": disease}, timeout=20)
        dispatcher.utter_message(text=r.json().get("answer", ""))
        return []

class ActionVaccineSchedule(Action):
    def name(self):
        return "action_vaccine_schedule"
    async def run(self, dispatcher, tracker, domain):
        months = next(tracker.get_latest_entity_values("age_months"), None) or "0"
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{BACKEND}/vaccine/schedule", params={"age_months": months}, timeout=20)
        dispatcher.utter_message(text=r.text)
        return []

class ActionOutbreakStatus(Action):
    def name(self):
        return "action_outbreak_status"
    async def run(self, dispatcher, tracker, domain):
        district = next(tracker.get_latest_entity_values("district"), None)
        state = next(tracker.get_latest_entity_values("state"), None)
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{BACKEND}/outbreak/status", params={"district": district, "state": state}, timeout=20)
        dispatcher.utter_message(text=r.text)
        return []
