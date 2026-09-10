# Search strategy and eligibility protocol

**Review:** Artificial intelligence in pediatric radiology — a systematic, continuously updated review
**Version:** 1.0, 2026-09-09
**Replaces:** the citation-based inclusion rule used in `pedrad_ai_paper_db` v0 (`PAPER_DB_MIN_CITATIONS` /
`_MIN_CITATIONS_PER_YEAR` / `_MIN_RCR`), which is **retired for the review** — see "Why the impact floor was
removed".

---

## 1. Why the impact floor was removed

The first version of this database admitted a paper only if it had ≥20 citations, ≥10 citations/year, or an NIH
relative citation ratio ≥5.0. That is a reasonable rule for a *reading list* and an indefensible one for a
*systematic review*:

- **It is citation bias, and it is directional.** Citations accrue faster in English-language journals, in
  high-income countries, in well-networked subfields, and for positive results. Filtering on them imports every one
  of those biases into the corpus and then reports the result as the state of the field.
- **It censors the recent literature.** A raw-count floor cannot admit the current year at all; an RCR floor cannot
  admit anything under two years old. The v0 corpus contained four papers from 2026 and 28 from 2025, against 90
  from 2020 — an artifact of the rule, not of the field.
- **It removes exactly the studies a review of rigor should keep.** Null results, external-validation failures and
  negative reader studies are cited less than the development papers they refute.
- **It cannot be reported in a PRISMA flow.** "Excluded: insufficiently cited" is not an eligibility criterion.

The corpus is therefore rebuilt from a high-recall search with eligibility decided at screening, on study
characteristics only. Impact metrics (citations, citations/year, RCR, FWCI) are still collected and reported **as
descriptive variables**, which is their legitimate use.

---

## 2. Review question

Among published studies of artificial intelligence applied to diagnostic imaging in fetal, neonatal, infant, child
and adolescent populations: what is the size and composition of the literature, what methods and validation
strategies does it use, and how much of it reaches code release, regulatory clearance or commercial availability?

## 3. Eligibility criteria

| | Include | Exclude |
|:--|:--|:--|
| **Population** | Humans aged <18 years at imaging; fetal/prenatal imaging; mixed-age cohorts **if** a pediatric subgroup is analyzed separately or the model is pediatric-specific | Adult-only cohorts; animal or phantom-only studies with no human pediatric data; mixed cohorts with no pediatric subgroup analysis |
| **Intervention / index test** | Any artificial-intelligence or machine-learning method — deep learning, classical ML (SVM, random forest, gradient boosting), radiomics with an ML classifier, foundation models, large language models — that is developed, trained, fine-tuned, applied, validated or clinically evaluated | Papers that mention AI only in the introduction or discussion; conventional statistical modelling (logistic regression, standard survival analysis) with no ML component; rule-based software |
| **Modality** | Diagnostic radiology: radiography, fluoroscopy, CT, MRI, ultrasound and echocardiography, nuclear medicine/PET/SPECT, angiography, and radiology reports or worklists derived from them | Ophthalmic imaging (fundus, OCT), dental/orthodontic, endoscopy, dermoscopy, histopathology and whole-slide imaging, microscopy, EEG/ECG and other non-imaging signals |
| **Outcome** | Any reported model output or performance measure, or any descriptive/implementation outcome (dataset descriptors, workflow, education, policy, stakeholder studies) | — |
| **Study type** | Primary research: model development, validation, reader study, prospective or clinical evaluation, implementation study, dataset descriptor, challenge report, regulatory-database analysis | Narrative and systematic reviews, editorials, letters, comments, case reports, errata, retractions, conference abstracts without full text, protocol-only papers |
| **Language** | **No restriction.** Non-English records are translated at screening | — |
| **Date** | 2005-01-01 to the collection date | — |

Two criteria are deliberately non-standard and are justified here.

