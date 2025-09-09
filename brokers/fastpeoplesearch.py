from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from models import ClientProfile, BrokerResult
from utils import polite_get, jitter_sleep

BASE = "https://www.fastpeoplesearch.com"

def _name_path(name: str) -> str:
    parts = [p for p in (name or "").strip().split() if p]
    return "-".join(parts)

def search(profile: ClientProfile) -> BrokerResult:
    # Try path-based query; falls back gracefully
    path = _name_path(profile.name)
    url = f"{BASE}/name/{quote_plus(path)}"
    if profile.city and profile.state:
        url += f"/{quote_plus(profile.city)}-{quote_plus(profile.state)}"
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
        broker="FastPeopleSearch",
        found=found,
        url=url,
        title=title,
        notes="Opt-out: https://www.fastpeoplesearch.com/removal"
    )

