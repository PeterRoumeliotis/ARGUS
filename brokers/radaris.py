from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from models import ClientProfile, BrokerResult
from utils import polite_get, jitter_sleep

BASE = "https://radaris.com"

def search(profile: ClientProfile) -> BrokerResult:
    name_path = "-".join([p for p in profile.name.split() if p])
    q = profile.name
    if profile.city:
        q += f" {profile.city}"
    if profile.state:
        q += f" {profile.state}"
    url = f"{BASE}/p/{quote_plus(name_path)}?search={quote_plus(q)}"
    r = polite_get(url, timeout=10.0, attempts=2, allow_fail=True)
    html = getattr(r, "text", "") or ""
    found = False
    title = None
    if html:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True).lower()
        parts = profile.name.split()
        if parts and len(parts) >= 2:
            first, last = parts[0].lower(), parts[-1].lower()
            found = (first in text and last in text)
        elif parts:
            found = parts[0].lower() in text
        h = soup.find(["h1","h2","title"]) or None
        if h:
            title = h.get_text(" ", strip=True)[:160]
    jitter_sleep()
    return BrokerResult(
        broker="Radaris",
        found=found,
        url=url,
        title=title,
        notes="Opt-out: https://radaris.com/page/how-to-remove"
    )