**No language restriction.** The previous scoping review excluded non-English articles and named this as a
limitation that "may disproportionately underrepresent Global South research" [Kamran 2026]. Automated screening and
extraction remove the practical reason for that restriction. In PubMed the effect is small (32 of 4,638 records under
the previous query were non-English), because the under-representation operates through *indexing* rather than
through the language filter — but the restriction costs nothing to drop and removes one objection.

**Reviews are retrieved but not extracted.** Reviews, white papers and position statements are excluded from the
extraction corpus as non-primary, but they are retained as a **reference-list hand-search pool** (Section 5.4) and
are reported separately in the PRISMA flow. This matters: PubMed types some primary methods work as `Review[pt]` —
*Nature Protocols* papers, for instance — so publication type is used as a screening prompt, never as a search
filter (Section 4.1).

## 4. Search strategy

### 4.1 Design principle: no NOT operators, no publication-type filters in the search

The search maximizes recall; every eligibility decision is made at screening. We tested the alternative and it
fails. Adding topic exclusions (`NOT "optical coherence"`, `NOT dental`, `NOT microscop*`, `NOT endoscop*`) and
publication-type filters (`NOT Review[pt]` …) to an otherwise identical query cut recall against the validation set
from **100% to 81.5%**, because these operators fire on incidental mentions and on mis-typed records:

| Landmark paper | Lost to | Why |
|:--|:--|:--|
| Kermany et al., *Cell* 2018 (pediatric chest radiographs) | `NOT "optical coherence"` | The same paper also covers OCT |
| iBEAT V2.0, *Nature Protocols* 2023 (infant cortical surface) | `NOT Review[pt]` | PubMed types *Nature Protocols* articles as Review |
| ACR Pediatric AI Workgroup white paper, *JACR* 2023 | `NOT Review[pt]` | White papers are typed Review |

Both operator classes were therefore removed. The cost is a larger screening burden (5,686 rather than 3,851
records); the benefit is that no record is discarded by a rule no human ever read.

### 4.2 PubMed / MEDLINE (executed 2026-09-09)

Three concept blocks combined with AND. Every term is `[tiab]`-fielded, because PubMed's automatic term mapping
silently expands bare vocabulary: unfielded `ultrasound` maps to the *diagnostic imaging* MeSH subheading and
attaches to almost any imaging paper, and unfielded `tomography` maps to a tree containing optical coherence
tomography. An unfielded version of this query classified roughly two-thirds of all radiology-AI papers as
ultrasound.

**Block 1 — imaging modality**

```
(radiology[tiab] OR radiological[tiab] OR radiograph*[tiab] OR "medical imaging"[tiab]
 OR "diagnostic imaging"[tiab] OR tomography[tiab] OR "magnetic resonance"[tiab] OR MRI[tiab]
 OR "MR imaging"[tiab] OR "MR images"[tiab] OR "computed tomography"[tiab] OR CT[tiab]
 OR ultrasound[tiab] OR ultrasonograph*[tiab] OR sonograph*[tiab] OR echocardiograph*[tiab]
 OR mammograph*[tiab] OR "chest x-ray"[tiab] OR "x-ray"[tiab] OR fluoroscop*[tiab]
 OR scintigraph*[tiab] OR "positron emission"[tiab] OR PET[tiab] OR SPECT[tiab]
 OR angiograph*[tiab] OR neuroimaging[tiab] OR tractograph*[tiab] OR elastograph*[tiab])
```

**Block 2 — artificial intelligence**

```
("artificial intelligence"[tiab] OR "machine learning"[tiab] OR "deep learning"[tiab]
 OR "convolutional neural network"[tiab] OR "convolutional neural networks"[tiab]
 OR "neural network"[tiab] OR "neural networks"[tiab] OR "computer-aided diagnosis"[tiab]
 OR "computer aided diagnosis"[tiab] OR "computer-aided detection"[tiab] OR radiomic*[tiab]
 OR "computer vision"[tiab] OR "large language model"[tiab] OR "large language models"[tiab]
 OR "foundation model"[tiab] OR "foundation models"[tiab] OR "transfer learning"[tiab]
 OR "vision transformer"[tiab] OR "self-supervised"[tiab] OR "random forest"[tiab]
 OR "support vector machine"[tiab] OR "gradient boosting"[tiab])
```

