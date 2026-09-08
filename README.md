# pediatric_radiology_ai

## TLDR:

python scripts/refresh.py
python scripts/build_slides.py
python scripts/build_pptx.py
*download pptx*

## AI slop:

Tools to measure the **growth and landscape of radiology AI**, with a focus on
the **pediatric** subset. Built to brief clinical and research leadership at a
children's hospital — not to produce a paper.

## What it answers

- **How popular is radiology AI, and is it still growing?** Tracks PubMed and
  Crossref publication counts, PatentsView granted patents, GitHub software, and
  the share of NeurIPS / MICCAI / CVPR / ISBI that is on-topic — from a 2008
  pre-deep-learning baseline to today.
- **How much of radiology AI is pediatric?** The pediatric fraction over time
  and by modality.
- **Who are the biggest players?** Most-cited papers (Semantic Scholar) and
  most-starred open-source tools (GitHub), overall and pediatric-specific.
- **What does the field do well / what is bleeding-edge / what is unresolved?**
  A curated synthesis for clinicians.
- **What, specifically, has been built for children?** A structured database
  with one row per pediatric radiology-AI paper: model name, modality, patient
  population, clinical problem, a plain-language description of what the model
  does, journal, year, DOI, and whether the model is open-source, commercial, or
  unreleased.

## Quickstart

```bash
pip install -e .
python scripts/run_all.py --quick      # fast headline run
python scripts/run_all.py              # full run (slower, hits more queries)
python scripts/refresh.py              # bring everything up to today: clears the
                                       # HTTP cache, re-collects, rebuilds, compiles slides
```

`run_all.py` rebuilds from cached responses (reproducible); `refresh.py`
re-pulls every source as of today. A monthly GitHub Action
(`.github/workflows/refresh.yml`) runs the refresh and opens a pull request.

Outputs land in:

- `reports/00_popularity_trends.md` — growth + pediatric share, with tables
- `reports/01_landscape_players.md` — most-cited papers, most-starred tools
- `reports/02_state_of_the_field.md` — does-well / bleeding-edge / unresolved
- `data/processed/pedrad_paper_db.csv` — the paper database, one row per paper
  (`reports/04_paper_database.md` is the readable view of it)
- `reports/references.bib` — doi2bib output for cited papers
- `figures/*.png` — trend and breakdown plots
- `slides/pedrad_ai_slides.pdf` — Beamer deck summarizing the whole story
  (regenerate with `python scripts/build_slides.py` then `latexmk -pdf` in `slides/`)
- `slides/pedrad_ai_slides.pptx` — the same deck as an editable PowerPoint file:
  every figure is a movable picture, text lives in text boxes, tables are real
  tables (`pip install -e ".[slides]"` then `python scripts/build_pptx.py`)

## The paper database

`data/processed/pedrad_paper_db.csv` is built by code, not maintained by hand.
Candidates come from the pediatric radiology-AI PubMed query; each new abstract
is read once by Claude under a fixed Pydantic schema
(`pedrad_ai/extract.py`), and the row is stored with a hash of the text it was
read from. So a re-run only pays for papers that are new, an interrupted run
resumes, and a fresh clone rebuilds the whole table from the committed JSON
with no API calls at all.

```bash
pip install -e ".[db]"                          # anthropic + pydantic
export ANTHROPIC_API_KEY=...
python scripts/build_paper_db.py --dry-run      # how many are outstanding, and what it would cost
python scripts/build_paper_db.py                # read the next 250 papers
python scripts/build_paper_db.py --all          # read every outstanding paper
python scripts/build_paper_db.py --rebuild      # regenerate the CSV/report, no API calls
```

`refresh.py` runs it as a step, capped per run; `--skip paperdb` leaves it
alone. Corrections go in `data/paper_db_overrides.json` keyed by PMID — they are
applied when the table is written, so re-extraction never overwrites a fix and
deleting an entry reverts that row.

## How it works

Each data source is a small collector in `pedrad_ai/` that hits a free public
API (no keys required, faster with them) and caches responses under
`data/raw/cache/`. `pedrad_ai/config.py` holds every search query and the year
range — edit there to retune scope. See `CLAUDE.md` for details, API-key
options, and conventions.

## Conferences and societies

ML/CV venues (CVPR, ICCV, NeurIPS, ICML, ICLR) are pulled from DBLP and reported
as the *radiology share* of each venue. Radiology societies (RSNA, ACR, ECR,
SPR) have no machine-readable program, so their engagement with AI is proxied by
the *AI share* of their flagship journals via PubMed, tracked 2016–2026.

## Caveats

Rows in the paper database are read from abstracts, so a field is blank when the
abstract does not state it; "unclear" in the release column means the paper does
not say, not that the model is unavailable. Counts reflect indexed records at
collection time and **undercount the most recent year** (MEDLINE indexing and patent grants lag). DBLP throttles automated
access, so ML-venue coverage may be partial in a given run. Conference fractions
use title-keyword labelling and are conservative lower bounds. Citation and star
counts are snapshots. The reports state these caveats inline.

## License

MIT
