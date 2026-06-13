# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This repository measures and reports on the growth and current landscape of
**artificial intelligence in radiology**, with particular attention to the
**pediatric** subset. It exists to inform clinical and research leadership at a
children's hospital — there is **no manuscript** that comes from this work and no
LaTeX build. The deliverables are data pulls, figures, and plain-language
markdown reports.

The questions it answers:

1. **How popular is radiology AI, and is it still growing?** Publication counts
   (PubMed, Crossref), granted patents (PatentsView), open-source software
   (GitHub), and the share of major AI / imaging conferences (DBLP) that is
   on-topic — tracked over time from a pre-deep-learning 2008 baseline.
2. **How much of radiology AI is pediatric?** The pediatric fraction of the
   radiology-AI corpus, by year and by modality.
3. **Who are the biggest players?** Most-cited papers (Semantic Scholar) and
   most-starred open-source tools (GitHub), for radiology AI overall and for
   pediatric radiology specifically.
4. **What does the field do well, what is bleeding-edge, what is unresolved?** A
   curated synthesis for clinical leadership.

## Repository Layout

- `pedrad_ai/` — core Python package. Each public data source has its own
  collector module; `analysis.py` derives trends and fractions; `utils.py` is a
  cached, rate-limited HTTP client. Collectors use **only the standard library**
  for networking so pulls run anywhere.
  - `config.py` — **the single place to retune scope**: search queries, year
    range, venues, keyword sets.
  - `pubmed.py`, `crossref.py` — publication counts over time.
  - `patents.py` — PatentsView granted-patent counts.
  - `github_repos.py` — repository star leaderboards (uses `gh` CLI auth or
    `GITHUB_TOKEN`).
  - `semantic_scholar.py` — citation counts and most-cited papers.
  - `conferences.py` — DBLP venue title pulls + keyword labelling.
  - `doi2bib.py` — DOI → BibTeX (see "Adding References" below).
- `scripts/` — runnable CLI entry points. `run_all.py` runs the whole pipeline;
  individual `collect_*.py` scripts run one source; `make_figures.py` and
  `build_reports.py` produce the deliverables.
- `notebooks/` — exploratory analysis and figure generation.
- `reports/` — generated markdown reports and `references.bib`.
- `figures/` — generated PNGs.
- `data/raw/`, `data/processed/` — collector output (gitignored except for a
  small committed snapshot if needed). `data/raw/cache/` holds the HTTP cache.

## Development Setup

```bash
pip install -e .
# optional extras
pip install -e ".[notebooks,dev]"
```

`pyproject.toml` is the authoritative source for dependencies. Add new
dependencies there rather than installing ad hoc.

## Running the Pipeline

```bash
python scripts/run_all.py            # full collection -> figures -> reports
python scripts/run_all.py --quick    # headline PubMed queries only (fast)

# or one source at a time
python scripts/collect_pubmed.py
python scripts/collect_landscape.py
python scripts/collect_conferences.py
python scripts/collect_patents.py
python scripts/make_figures.py
python scripts/build_reports.py
```

### API etiquette and keys

All collectors work **without API keys** but are faster and less rate-limited
with them. Set as environment variables:

- `PEDRAD_AI_EMAIL` — identifying email sent to NCBI/Crossref (defaults set).
- `NCBI_API_KEY` — raises the PubMed rate limit from 3 to 10 req/s.
- `SEMANTIC_SCHOLAR_API_KEY` — raises the Semantic Scholar limit.
- `GITHUB_TOKEN` — for GitHub search; otherwise the `gh` CLI token is used.

Responses are cached under `data/raw/cache/`. Delete that directory to force a
fresh pull. Be patient: a full PubMed pull is hundreds of small queries paced
under the rate limit.

## Adding References

Per project convention, **every paper cited in a report passes through doi2bib**:

1. Fetch BibTeX from `https://www.doi2bib.org/bib/<DOI>` (the `pedrad_ai.doi2bib`
   module does this and de-duplicates by cite key).
2. New entries are appended to `reports/references.bib`.

`build_reports.py` collects DOIs from the most-cited-paper tables and the
curated landmark list and runs them through doi2bib automatically.

## Writing Style for Reports

The audience is **clinical leadership at a children's hospital**, not ML
researchers. Favor clinical framing (workflow, dose, validation, liability) over
model-architecture detail. Use American English spelling. Do not overstate:
distinguish retrospective accuracy from prospective clinical benefit, and flag
that recent-year counts undercount because of indexing/grant lag. Keep
quantitative claims consistent with the collected data in `data/processed/`.

## Conventions

- Standard-library-only networking in collectors; analysis/plotting may use
  pandas/numpy/matplotlib.
- Every collector degrades gracefully (returns empty / zero) if its service is
  unreachable, so one blocked API never aborts the pipeline.
- Determinism: counts are date-stamped by the year facet, not by "now", so
  re-running reproduces the same series (modulo new records being indexed).
