"""Authorized RSS fetching with timeout, retries, backoff, and pacing."""

import logging
import time
from threading import Lock

import httpx

logger = logging.getLogger(__name__)


class FeedFetcher:
    def __init__(self, timeout: float = 10.0, retries: int = 3, min_interval: float = 1.0) -> None:
        self.timeout = timeout
        self.retries = retries
        self.min_interval = min_interval
        self._last_request = 0.0
        self._lock = Lock()

    def fetch(self, url: str) -> str:
        with self._lock:
            wait = self.min_interval - (time.monotonic() - self._last_request)
            if wait > 0:
                time.sleep(wait)
            self._last_request = time.monotonic()

        for attempt in range(self.retries + 1):
            try:
                response = httpx.get(url, timeout=self.timeout, follow_redirects=True)
                response.raise_for_status()
                return response.text
            except (httpx.HTTPError, ValueError) as error:
                if attempt == self.retries:
                    logger.exception("Feed request failed after %s retries", self.retries)
                    raise
                delay = 2 ** attempt
                logger.warning("Feed request failed (%s); retrying in %ss", error, delay)
                time.sleep(delay)
        raise RuntimeError("unreachable")
