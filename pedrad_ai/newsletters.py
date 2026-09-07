"""Newsletter and trade-press archive collector.

The peer-reviewed literature runs a year or more behind what the field is
actually doing; industry newsletters (The Imaging Wire), society news (RSNA
News), analyst blogs (Signify Research), trade press (Radiology Business,
Health Imaging) and general-tech digests (TLDR) do not. This module enumerates
each source's public archive, splits every issue into its individual stories,
and keeps the stories where **pediatric** and **AI** vocabulary co-occur
(plus **radiology** vocabulary for sources that are not imaging-specific).

Four archive shapes are supported, selected by ``kind`` in
:data:`config.NEWSLETTER_SOURCES`:

* ``wordpress`` - the WordPress REST API (``/wp-json/wp/v2/<type>``), which
  pages through an entire archive 100 items at a time with full HTML content.
* ``rsna_news`` - the RSNA News archive page lists every article since 2014;
  article bodies are fetched only for titles that already carry a pediatric or
  AI term, which is what the pediatric-AI hit needs.
* ``tldr`` - TLDR publishes one static page per weekday at
  ``/<newsletter>/YYYY-MM-DD``; the pages are enumerated by date.
* ``rss`` - a plain RSS/Atom feed (recent window only).

Everything goes through :func:`utils.http_get`, so archives are cached on disk
and a re-run only fetches new issues. Standard library only.
"""

from __future__ import annotations

import datetime as dt
import html as htmllib
import json
import re
import urllib.error
import xml.etree.ElementTree as ET
from typing import Any, Iterable

from . import config, utils

# --------------------------------------------------------------------------- #
# Text utilities
# --------------------------------------------------------------------------- #
_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_RE = re.compile(r"<(script|style|noscript)\b.*?</\1>", re.S | re.I)
_BLOCK_END_RE = re.compile(r"</(p|div|li|h[1-6]|tr|article|section|blockquote)>|<br\s*/?>", re.I)
# Stories start at a heading, an <article>, or (older email-style issues that
# never use heading tags) a paragraph that opens with a bold run-in title.
_HEADING_SPLIT_RE = re.compile(r"(?=<(?:h[1-4]|article)\b)", re.I)
_BOLD_SPLIT_RE = re.compile(r"(?=<p\b[^>]*>\s*<(?:strong|b)\b)", re.I)
_HEADING_RE = re.compile(r"<(h[1-4]|strong|b)\b[^>]*>(.*?)</\1>", re.S | re.I)
# A heading-delimited section longer than this that still contains several
# bold run-in titles is an old email-style digest; sub-split it.
_LONG_SECTION = 2500
# A section that is mostly a bullet list of unrelated one-liners (The Imaging
# Wire's "The Wire" / "Industry Wire" digests) is split into its list items.
_LI_RE = re.compile(r"<li\b[^>]*>(.*?)</li>", re.S | re.I)
_BOLD_P_RE = re.compile(r"<p\b[^>]*>\s*<(?:strong|b)\b", re.I)
_DIGEST_MIN_ITEMS = 8
_MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], 1)}


