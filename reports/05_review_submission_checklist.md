# European Radiology submission checklist

## Format compliance

- [x] Review structured with Introduction, topical headings/subheadings, and Conclusion.
- [x] Introduction states background, clinical relevance, objectives, and article inclusion criteria.
- [x] Abstract is unstructured and within 250 words (215 words).
- [x] Four MeSH keywords are supplied (allowed range: 1–5).
- [x] Main text is within 5,000 words (3,143 words from Introduction through Conclusion, excluding headings).
- [x] Four main tables are supplied (maximum: 5).
- [x] Six figures are supplied (maximum: 12).
- [x] Conclusion summarizes key findings, gives a take-home message, addresses policy/practice, identifies limitations and research gaps, and proposes future directions.
- [x] Full search strategies and eligibility criteria are separated into supplementary material.
- [x] Funding and conflict-of-interest statements preserve the authors' existing entries.

## Author information still required

- [ ] Add institutional affiliations for Joseph Rich and Amit Sura.
- [ ] Identify the corresponding author and add postal address, email address, and telephone number.
- [ ] Add a CRediT author-contribution statement.
- [ ] Add the public repository URL and an archived, version-specific DOI (for example, Zenodo).
- [ ] Confirm whether “Acknowledgments: None” is correct.

## Methodological work required before submission

- [ ] Complete the prespecified dual-human screening validation sample; resolve eligibility boundary rules and report sensitivity, specificity, and inter-reviewer agreement.
- [ ] Complete duplicate human extraction of the prespecified sample and report agreement for modality, task, validation, and release status.
- [ ] Decide whether to archive the protocol retrospectively. Do not describe a retrospective archive as prospective registration.
- [ ] Decide whether Web of Science, Scopus, IEEE Xplore, and/or Cochrane must be searched. The manuscript currently states transparently that they were not searched.
- [ ] Recalculate every headline number and both word counts after the human-validation corrections and immediately before submission.
- [ ] Complete a PRISMA 2020 checklist and ensure the flow diagram terminology matches the final screening workflow.
- [ ] Expand and verify the scientific reference base. The formatted draft retains the 17 references present in the source draft; this is likely too limited for a comprehensive review.

## Submission files

- [x] Main manuscript: `reports/05_review_manuscript.md`
- [x] Word manuscript: `reports/05_review_manuscript_european_radiology.docx`
- [x] Supplement: `reports/05_review_supplement.md`
- [x] Word supplement: `reports/05_review_supplement_european_radiology.docx`
- [x] Figure 1: `figures/review_prisma.png`
- [x] Figure 2: `figures/review_by_year.png`
- [x] Figure 3: `figures/review_modality_year.png`
- [x] Figure 4: `figures/review_validation_era.png`
- [x] Figure 5: `figures/review_funnel.png`
- [x] Figure 6: `figures/review_impact_subset.png`

The Word files should be regenerated after any Markdown edit:

```bash
pandoc reports/05_review_manuscript.md -o reports/05_review_manuscript_european_radiology.docx
pandoc reports/05_review_supplement.md -o reports/05_review_supplement_european_radiology.docx
```
