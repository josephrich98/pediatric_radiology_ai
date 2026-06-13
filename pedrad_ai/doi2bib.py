"""doi2bib helper: turn a DOI into a BibTeX entry.

Per the project convention (inherited from the sibling radiogenomics repo),
every paper that ends up cited in a report passes through doi2bib so the
references are clean and consistent.

doi2bib works by content-negotiation: it asks ``doi.org`` for the record with an
``Accept: application/x-bibtex`` header and returns the BibTeX the registrar
sends back. We do exactly that directly against ``doi.org`` (more reliable than
scraping the doi2bib.org front end, which 404s on some valid DOIs), and fall
back to the doi2bib.org endpoint if needed. New entries are de-duplicated by
cite key and appended to a ``.bib`` file.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import config, utils

DOI_ORG = "https://doi.org/"
DOI2BIB = "https://www.doi2bib.org/bib/"
_BIBTEX_HEADERS = {"Accept": "application/x-bibtex; charset=utf-8"}


def fetch_bibtex(doi: str) -> str | None:
    """Return the BibTeX string for ``doi`` (or None on failure)."""
    if not doi:
        return None
    doi = doi.strip()
    # Primary: doi.org content negotiation (what doi2bib does under the hood).
    for url, headers in ((DOI_ORG + doi, _BIBTEX_HEADERS), (DOI2BIB + doi, None)):
        try:
            text = utils.http_get(url, headers=headers, pause=0.4).strip()
        except Exception:
            continue
        if text.startswith("@"):
            return _tidy(text)
    return None


def _tidy(bib: str) -> str:
    """Collapse the internal whitespace registrars sometimes inject into fields."""
    return re.sub(r"[ \t]{2,}", " ", bib).strip()


def _existing_keys(bib_path: Path) -> set[str]:
    if not bib_path.exists():
        return set()
    return set(re.findall(r"@\w+\{([^,]+),", bib_path.read_text(encoding="utf-8")))


def append_dois(dois: list[str], bib_path: str | Path | None = None) -> dict[str, int]:
    """Fetch BibTeX for each DOI and append new entries to ``bib_path``.

    Returns a small summary dict (added / skipped / failed). Entries already
    present (by cite key) are skipped so the file can be regenerated safely.
    """
    bib_path = Path(bib_path) if bib_path else config.REPORT_DIR / "references.bib"
    bib_path.parent.mkdir(parents=True, exist_ok=True)
    existing = _existing_keys(bib_path)
    added = skipped = failed = 0
    chunks: list[str] = []
    for doi in dict.fromkeys(d for d in dois if d):  # de-dup, preserve order
        bib = fetch_bibtex(doi)
        if not bib:
            failed += 1
            continue
        key_match = re.match(r"@\w+\{([^,]+),", bib)
        key = key_match.group(1) if key_match else None
        if key and key in existing:
            skipped += 1
            continue
        if key:
            existing.add(key)
        chunks.append(bib)
        added += 1
    if chunks:
        with bib_path.open("a", encoding="utf-8") as fh:
            if bib_path.stat().st_size > 0:
                fh.write("\n\n")
            fh.write("\n\n".join(chunks) + "\n")
    return {"added": added, "skipped": skipped, "failed": failed}
