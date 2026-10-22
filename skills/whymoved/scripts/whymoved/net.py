"""Tiny HTTP helper with retries. Standard library only."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

USER_AGENT = "Mozilla/5.0"  # some free endpoints rate-limit unfamiliar agents harder


class FetchError(RuntimeError):
    pass


def fetch(url: str, *, timeout: float = 15.0, retries: int = 2, headers: dict | None = None,
          data: bytes | None = None) -> bytes:
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT, **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last = e
            # 4xx other than rate limiting will not get better on retry
            if e.code < 500 and e.code != 429:
                break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    raise FetchError(f"GET {url} failed: {last}")


def fetch_json(url: str, **kw) -> object:
    return json.loads(fetch(url, **kw).decode("utf-8"))
