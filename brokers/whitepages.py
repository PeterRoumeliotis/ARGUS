from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from models import ClientProfile, BrokerResult
from utils import polite_get, jitter_sleep

BASE = "https://www.whitepages.com"

def search(profile: ClientProfile) -> BrokerResult:
    q = quote_plus(profile.name)
    url = f"{BASE}/name/{q}"
    if profile.city and profile.state:
        url += f"/{quote_plus(profile.city)}/{quote_plus(profile.state)}"
    r = polite_get(url)
    soup = BeautifulSoup(r.text, "lxml")
    text = soup.get_text(" ", strip=True).lower()
    found = (profile.name.split()[-1].lower() in text)
    jitter_sleep()
    return BrokerResult(
        broker="Whitepages",
        found=found,
        url=url,
        notes="Opt-out: https://www.whitepages.com/suppression_requests"
    )