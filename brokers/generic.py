from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from typing import Dict, Optional
from models import ClientProfile, BrokerResult
from utils import polite_get, jitter_sleep

DUCK_BASE = "https://duckduckgo.com/html/"

def _build_query(domain: str, profile: ClientProfile) -> str:
    parts = []
    name = (profile.name or "").strip()
    if name:
        parts.append(f'"{name}"')
    if profile.city:
        parts.append(f'"{profile.city}"')
    if profile.state:
        parts.append(f'"{profile.state}"')
    # constrain by site
    parts.append(f"site:{domain}")
    return " ".join(parts).strip()

def search(profile: ClientProfile, site: Dict) -> BrokerResult:
    """Generic search via DuckDuckGo HTML for a given domain.

    Expects site dict with at least { 'name': str, 'domain': str }.
    """
    domain = (site.get("domain") or site.get("name") or "").strip()
    if domain.startswith("http://") or domain.startswith("https://"):
        # strip scheme if included
        domain = domain.split("://", 1)[1]
    domain = domain.strip("/")

    q = _build_query(domain, profile)
    url = f"{DUCK_BASE}?q={quote_plus(q)}&kp=-2"

    # Perform the search quickly; allow failure without blocking
    r = polite_get(url, timeout=10.0, attempts=2, allow_fail=True)
    html = getattr(r, "text", "") or ""
    soup = BeautifulSoup(html, "lxml") if html else None

    found = False
    first_title: Optional[str] = None
    first_url: Optional[str] = None

    if soup is not None:
        for a in soup.select("a.result__a, a.result__url, a.result__snippet, a.result__a\, .result__a"):
            href = a.get("href") or ""
            text = a.get_text(" ", strip=True) or ""
            if domain.split("/", 1)[0].lower() in (href.lower() + " " + text.lower()):
                first_title = text[:160] or first_title
                first_url = href or first_url
                found = True
                break

    jitter_sleep()
    return BrokerResult(
        broker=site.get("name") or domain,
        found=found,
        url=first_url or url,
        title=first_title,
        notes=(site.get("optout_url") and f"Opt-out: {site['optout_url']}") or None,
    )