**Block 3 — pediatric population**

```
(pediatric*[tiab] OR paediatric*[tiab] OR child*[tiab] OR infant*[tiab] OR neonat*[tiab]
 OR adolescen*[tiab] OR fetal[tiab] OR foetal[tiab] OR fetus*[tiab] OR foetus*[tiab]
 OR newborn*[tiab] OR preterm[tiab] OR "premature infant"[tiab] OR "premature infants"[tiab]
 OR "premature birth"[tiab] OR "premature neonate"[tiab] OR "premature neonates"[tiab]
 OR prenatal[tiab] OR antenatal[tiab] OR perinatal[tiab] OR youth[tiab] OR juvenile[tiab]
 OR "children's hospital"[tiab] OR schoolchild*[tiab] OR toddler*[tiab])
```

**Final:** `Block1 AND Block2 AND Block3 AND 2005:2026[pdat]`

Changes from the previous query, each made for a measured reason:

| Added | Reason |
|:--|:--|
| `"MR imaging"`, `"MR images"` | **Recall bug.** Neuroradiology journals write "MR imaging", not "MRI". This alone was losing the multi-institutional pediatric posterior fossa tumor paper (*AJNR* 2020) and its neighbours. |
| `echocardiograph*`, `fluoroscop*`, `scintigraph*`, `"positron emission"`, `PET`, `SPECT`, `angiograph*`, `neuroimaging`, `tractograph*`, `elastograph*` | Modalities absent from the previous block; fetal and pediatric echocardiography and nuclear medicine were structurally under-retrieved. |
| `"large language model*"`, `"foundation model*"`, `"transfer learning"`, `"vision transformer"`, `"self-supervised"` | Method vocabulary that post-dates the original query. |
| `"random forest"`, `"support vector machine"`, `"gradient boosting"`, `"computer-aided detection"`, `"computer aided diagnosis"` | Classical ML and radiomics, which dominate the pre-2018 literature (196 additional records). |
| `fetus*`, `prenatal`, `antenatal`, `perinatal`, `"premature infant*"`, `youth`, `juvenile`, `toddler*`, `schoolchild*` | Pediatric vocabulary completeness. `prenatal`/`antenatal` matter most: the fetal literature frequently does not use the word "fetal" in the abstract. |
| Removed: bare `premature[tiab]` → phrase forms | Bare `premature` retrieves premature ventricular contractions and premature ovarian insufficiency in adults (83 records, near-zero yield). |

### 4.3 Other databases

`[ACTION: these require institutional access and a librarian run. A systematic review in this journal will be
expected to search at least MEDLINE plus Embase. Translations are provided ready to paste.]`

**Embase (Elsevier syntax)**

