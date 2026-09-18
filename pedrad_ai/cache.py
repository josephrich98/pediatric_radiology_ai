"""Selective cache refresh: expire only what can hide a newly published record.

The on-disk HTTP cache (``data/raw/cache/``) has no expiry, which is what makes
a re-run reproducible — and also what makes it useless as an update: a cached
PubMed ESearch returns the PMID list as it stood at the first pull, so
``collect_pubmed.py`` re-runs happily and reproduces last month's numbers.

The blunt fix is to delete the cache, but that throws away 1.3 GB of records
that cannot go stale (EFetch abstracts, article bodies, DOI metadata) and turns
a top-up into a cold re-pull. This module is the sharp fix. A refresh does not
delete anything: it marks *some* cached responses as stale at request time, so
:func:`utils.http_get` re-fetches those and serves everything else from disk.

Three things decide staleness, and all three are visible on the request URL, so
there is nothing to back-fill and nothing to keep in sync with the collectors:

* **Kind.** A rule classifies each URL. ``INDEX`` is a listing or an unbounded
  search — it is what hides a new record, and it is always re-fetched. ``WINDOW``
  is a year-scoped count, re-fetched only when its year range reaches into the
  live window. ``METRICS`` is a citation count or a star count, which drifts
  rather than hides, and is opt-in because refreshing it costs thousands of
  requests against budgeted APIs. ``KEEP`` is a fetched record and is never
  re-fetched.
* **The live window.** A ``WINDOW`` URL naming only years before
  ``END_YEAR - (window - 1)`` is left alone: the 2015 count is not going to move.
  This is what keeps a refresh to tens of requests instead of hundreds.
* **Age.** ``--refresh-max-age`` leaves entries fetched in the last N hours
  alone, so an interrupted refresh resumes instead of starting over.

**Anything a rule does not match is kept.** A refresh can therefore only
re-fetch what this file names, which is the property that makes it safe to run
against a cache you do not want to lose.
"""

from __future__ import annotations

import atexit
import fnmatch
import os
import re
import time
import urllib.parse
from pathlib import Path
from typing import Any, Callable, NamedTuple

from . import config

# Kinds, in the order a refresh cares about them.
KEEP = "keep"        # a fetched record: never re-fetched
INDEX = "index"      # a listing / unbounded search: always re-fetched
WINDOW = "window"    # a year-scoped search: re-fetched inside the live window
METRICS = "metrics"  # citations, stars, impact: opt-in

ENV_ENABLED = "PEDRAD_AI_REFRESH"
ENV_YEARS = "PEDRAD_AI_REFRESH_YEARS"
ENV_MAX_AGE = "PEDRAD_AI_REFRESH_MAX_AGE"
ENV_SCOPES = "PEDRAD_AI_REFRESH_SCOPES"

DEFAULT_WINDOW_YEARS = 2


# --------------------------------------------------------------------------- #
# Rules
# --------------------------------------------------------------------------- #
class Rule(NamedTuple):
    name: str
    kind: str
    match: Callable[[str], bool]
    years: Callable[[str], tuple[int, int] | None] | None = None
    opt_in: str | None = None   # scope name that must be enabled for this rule


def _host(pattern: str) -> Callable[[str], bool]:
    return lambda u: fnmatch.fnmatch(u, pattern)


def _span(text: str, pattern: str) -> tuple[int, int] | None:
    """First (start, end) year pair matched by ``pattern`` in ``text``.

    Groups that did not participate in the match are ignored, so a pattern may
    offer alternative spellings of the same date filter without the caller
    having to know which branch matched.
    """
    m = re.search(pattern, text)
    if not m:
        return None
    found = [int(g) for g in m.groups() if g and g.isdigit()]
    if not found:
        return None
    return (min(found), max(found))


def _pubmed_years(u: str) -> tuple[int, int] | None:
    # term=(...) AND 2015[pdat]   /   term=(...) AND 2008:2026[pdat]
    return _span(u, r"(\d{4})(?::(\d{4}))?\[pdat\]")


def _arxiv_years(u: str) -> tuple[int, int] | None:
    return _span(u, r"submittedDate:\[(\d{4})\d*\s+TO\s+(\d{4})\d*\]")


