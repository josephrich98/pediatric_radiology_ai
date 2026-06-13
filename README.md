# pediatric_radiology_ai

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

## Quickstart

```bash
pip install -e .
python scripts/run_all.py --quick      # fast headline run
python scripts/run_all.py              # full run (slower, hits more queries)
```

Outputs land in:

- `reports/00_popularity_trends.md` — growth + pediatric share, with tables
- `reports/01_landscape_players.md` — most-cited papers, most-starred tools
- `reports/02_state_of_the_field.md` — does-well / bleeding-edge / unresolved
- `reports/references.bib` — doi2bib output for cited papers
- `figures/*.png` — trend and breakdown plots
- `slides/pedrad_ai_slides.pdf` — Beamer deck summarizing the whole story
  (regenerate with `python scripts/build_slides.py` then `latexmk -pdf` in `slides/`)

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

Counts reflect indexed records at collection time and **undercount the most
recent year** (MEDLINE indexing and patent grants lag). DBLP throttles automated
access, so ML-venue coverage may be partial in a given run. Conference fractions
use title-keyword labelling and are conservative lower bounds. Citation and star
counts are snapshots. The reports state these caveats inline.

## License

MIT
