from typing import List, Optional
import requests
from bs4 import BeautifulSoup


def _http_get(url: str, params: dict | None, timeout: float) -> requests.Response:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    return requests.get(url, params=params or {}, headers=headers, timeout=timeout)


def search(full_name: str, city: Optional[str] = None, state: Optional[str] = None,
           timeout: float = 15.0, limit: int = 5) -> List[str]:
    """Query FastPeopleSearch results and return matching URLs."""
    # Two patterns seem to work: query params and path-based
    base = "https://www.fastpeoplesearch.com/name"
    params = {"name": full_name}
    if state or city:
        loc = ", ".join(filter(None, [city, state]))
        params["citystatezip"] = loc
    resp = _http_get(base, params, timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    urls: List[str] = []
    parts = full_name.lower().split()
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else ""
    for a in soup.select("a[href]"):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("/"):
            href = "https://www.fastpeoplesearch.com" + href
        if "fastpeoplesearch.com" not in href:
            continue
        path_l = href.lower()
        if not ("/person/" in path_l or "/name/" in path_l):
            continue
        text_l = a.get_text(" ", strip=True).lower()
        if first and last and not ((first in path_l and last in path_l) or (first in text_l and last in text_l)):
            continue
        urls.append(href)
        if len(urls) >= limit:
            break
    # De-dupe
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            out.append(u)
            seen.add(u)
    return out[:limit]