def _epmc_years(u: str) -> tuple[int, int] | None:
    return _span(u, r"PUB_YEAR:(?:\[(\d{4})\s+TO\s+(\d{4})\]|(\d{4}))")


def _openalex_years(u: str) -> tuple[int, int] | None:
    a = re.search(r"from_publication_date:(\d{4})", u)
    b = re.search(r"to_publication_date:(\d{4})", u)
    if not a and not b:
        return None
    start = int(a.group(1)) if a else config.START_YEAR
    end = int(b.group(1)) if b else config.END_YEAR
    return (start, end)


def _is_pubmed_record_lookup(u: str) -> bool:
    """A DOI/PMID resolution, not a survey of the literature."""
    return "[doi]" in u or "[pmid]" in u or "[uid]" in u


# Order matters: the first matching rule wins.
_RULES: list[Rule] = [
    # ---- PubMed ---------------------------------------------------------- #
    Rule("pubmed.efetch", KEEP, _host("*eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch*")),
    Rule("pubmed.esummary", KEEP, _host("*eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary*")),
    Rule("pubmed.doi-lookup", KEEP,
         lambda u: "esearch.fcgi" in u and _is_pubmed_record_lookup(u)),
    Rule("pubmed.esearch", WINDOW, _host("*eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch*"),
         years=_pubmed_years),

    # ---- Preprints ------------------------------------------------------- #
    Rule("arxiv.query", WINDOW, _host("*export.arxiv.org/api/query*"), years=_arxiv_years),
    Rule("europepmc.preprint-search", WINDOW,
         lambda u: "europepmc" in u and "SRC:PPR" in u, years=_epmc_years),
    Rule("europepmc.lookup", KEEP, _host("*europepmc*")),

    # ---- OpenAlex -------------------------------------------------------- #
    Rule("openalex.doi-batch", METRICS, lambda u: "api.openalex.org/works" in u and "filter=doi:" in u),
    Rule("openalex.work", METRICS, lambda u: bool(re.search(r"api\.openalex\.org/works/", u))),
    Rule("openalex.sources", METRICS, _host("*api.openalex.org/sources*")),
    Rule("openalex.search", WINDOW, _host("*api.openalex.org/works*"), years=_openalex_years),

    # ---- Other metrics --------------------------------------------------- #
    Rule("icite", METRICS, _host("*icite.od.nih.gov*")),
    Rule("github", METRICS, _host("*api.github.com*")),
    Rule("semanticscholar.lookup", METRICS, _host("*api.semanticscholar.org*")),

    # ---- Newsletters ----------------------------------------------------- #
    # The WP listing (_fields=id) is what hides a new post; the include= batches
    # that carry the post bodies are records and cost real bandwidth.
    Rule("newsletter.wp-content", KEEP, lambda u: "/wp-json/wp/v2/" in u and "include=" in u),
    Rule("newsletter.wp-index", INDEX, lambda u: "/wp-json/wp/v2/" in u),
    Rule("newsletter.rsna-archive", INDEX, lambda u: "rsna.org/news/archive" in u),
    Rule("newsletter.rsna-article", KEEP, lambda u: "rsna.org/news/" in u),
    # TLDR enumerates one URL per weekday up to today, so a new day is a new key
    # and already misses the cache; the pages themselves never change.
    Rule("newsletter.tldr", KEEP, _host("*tldr.tech*")),

    # ---- Conferences ----------------------------------------------------- #
    # The accepted-paper list for a meeting that has already happened does not
    # change, and these are large files, so only the live years are re-fetched.
    # A URL with no year in it (the PMLR volume pages) falls back to re-fetching.
    Rule("venue.accepted-list", WINDOW,
         lambda u: any(h in u for h in ("neurips.cc", "iclr.cc", "icml.cc",
                                        "openaccess.thecvf.com", "proceedings.mlr.press",
                                        "papers.miccai.org", "conferences.miccai.org")),
         years=lambda u: _span(u, r"(20\d{2})")),
    # DBLP throttles hard and a cold re-sample can lose venue-years, so it is
    # opt-in, mirroring refresh.py's long-standing --drop-dblp-cache.
    Rule("dblp", INDEX, _host("*dblp.org*"), opt_in="dblp"),

    # ---- Patents --------------------------------------------------------- #
    Rule("patentsview", INDEX, _host("*patentsview.org*")),

    # ---- Reference resolution (stable by construction) -------------------- #
    Rule("crossref.work", KEEP, lambda u: re.search(r"api\.crossref\.org/works/", u) is not None),
    Rule("crossref.search", INDEX, _host("*api.crossref.org/works*")),
    Rule("doi.org", KEEP, _host("*doi.org*")),
    Rule("doi2bib", KEEP, _host("*doi2bib*")),
]


