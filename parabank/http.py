"""Polite HTTP for a shared public demo site: a small pause between requests, and a clear stop
when the site rate-limits us (HTTP 429) instead of retrying and making it worse."""
import time

import requests

from .config import TIMEOUT_S

MIN_INTERVAL_S = 0.3
_last = [0.0]


class RateLimitedError(RuntimeError):
    pass


def check_rate_limit(r: requests.Response) -> requests.Response:
    if r.status_code == 429:
        raise RateLimitedError(f"ParaBank demo rate-limited the tests (HTTP 429, Retry-After: "
                               f"{r.headers.get('Retry-After', '?')} s). Wait and run again.")
    return r


class PoliteSession(requests.Session):
    def request(self, method, url, **kwargs):
        wait = MIN_INTERVAL_S - (time.monotonic() - _last[0])
        if wait > 0:
            time.sleep(wait)
        kwargs.setdefault("timeout", TIMEOUT_S)
        try:
            return check_rate_limit(super().request(method, url, **kwargs))
        finally:
            _last[0] = time.monotonic()
