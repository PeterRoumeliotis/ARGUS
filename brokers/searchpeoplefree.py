from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from models import ClientProfile, BrokerResult
from utils import polite_get, jitter_sleep

BASE = "https://www.searchpeoplefree.com"

def search(profile: ClientProfile) -> BrokerResult:
    parts = [p for p in profile.name.split() if p]
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else ""
    qs = f"firstname={quote_plus(first)}&lastname={quote_plus(last)}"
    if profile.state:
        qs += f"&state={quote_plus(profile.state)}"
    url = f"{BASE}/find?{qs}"

    r = polite_get(url, timeout=10.0, attempts=2, allow_fail=True)
    html = getattr(r, "text", "") or ""
    found = False
    title = None
    if html:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True).lower()
        if first and last:
            found = (first.lower() in text and last.lower() in text)
        elif first:
            found = first.lower() in text
        h = soup.find(["h1","h2","title"]) or None
        if h:
            title = h.get_text(" ", strip=True)[:160]
    jitter_sleep()
    return BrokerResult(
        broker="SearchPeopleFree",
        found=found,
        url=url,
        title=title,
        notes="Opt-out: https://www.searchpeoplefree.com/opt-out"
    )

