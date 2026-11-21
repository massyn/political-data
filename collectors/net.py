"""Shared HTTP download with retries, used by the collectors."""

import logging
import time
import urllib.error
import urllib.request

log = logging.getLogger(__name__)


def get(
    url: str,
    headers: dict | None = None,
    timeout: int = 60,
    attempts: int = 3,
    backoff: int = 5,
    user_agent: str | None = "Mozilla/5.0",
) -> bytes:
    """GET a URL, retrying transient network failures; raises the last error if all fail.

    user_agent=None sends urllib's own default, which some servers (FRED) require.
    """
    base = {"User-Agent": user_agent} if user_agent else {}
    req = urllib.request.Request(url, headers={**base, **(headers or {})})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except (TimeoutError, urllib.error.URLError) as exc:
            log.warning("download attempt %d/%d failed for %s: %s", attempt, attempts, url, exc)
            if attempt == attempts:
                raise
            time.sleep(backoff * attempt)