# --------------------------------------------------------------------------- #
# State
# --------------------------------------------------------------------------- #
class _State:
    def __init__(self) -> None:
        self.enabled = False
        self.window_years = DEFAULT_WINDOW_YEARS
        self.max_age_seconds = 0.0
        self.scopes: set[str] = set()
        self.refetched = 0
        self.reused = 0
        self.by_rule: dict[str, int] = {}
        self.fallbacks = 0

    def load_env(self) -> None:
        self.enabled = os.environ.get(ENV_ENABLED, "").strip() not in ("", "0", "false", "no")
        if not self.enabled:
            return
        try:
            self.window_years = max(1, int(os.environ.get(ENV_YEARS, "") or DEFAULT_WINDOW_YEARS))
        except ValueError:
            self.window_years = DEFAULT_WINDOW_YEARS
        try:
            self.max_age_seconds = max(0.0, float(os.environ.get(ENV_MAX_AGE, "") or 0.0)) * 3600.0
        except ValueError:
            self.max_age_seconds = 0.0
        self.scopes = {s.strip() for s in os.environ.get(ENV_SCOPES, "").split(",") if s.strip()}


_state = _State()
_state.load_env()
def _report_at_exit() -> None:
    """Print the refresh summary, unless this process made no cached request."""
    if _state.refetched or _state.reused or _state.by_rule:
        print(summary_line())


if _state.enabled:
    # Inherited from a parent process (refresh.py exports the settings to its
    # children), so report at exit the way an explicit --refresh does.
    atexit.register(_report_at_exit)


def enable(*, window_years: int = DEFAULT_WINDOW_YEARS, max_age_hours: float = 0.0,
           scopes: set[str] | None = None, export_env: bool = True) -> None:
    """Turn refresh mode on for this process (and, by default, its children)."""
    _state.enabled = True
    _state.window_years = max(1, int(window_years))
    _state.max_age_seconds = max(0.0, float(max_age_hours)) * 3600.0
    _state.scopes = set(scopes or ())
    if export_env:
        os.environ[ENV_ENABLED] = "1"
        os.environ[ENV_YEARS] = str(_state.window_years)
        os.environ[ENV_MAX_AGE] = str(_state.max_age_seconds / 3600.0)
        os.environ[ENV_SCOPES] = ",".join(sorted(_state.scopes))


def disable() -> None:
    _state.enabled = False
    for key in (ENV_ENABLED, ENV_YEARS, ENV_MAX_AGE, ENV_SCOPES):
        os.environ.pop(key, None)


def is_enabled() -> bool:
    return _state.enabled


def live_window() -> tuple[int, int]:
    """The years a refresh considers unsettled."""
    return (config.END_YEAR - (_state.window_years - 1), config.END_YEAR)


# --------------------------------------------------------------------------- #
# Classification
# --------------------------------------------------------------------------- #
def classify(url: str, body: bytes | None = None) -> tuple[Rule | None, str]:
    """Return the matching rule and a one-line reason."""
    text = urllib.parse.unquote_plus(url)
    if body:
        text += "::" + body.decode("utf-8", "replace")
    for rule in _RULES:
        try:
            if not rule.match(text):
                continue
        except Exception:  # noqa: BLE001 - a bad rule must never break a request
            continue
        if rule.kind == KEEP:
            return rule, "record"
        if rule.opt_in and rule.opt_in not in _state.scopes:
            return rule, f"{rule.opt_in} not in scope"
        if rule.kind == METRICS and "metrics" not in _state.scopes:
            return rule, "metrics not in scope"
        if rule.kind == WINDOW:
            try:
                span = rule.years(text) if rule.years else None
            except Exception:  # noqa: BLE001 - a bad extractor must not break a request
                span = None
            if span is None:
                return rule, "no year in request"   # unbounded search: treat as index
            lo, _hi = live_window()
            if span[1] < lo:
                return rule, f"settled years {span[0]}-{span[1]}"
            return rule, f"live years {span[0]}-{span[1]}"
        return rule, rule.kind
    return None, "unmatched"