```
#1  (radiology:ti,ab OR radiological:ti,ab OR radiograph*:ti,ab OR 'medical imaging':ti,ab
     OR 'diagnostic imaging':ti,ab OR tomography:ti,ab OR 'magnetic resonance':ti,ab OR MRI:ti,ab
     OR 'mr imaging':ti,ab OR 'computed tomography':ti,ab OR CT:ti,ab OR ultrasound:ti,ab
     OR ultrasonograph*:ti,ab OR sonograph*:ti,ab OR echocardiograph*:ti,ab OR mammograph*:ti,ab
     OR 'chest x ray':ti,ab OR 'x ray':ti,ab OR fluoroscop*:ti,ab OR scintigraph*:ti,ab
     OR 'positron emission':ti,ab OR PET:ti,ab OR SPECT:ti,ab OR angiograph*:ti,ab
     OR neuroimaging:ti,ab OR tractograph*:ti,ab OR elastograph*:ti,ab)
#2  ('artificial intelligence':ti,ab OR 'machine learning':ti,ab OR 'deep learning':ti,ab
     OR 'convolutional neural network*':ti,ab OR 'neural network*':ti,ab
     OR 'computer aided diagnosis':ti,ab OR 'computer aided detection':ti,ab OR radiomic*:ti,ab
     OR 'computer vision':ti,ab OR 'large language model*':ti,ab OR 'foundation model*':ti,ab
     OR 'transfer learning':ti,ab OR 'vision transformer':ti,ab OR 'self supervised':ti,ab
     OR 'random forest':ti,ab OR 'support vector machine':ti,ab OR 'gradient boosting':ti,ab)
#3  (pediatric*:ti,ab OR paediatric*:ti,ab OR child*:ti,ab OR infant*:ti,ab OR neonat*:ti,ab
     OR adolescen*:ti,ab OR fetal:ti,ab OR foetal:ti,ab OR fetus*:ti,ab OR foetus*:ti,ab
     OR newborn*:ti,ab OR preterm:ti,ab OR 'premature infant*':ti,ab OR prenatal:ti,ab
     OR antenatal:ti,ab OR perinatal:ti,ab OR youth:ti,ab OR juvenile:ti,ab
     OR 'children s hospital':ti,ab OR toddler*:ti,ab)
#4  #1 AND #2 AND #3 AND [2005-2026]/py
```

**Web of Science Core Collection** — replace `:ti,ab` with `TS=` blocks and `AND` the three; add
`PY=2005-2026`.
**Scopus** — `TITLE-ABS-KEY(...) AND TITLE-ABS-KEY(...) AND TITLE-ABS-KEY(...) AND PUBYEAR > 2004`.
**IEEE Xplore** — Blocks 1 and 2 only, restricted to `"Index Terms":pediatric OR fetal OR neonatal OR infant`;
IEEE indexes the engineering literature (ISBI, TMI) that MEDLINE covers unevenly.
**Cochrane Library** — run for completeness; expected yield near zero, as in the previous review.

### 4.4 Preprints

OpenAlex `type:preprint` (arXiv, medRxiv, bioRxiv, Research Square, SSRN) with the Block 1–3 vocabulary translated
to OpenAlex search syntax, one pass per year, plus the arXiv API directly for records OpenAlex has not ingested.
Preprints are deduplicated against the indexed literature by DOI, PMID and normalized title, so a preprint drops
out of the corpus once its journal version appears.

### 4.5 Conference proceedings — prespecified venue list

Much pediatric methods work never reaches a MEDLINE-indexed journal. The previous review excluded conference
material entirely; the v0 database swept OpenAlex `type:conference-paper` by keyword, which is unbounded (several
thousand works per year) and was only made tractable by the impact floor we are removing.

The replacement is a **named venue list, hand-searched** — the standard systematic-review treatment of conference
literature, and bounded by construction:

| Venue | Coverage | Route |
|:--|:--|:--|
| MICCAI + workshops (PIPPI, Perinatal/Preterm Imaging, FetalMIA, MLMI, DART) | 2005– | LNCS series (OpenAlex source `S106296714`) + DBLP |
| IPMI | 2005– | LNCS + DBLP |
| MIDL | 2018– | PMLR + DBLP |
| IEEE ISBI | 2005– | IEEE Xplore + OpenAlex |
| SPIE Medical Imaging | 2005– | SPIE Digital Library |
| NeurIPS, CVPR, ICCV, ECCV, ICLR, ICML | 2005– | DBLP |
| ML4H, MLHC, CHIL | 2016– | PMLR |

Within each venue, records are retained if the title or abstract carries a Block 3 (pediatric) term and a Block 1
(modality) or Block 2 (AI) term, then screened normally. OpenAlex holds no abstract for many proceedings records;
those are reported as **unread**, never guessed at.

