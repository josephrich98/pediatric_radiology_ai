"""Which stored records the review actually describes, and how they rank.

The paper-database store (``pedrad_paper_db.json``) holds every record the
systematic search retrieved, screened in or out, so that a rejected record
costs one reading ever. The manuscript, the exported table and the slides must
nonetheless all describe the *same* subset of it — the included primary studies
— or a number in one will contradict a number in another. This module is the
one place that subset is defined; :mod:`pedrad_ai.paper_db` exports it,
``scripts/review_stats.py`` counts it, ``scripts/make_review_figures.py`` draws
it and ``scripts/build_slides.py`` presents it.

The partition follows the PRISMA flow:

``screened_all``
    every stored record
``conference``
    removed before screening by the publication-form criterion
``screened``
    what remains — the records that were read
``excluded``
    screened out as not pediatric radiology AI
``in_scope``
    screened in
``non_primary``
    in scope but a review, editorial, comment or guideline: kept in the store
    (they are part of the literature, and their reference lists were checked)
    but reported separately, because the eligibility criteria admit primary
    research only
``included``
    primary studies — the review corpus

The second half of the module is the impact ranking. The corpus is far too
large to put on a slide, so the slides show all of it in aggregate and then
name individual papers by a field- and year-normalized citation measure. See
:func:`impact` for why that measure is FWCI first and RCR second.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from . import config

# Conference proceedings are outside the review's publication-form criterion
# (Supplementary Table S2): they cannot support judgements about study design,
# most are not extractable, and unlike preprints they carry no DOI linking them
# to the later full paper, so deduplication cannot resolve the double count.
# They are retrieved and reported, but not screened. Detected from the venue
# string, because the record itself does not carry a publication form.
CONFERENCE_VENUE = re.compile(
    r"lecture notes in computer science|proceedings|symposium|conference|workshop|"
    r"\bisbi\b|\bspie\b|\bmiccai\b|\bcvpr\b|\biccv\b|\beccv\b|\bneurips\b|\bmidl\b|"
    r"\bipmi\b|\bembc\b|\bicip\b|\baaai\b|communications in computer and information science",
    re.I,
)

# PubMed publication types that make a record non-primary. `Review` alone is not
# enough — PubMed types Nature Protocols articles and society white papers as
# Review — so a record is non-primary only when its own extracted study_design
# also reads as a review, or when the type is unambiguous.
NONPRIMARY_TYPES = {
    "Editorial", "Comment", "Letter", "News", "Published Erratum",
    "Retraction of Publication", "Retracted Publication", "Practice Guideline",
    "Guideline", "Consensus Development Conference",
}
NONPRIMARY_DESIGN = re.compile(
    r"\b(narrative review|systematic review|scoping review|literature review|state-of-the-art review|"
    r"review article|editorial|commentary|consensus statement|position statement|white paper|"
    r"multi-society|perspective|opinion)\b", re.I)


def key(row: dict[str, Any]) -> str:
    """The store key for a record: PMID, or the source-prefixed id without one."""
    return str(row.get("record_id") or row.get("pmid") or "")


def is_conference(row: dict[str, Any]) -> bool:
    """True when the record's venue is a conference proceedings volume."""
    return bool(CONFERENCE_VENUE.search(str(row.get("journal") or "")))


def publication_types(row: dict[str, Any]) -> list[str]:
    """The record's PubMed publication types, however they were stored."""
    types = row.get("publication_types") or []
    if isinstance(types, str):
        types = [t.strip(" '\"[]") for t in types.split(";" if ";" in types else ",")]
    return [t for t in (str(t).strip() for t in types) if t]


def is_nonprimary(row: dict[str, Any]) -> bool:
    """True for reviews, editorials, comments, guidelines and errata."""
    if NONPRIMARY_DESIGN.search(row.get("study_design") or ""):
        return True
    return bool(NONPRIMARY_TYPES & set(publication_types(row)))


@dataclass
class Partition:
    """The PRISMA partition of the store. Every record lands in exactly one of
    ``conference``, ``excluded``, ``non_primary`` and ``included``."""

    screened_all: list[dict[str, Any]] = field(default_factory=list)
    conference: list[dict[str, Any]] = field(default_factory=list)
    screened: list[dict[str, Any]] = field(default_factory=list)
    excluded: list[dict[str, Any]] = field(default_factory=list)
    in_scope: list[dict[str, Any]] = field(default_factory=list)
    non_primary: list[dict[str, Any]] = field(default_factory=list)
    included: list[dict[str, Any]] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        return {
            "screened_all_sources": len(self.screened_all),
            "conference_excluded": len(self.conference),
            "screened": len(self.screened),
            "excluded_screening": len(self.excluded),
            "in_scope": len(self.in_scope),
            "non_primary": len(self.non_primary),
            "included": len(self.included),
        }


def partition(rows: Iterable[dict[str, Any]]) -> Partition:
    """Split records into the PRISMA boxes. Duplicate keys are dropped once."""
    part = Partition()
    seen: set[str] = set()
    for row in rows:
        rid = key(row)
        if rid and rid in seen:
            continue
        if rid:
            seen.add(rid)
        part.screened_all.append(row)
        if is_conference(row):
            part.conference.append(row)
            continue
        part.screened.append(row)
        if not row.get("include"):
            part.excluded.append(row)
            continue
        part.in_scope.append(row)
        (part.non_primary if is_nonprimary(row) else part.included).append(row)
    return part