def html_to_text(raw: str) -> str:
    """Strip tags, keeping block boundaries as newlines."""
    s = _SCRIPT_RE.sub(" ", raw or "")
    s = _BLOCK_END_RE.sub("\n", s)
    s = _TAG_RE.sub(" ", s)
    s = htmllib.unescape(s)
    s = re.sub(r"[ \t\r\f\v ]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def split_sections(raw: str, fallback_title: str) -> list[tuple[str, str]]:
    """Split an HTML document into (heading, text) stories.

    Splits at every ``<h1>``-``<h4>`` or ``<article>`` tag. A document with fewer
    than two such blocks is returned as a single story titled ``fallback_title``.
    """
    parts = [p for p in _HEADING_SPLIT_RE.split(raw or "") if p and p.strip()]
    if len(parts) < 2:
        parts = [p for p in _BOLD_SPLIT_RE.split(raw or "") if p and p.strip()]
    if len(parts) < 2:
        return [(fallback_title, html_to_text(raw))]
    # Only digests that never use real sub-headings (h2-h4) get sub-split at
    # bold run-in titles; modern issues bold the first words of paragraphs.
    has_subheadings = bool(re.search(r"<h[2-4]\b", raw or "", re.I))
    expanded: list[str] = []
    for part in parts:
        if not has_subheadings and len(part) > _LONG_SECTION:
            sub = [p for p in _BOLD_SPLIT_RE.split(part) if p and p.strip()]
            if len(sub) >= 3:
                expanded.extend(sub)
                continue
        expanded.append(part)
    out: list[tuple[str, str]] = []
    for part in expanded:
        m = _HEADING_RE.search(part)
        heading = html_to_text(m.group(2)) if m else ""
        heading = re.sub(r"\s+", " ", heading).strip() or fallback_title
        lis = _LI_RE.findall(part)
        if len(lis) >= _DIGEST_MIN_ITEMS and len(lis) > 2 * len(_BOLD_P_RE.findall(part)):
            # Digest list: each bullet is its own story.
            lead = html_to_text(part[: part.lower().find("<li")])
            if lead:
                out.append((heading, lead))
            for li in lis:
                li_text = html_to_text(li)
                if not li_text:
                    continue
                lm = _HEADING_RE.search(li)
                li_head = re.sub(r"\s+", " ", html_to_text(lm.group(2))).strip() if lm else ""
                if not li_head:
                    li_head = li_text.split(":")[0][:80] if ":" in li_text[:100] else li_text[:80]
                out.append((f"{heading} · {li_head}", li_text))
            continue
        text = html_to_text(part)
        if not text:
            continue
        out.append((heading, text))
    return out


def _compile(patterns: Iterable[str]) -> list[tuple[str, re.Pattern[str]]]:
    out = []
    for pat in patterns:
        rx = pat
        if not rx.startswith("\\b"):
            rx = r"\b" + rx
        out.append((pat, re.compile(rx, re.I)))
    return out


_PED = _compile(config.NEWS_PEDIATRIC_PATTERNS)
_AI = _compile(config.NEWS_AI_PATTERNS)
_RAD = _compile(config.NEWS_RADIOLOGY_PATTERNS)
_TOPICS = {name: _compile(pats) for name, pats in config.NEWS_TOPIC_PATTERNS.items()}
_PLAYERS = {name: _compile(pats) for name, pats in config.NEWS_PLAYER_PATTERNS.items()}


def _hits(text: str, vocab: list[tuple[str, re.Pattern[str]]]) -> list[str]:
    found = []
    for label, rx in vocab:
        m = rx.search(text)
        if m:
            found.append(m.group(0).lower())
    return sorted(set(found))


def _snippet(text: str, width: int = 320) -> str:
    """A short excerpt centred on the first pediatric term."""
    for _, rx in _PED:
        m = rx.search(text)
        if m:
            lo = max(0, m.start() - width // 2)
            hi = min(len(text), m.end() + width // 2)
            snip = text[lo:hi].replace("\n", " ").strip()
            return ("…" if lo > 0 else "") + snip + ("…" if hi < len(text) else "")
    return text[:width].replace("\n", " ")


def label_story(heading: str, text: str, radiology_domain: bool) -> dict[str, Any]:
    """Classify one story. Returns term lists and the three boolean flags."""
    blob = f"{heading}\n{text}"
    ped = _hits(blob, _PED)
    ai = _hits(blob, _AI)
    rad = _hits(blob, _RAD)
    is_rad = radiology_domain or bool(rad)
    is_rad_ai = bool(ai) and is_rad
    is_ped_rad_ai = is_rad_ai and bool(ped)
    topics = [name for name, vocab in _TOPICS.items() if _hits(blob, vocab)] if is_ped_rad_ai else []
    # Player mentions: skip sponsor blocks (newsletters repeat their sponsor
    # roster in every issue, which would count a vendor hundreds of times
    # without any news about it) and "everyone" round-ups.
    players: list[str] = []
    if is_rad_ai and not re.search(r"sponsor|advertis|partners? of the wire", blob, re.I):
        players = [name for name, vocab in _PLAYERS.items() if _hits(blob, vocab)]
        if len(players) > 5:
            players = []
    return {
        "players": players,
        "pediatric_terms": ped,
        "ai_terms": ai,
        "radiology_terms": rad,
        "radiology_ai": is_rad_ai,
        "pediatric_radiology_ai": is_ped_rad_ai,
        "topics": topics,
    }


# --------------------------------------------------------------------------- #
# Source adapters. Each yields documents:
#   {"source", "date" (YYYY-MM-DD), "url", "title", "html"}
# --------------------------------------------------------------------------- #
def _iso_date(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return m.group(0)
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%d %b %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    m = re.search(r"([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})", s)
    if m and m.group(1).lower() in _MONTHS:
        return dt.date(int(m.group(3)), _MONTHS[m.group(1).lower()], int(m.group(2))).isoformat()
    return None


def _wp_fetch(url: str, params: dict[str, Any]) -> list[dict[str, Any]] | None:
    """One WP REST page; None on a server error (some items crash rendering)."""
    try:
        items = utils.http_get_json(url, params, pause=0.5, timeout=120, max_retries=2)
    except urllib.error.HTTPError as exc:
        if exc.code == 400:
            return []
        return None
    except Exception:  # noqa: BLE001
        return None
    return items if isinstance(items, list) else []


def wordpress_docs(name: str, src: dict[str, Any]) -> list[dict[str, Any]]:
    """Page through every item of each post type via the WP REST API.

    Ids are listed first (cheap, no content), then content is fetched in small
    ``include=`` batches. A batch that returns a server error is bisected so a
    single item whose rendering crashes the server is skipped, not the archive.
    """
    docs: list[dict[str, Any]] = []
    for ptype in src["types"]:
        url = f"{src['base']}/wp-json/wp/v2/{ptype}"
        ids: list[int] = []
        page = 1
        while True:
            items = _wp_fetch(url, {"per_page": 100, "page": page, "orderby": "date",
                                    "order": "asc", "_fields": "id"})
            if not items:
                break
            ids.extend(int(it["id"]) for it in items if "id" in it)
            if len(items) < 100:
                break
            page += 1
        if not ids:
            print(f"    [warn] {name}/{ptype}: could not list items")
            continue

        skipped = 0
        fields = "id,date,link,title,content"

        def fetch_batch(batch: list[int]) -> list[dict[str, Any]]:
            nonlocal skipped
            items = _wp_fetch(url, {"include": ",".join(map(str, batch)), "per_page": len(batch),
                                    "orderby": "include", "_fields": fields})
            if items is not None:
                return items
            if len(batch) == 1:
                skipped += 1
                return []
            mid = len(batch) // 2
            return fetch_batch(batch[:mid]) + fetch_batch(batch[mid:])

        for i in range(0, len(ids), 10):
            for it in fetch_batch(ids[i:i + 10]):
                docs.append(
                    {
                        "source": name,
                        "date": _iso_date(it.get("date")),
                        "url": it.get("link"),
                        "title": html_to_text((it.get("title") or {}).get("rendered", "")),
                        "html": (it.get("content") or {}).get("rendered", ""),
                    }
                )
        print(f"    {name}/{ptype}: {len(ids)} items listed, {len(docs)} fetched so far"
              + (f", {skipped} skipped (server error)" if skipped else ""))
    return docs


_RSNA_LINK_RE = re.compile(
    r'<a\s+href="(https://www\.rsna\.org/news/(\d{4})/([a-z\-]+)/[^"]+)">(.*?)</a>', re.S | re.I
)


def rsna_docs(name: str, src: dict[str, Any]) -> list[dict[str, Any]]:
    """RSNA News: archive page for titles; bodies for pediatric/AI candidates."""
    try:
        page = utils.http_get(src["archive"], pause=0.5, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"    [warn] {name} archive unreachable: {exc}")
        return []
    seen: set[str] = set()
    docs: list[dict[str, Any]] = []
    for m in _RSNA_LINK_RE.finditer(page):
        url, year, month, title_html = m.groups()
        if url in seen:
            continue
        seen.add(url)
        title = html_to_text(title_html)
        mon = month.split("-")[0]
        month_num = _MONTHS.get(mon, 1)
        date = f"{year}-{month_num:02d}-01"
        html = f"<p>{htmllib.escape(title)}</p>"
        candidate = bool(_hits(title, _PED)) or bool(_hits(title, _AI))
        if candidate:
            try:
                body = utils.http_get(url, pause=0.5, timeout=120)
                # Keep only the article's main column; the right rail carries
                # teasers for unrelated stories that would contaminate labels.
                i = body.find('class="col-lg-9 col-12"')
                if i < 0:
                    i = body.find('<div id="content"')
                if i > 0:
                    i = max(body.rfind("<div", 0, i), 0)
                body = body[i:] if i >= 0 else body
                for marker in ('class="col-lg-3 col-12"', "rsna-footer"):
                    j = body.find(marker)
                    if j > 0:
                        body = body[: max(body.rfind("<", 0, j), 0) or j]
                # Drop the trailing "For More Information" block: it carries a
                # teaser list of unrelated RSNA News stories.
                m_more = re.search(r"<h[2-4][^>]*>\s*For More Information", body, re.I)
                if m_more:
                    body = body[: m_more.start()]
                text = html_to_text(body)
                d = _iso_date(text[:800])
                if d:
                    date = d
                html = "<p>" + htmllib.escape(text) + "</p>"
            except Exception as exc:  # noqa: BLE001
                print(f"    [warn] {name}: {url}: {exc}")
        docs.append({"source": name, "date": date, "url": url, "title": title, "html": html})
    print(f"    {name}: {len(docs)} articles listed ({sum(1 for d in docs if len(d['html']) > 400)} bodies fetched)")
    return docs


def _weekdays(start: dt.date, end: dt.date) -> Iterable[dt.date]:
    d = start
    while d <= end:
        if d.weekday() < 5:
            yield d
        d += dt.timedelta(days=1)


def tldr_docs(name: str, src: dict[str, Any]) -> list[dict[str, Any]]:
    """TLDR: one page per weekday, enumerated from NEWSLETTER_START_DATE."""
    start = dt.date.fromisoformat(config.NEWSLETTER_START_DATE)
    today = dt.date.today()
    nl = src["newsletter"]
    docs: list[dict[str, Any]] = []
    misses = 0
    for day in _weekdays(start, today):
        url = f"{src['base']}/{nl}/{day.isoformat()}"
        try:
            page = utils.http_get(url, pause=0.3, timeout=60)
        except urllib.error.HTTPError:
            misses += 1
            continue
        except Exception as exc:  # noqa: BLE001
            print(f"    [warn] {name} {day}: {exc}")
            continue
        # Holiday / missing dates redirect to the latest issue; discard those.
        if day.isoformat() not in page[:20000]:
            misses += 1
            continue
        title_m = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
        title = html_to_text(title_m.group(1)) if title_m else f"{name} {day}"
        # Keep only the story blocks.
        arts = re.findall(r"<article\b.*?</article>", page, re.S)
        body = "".join(arts) if arts else page
        docs.append({"source": name, "date": day.isoformat(), "url": url, "title": title, "html": body})
    print(f"    {name}: {len(docs)} issues ({misses} dates without an issue)")
    return docs


def rss_docs(name: str, src: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        raw = utils.http_get(src["feed"], pause=0.5, use_cache=False)
        root = ET.fromstring(raw.encode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"    [warn] {name} feed unreachable: {exc}")
        return []
    ns = {"content": "http://purl.org/rss/1.0/modules/content/", "atom": "http://www.w3.org/2005/Atom"}
    docs: list[dict[str, Any]] = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        date = _iso_date(it.findtext("pubDate") or it.findtext("dc:date"))
        body = it.findtext("content:encoded", namespaces=ns) or it.findtext("description") or ""
        docs.append({"source": name, "date": date, "url": link, "title": title, "html": body})
    for it in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = (it.findtext("atom:title", namespaces=ns) or "").strip()
        link_el = it.find("atom:link", ns)
        link = link_el.get("href") if link_el is not None else ""
        date = _iso_date(it.findtext("atom:published", namespaces=ns) or it.findtext("atom:updated", namespaces=ns))
        body = it.findtext("atom:content", namespaces=ns) or it.findtext("atom:summary", namespaces=ns) or ""
        docs.append({"source": name, "date": date, "url": link, "title": title, "html": body})
    print(f"    {name}: {len(docs)} feed items")
    return docs


_ADAPTERS = {
    "wordpress": wordpress_docs,
    "rsna_news": rsna_docs,
    "tldr": tldr_docs,
    "rss": rss_docs,
}


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def _norm_title(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()[:80]


def collect(sources: dict[str, dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run every source; return (pediatric-radiology-AI stories, summary).

    ``summary`` carries per-source and per-year denominators (documents scanned,
    stories, radiology-AI stories) so the report can express pediatric AI news
    as a *share* of AI news, not just a count.
    """
    sources = sources or config.NEWSLETTER_SOURCES
    items: list[dict[str, Any]] = []
    per_source: dict[str, dict[str, Any]] = {}
    by_year: dict[str, dict[str, dict[str, int]]] = {}
    topic_counts: dict[str, int] = {t: 0 for t in config.NEWS_TOPIC_PATTERNS}
    # Who is being talked about: stories mentioning each company / tool, over
    # all radiology-AI stories and over the pediatric subset, by year.
    player_counts: dict[str, dict[str, Any]] = {
        p: {"radiology_ai": 0, "pediatric_radiology_ai": 0, "by_year": {}} for p in config.NEWS_PLAYER_PATTERNS
    }

    for name, src in sources.items():
        print(f"  {name} ({src['kind']})")
        adapter = _ADAPTERS[src["kind"]]
        docs = adapter(name, src)
        rad_domain = bool(src.get("radiology_domain"))
        stats = {
            "kind": src["kind"],
            "url": src.get("url"),
            "docs": len(docs),
            "stories": 0,
            "radiology_ai_stories": 0,
            "pediatric_radiology_ai_stories": 0,
            "archive_from": None,
            "archive_to": None,
        }
        dates = sorted(d["date"] for d in docs if d.get("date"))
        if dates:
            stats["archive_from"], stats["archive_to"] = dates[0], dates[-1]
        seen: set[str] = set()
        seen_stories: set[str] = set()
        yrs = by_year.setdefault(name, {})
        for doc in docs:
            year = (doc.get("date") or "")[:4] or "unknown"
            y = yrs.setdefault(year, {"docs": 0, "stories": 0, "radiology_ai": 0, "pediatric_radiology_ai": 0})
            y["docs"] += 1
            for heading, text in split_sections(doc["html"], doc["title"]):
                # A story re-run in a later issue (same heading and opening
                # text) is counted once, in numerator and denominator alike.
                key = _norm_title(heading) + "|" + _norm_title(text[:160])
                if key in seen:
                    continue
                seen.add(key)
                lab = label_story(heading, text, rad_domain)
                stats["stories"] += 1
                y["stories"] += 1
                if lab["radiology_ai"]:
                    stats["radiology_ai_stories"] += 1
                    y["radiology_ai"] += 1
                    for pl in lab["players"]:
                        pc = player_counts[pl]
                        pc["radiology_ai"] += 1
                        pc["by_year"][year] = pc["by_year"].get(year, 0) + 1
                        if lab["pediatric_radiology_ai"]:
                            pc["pediatric_radiology_ai"] += 1
                if not lab["pediatric_radiology_ai"]:
                    continue
                # The same story often appears as a feature and again as a
                # digest bullet (with a "The Wire · " prefix); keep the first.
                story_key = _norm_title(re.sub(r"^.*?·\s*", "", heading).rstrip(": "))
                if story_key and story_key in seen_stories:
                    continue
                seen_stories.add(story_key)
                stats["pediatric_radiology_ai_stories"] += 1
                y["pediatric_radiology_ai"] += 1
                for t in lab["topics"]:
                    topic_counts[t] += 1
                items.append(
                    {
                        "source": name,
                        "date": doc.get("date"),
                        "issue_title": doc["title"],
                        "story": heading,
                        "url": doc["url"],
                        "snippet": _snippet(text),
                        "pediatric_terms": lab["pediatric_terms"],
                        "ai_terms": lab["ai_terms"],
                        "radiology_terms": lab["radiology_terms"],
                        "topics": lab["topics"],
                        "players": lab["players"],
                    }
                )
        per_source[name] = stats
        print(
            f"    -> {stats['stories']} stories, {stats['radiology_ai_stories']} radiology-AI, "
            f"{stats['pediatric_radiology_ai_stories']} pediatric radiology-AI"
        )

    items.sort(key=lambda r: (r.get("date") or "", r["source"]), reverse=True)
    summary = {
        "collected_on": dt.date.today().isoformat(),
        "tldr_start_date": config.NEWSLETTER_START_DATE,
        "sources": per_source,
        "by_year": by_year,
        "topics": dict(sorted(topic_counts.items(), key=lambda kv: kv[1], reverse=True)),
        "players": dict(sorted(player_counts.items(), key=lambda kv: kv[1]["radiology_ai"], reverse=True)),
        "blocked": config.NEWSLETTER_BLOCKED,
        "total_pediatric_radiology_ai_stories": len(items),
    }
    return items, summary


def load_items() -> list[dict[str, Any]]:
    p = config.PROCESSED_DIR / "newsletter_items.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
