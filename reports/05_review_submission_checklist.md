# Landscape review: editorial and submission checklist

The September 11, 2026 rewrite is a scoping review with bibliometric analysis and narrative synthesis. It maps the field rather than pooling model performance. Journal-specific requirements must be checked against the target journal's current guidance before submission.

## Completed draft work

- [x] Reconstructed the narrative from the current 3,496 included-record cohort.
- [x] Separated broad PubMed query counts from screened-cohort counts.
- [x] Described historical trends, clinical topics, modality and age combinations, datasets, and open tools.
- [x] Treated 2025 and 2026 separately, with 2026 explicitly year to date.
- [x] Added concrete recent examples, including NeoCLIP, FetalCLIP, reconstruction, and clinical fracture evaluation.
- [x] Distinguished resource mentions, model availability, and clinical benefit.
- [x] Retained overlap with the presentation through three existing figures and shared clinical examples.
- [x] Generated three new figures, including vector PDF versions, and reproducible supplementary tables.
- [x] Audited exact cohort membership and repeated normalized titles; preserved the shared cohort and reported a title-collapse sensitivity.
- [x] Supplied five tables and six main figures; draft word counts are 211 abstract and 3,376 main-text words.
- [x] Preserved the authors and existing funding/conflict declarations.

## Required scientific checks before submission

- [ ] Adjudicate the 79 repeated-title groups (161 records) listed in Table L5, and check DOI matches and versions with changed titles. The 3,496 denominator is currently records, not verified independent investigations.
- [ ] Complete independent human validation of screening and extraction; automated-model agreement is not a substitute.
- [ ] Review the exploratory clinical-topic and dataset-name matches. In particular, low counts and unmatched text cannot establish absence of research or confirmed dataset use.
- [ ] Reconcile online-first, preprint, and journal issue dates if interpreting precise year-to-year change.
- [ ] Decide whether engineering/conference coverage should be extended for publication; the current map explicitly retains the existing exclusions.
- [ ] Complete the applicable scoping-review reporting checklist and reconcile selection-flow wording with the final deduplicated cohort.
- [ ] Recalculate figures, tables, and word counts after cohort corrections. The narrative is not automatically rewritten by the pipeline.
- [ ] Finalize reference formatting and check version-specific resource citations and software access conditions.

These are disclosed limitations and pre-submission tasks; the landscape draft itself is complete. Formal risk-of-bias scoring of every paper or an omnibus pooled accuracy estimate is not required to fulfill this review's stated purpose.

## Author information

- [ ] Add affiliations and corresponding-author contact details.
- [ ] Add a CRediT contribution statement.
- [ ] Add repository URL and a version-specific archive DOI.
- [ ] Confirm funding, conflicts, acknowledgments, and any journal-required AI assistance disclosure.

## Deliverable map

| Deliverable | File |
|:--|:--|
| Manuscript source | [05_review_manuscript.md](05_review_manuscript.md) |
| Manuscript Word export | [05_review_manuscript_european_radiology.docx](05_review_manuscript_european_radiology.docx) |
| Methods supplement | [05_review_supplement.md](05_review_supplement.md) |
| Supplement Word export | [05_review_supplement_european_radiology.docx](05_review_supplement_european_radiology.docx) |
| Reproducible tables and duplicate audit | [05_landscape_analysis.md](05_landscape_analysis.md) |
| Tables and audit Word export | [05_landscape_analysis.docx](05_landscape_analysis.docx) |
| Analysis and figure generator | [build_landscape_review.py](../scripts/build_landscape_review.py) |

The Word filenames retain the earlier target-journal naming for continuity; this does not certify journal-format compliance.

## Figure and presentation overlap

| Main figure | File in figures/ | Relationship to presentation |
|:--|:--|:--|
| 1. Publication years | review_by_year.png | Existing shared figure |
| 2. Modality over time | review_modality_year.png | Existing shared figure |
| 3. Clinical topic × modality | review_topic_modality.png / .pdf | New landscape analysis |
| 4. Age × modality | review_age_modality.png / .pdf | New landscape analysis |
| 5. Tasks over time | review_task_year.png | Existing shared figure |
| 6. Recent task shares | review_recent_tasks.png / .pdf | New landscape analysis |
| S1. Recorded selection flow | review_prisma.png | Existing shared figure, with updated interpretation in the supplement |

The available presentation source is `slides/pedrad_ai_slides.tex`; no file named `slidex.tex` was found. Its disease-query figure (`ped_problems.png`) uses the broad PubMed layer and must not be presented as a count of screened included records. The manuscript's new disease map uses the included-record cohort instead.

Reproduction commands are provided at the end of the methods supplement. All three Word exports must be regenerated after changing their Markdown sources.
