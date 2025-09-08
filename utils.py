import time, random
import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def polite_get(url, **kwargs):
    headers = kwargs.pop("headers", {})
    merged = {**DEFAULT_HEADERS, **headers}
    for attempt in range(3):
        r = requests.get(url, headers=merged, timeout=30, **kwargs)
        if r.status_code in (200, 404):
            return r
        time.sleep(2 * (attempt + 1))
    r.raise_for_status()
    return r

def jitter_sleep(min_s=0.7, max_s=1.6):
    time.sleep(random.uniform(min_s, max_s))