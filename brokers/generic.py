from typing import List, Optional, Dict, Tuple
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode


def _http_get(url: str, params: Dict[str, str] | None, timeout: float) -> requests.Response:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    return requests.get(url, params=params or {}, headers=headers, timeout=timeout)


def _name_parts(full_name: str) -> Tuple[str, str]:
    parts = (full_name or "").strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]


def _build_candidates(domain: str, full_name: str, city: Optional[str], state: Optional[str]) -> List[Tuple[str, Dict[str, str] | None]]:
    first, last = _name_parts(full_name)
    name_dash = "-".join([x for x in [first, last] if x])
    loc_comma = ", ".join([x for x in [city or "", state or ""] if x]).strip(", ")
    loc_dash = "-".join([x for x in [city or "", state or ""] if x]).strip("-")

    # Query parameter-based candidates
    q_candidates: List[Tuple[str, Dict[str, str] | None]] = []
    for path in [
        "/search",
        "/people-search",
        "/find",
        "/name",
        "/",
    ]:
        base = f"https://{domain}{path}"
        for key in ["q", "name", "fullName", "search", "query", "term", "s"]:
            params = {key: full_name}
            if loc_comma:
                # Common param names for location
                for lkey in ["where", "location", "citystatezip", "citystate", "loc", "place", "city"]:
                    q_candidates.append((base, {**params, lkey: loc_comma}))
            q_candidates.append((base, params))

    # Path-based candidates
    p_candidates: List[Tuple[str, Dict[str, str] | None]] = []
    for path_tpl in [
        f"/name/{name_dash}",
        f"/people/{name_dash}",
        f"/person/{name_dash}",
        f"/people-search/{name_dash}",
    ]:
        if name_dash:
            p_candidates.append((f"https://{domain}{path_tpl}", None))
            if loc_dash:
                p_candidates.append((f"https://{domain}{path_tpl}/{loc_dash}", None))

    return q_candidates + p_candidates


def _extract_links(domain: str, html: str, limit: int, first: str, last: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls: List[str] = []
    # Heuristics: prefer anchors that look like person/profile/results links
    anchors = soup.select("a[href]")
    first_l = (first or "").strip().lower()
    last_l = (last or "").strip().lower()
    blacklist = [
        "/help", "/privacy", "/terms", "/about", "/welcome", "/blog", "/news",
        "/legal", "/contact", "/support", "/faq", "/auth", "/account",
        "/signin", "/signup", "/login", "/careers", "/press", "/advertising",
        "/partners", "/api", "/developers", "/cookies", "/donate", "/pricing",
    ]
    whitelist = [
        "/name/", "/person/", "/people/", "/profile/", "/details", "/result",
        "/results", "/records", "/people-search/",
    ]
    for a in anchors:
        href = a.get("href")
        if not href:
            continue
        if href.startswith("/"):
            href = f"https://{domain}" + href
        if domain not in href:
            continue
        path = href.split("//", 1)[-1].split("/", 1)[1] if "//" in href and "/" in href.split("//", 1)[-1] else href
        path_l = path.lower()
        if any(seg in path_l for seg in blacklist):
            continue
        if not any(seg in path_l for seg in whitelist):
            # Must look like a person/results path
            continue
        text_l = a.get_text(" ", strip=True).lower()
        # Require both first and last name appear somewhere (URL or anchor text)
        if first_l and last_l:
            found_in_href = (first_l in path_l and last_l in path_l)
            found_in_text = (first_l in text_l and last_l in text_l)
            if not (found_in_href or found_in_text):
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


def search_domain(domain: str, full_name: str, city: Optional[str] = None, state: Optional[str] = None,
                  timeout: float = 15.0, limit: int = 5) -> List[str]:
    """Attempt to query a site's internal search using a variety of common patterns.

    This is a best-effort generic scraper and may not work for all sites.
    """
    if not domain or not full_name:
        return []
    candidates = _build_candidates(domain, full_name, city, state)
    first, last = _name_parts(full_name)
    for url, params in candidates:
        try:
            resp = _http_get(url, params, timeout)
            if resp.status_code >= 400:
                continue
            urls = _extract_links(domain, resp.text, limit, first, last)
            if urls:
                return urls
        except Exception:
            continue
    return []
