from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from models import ClientProfile, BrokerResult
from utils import polite_get, jitter_sleep

BASE = "https://www.spokeo.com"

def search(profile: ClientProfile) -> BrokerResult:
    q = quote_plus(profile.name)
    url = f"{BASE}/search?q={q}"
    # Append location hints if provided; city alone helps narrow results
    if profile.city and profile.state:
        url += quote_plus(f" {profile.city} {profile.state}")
    elif profile.city:
        url += quote_plus(f" {profile.city}")
    r = polite_get(url)
    soup = BeautifulSoup(r.text, "lxml")
    found, snippet, title = False, None, None
    first_last = profile.name.split()[0], profile.name.split()[-1]
    for a in soup.select("a"):
        text = (a.get_text(" ", strip=True) or "").lower()
        if first_last[0].lower() in text and first_last[1].lower() in text:
            found = True
            title = a.get_text(" ", strip=True)[:120]
            snippet = title
            break
    jitter_sleep()
    return BrokerResult(
        broker="Spokeo",
        found=found,
        url=url,
        title=title,
        raw_snippet=snippet,
        notes="If found, submit opt-out: https://www.spokeo.com/opt_out"
    )