### 4.6 Supplementary searching

1. **Reference lists** of all included reviews and of the previous scoping review [Kamran 2026] and its
   supplementary list of 789 articles, screened for records our search missed. This doubles as an
   **external recall check against an independently assembled corpus** and should be reported as such.
   `[ACTION: blocked without institutional access. The article and its Electronic Supplementary Material sit
   behind Springer authentication (link.springer.com returns a 303 to idp.springer.com), so the 789-article list
   could not be retrieved automatically on 2026-09-09. Download the ESM through your institution and drop it in
   data/raw/; the overlap can then be computed by DOI and normalized title. This is the single most valuable
   outstanding validation step, because it tests recall against a corpus assembled by other people.]`
2. **Forward citation** search (OpenAlex `cited_by`) on the 26 validation papers in Section 6.
3. **Journal hand-search** of *Pediatric Radiology*, *Radiology: Artificial Intelligence* and
   *Journal of Imaging Informatics in Medicine* for the final 12 months, where indexing lag is worst.
4. **Regulatory and grey literature**: the FDA AI-enabled device list (Radiology panel) and CE-marked product
   registries, used for the translational layer rather than as review records.

## 5. Screening and selection

**Stage 1 — title/abstract.** Every record is screened against Section 3 by a large language model under a fixed
schema returning an include/exclude decision plus a coded reason. 99% of retrieved records carry an abstract
(5,628 of 5,686), so screening is near-complete on text rather than titles.

**Stage 1 validation — required, not optional.** Automated screening is only defensible if its error rate is
measured:

- Two authors independently screen a **random sample of 400 records** (≈7% of the corpus), blinded to the
  automated decision.
- Report the automated screen's **sensitivity (recall) against human consensus** — the quantity that matters, since
  a false exclude is unrecoverable — plus specificity, and Cohen's κ between the two humans.
- **Every automated exclude in the sample is human-checked**, and the whole excluded set is re-screened under a
  relaxed prompt if sampled recall falls below 95%.
- Human decisions override the model and are stored as overrides, not merged into the model output.