def included_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Just the review corpus: included primary studies."""
    return partition(rows).included


def included_ids(path: str | None = None) -> set[str]:
    """The corpus ids as last exported by ``scripts/review_stats.py``.

    Consumers that read the exported CSV rather than the store use this so they
    do not re-derive the rule; an empty set means "no filter available".
    """
    p = config.PROCESSED_DIR / "review_included_ids.json" if path is None else path
    try:
        return set(json.loads(open(p, encoding="utf-8").read()))
    except (OSError, ValueError):
        return set()


# --------------------------------------------------------------------------- #
# Impact
# --------------------------------------------------------------------------- #
# Two measures on the same scale, both "1.0 = the average paper of this field
# and year":
#
#   fwci  OpenAlex's field-weighted citation impact. Computed for anything with
#         a DOI, which is what makes it usable here: the Embase-only records
#         have no PMID and therefore no RCR, and dropping them would quietly
#         restrict every impact-filtered view to the PubMed layer. OpenAlex also
#         computes it for the current year.
#   rcr   iCite's relative citation ratio. PubMed only, and undefined until a
#         paper is about two years old, but it is the measure clinical readers
#         know and it is computed over the biomedical literature rather than
#         over all of scholarship.
#
# FWCI is preferred so that one measure covers the whole corpus; RCR fills in
# where OpenAlex has no value. Rows with neither fall back to citations per
# year, which is not normalized and therefore only breaks ties.
IMPACT_SOURCES = ("fwci", "rcr")


def _as_float(value: Any) -> float | None:
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return float(value) if isinstance(value, (int, float)) else None


def impact(row: dict[str, Any], min_citations: int | None = None) -> tuple[float | None, str]:
    """(value, measure) for a record: FWCI, else RCR, else (None, "").

    Both measures divide by the expected citation count for the field and year,
    and that expectation is a fraction of a citation for the current year — so a
    paper published this month with one citation scores 90x the world average
    and would head any ranking. A normalized value is therefore reported only
    once the raw count reaches ``config.IMPACT_MIN_CITATIONS``; below that the
    record ranks on citations per year, where being new is a handicap rather
    than an advantage.
    """
    floor = config.IMPACT_MIN_CITATIONS if min_citations is None else min_citations
    if floor and (_as_float(row.get("citations")) or 0.0) < floor:
        return None, ""
    for name in IMPACT_SOURCES:
        val = _as_float(row.get(name))
        if val is not None:
            return val, name
    return None, ""


def impact_value(row: dict[str, Any]) -> float | None:
    return impact(row)[0]


def _num(value: Any) -> float:
    return _as_float(value) or 0.0


def impact_sort_key(row: dict[str, Any]) -> tuple:
    """Descending impact, then citation rate, then raw count, then recency."""
    val, _ = impact(row)
    return (
        0 if val is None else 1,
        val or 0.0,
        _num(row.get("citations_per_year")),
        _num(row.get("citations")),
        _num(row.get("year")),
    )


def by_impact(rows: Iterable[dict[str, Any]], limit: int | None = None) -> list[dict[str, Any]]:
    """Records ranked by normalized citation impact, highest first."""
    ranked = sorted(rows, key=impact_sort_key, reverse=True)
    return ranked[:limit] if limit else ranked


def impact_threshold(rows: Iterable[dict[str, Any]], percentile: int | None = None) -> float | None:
    """The impact value at ``percentile`` of the scored records.

    A percentile rather than a fixed multiple, because the corpus does not sit
    at 1.0: the median included study has an FWCI near 2, so a plain "twice the
    world average" would select half of it. The top decile is a claim about
    this literature that stays true as the corpus grows.
    """
    pct = config.SLIDE_IMPACT_PERCENTILE if percentile is None else percentile
    values = sorted(v for v in (impact_value(r) for r in rows) if v is not None)
    if not values:
        return None
    return values[min(len(values) - 1, int(len(values) * pct / 100))]


def high_impact(rows: Iterable[dict[str, Any]], floor: float | None = None,
                percentile: int | None = None) -> list[dict[str, Any]]:
    """The most-cited slice of the corpus, on the normalized measure.

    Records with no normalized measure at all are excluded rather than assumed
    average: the point of the subset is to name work the field demonstrably
    engaged with.
    """
    rows = list(rows)
    if floor is None:
        floor = impact_threshold(rows, percentile)
    if floor is None:
        return []
    return [r for r in rows if (impact_value(r) or 0.0) >= floor]


def citations_per_year(citations: int | None, year: int | None,
                       today: dt.date | None = None) -> float | None:
    """iCite's definition, for records iCite does not cover.

    Citations divided by years since publication, with the current year counted
    as a whole year so that this year's papers get a rate rather than a division
    by zero.
    """
    if citations is None or not year:
        return None
    span = max(1, (today or dt.date.today()).year - int(year) + 1)
    return round(citations / span, 2)


def source_label(row: dict[str, Any]) -> str:
    """Where the record entered the corpus, for the tables that say so."""
    return {"pubmed": "PubMed", "embase": "Embase", "openalex": "OpenAlex"}.get(
        str(row.get("source") or "pubmed"), str(row.get("source")))


def counts_by_source(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        label = source_label(row)
        out[label] = out.get(label, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))
