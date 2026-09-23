import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
VACC = json.loads(Path(BASE / "kb" / "vaccine_schedule_india.json").read_text(encoding="utf-8"))

def get_vaccine_text(age_months: int):
    age = int(age_months)
    closest = min(VACC, key=lambda x: abs(x["age_months"] - age))
    items = [f"- {v['name']} ({v['dose']})" for v in closest["vaccines"]]
    return "\n".join([f"Vaccines at ~{closest['age_months']} months:"] + items)