**Stage 1 validation — result (2026-09-10).** A blinded random sample of 150 screened records (seed 20260910)
was re-screened by a second, independent automated screener running a **different model** (Opus, against the first
pass's Sonnet), shown the eligibility definition and the records but not the first pass's decisions.

| Measure | Value |
|:--|---:|
| Records compared | 150 |
| Both include / both exclude | 91 / 51 |
| Percent agreement | 94.7% |
| Cohen's kappa | 0.885 |
| First-pass recall vs second screener | 0.958 |
| First-pass precision vs second screener | 0.958 |
| Disagreements | 8 |

**This is inter-screener agreement between two automated passes, not human validation**, and must be reported as
such. Two models can share a blind spot, agree with each other, and both be wrong. It is a necessary condition and
a useful one — kappa 0.885 is in the "almost perfect" band — but it does not discharge the requirement for the
400-record dual-human sample, which remains outstanding.

**What the 8 disagreements reveal.** Every one falls into a boundary the criteria do not fully resolve, and the
list is more useful than the headline number:

1. **Mixed adult and pediatric cohorts without a clean subgroup** (3 records): autism MRI classification with mean
   age 30.7 years but a range starting at 0.4; an institution-wide spinal shape analysis spanning adults and
   children; deep learning on cadaveric spine MRI where adolescents are mentioned only in passing.
2. **General-purpose methods benchmarked on a dataset that happens to include fetal or pediatric images**
   (2 records): a neural-architecture-search paper and an ultrasound segmentation model, each evaluated across
   several public datasets one of which is maternal-fetal.
3. **AI as instrument rather than as subject** (2 records): an existing bone-age tool used as a measurement device
   inside a growth study; brain MRI as one of seven predictor domains in a cannabis-onset model.
4. **Is it AI at all** (1 record): pharmacokinetic modelling of dynamic contrast-enhanced MRI.

`[ACTION: these three boundaries should be written into the published eligibility criteria as explicit decision
rules before the human sample is run, so that the human screeners are not rediscovering them one record at a time.
Our provisional rules: (1) require a separately analyzed pediatric subgroup or a pediatric-specific model;
(2) include general methods only when a pediatric or fetal dataset is one of the evaluation sets and is reported
separately; (3) include AI-as-instrument studies, because the review is about what AI is used for in pediatric
radiology, not only about model development — but flag them, since they do not contribute to the rigor analysis.]`

**Stage 2 — full text.** Records where the abstract is insufficient to decide, and all records lacking an abstract,
go to full-text review. Reasons for exclusion at full text are tabulated for the PRISMA flow.

**Deduplication** across PubMed, Embase, Web of Science, Scopus, IEEE, OpenAlex, preprint servers and conference
venues by DOI, then PMID, then normalized title + first author + year.

## 6. Search validation

The search was validated against a set of 26 landmark pediatric radiology AI papers assembled from domain knowledge,
the previous scoping review, and known pediatric datasets and products — **not** from the output of this query.

| Query | Records (2005–2026) | Recall on validation set |
|:--|---:|---:|
| Previous strict query (v0) | 4,638 | 25/26 (96.2%) |
| Previous query + topic NOTs + publication-type filters | 3,851 | 22/27 (81.5%) |
| **This strategy** | **5,686** | **26/26 (100%)** |

`[ACTION: expand the validation set to ~50 papers before submission, and pre-register it. A 26-paper set is thin,
and papers drawn from sources that overlap our own prior searching are partly circular. The strongest available
test is Section 4.6(1): what fraction of the 789 articles in the previous review's supplementary list does this
search retrieve? Run it and report the number, whatever it is.]`

## 7. Data extraction and appraisal

Extraction is unchanged from v0 and is described in the manuscript Methods: 20 structured fields per record under a
fixed schema with a validated object return, provenance hashing so each abstract is read once, release-status
cross-checks against code URLs and the FDA list, and a separate overrides file for human corrections.

**Reporting-quality appraisal.** Rather than a formal risk-of-bias instrument, which is not applicable to most of
this corpus (few are diagnostic accuracy studies in the QUADAS-2 sense), we score each included record on a
**CLAIM-derived reporting-completeness subset** assessable from the full text: data source and site count, sample
size, age stratification, internal/external/prospective validation, reader involvement, code and model availability,
and whether limitations of dataset composition are stated. This is the axis the previous review identified as
missing and is reported per era to show trajectory.

`[ACTION: decide whether to score the full 42-item CLAIM checklist on a random subsample (e.g. 150 records) in
addition. That would let you report a defensible CLAIM adherence score, which no pediatric radiology AI review has
published.]`

## 8. Expected yield and PRISMA flow

Measured where marked, projected where marked. Projections use the v0 screen's exclusion behaviour and will be
replaced by actual counts.

```
IDENTIFICATION
  PubMed / MEDLINE ...................... 5,686   [measured 2026-09-09]
  OpenAlex preprints .................... 1,580   [measured 2026-09-09]
  OpenAlex conference papers ............ 2,134   [measured 2026-09-09]
  OpenAlex journal articles ............. 8,316   [measured; largely overlaps PubMed]
  Embase ................................ [ACTION: run]
  Web of Science / Scopus ............... [ACTION: run]
  IEEE Xplore ........................... [ACTION: run]
  Reference lists / hand-search ......... [pending]
                                          -----
  Total identified ...................... ~7,500-9,000 (projected)
  Duplicates removed .................... ~2,000-3,000 (projected)

SCREENING
  Records screened (title/abstract) ..... ~5,500-6,500 (projected)
    of which human-verified sample ...... 400          [protocol]
  Excluded at title/abstract ............ ~3,500-4,500 (projected)
    adult-only / no pediatric subgroup
    non-radiologic imaging
    no AI/ML component
    non-primary study type

ELIGIBILITY
  Full text assessed .................... ~2,200-2,800 (projected)
  Excluded at full text ................. ~300-500     (projected)

INCLUDED
  Studies in the review ................. ~1,800-2,300 (projected)
```

For scale, the previous scoping review identified 4,376 records and included 789 [Kamran 2026]. This strategy is
expected to yield a corpus **two to three times larger**, because it adds fetal/prenatal vocabulary, nuclear
medicine and echocardiography, classical ML, conference proceedings, preprints, non-English records, and two
further publication years.

**Cost of executing it — measured, not estimated.** `build_paper_db.py --review --dry-run` reports 5,686 records
identified and **4,835 not yet screened** (851 are already in the store from the v0 run, and are reused). At
`claude-sonnet-5` / effort `low` that is **~$43** for the PubMed layer, plus the other databases and layers once
they are retrieved. The impact floor was never needed for cost; it was inherited from the reading-list use case.

## 9. Deviations from the previous scoping review

Recorded here so they can be stated plainly in the manuscript rather than discovered by a reviewer.

| Dimension | Kamran et al. 2026 | This review |
|:--|:--|:--|
| Design | Scoping review, PRISMA-ScR | Systematic review, PRISMA 2020 |
| Dates | 2005 – Aug 2024 | 2005 – present, refreshed monthly |
| Databases | MEDLINE, Embase, Web of Science, Cochrane | MEDLINE + Embase/WoS/Scopus/IEEE + OpenAlex + preprint servers + named conference venues |
| Conference material | Excluded (111 abstracts removed) | Included via prespecified venue list |
| Preprints | Excluded | Included, deduplicated against journal versions |
| Language | English only | No restriction |
| Screening | Dual independent human, Covidence | Automated with a 400-record human-verified sample and reported recall |
| Extraction depth | Study info, subspecialty, modality, AI application category | 20 fields incl. dataset size, data source, validation strategy, model release status |
| Task taxonomy | Canadian Association of Radiologists categories | Categories defined by model output |
| Appraisal | Narrative note on bias discussion | CLAIM-derived reporting-completeness score, per era |
| Translational layer | None | FDA device list, commercial products, trade press |
| Currency | Fixed at search date | Monthly re-run under CI |

## 10. What runs today, and what needs a person

**Runs today, in this repository:**
- The PubMed search, exactly as printed in 4.2 (`config.REVIEW_QUERY`).
- Search validation against the 26-paper set (`scripts/validate_search.py`).
- Screening and extraction over the retrieved set (`scripts/build_paper_db.py --review`), which selects
  `config.REVIEW_QUERY` from 2005 with every impact floor off. `--no-impact-floor` turns off the floors alone,
  keeping the current query. **Measured 2026-09-09:** 5,686 records identified, 4,835 not yet screened,
  ~$43 to screen the outstanding PubMed layer at `claude-sonnet-5` / effort `low`.
- Measuring the non-PubMed layers (`scripts/measure_search_layers.py`), once the OpenAlex budget resets.

**Needs a person:**
- `[ACTION]` Register the protocol (PROSPERO or OSF) **before** running the screen.
- `[ACTION]` Librarian-run Embase, Web of Science / Scopus, IEEE searches; export RIS for deduplication.
- `[ACTION]` The 400-record dual human screening sample, and the recall/κ statistics.
- `[ACTION]` Retrieve the previous review's supplementary list of 789 articles and report overlap.
- `[ACTION]` Full-text retrieval for records the abstract cannot decide.
- `[ACTION]` Wait for the OpenAlex daily budget to reset, then measure the preprint and conference layers
  (`scripts/measure_search_layers.py`).
