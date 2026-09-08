# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Desired Venues: Society of pediatric radiology (SPR) abstract, Pediatric Radiology journal review paper

SPR: SCIENTIFIC ABSTRACTS (BOTH ORAL & POSTER FORMAT) - You will need to complete ALL of the sections listed, i.e. Title, Purpose, Methods, Results and Conclusions. 

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
   on-topic — tracked over time from a pre-deep-learning 2008 baseline through
   the current (partial, "YTD") year.
2. **How much of radiology AI is pediatric?** The pediatric fraction of the
   radiology-AI corpus, by year and by modality.
3. **Who are the biggest players?** Most-cited papers (Semantic Scholar) and
   most-starred open-source tools (GitHub), for radiology AI overall and for
   pediatric radiology specifically.
4. **What does the field do well, what is bleeding-edge, what is unresolved?** A
   curated synthesis for clinical leadership.
5. **What is the news saying about pediatric radiology AI?** Newsletter and
   trade-press archives (The Imaging Wire, RSNA News, TLDR, Signify Research,
   Radiology Business) scanned for stories where pediatric and AI terms
   co-occur, with counts by year/source and topic tags.

## Repository Layout

- `pedrad_ai/` — core Python package. Each public data source has its own
  collector module; `analysis.py` derives trends and fractions; `utils.py` is a
  cached, rate-limited HTTP client. Collectors use **only the standard library**
  for networking so pulls run anywhere.
  - `config.py` — **the single place to retune scope**: search queries, year
    range, venues, keyword sets.
  - `pubmed.py`, `crossref.py` — publication counts over time; `pubmed.py` also
    computes the AI fraction of a journal set (used for the RSNA/ACR/ECR/SPR
    society analysis).
  - `patents.py` — PatentsView granted-patent counts (needs `PATENTSVIEW_API_KEY`).
  - `github_repos.py` — repository star leaderboards (uses `gh` CLI auth or
    `GITHUB_TOKEN`).
  - `openalex.py` — citation counts and most-cited papers. `top_cited_union`
    runs several modality/task searches and dedupes, because a single
    "radiology deep learning" query misses landmark papers whose titles never
    say "radiology" (e.g. TotalSegmentator). Replaces the rate-limited
    `semantic_scholar.py` (kept as a fallback).
  - `conferences.py` — ML/CV venues via DBLP (radiology share) and radiology
    societies via their journals (AI share). DBLP throttles hard; the collector
    paces gently and skips fast on failure.
  - `newsletters.py` — newsletter / trade-press archive scanner. Four adapter
    kinds (`wordpress` REST API, `rsna_news` archive page, `tldr` dated daily
    pages, `rss`); each issue is split into stories at heading boundaries and
    labelled by keyword co-occurrence (`NEWS_*_PATTERNS` in `config.py`).
    Sources are declared in `config.NEWSLETTER_SOURCES`; AuntMinnie and
    Diagnostic Imaging are Cloudflare-blocked and listed in
    `NEWSLETTER_BLOCKED` so the report can say so.
  - `fda_devices.py` — parses the FDA AI-enabled device list spreadsheet
    (standard library only) and keeps the Radiology panel: devices per year,
    clearances per company, pediatric-named devices. The commercial-players
    slide/report also cross-checks `config.COMMERCIAL_PEDIATRIC` (curated
    products with pediatric indications) against it.
  - `validation.py` — "is the query sufficient?": recall on
    `config.GOLD_PAPERS` (landmark DOIs resolved to PMIDs), a strict
    title/abstract-only variant of each query as a precision proxy, and an
    audit of PubMed's automatic term translation. Output feeds the methods
    slide and the trends report.
  - `examples.py` — fetches representative images (repository README image,
    open-access article figure via PMC, vendor page image) into
    `figures/examples/` with a manifest for the "what it looks like" slides.
  - `paper_db.py`, `extract.py` — the **paper database**: one structured row
    per pediatric radiology-AI paper (model name, modality, patient population,
    clinical problem, plain-language model description, journal, year, DOI/link,
    and whether the model is open-source / commercial / unreleased / unclear).
    `extract.py` reads one abstract with Claude under a fixed Pydantic schema
    (`client.messages.parse` with `output_format=`, so the reply is a validated
    object, not text to scrape); `paper_db.py` owns the store, the candidate
    search, the release-status cross-checks, and the CSV / markdown exports.
    See "Paper database" below.
  - `curated.py` — hand-written context that follows the data: the clinical
    question each most-cited paper answers (keyed by DOI), what each
    well-known repository is, and the "worth knowing" list.
  - `doi2bib.py` — DOI → BibTeX via doi.org content negotiation (see "Adding
    References" below).
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
python scripts/collect_newsletters.py   # or --source "RSNA News" to restrict
python scripts/collect_fda.py           # FDA AI-enabled device list (Radiology panel)
python scripts/validate_queries.py      # recall / precision / term audit of the PubMed queries
python scripts/collect_examples.py      # example images for the slides
python scripts/build_paper_db.py        # paper database (reads abstracts; costs money — see below)
python scripts/make_figures.py
python scripts/build_reports.py
python scripts/build_slides.py      # writes slides/pedrad_ai_slides.tex
cd slides && latexmk -pdf pedrad_ai_slides.tex   # compile the Beamer deck
python scripts/build_pptx.py        # editable PowerPoint version of the same deck (needs python-pptx)
```

The Beamer deck (`slides/`) is generated from the same processed data, so its
headline numbers stay consistent with the reports. The template uses `@@KEY@@`
placeholders (not `str.format`) because the LaTeX body is full of literal braces.
The footline is just "n / N" bottom-right (no Madrid bottom bar).
`scripts/build_pptx.py` parses the generated `.tex` and rebuilds each frame as
a native PowerPoint slide (pictures, text boxes, tables, columns), so figures
can be moved and resized in PowerPoint. It only understands the LaTeX subset
the template uses; if a new construct is added to the template, add a case
there too. Requires `python-pptx` (`pip install -e ".[slides]"`).

### API etiquette and keys

All collectors work **without API keys** but are faster and less rate-limited
with them. Set as environment variables:

- `PEDRAD_AI_EMAIL` — identifying email sent to NCBI/Crossref (defaults set).
- `NCBI_API_KEY` — raises the PubMed rate limit from 3 to 10 req/s.
- `SEMANTIC_SCHOLAR_API_KEY` — raises the Semantic Scholar limit.
- `GITHUB_TOKEN` — for GitHub search; otherwise the `gh` CLI token is used.
- `ANTHROPIC_API_KEY` — required only by the paper database; without it that
  step keeps the committed database and just regenerates its exports.
  `PEDRAD_AI_EXTRACT_MODEL` / `_EFFORT` / `_LIMIT` / `_WORKERS` override the
  extraction defaults in `config.py`.

Responses are cached under `data/raw/cache/`. Delete that directory to force a
fresh pull. Be patient: a full PubMed pull is hundreds of small queries paced
under the rate limit.

## Paper database

`data/processed/pedrad_paper_db.csv` (readable view: `reports/04_paper_database.md`)
is the one deliverable produced by reading papers rather than counting them. It
is built by code and must stay that way:

- **Candidates** are whatever `config.QUERIES["pediatric_radiology_ai"]` returns
  from `PAPER_DB_START_YEAR` to `END_YEAR`, one ESearch per year. No hand-picking.
- **Each new abstract is read once.** Every row stores the hash of the exact
  text the model saw (`input_fingerprint`) plus the prompt/schema fingerprint. A
  paper is re-read only when it is new, when PubMed changed the record, or when
  `extract.PROMPT_VERSION` / `config.PAPER_DB_SCHEMA_VERSION` is bumped. Bump
  those when the field set or the instructions change; re-extracting the whole
  corpus is then a `--reextract` run, not a manual cleanup.
- **Screened-out papers stay in the store** with `include: false`, so a rejected
  record costs one extraction ever, not one per refresh.
- **Nothing in the table is hand-edited in place.** Corrections go in
  `data/paper_db_overrides.json` keyed by PMID; they are applied when the CSV
  and markdown are written, never baked into the stored extraction. Deleting an
  entry reverts that row. Apply with `--rebuild`, which makes no API calls.
- **A fresh clone reproduces the table** from the committed JSON with
  `python scripts/build_paper_db.py --rebuild`.
- **Cost.** Each new paper is one structured-output call (~$0.02 with
  `claude-opus-5` at effort `low`), so a run is capped at
  `config.PAPER_DB_RUN_LIMIT` papers. `--dry-run` prints the count and the
  estimate before spending anything. The full 2015-present corpus is ~10,000
  papers; fill it in batches, or with `--all` deliberately.
- **The release column is not left to the model alone.** A code-hosting URL in
  the abstract settles "open-source", and a product already on
  `config.COMMERCIAL_PEDIATRIC` or the FDA pediatric-named device list settles
  "commercial"; both only upgrade an "unclear" verdict, and the evidence is
  recorded in `release_evidence`. Read "unclear" as "the abstract does not say",
  not as "unavailable", in both the report and the slides.

Vocabularies (`PAPER_DB_MODALITIES`, `PAPER_DB_TASKS`, ...) live in `config.py`
and are compiled straight into the extraction schema, so the database groups on
the same axes as the count-based breakdowns. Adding a value there is enough; do
not hard-code categories in `extract.py`.

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

## Query hygiene (learned the hard way)

PubMed's automatic term mapping silently expands bare words: `ultrasound`
becomes the "diagnostic imaging" MeSH *subheading* (attached to almost any
imaging paper), `tomography` becomes a MeSH tree that includes optical
coherence tomography, and `CT` maps to journal names. Query version 1 counted
about two-thirds of radiology-AI papers as "ultrasound" for this reason.
Rules now in force in `config.py`:

- Modality and task term groups (`MODALITY_TERMS`, `TASK_TERMS`) are entirely
  `[tiab]`-fielded: a paper counts only if its title/abstract names the term.
- `_RADIOLOGY_TERMS` fields the ambiguous tokens and excludes ophthalmic,
  dental, pathology, endoscopic and microscopy imaging with a `NOT` clause.
- After any change to a query, run `scripts/validate_queries.py` and look at
  the `broad_only_sample` in `data/processed/query_validation.json`.
- Task categories are defined by what the model *produces*, one product each
  (v3, 2026-09): detection / diagnosis (a present-finding label or box),
  segmentation (a mask), measurement / quantification (a number: bone age,
  Cobb angle, volume), outcome prediction (a future risk), reconstruction /
  imputation (a better or missing image), report generation / LLM (text),
  foundation model / vision-language (a reusable backbone), agent /
  autonomous, workflow / non-interpretive. `config.TASK_GLOSS` carries the
  one-line meaning shown under the modality x task slides.
- `config.PEDIATRIC_PROBLEM_TERMS` (clinical problems: bone age, fracture,
  pneumonia, appendicitis, brain tumor, ...) is counted against the pediatric
  query per era (`config.ERAS`: 2008-2022 and 2023-present) by
  `pubmed.problem_counts` into `data/processed/pubmed_pediatric_problems.json`.
- The most-cited lists are also collected per era
  (`top_papers_<name>_<era>.json`, OpenAlex `to_publication_date`) because
  citation counts favor old papers; the slides show one table per era.
- `pubmed.crosstab` builds the modality x task tables with one date-range
  query per cell (`data/processed/pubmed_crosstab.json`).

## Conventions

- Standard-library-only networking in collectors; analysis/plotting may use
  pandas/numpy/matplotlib.
- Every collector degrades gracefully (returns empty / zero) if its service is
  unreachable, so one blocked API never aborts the pipeline.
- Determinism: counts are date-stamped by the year facet, not by "now", so
  re-running reproduces the same series (modulo new records being indexed).
- `END_YEAR` is the current calendar year, so every re-run reaches the present.
  That year is partial: `analysis.summarize` uses the last complete year for
  headline numbers and growth rates and reports the current year as `*_ytd`;
  reports and figures label it "YTD".
- Slides are regenerated by `scripts/build_slides.py`; the most-cited tables
  show the top 10 per era and fall back to a title heuristic for papers not in
  `curated.PAPER_QUESTIONS`. Add new entries there when the rankings change.
  Hand-written slide content lives next to the data it follows:
  `curated.PAPER_SPOTLIGHTS` (one slide per landmark pediatric paper, image
  from `config.EXAMPLE_IMAGES` group "spotlight", fetched by
  `collect_examples.py` from PMC by figure number), `config.PEDIATRIC_DATASETS`
  (the datasets slide; sizes verified against primary sources on 2026-09-07),
  and `curated.WORTH_KNOWING`. The pediatric modality chart omits mammography
  (its pediatric-query hits are adult breast papers). The trade-press section
  lists every pediatric story per year from 2023 (`newsletter_items.json`).
- The deck has one slide summarizing Kamran et al. 2025 (Pediatr Radiol
  scoping review, `reference.pdf`) as an independent cross-check; that is the
  only place it is cited.
- To refresh to today, run `python scripts/refresh.py` (clears the cache except
  DBLP entries, re-runs every collector incl. FDA, validation and example
  images, adds the papers that are new since the last run to the paper database
  (`--skip paperdb`, `--paper-db-limit N`, `--paper-db-all`), then figures, reports, slides,
  latexmk, and the `.pptx` export; `--quick`, `--keep-cache`, `--no-slides`, `--skip <collector>`,
  `--dry-run`). The same script runs monthly in
  `.github/workflows/refresh.yml`, which opens a pull request with the
  regenerated deliverables rather than pushing to main; it can also be
  triggered by hand from the Actions tab.