def _is_volatile(rule: Rule | None, reason: str) -> bool:
    if rule is None or rule.kind == KEEP:
        return False
    if reason.startswith("settled years") or reason.endswith("not in scope"):
        return False
    return True


def should_refetch(url: str, path: Path, body: bytes | None = None) -> bool:
    """True when ``path`` holds a cached response a refresh should replace."""
    if not _state.enabled:
        return False
    try:
        rule, reason = classify(url, body)
    except Exception:  # noqa: BLE001 - never let the policy take down a collector
        return False
    if not _is_volatile(rule, reason):
        return False
    if _state.max_age_seconds:
        try:
            if time.time() - path.stat().st_mtime < _state.max_age_seconds:
                return False
        except OSError:
            pass
    assert rule is not None
    _state.by_rule[rule.name] = _state.by_rule.get(rule.name, 0) + 1
    return True


def note_reuse() -> None:
    _state.reused += 1


def note_refetch() -> None:
    _state.refetched += 1


def note_fallback() -> None:
    _state.fallbacks += 1


def stats() -> dict[str, Any]:
    return {
        "enabled": _state.enabled,
        "window": list(live_window()) if _state.enabled else None,
        "scopes": sorted(_state.scopes),
        "refetched": _state.refetched,
        "served_from_cache": _state.reused,
        "stale_fallbacks": _state.fallbacks,
        "by_rule": dict(sorted(_state.by_rule.items())),
    }


def summary_line() -> str:
    if not _state.enabled:
        return "cache: refresh off (every cached response reused)"
    lo, hi = live_window()
    parts = [f"cache refresh: live window {lo}-{hi}",
             f"{_state.refetched} re-fetched",
             f"{_state.reused} reused"]
    if _state.fallbacks:
        parts.append(f"{_state.fallbacks} stale kept (fetch failed)")
    if _state.by_rule:
        parts.append("by rule: " + ", ".join(f"{k}={v}" for k, v in sorted(_state.by_rule.items())))
    return " | ".join(parts)


# --------------------------------------------------------------------------- #
# CLI helper — shared by every collect_*.py
# --------------------------------------------------------------------------- #
def add_cli(parser: Any) -> Any:
    g = parser.add_argument_group("cache refresh")
    g.add_argument("--refresh", action="store_true",
                   help="re-fetch the cached listings and recent-year searches that would "
                        "otherwise hide newly published records (deletes nothing)")
    g.add_argument("--refresh-years", type=int, default=DEFAULT_WINDOW_YEARS, metavar="N",
                   help=f"how many calendar years count as unsettled (default {DEFAULT_WINDOW_YEARS}: "
                        f"{config.END_YEAR - 1} and {config.END_YEAR})")
    g.add_argument("--refresh-max-age", type=float, default=0.0, metavar="HOURS",
                   help="leave entries re-fetched in the last HOURS alone (resumes an interrupted refresh)")
    g.add_argument("--refresh-metrics", action="store_true",
                   help="also re-fetch citation counts, FWCI, RCR and GitHub stars "
                        "(thousands of requests against budgeted APIs)")
    g.add_argument("--refresh-dblp", action="store_true",
                   help="also re-sample DBLP (throttles hard; a cold re-sample can lose venue-years)")
    return parser


def apply_cli(args: Any) -> bool:
    """Turn refresh mode on if the parsed args asked for it. Returns whether it is on."""
    if not getattr(args, "refresh", False):
        return False
    scopes: set[str] = set()
    if getattr(args, "refresh_metrics", False):
        scopes.add("metrics")
    if getattr(args, "refresh_dblp", False):
        scopes.add("dblp")
    enable(window_years=getattr(args, "refresh_years", DEFAULT_WINDOW_YEARS),
           max_age_hours=getattr(args, "refresh_max_age", 0.0),
           scopes=scopes)
    # Printed at exit rather than at the end of each main(), so a collector that
    # bails out early still reports what it re-fetched.
    atexit.register(_report_at_exit)
    lo, hi = live_window()
    print(f"Refresh mode: re-fetching listings and {lo}-{hi} searches; "
          f"records, settled years{'' if 'metrics' in scopes else ' and metrics'} served from cache")
    return True
