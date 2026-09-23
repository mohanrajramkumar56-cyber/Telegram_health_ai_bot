import threading
import time

import feedparser
import schedule

WHO_RSS = "https://www.who.int/feeds/entity/csr/don/en/rss.xml"
_latest = {"who": []}

def fetch_who():
    d = feedparser.parse(WHO_RSS)
    _latest["who"] = [{"title": e.title, "link": e.link} for e in d.entries[:10]]

def get_status_text(district=None, state=None):
    fetch_who()
    loc = district or state or "your area"
    lines = [f"\U0001F9A0 Outbreak updates for {loc}:", "• WHO global DONs (latest):"]
    lines += [f"  - {x['title']}" for x in _latest["who"][:3]]
    return "\n".join(lines)

def run_scheduler():
    schedule.every(6).hours.do(fetch_who)
    while True:
        schedule.run_pending()
        time.sleep(30)

def start_alert_scheduler():
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()
