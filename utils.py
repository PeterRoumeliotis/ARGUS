import time, random
import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def polite_get(url, *, timeout: float = 12.0, attempts: int = 2, sleep_base: float = 1.0, allow_fail: bool = True, **kwargs):
    """HTTP GET with sane defaults and quick failure.

    - Shorter default timeout per attempt
    - Fewer retries
    - Returns a dummy empty response if allow_fail and all attempts fail
    """
    headers = kwargs.pop("headers", {})
    merged = {**DEFAULT_HEADERS, **headers}
    last_exc = None
    last_resp = None
    for attempt in range(attempts):
        try:
            r = requests.get(url, headers=merged, timeout=timeout, **kwargs)
            last_resp = r
            if r.status_code in (200, 404):
                return r
        except Exception as e:
            last_exc = e
        # backoff between attempts
        time.sleep(sleep_base * (attempt + 1))
    if allow_fail:
        class _Dummy:
            status_code = 0
            text = ""
            content = b""
            url = None  # set below
        d = _Dummy()
        d.url = url
        return d
    # If not allowing failures, raise the last exception or HTTP error
    if last_resp is not None:
        last_resp.raise_for_status()
    if last_exc:
        raise last_exc
    raise RuntimeError("polite_get failed without response or exception")

def jitter_sleep(min_s=0.2, max_s=0.5):
    time.sleep(random.uniform(min_s, max_s))
