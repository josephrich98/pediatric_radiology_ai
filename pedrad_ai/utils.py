"""Shared plumbing: a polite, cached, retrying HTTP client plus small IO helpers.

Every collector hits a public API that rate-limits and occasionally fails, so a
single well-behaved request function saves a lot of duplicated retry logic. The
on-disk cache (``data/raw/cache/``) means re-running an analysis does not re-hit
the network, which keeps the pulls reproducible and friendly to the services.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from . import cache, config

CACHE_DIR = config.RAW_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
# Services that answer HTTP 200 with an error *body*. NCBI does this under load
# ("Search Backend failed: ... returned 502 status"), and because the status is
# 200 the response used to be cached as if it were a count — poisoning the entry
# for good and crashing the collector with a KeyError on every later run. A soft
# error is treated as a failed fetch: never written to the cache, and never
# served from it, so a poisoned entry left over from an earlier run heals itself
# on the next request rather than needing anyone to find and delete it.
_SOFT_ERROR_MARKERS = (
    '"ERROR":',           # NCBI ESearch/ESummary
    '"error":"Search Backend failed',
)


def is_soft_error(text: str) -> bool:
    head = text[:2000]
    if '"esearchresult"' in head or '"esummaryresult"' in head:
        return any(m in head for m in _SOFT_ERROR_MARKERS)
    return False


class SoftHTTPError(RuntimeError):
    """A 200 response whose body says the service failed."""


def _cache_path(url: str, body: bytes | None) -> Path:
    key = url if body is None else url + "::" + body.decode("utf-8", "replace")
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
    return CACHE_DIR / f"{digest}.cache"


def http_get(
    url: str,
    params: dict[str, Any] | None = None,
    *,
    headers: dict[str, str] | None = None,
    use_cache: bool = True,
    max_retries: int = 4,
    pause: float = 0.34,
    timeout: float = 60.0,
) -> str:
    """GET ``url`` with retries, exponential backoff, and an on-disk cache.

    ``pause`` is the minimum delay applied before a live request; the default
    keeps us under NCBI's 3 requests/second limit. Returns the response body as
    text. Raises the last error if every retry fails.
    """
    if params:
        url = url + "?" + urllib.parse.urlencode(params, doseq=True)

    cache_file = _cache_path(url, None)
    # In refresh mode a cached response that could hide a newly published record
    # is re-fetched; everything else is still served from disk. The stale copy is
    # kept in hand so a failed re-fetch degrades to last month's answer rather
    # than taking the collector down with it.
    stale_text: str | None = None
    if use_cache and cache_file.exists():
        try:
            cached = cache_file.read_text(encoding="utf-8")
        except OSError:
            cached = None
        if cached is not None and is_soft_error(cached):
            cached = None          # poisoned entry: re-fetch, and do not fall back to it
        if cached is not None:
            if not cache.should_refetch(url, cache_file):
                cache.note_reuse()
                return cached
            stale_text = cached

    req_headers = {"User-Agent": config.USER_AGENT}
    if headers:
        req_headers.update(headers)

    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            time.sleep(pause)
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                text = resp.read().decode("utf-8", "replace")
            if is_soft_error(text):
                raise SoftHTTPError(text[:200])
            if use_cache:
                cache_file.write_text(text, encoding="utf-8")
            if stale_text is not None:
                cache.note_refetch()
            return text
        except SoftHTTPError as exc:
            # The service is up but failing; back off like a 503 and try again.
            last_err = exc
            time.sleep(pause * (2 ** attempt) + 3.0)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            last_err = exc
            code = getattr(exc, "code", None)
            # Client errors other than rate-limiting won't succeed on retry
            # (e.g. a 404 for an unregistered DOI) — fail fast instead of
            # burning the backoff schedule.
            if code is not None and 400 <= code < 500 and code != 429:
                if stale_text is not None:
                    cache.note_fallback()
                    return stale_text
                raise
            # Back off harder on rate-limit / server errors and on the abrupt
            # disconnects that hosts like DBLP use to throttle bursts.
            throttled = code in (429, 500, 502, 503) or isinstance(exc, (ConnectionError, OSError))
            backoff = pause * (2 ** attempt) + (3.0 if throttled else 0.0)
            time.sleep(backoff)
    if stale_text is not None:
        cache.note_fallback()
        return stale_text
    assert last_err is not None
    raise last_err


def http_get_json(url: str, params: dict[str, Any] | None = None, **kw: Any) -> Any:
    """GET and parse JSON."""
    return json.loads(http_get(url, params, **kw))


def http_post_json(
    url: str,
    payload: dict[str, Any],
    *,
    headers: dict[str, str] | None = None,
    use_cache: bool = True,
    max_retries: int = 4,
    pause: float = 0.5,
    timeout: float = 60.0,
) -> Any:
    """POST a JSON body and parse the JSON response, with cache + retries."""
    body = json.dumps(payload).encode("utf-8")
    cache_file = _cache_path(url, body)
    stale_text = None
    if use_cache and cache_file.exists():
        try:
            cached = cache_file.read_text(encoding="utf-8")
        except OSError:
            cached = None
        if cached is not None and is_soft_error(cached):
            cached = None
        if cached is not None:
            if not cache.should_refetch(url, cache_file, body=body):
                cache.note_reuse()
                return json.loads(cached)
            stale_text = cached

    req_headers = {
        "User-Agent": config.USER_AGENT,
        "Content-Type": "application/json",
    }
    if headers:
        req_headers.update(headers)

    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            time.sleep(pause)
            req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                text = resp.read().decode("utf-8", "replace")
            if is_soft_error(text):
                raise SoftHTTPError(text[:200])
            if use_cache:
                cache_file.write_text(text, encoding="utf-8")
            if stale_text is not None:
                cache.note_refetch()
            return json.loads(text)
        except SoftHTTPError as exc:
            last_err = exc
            time.sleep(pause * (2 ** attempt) + 3.0)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
            time.sleep(pause * (2 ** attempt) + 1.0)
    if stale_text is not None:
        cache.note_fallback()
        return json.loads(stale_text)
    assert last_err is not None
    raise last_err


# --------------------------------------------------------------------------- #
# IO
# --------------------------------------------------------------------------- #
def save_json(obj: Any, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_csv(rows: list[dict[str, Any]], path: str | Path, columns: list[str] | None = None) -> Path:
    """Write a list of dict rows to CSV without requiring pandas."""
    import csv

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    columns = columns or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def years() -> list[int]:
    """The configured year range as a list, clamped to a sane upper bound."""
    return list(range(config.START_YEAR, config.END_YEAR + 1))
