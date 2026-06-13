# Reports

Generated deliverables for the children's hospital briefing. Regenerate with
`python scripts/run_all.py` (collection) followed by the figures/reports steps,
or rebuild just the prose from already-collected data with
`python scripts/build_reports.py`.

| File | What it covers |
|:--|:--|
| [00_popularity_trends.md](00_popularity_trends.md) | How fast radiology AI is growing, its share of all radiology, the pediatric fraction, modality/task breakdowns, the AI share of RSNA's own journals, patents, and conference attention. |
| [01_landscape_players.md](01_landscape_players.md) | The biggest players: most-cited radiology-AI and pediatric-radiology-AI papers, and the most-starred open-source tools. |
| [02_state_of_the_field.md](02_state_of_the_field.md) | Curated synthesis for clinical leadership: what radiology AI does well, the bleeding edge, what remains unresolved, and implications for a children's hospital. |
| [references.bib](references.bib) | BibTeX for every cited paper, resolved through doi2bib. |

A **Beamer slide deck** summarizing all of this (objectives, methods, results,
implications) is generated separately at
[`../slides/pedrad_ai_slides.pdf`](../slides/pedrad_ai_slides.pdf) — rebuild with
`python scripts/build_slides.py && cd slides && latexmk -pdf pedrad_ai_slides.tex`.

Figures referenced by the reports live in [`../figures/`](../figures). Underlying
data tables are in [`../data/processed/`](../data/processed).

## Caveats that apply throughout

- Counts reflect records indexed at collection time and **undercount the most
  recent year** (MEDLINE indexing and patent grants lag).
- Conference fractions use title-keyword labelling on a per-venue-year sample
  and are conservative lower bounds; DBLP throttling may leave that section
  incomplete in a given run.
- Citation and GitHub-star counts are point-in-time snapshots.
- Patent counts require a free PatentsView API key (`PATENTSVIEW_API_KEY`); without
  one that section reports zero.
