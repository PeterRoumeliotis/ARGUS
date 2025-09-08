import json
import os
from typing import List, Dict, Callable, Optional


def _slug(name: str) -> str:
    s = name.strip().lower()
    out = []
    for ch in s:
        out.append(ch if ch.isalnum() else "-")
    s2 = "".join(out)
    while "--" in s2:
        s2 = s2.replace("--", "-")
    return s2.strip("-") or "site"


def _to_domain(display: str) -> str:
    s = (display or "").strip().lower()
    # Strip URL schemes and paths if a full URL was given
    for prefix in ("http://", "https://"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
    # Remove leading www.
    if s.startswith("www."):
        s = s[4:]
    # Keep only hostname part before any path/query
    for sep in ["/", "?", "#"]:
        if sep in s:
            s = s.split(sep, 1)[0]
    return s


def get_brokers(sites_path: str = None) -> List[Dict[str, str]]:
    """Load broker sites from sites.json and normalize into dicts.

    Returns list of { key, display } items.
    """
    # Default path: sibling to this package's parent, named sites.json
    if sites_path is None:
        base = os.path.dirname(os.path.dirname(__file__))
        sites_path = os.path.join(base, "sites.json")

    sites: List[str] = []
    try:
        with open(sites_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # Accept list of strings or objects with 'name'/'display'
                for item in data:
                    if isinstance(item, str):
                        sites.append(item)
                    elif isinstance(item, dict):
                        name = item.get("name") or item.get("display") or ""
                        if name:
                            sites.append(str(name))
    except Exception:
        # If file missing or invalid, fall back to a minimal set
        sites = ["Spokeo.com", "WhitePages.com", "TruthFinder.com"]

    brokers: List[Dict[str, str]] = []
    for site in sites:
        display = str(site).strip()
        key = _slug(display)
        domain = _to_domain(display)
        brokers.append({"key": key, "display": display, "domain": domain})
    return brokers


# --- Specialized broker registry ---
_SPECIALIZATIONS: Dict[str, Callable[..., List[str]]] = {}

def _register_specializations():
    global _SPECIALIZATIONS
    try:
        from . import spokeo  # type: ignore
        _SPECIALIZATIONS["spokeo.com"] = spokeo.search  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        from . import whitepages  # type: ignore
        _SPECIALIZATIONS["whitepages.com"] = whitepages.search  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        from . import truepeoplesearch  # type: ignore
        _SPECIALIZATIONS["truepeoplesearch.com"] = truepeoplesearch.search  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        from . import fastpeoplesearch  # type: ignore
        _SPECIALIZATIONS["fastpeoplesearch.com"] = fastpeoplesearch.search  # type: ignore[attr-defined]
    except Exception:
        pass


def get_specialized(domain: str) -> Optional[Callable[..., List[str]]]:
    # Ensure built-ins are registered
    if not _SPECIALIZATIONS:
        _register_specializations()

    # If this domain not present yet, attach a generic scraper bound to the domain
    if domain not in _SPECIALIZATIONS:
        try:
            from .generic import search_domain  # type: ignore
            _SPECIALIZATIONS[domain] = lambda full_name, city=None, state=None, timeout=15.0, limit=5, _d=domain: (
                search_domain(_d, full_name, city, state, timeout=timeout, limit=limit)
            )
        except Exception:
            # Leave it missing if generic cannot be imported
            return None
    return _SPECIALIZATIONS.get(domain)
