# From evidence to deployment: a systematic, continuously updated review of artificial intelligence in pediatric radiology

**Running title:** Pediatric radiology AI: from evidence to deployment

**Authors:** Joseph Rich, Amit Sura [+ co-authors TBD]

**Target venue:** *Pediatric Radiology* (review)

**Status:** draft, 2026-09-10. Placeholders needing author action are marked `[ACTION]`.

> **Corpus complete for PubMed and Embase.** The citation-based inclusion rule used in the first draft has been
> retired (it is selection bias and cannot appear in a PRISMA flow). The replacement search is specified in
> `reports/06_search_strategy.md` and wired into `config.REVIEW_QUERY`. 13,508 records were identified across
> PubMed/MEDLINE and Embase, 6,600 were screened after duplicate and publication-form removal, and **3,494
> primary studies are included**. Every structured-review number below is computed from
> `scripts/review_stats.py` on that corpus. Web of Science, Scopus and IEEE Xplore have not been run — see
> Limitations.

---

## Abstract

**Background** Artificial intelligence (AI) research in radiology continues to expand rapidly, but the pediatric
share of that work, and the extent to which it reaches children at the scanner, have not been quantified in a way
that can be kept current.

**Objective** To measure the size, composition, methodological rigor and translational status of the pediatric
radiology AI literature, to link that literature to the regulatory and commercial record, and to publish the whole
analysis as a reproducible database that is refreshed monthly rather than fixed at a single search date.

**Materials and methods** We combined two layers. A bibliometric layer counted PubMed records from 2008 to 2026
for four fielded boolean queries, stratified by modality and clinical task, with an arXiv preprint layer added
because PubMed does not index arXiv. A structured-review layer applied a high-recall search of PubMed/MEDLINE and
Embase with no citation, language, publication-type or topic filter, screened every record against explicit
eligibility criteria, and extracted 20 structured fields per included study under a fixed schema. The search
retrieved 96.4% of the previous scoping review's independently assembled article list and 99.7% of 3,728
MEDLINE-indexed records returned by the same strategy run in Embase. Screening agreement between two independent
automated screeners running different models was 94.7% (Cohen's kappa 0.885). We cross-linked the corpus to the
FDA AI-enabled device list (1,164 radiology-panel devices) and to 7,967 radiology AI stories in seven trade-press
archives.

**Results** Radiology AI publications grew from 715 (2008) to 20,831 (2025) PubMed records; pediatric records
grew from 58 to 2,348. AI accounted for 11.4% of all radiology publishing in 2025 but only 7.4% of pediatric
radiology publishing, a penetration ratio of 0.65 that has not exceeded 0.81 in eighteen years. Of 6,600 records
screened, 2,650 were excluded and 456 were non-primary, leaving **3,494 included studies** — 4.4 times the size of
the previous scoping review's corpus. MRI (45.5%) and ultrasound (23.7%) led radiography (19.3%) and CT (9.3%).
By age, children (37.2%) led adolescents (25.4%) and fetal imaging (22.4%); fetal work was nonetheless the single
largest coherent segment by modality, being 71% ultrasound. By what the model produces, detection/diagnosis
accounted for 38.2% of studies, measurement/quantification 23.9%, outcome prediction 19.5%, segmentation 18.9% and
reconstruction/imputation 7.9%. Validation was internal only in 67.3%, external or multi-center in 18.7%, a reader
study in 6.2% and prospective in 3.3%. Data source was unstated in 39.1%. Code was available for 2.6%. External
validation rose across eras from 4.2% (2005-2014) to 20.3% (2023-2026) and multi-center data from 8.5% to 22.3%,
while reader studies did not improve (7.0% to 5.7%) and prospective evaluation, having fallen to 1.6% in
2020-2022, reached only 4.0%. Embase contributed 365 included studies that PubMed does not index; 71% of its
eligible new journal articles had a corresponding author outside North America and Western Europe. Of 1,164 FDA-cleared radiology AI devices, 11 (0.9%) carry a
pediatric device name, from five companies, covering bone age, fracture detection and fetal echocardiography.
Pediatric stories were 2.0% of radiology AI trade-press coverage.

**Conclusion** Pediatric radiology AI is growing as fast as adult radiology AI but has never closed the relative
gap. Reporting rigor is improving measurably on the axes that can be improved retrospectively, and not on the two
that require prospective contact with patients: reader studies are no more common than twenty years ago, and
prospective evaluation remains below one study in twenty. The funnel from publication to a tool a child benefits
from remains extremely narrow: fewer than one study in five is externally validated, one in sixteen involves a
reader, one in thirty is prospective, one in thirty-eight releases code, and eleven of 1,164 cleared radiology AI
devices carry a pediatric name. We release
the screened corpus and the code that produced it so these estimates can be audited and updated rather than
re-derived.

**Keywords** Artificial intelligence · Pediatric radiology · Systematic review · Living review · Fetal imaging ·
Regulatory clearance · External validation · Reproducible research

---

## Introduction

Artificial intelligence is now a standing feature of radiology practice and of radiology publishing. One in nine
radiology papers indexed in PubMed in 2025 concerned AI, up from fewer than one in a hundred in 2008, and the U.S.
Food and Drug Administration has authorized more than 1,100 AI-enabled devices under its radiology panel. Children
have shared in that expansion unevenly. The reasons are structural and widely rehearsed: pediatric imaging volumes
are smaller and deliberately constrained by dose considerations, normal anatomy and normal ranges shift continuously
with growth, disease spectra are dominated by rare entities, and consent and privacy constraints are tighter. The
consequence is that tools built and cleared for adults are frequently the only tools available for children.

Kamran and colleagues recently mapped this territory for *Pediatric Radiology* in a scoping review of 789 original
articles published between 2005 and August 2024 [1]. Their contribution was to establish, by hand and in duplicate,
what pediatric radiology AI research is *about*: which countries produce it, which modalities and subspecialties it
covers, and which of the Canadian Association of Radiologists' categories of AI application it falls into. They
found that research concentrates in China and the United States, that radiography and MRI dominate, that
musculoskeletal and neurological imaging dominate subspecialty focus, and that 91.1% of articles addressed image
interpretation or diagnosis, leaving communication, education, policy and stakeholder perspectives nearly empty.
They closed by naming what their design could not deliver: their review "does not provide any detailed information
regarding the AI models, or their dataset size, validation strategies, or performance," and they explicitly invited
future systematic reviews to evaluate dataset sizes and model accuracy [1].

This review takes up that invitation and adds two dimensions that no synthesis of pediatric radiology AI has yet
covered.

The first is the **translational funnel**. Counting publications answers how much research exists; it does not answer
how much of that research could reach a child. Between a published model and a deployed one lie several filters that
can be measured from the literature and the regulatory record: whether the model was validated outside the
institution that built it, whether radiologists were ever put in the loop, whether the study was prospective, whether
the code or the product exists at all, and whether any regulator has reviewed it for use in children. We measure each
of these and report the corpus as a funnel rather than a count.

The second is **currency**. A scoping or systematic review is a photograph of a literature that in this field
doubles roughly every three years. Kamran et al.'s search closed in August 2024; by the time their review appeared in
print, PubMed had indexed a further 4,245 pediatric radiology AI records. Rather than accept that decay, we built the
review as executable code: every query, screening rule, extraction schema and figure is versioned in a public
repository and re-run on a monthly schedule, so that the numbers reported here are a dated instance of a database
that continues past publication. This is the design that Elliott and colleagues termed a living systematic review,
applied to a bibliometric and translational question rather than to a clinical one.

Our aims were therefore to (1) quantify the growth of pediatric radiology AI relative to radiology AI as a whole, on
a shared denominator; (2) characterize the composition of the pediatric corpus by modality, task and
age group; (3) measure methodological rigor and its trajectory; (4) link the literature to cleared commercial
products; and (5) release the whole analysis as a reproducible, continuously updated resource.

---

## Materials and methods

This review is reported in accordance with PRISMA 2020 where the items apply to an automated, continuously updated
design. `[ACTION: register the protocol on PROSPERO or the Open Science Framework and insert the identifier here
before submission.]`

### Study design

We combined a **bibliometric layer**, which counts records without reading them and is therefore able to cover the
whole field from 2008 onward, with a **structured-review layer**, which reads abstracts under a fixed schema and is
restricted to work the field has demonstrably engaged with. The two layers answer different questions and are
reported separately throughout: the bibliometric layer describes *what is published*, the structured layer describes
*what is used*. A third, **translational layer** links both to the regulatory and commercial record.

### Bibliometric layer

For each year from 2008 to 2026 we queried PubMed E-utilities using the `[pdat]` publication-date facet for four
boolean queries: all radiology; radiology AND AI; pediatric radiology; and pediatric radiology AND AI. The full query
strings are given in Supplementary Table S1 and in the repository's configuration file.

Query construction followed two rules learned during development and worth stating, because they materially change
the answer. First, PubMed's automatic term mapping silently expands bare vocabulary: unfielded `ultrasound` maps to
the *diagnostic imaging* MeSH subheading, which attaches to almost any imaging paper, and unfielded `tomography` maps
to a tree that includes optical coherence tomography. An early version of our query consequently classified roughly
two-thirds of all radiology AI papers as ultrasound. Every modality and task term in the final query is therefore
`[tiab]`-fielded, and a `NOT` clause excludes ophthalmic, dental, pathology, endoscopic and microscopy imaging.
Second, task categories are defined by *what the model produces* — a label or box (detection/diagnosis), a mask
(segmentation), a number (measurement/quantification), a future risk (outcome prediction), a better or missing image
(reconstruction/imputation), text (report generation/LLM), a reusable backbone (foundation/vision-language model),
an autonomous multi-step action (agent), or a non-image output (workflow/non-interpretive). This differs from
taxonomies organized by clinical purpose and the difference is consequential; we return to it in the Discussion.

Query adequacy was assessed three ways: recall against 30 hand-selected landmark radiology AI papers resolved from
DOI to PMID; a precision proxy comparing each query with a strict title/abstract-only variant of the same vocabulary
and manual inspection of records returned only by the broader query; and an audit of PubMed's automatic translation
of every single-word term. Recall was 26/30 (86.7%) overall and 11/11 for the pediatric subset; the four misses were
methods papers naming no modality (nnU-Net) or cross-domain papers removed by the non-radiologic imaging exclusion.
For the pediatric query in 2025, 71.8% of the headline count was confirmed by explicit title/abstract wording.

Because PubMed does not index arXiv, the same queries were translated to arXiv API syntax and counted separately, in
the same yearly, modality and task shapes. The translation is approximate — stemming instead of truncation, no MeSH
expansion — so preprint counts are indicative and are always reported as an identified additional layer, never
silently merged.

### Structured-review layer

**Eligibility criteria.** Records were eligible if they reported primary research in which an artificial-intelligence
or machine-learning method — deep learning, classical machine learning, radiomics with a machine-learning classifier,
foundation models or large language models — was developed, applied, validated or clinically evaluated on diagnostic
radiologic imaging (radiography, fluoroscopy, CT, MRI, ultrasound and echocardiography, nuclear medicine/PET/SPECT,
angiography, or reports and worklists derived from them) in humans aged under 18 years or in fetal/prenatal imaging.
Mixed-age cohorts were eligible only where a pediatric subgroup was analyzed separately or the model was
pediatric-specific. We excluded reviews, editorials, letters, comments, case reports, errata and conference abstracts
without full text; ophthalmic, dental, endoscopic, dermoscopic, histopathologic and microscopic imaging; non-imaging
signals; and papers mentioning artificial intelligence only in passing. **No language restriction was applied**, a
deliberate departure from the previous scoping review, which excluded non-English articles and identified this as a
limitation likely to under-represent research from the Global South [1]. The full criteria are given in
Supplementary Table S2.

**Information sources and search.** Two databases were searched and are complete: **PubMed/MEDLINE** (6,000
records) and **Embase** (7,288 records), the latter run in two halves so that its MEDLINE-indexed portion could
serve as an audit of the PubMed query and its non-MEDLINE portion as new material. Preprints (arXiv, medRxiv,
bioRxiv, SSRN) are included and were drawn from the Embase layer and from OpenAlex records typed `preprint`.
Reference lists of all included reviews, and the supplementary article list of the previous scoping review [1],
were hand-searched; the latter doubles as an external recall check against an independently assembled corpus.
Sources were deduplicated by DOI resolved through the NCBI ID converter, then PMID, then normalized title with
first author and year, so that a preprint drops out of the corpus once its journal version appears. The search
covered 2005 onward, which contains the previous review's window in full and extends it by two years. Web of
Science, Scopus and IEEE Xplore were not run; their translations are given in Supplementary Table S1 and the
consequence is stated in Limitations.

**Publication forms.** Journal articles and preprints are included. **Conference abstracts and proceedings are
excluded**: they cannot support a judgement about study design, most are not extractable (only 62 of 81 eligible
conference abstracts sampled carried enough method and result detail to fill a database row), and unlike a
preprint a meeting abstract carries no DOI linking it to the full paper that supersedes it, so deduplication
cannot resolve the double count. 2,168 conference records were retrieved, removed before screening, and are
reported in the Discussion as a finding rather than analyzed as a corpus.

The PubMed strategy combined three `[tiab]`-fielded concept blocks — imaging modality, artificial intelligence, and
pediatric population — with AND. Every term is fielded because PubMed's automatic term mapping silently expands bare
vocabulary, as described above. The complete strings for every database are given in Supplementary Table S1.

**No topic exclusions and no publication-type filters were used in the search**, and this was decided empirically
rather than by preference. We tested the alternative: adding topic `NOT` clauses (optical coherence, dental,
microscopy, endoscopy) and publication-type filters (`NOT Review[pt]` and equivalents) to an otherwise identical
query reduced recall against our validation set from 100% to 81.5%. Both operator classes fire on incidental
properties rather than on a paper's subject. Kermany et al.'s pediatric chest radiograph study was removed because
the same paper also covers optical coherence tomography; iBEAT V2.0 and the ACR Pediatric AI Workgroup white paper
were removed because PubMed types *Nature Protocols* articles and white papers as `Review[pt]`. Recall is the
search's responsibility and precision is screening's; conflating the two loses records that no human ever reads.

**Search validation.** The strategy was validated three ways. Against 26 landmark pediatric radiology AI papers
assembled from domain knowledge and known pediatric datasets and cleared products — not from the output of this
query — it retrieved 26 of 26 (100%).

Two external checks carry more weight, because both corpora were assembled by other people for other purposes.
First, the previous scoping review publishes the full list of its 789 included articles. 663 resolved to a PubMed
record, and this search retrieves **639 of them (96.4%)**; of the records it retrieves, our screen independently
agreed with their inclusion decision in 95.5%. Second, the same strategy translated into Embase returned 3,728
MEDLINE-indexed records, of which `REVIEW_QUERY` retrieves **3,715 (99.7%)**. All thirteen misses were read: four
errata, one tombstone record, one research-highlight note, two digital pathology and two neuroimaging studies with
no learned model (all four correctly outside the criteria), and one artifact of a publisher appending a
field-of-research code to an article title.

Each check found a real defect, and both were fixed rather than reported around. The first showed that PubMed
tokenizes "fMRI" separately from "MRI", hiding the functional-imaging literature; the second that it tokenizes
"MRIs" separately from "MRI". Three further candidate terms were measured and rejected, including one that would
have raised the score for six extra records but was chosen only because it appears in the validation set — tuning a
query on the corpus used to validate it destroys the validation. The full accounting is in
`reports/06_search_strategy.md` §6. `[ACTION: expand the internal landmark set to ~50 papers and pre-register it.
Neither external check can be repeated as a blinded test, since the query was tuned against the first of them.]`

**Why there is no citation threshold.** The first version of this database admitted a paper only if it reached 20
citations, 10 citations per year, or an NIH relative citation ratio of 5.0. That rule has been retired. Filtering on
citations is selection bias with a direction: citations accrue faster in English-language journals, in high-income
countries, in well-networked subfields and for positive results, and a corpus assembled that way reports those
biases as properties of the field. It also censors the recent literature that a review of a fast-moving area exists
to describe — a raw-count floor cannot admit the current year at all — and removes precisely the null results,
external-validation failures and negative reader studies that a review of methodological rigor most needs. It cannot
be written into a PRISMA flow, because "insufficiently cited" is not an eligibility criterion. Citation counts,
citation rate, relative citation ratio and field-weighted citation impact are still collected and reported, as
descriptive variables, which is their legitimate use.

**Screening.** Records were screened on title and abstract against the eligibility criteria; 99.0% of retrieved
records carry an abstract, so screening operates on text rather than titles. Records whose abstract was insufficient
to decide, and records without an abstract, went to full-text review. Screening was performed by a large language
model under a fixed schema returning an include/exclude decision with a coded reason.
**Screening agreement.** A blinded random sample of 150 screened records was re-screened by a second, independent
automated screener running a different model, shown the eligibility definition and the records but not the first
pass's decisions. Agreement was 94.7%, Cohen's kappa 0.885, and the first pass's recall against the second 0.958
with precision 0.958 (8 disagreements). All eight fell on three boundaries the criteria do not fully resolve: mixed
adult and pediatric cohorts without a separately analyzed subgroup; general-purpose methods benchmarked on a
dataset that happens to include fetal or pediatric images; and studies that use an existing AI tool as a
measurement instrument rather than developing one. **This is agreement between two automated screeners and is not
human validation** — two models can share a blind spot, agree, and both be wrong.
`[ACTION: the 400-record dual-human sample remains required before submission, and the three boundary rules above
should be written into the published eligibility criteria first so that human screeners are not rediscovering them
one record at a time.]`

**Data extraction.** Each included abstract was read once under a fixed Pydantic schema by a large language model
using constrained structured output, so that the reply is a validated object rather than free text to be parsed.
Twenty fields were extracted: an include/exclude verdict with reason, model name and family, modality, body
region, clinical problem, patient population, age groups, task, a plain-language model description, release status
and its evidence, code URL, dataset size, data source, validation strategy, headline result, study design and an
extraction confidence. Bibliographic fields (journal, year, DOI, authors) and impact metrics come from the source
record and are never model-generated. Controlled vocabularies for modality,
task and age group are compiled directly into the schema, so the database groups on the same axes as the
bibliometric layer.

Two fields are not left to the model alone. **Release status** is cross-checked against evidence: a code-hosting URL
in the abstract settles "open-source", and a product on the FDA pediatric-named device list or on a curated list of
commercial products with pediatric indications settles "commercial". Both checks only upgrade an "unclear" verdict,
and the evidence is recorded. "Unclear" must be read as *the abstract does not say*, not as *unavailable*.
**Impact metrics** (citations, citations per year, RCR, and field-weighted citation impact from OpenAlex) are
refreshed independently of extraction, so quoted numbers can be brought current without re-reading a single abstract.

Every row stores a hash of the exact text the model saw and a fingerprint of the prompt and schema version. A paper
is re-read only when it is new, when the source record changed, or when the prompt or schema is deliberately bumped.
Screened-out papers are retained with `include: false`, so a rejected record costs one extraction ever. Corrections
are made in a separate overrides file keyed by PMID and applied at export; nothing is hand-edited in place, and
deleting an override reverts the row. A fresh clone reproduces the exported tables from committed JSON with no
network access and no model calls.

`[ACTION: before submission, two authors should independently re-extract a random sample of at least 60 records and
report percent agreement and Cohen's kappa for modality, task, validation and release status. The pipeline supports
this directly through its worklist export, which emits the outstanding papers with their abstracts, the prompt and
the JSON schema for human completion, and validates human-written rows against the same schema on ingest. Without
this, extraction accuracy is asserted rather than demonstrated, and reviewers will say so.]`

### Translational layer

**Regulatory.** The FDA's public AI-enabled medical device list was parsed and filtered to the Radiology lead panel.
Devices whose names contain pediatric or fetal terms were flagged. This is a lower bound on pediatric relevance: a
device may carry a pediatric age range in its indication for use without saying so in its name, and the FDA list
does not publish indication text. The name-based count is therefore reported as a floor and contrasted with
indication-level estimates from other sources.

**Commercial.** A curated list of products with publicly stated pediatric indications was maintained alongside the
device list and cross-checked against it, recording vendor, product, task, pediatric status and the number of
listed clearances per company.

**Trade press.** Seven newsletter and trade-press archives (The Imaging Wire, RSNA News, ESR/ECR, TLDR AI, TLDR
Tech, Signify Research, Radiology Business) were scanned, each issue split into stories at heading boundaries. A
story counts as radiology AI when AI and imaging vocabulary co-occur, and as pediatric when pediatric vocabulary
also co-occurs within the same story. Where a story links to a publisher page, the link is resolved to a DOI and a
citation. Two major outlets (AuntMinnie, Diagnostic Imaging) block automated clients and are excluded; this is a
known and stated gap.

### Society and venue engagement

Because RSNA, ACR, ECR and SPR meetings publish no machine-readable program, each society's engagement with AI was
proxied by the AI share of its flagship journals in PubMed (RSNA: *Radiology*, *RadioGraphics*, *Radiology:
Artificial Intelligence*; ACR: *JACR*; ECR: *European Radiology*, *Insights into Imaging*; SPR: *Pediatric
Radiology*). Machine-learning and computer-vision venues (CVPR, ICCV, ICLR, ICML, NeurIPS) were sampled from DBLP
and labeled by title keywords, giving a conservative lower bound on their medical-imaging share.

### Reproducibility and update schedule

All collectors use only the Python standard library for networking, cache responses locally, and degrade gracefully
to empty results if a service is unreachable, so one blocked API never aborts a pull. Counts are date-stamped by the
year facet rather than by collection time, so re-running reproduces the same series apart from newly indexed
records. The complete pipeline runs monthly under continuous integration and opens a pull request with regenerated
data, figures and tables rather than pushing silently.

**Data reported here were collected on 2026-09-09 (bibliometric, structured and trade-press layers) and 2026-09-03
(FDA device list).** The 2026 figures are year-to-date and are not comparable to complete years; MEDLINE indexing
lag means the two most recent years are undercounted in all series.

### Statistics

This is a descriptive review. Counts and percentages are reported without inferential testing, because the
denominators are complete enumerations of an index rather than samples from a population, and chi-square tests
against an implicit uniform null answer a question no reader is asking. Where we compare eras, we report the raw
proportions and their denominators and let the reader judge. Compound annual growth rates are computed on endpoint
counts over the stated interval.

---

## Results

### The pediatric share of radiology AI is stable, not closing

Radiology AI publications rose from 715 PubMed records in 2008 to 20,831 in 2025, a compound annual growth rate of
21.9%; adding the arXiv preprint layer brings the 2025 total to 25,257. Pediatric radiology AI rose from 58 to 2,348
records over the same span, a compound annual growth rate of 24.3%. On the raw numbers, pediatric AI is growing
slightly faster than the field.

That framing is misleading, because pediatric radiology publishing as a whole is also growing. The informative
measure is **AI penetration**: the AI share of pediatric radiology publishing divided by the AI share of all
radiology publishing (Table 1). In 2025, AI accounted for 11.4% of all radiology records and 7.4% of pediatric
radiology records, a ratio of 0.65. That ratio has never exceeded 0.81, which it reached in 2015; it fell through
the deep-learning boom to a low of 0.53 in 2022 and has recovered only partially since. Pediatric radiology has been
roughly one-third less AI-saturated than radiology overall for fifteen years, and the deep-learning era widened
rather than narrowed the gap.

**Table 1** AI penetration of radiology and pediatric radiology publishing, PubMed, selected years

| Year | Radiology records | AI share of radiology | Pediatric radiology records | AI share of pediatric radiology | Penetration ratio |
|---:|---:|---:|---:|---:|---:|
| 2008 | 86,812 | 0.82% | 16,087 | 0.36% | 0.44 |
| 2012 | 115,476 | 0.49% | 21,150 | 0.30% | 0.60 |
| 2015 | 134,828 | 0.65% | 25,509 | 0.53% | 0.81 |
| 2018 | 140,927 | 1.87% | 26,955 | 1.26% | 0.68 |
| 2021 | 177,988 | 5.72% | 30,257 | 3.13% | 0.55 |
| 2022 | 169,514 | 7.36% | 26,678 | 3.89% | 0.53 |
| 2023 | 160,988 | 8.63% | 25,322 | 4.85% | 0.56 |
| 2024 | 167,690 | 9.67% | 28,488 | 5.95% | 0.62 |
| 2025 | 182,492 | 11.41% | 31,735 | 7.40% | 0.65 |
| 2026 (YTD) | 138,306 | 11.92% | 23,662 | 8.02% | 0.67 |

*Penetration ratio = (AI share of pediatric radiology) / (AI share of all radiology). A value of 1.0 would mean
pediatric radiology adopts AI at the same rate as radiology overall. Counts are PubMed only; 2026 is year-to-date.*

The same asymmetry appears in where the work is presented. The AI share of *Pediatric Radiology*, the SPR flagship
journal, rose from 0.4% in 2016 to 9.4% in 2025 and 16.0% year-to-date in 2026 — a genuine and accelerating
commitment, but one that trails RSNA's flagship journals (24.4% in 2025) and *European Radiology* and *Insights into
Imaging* (30.3%) by a wide margin, and that started three to four years later. In the general machine-learning and
computer-vision venues, medical imaging of any kind is 0-3.8% of accepted papers, flat across a decade of explosive
growth in those venues; pediatric imaging within that is a rounding error.

### What the corpus contains

13,508 records were identified across PubMed/MEDLINE (6,000), Embase (7,288) and an earlier OpenAlex pass (220).
6,908 were removed before screening — 4,726 as duplicates of the PubMed layer, 2,168 as conference abstracts or
proceedings excluded by the publication-form criterion, and 14 unresolved. Of the 6,600 records screened, 2,650
were excluded as adult-only, non-radiologic or without an AI/ML component, and 456 were in scope but not primary
research (reviews, editorials, guidelines and position statements, reported separately below). **3,494 primary
studies were included** (Fig. 1) — 4.4 times the 789 articles in the previous scoping review [1], and the largest
structured corpus of pediatric radiology AI assembled to date. 3,122 came from PubMed and 365 from Embase records
PubMed does not index; 231 are preprints.

Growth is steep and continuing: 29 included studies in 2015, 166 in 2020, 555 in 2024 and 685 in 2025, with 686
already indexed for 2026 at the collection date (Fig. 2). The composition (Table 2) is dominated by MRI (45.5%) and
ultrasound (23.7%); radiography, which led the previous review's count, is third at 19.3%, and CT is a distant
fourth at 9.3%.

**Table 2** Composition of the included corpus (n = 3,494 primary studies, 2005-2026)

| Axis | Category | n | % |
|:--|:--|---:|---:|
| **Modality** | MRI | 1,589 | 45.5 |
| | Ultrasound | 827 | 23.7 |
| | Radiography / x-ray | 676 | 19.3 |
| | CT | 325 | 9.3 |
| | Nuclear / PET | 53 | 1.5 |
| | Other / multiple / fluoroscopy | 101 | 2.9 |
| **Task (by model output)** | Detection / diagnosis (label or box) | 1,336 | 38.2 |
| | Measurement / quantification (number) | 836 | 23.9 |
| | Outcome prediction (future risk) | 683 | 19.5 |
| | Segmentation (mask) | 660 | 18.9 |
| | Reconstruction / imputation (better image) | 277 | 7.9 |
| | Workflow / non-interpretive | 167 | 4.8 |
| | Other | 123 | 3.5 |
| | Report generation / LLM (text) | 28 | 0.8 |
| | Foundation / vision-language model | 26 | 0.7 |
| **Age group** | Child | 1,301 | 37.2 |
| | Adolescent | 889 | 25.4 |
| | Fetal | 784 | 22.4 |
| | Infant | 515 | 14.7 |
| | Pediatric (unspecified) | 498 | 14.3 |
| | Neonate | 346 | 9.9 |
| | Mixed pediatric and adult | 316 | 9.0 |

*Modality, task and age group are multi-label; columns exceed 100%.*

### Fetal imaging is a quarter of the field and structurally distinct

Fetal and perinatal work accounts for 785 studies, 22.5% of the corpus. It does not lead on age group — children
(37.2%) and adolescents (25.4%) are ahead — but it is the most internally coherent segment in the review: **71% of
it is ultrasound** (560 of 785), against 23.7% ultrasound in the corpus overall, and its task profile is distinct,
led by segmentation (238) and detection (236) with measurement close behind (231).

This matters because the previous scoping review's subspecialty taxonomy contains no fetal or obstetric category,
and none of its ten most common clinical applications is a fetal one [1]. A quarter of the literature this search
retrieves is therefore invisible in that map.

The explanation is not a disagreement about the field. It is legible in their published search strategy, which
their supplementary material reproduces in full. Their population block is: *adolescent, child, infant, pediatrics,
paediatric\*, pediatric\*, child\*, neonat\*, infant\*, newborn\*, adolescen\*, teenager\**. **It contains no term for
fetal, foetal, fetus, prenatal, antenatal, perinatal, preterm or premature.** A fetal ultrasound study that
describes its population as fetal and prenatal, and never as a child, infant or neonate, cannot be retrieved by
that strategy at all. This is a structural exclusion, not a screening decision, and it accounts for the absence of
an entire quarter of the field from their map.

Two further vocabulary differences work in the same direction (Table 5). Their intervention block is four
concepts — *artificial intelligence, machine learning, neural network, deep learning* — with no term for radiomics,
computer-aided diagnosis or detection, computer vision, or any named classical method (support vector machine,
random forest, gradient boosting), and none for the vocabulary that post-dates their search (foundation model,
large language model, vision transformer, self-supervised). A radiomics study that says "radiomics" and "random
forest" but never "machine learning" is likewise unretrievable. Their modality block omits echocardiography,
mammography, fluoroscopy, angiography, scintigraphy and SPECT. They also used **focused (major-topic) MeSH**
explosions for the AI and radiology concepts, restricted to English, which trades recall for precision at both
ends.

**Table 5** Search vocabulary compared, by concept block

| Concept block | Kamran et al. 2026 [1] | This review |
|:--|:--|:--|
| Population | adolescent, child, infant, pediatrics, paediatric\*, pediatric\*, child\*, neonat\*, infant\*, newborn\*, adolescen\*, teenager\* | the same, **plus** fetal, foetal, fetus\*, foetus\*, prenatal, antenatal, perinatal, preterm, premature infant/neonate/birth, youth, juvenile, toddler\*, schoolchild\* |
| Intervention | artificial intelligence, machine learning, neural network, deep learning | the same, **plus** convolutional neural network, computer-aided diagnosis, computer-aided detection, radiomic\*, computer vision, transfer learning, self-supervised, vision transformer, foundation model, large language model, support vector machine, random forest, gradient boosting |
| Modality | radiology, diagnostic imaging, medical imaging, radiograph\*, computed tomography, CT scan\*, PET, fMRI, magnetic resonance, MRI, ultrasound\*, sonograph\*, sonogram\*, ultrasonograph\* | the same, **plus** MR imaging, MR images, echocardiograph\*, mammograph\*, x-ray, fluoroscop\*, scintigraph\*, SPECT, angiograph\*, neuroimaging, tractograph\*, elastograph\* |
| MeSH scope | focused (major topic) explosions | none — every term is title/abstract fielded |
| Language | English only | no restriction |
| Publication type | reviews and conference abstracts removed in the search | removed at screening, so mis-typed primary work is not lost |

*Their term lists are transcribed from the supplementary material of [1]; ours from `config.REVIEW_QUERY`.
Neither strategy is wrong — theirs buys precision and a manageable hand-screening burden, ours buys recall at the
cost of screening 6,600 records. But the difference determines what each review can see, and a reader comparing the
two should know that the fetal literature is outside one of them by construction.*

*A correction to our own earlier analysis is worth recording, because it shows the hazard the impact floor
introduced.* Under the citation-filtered corpus used in the first version of this database, fetal imaging appeared
to be the single largest age segment at 31.9%, ahead of children at 23.7%. On the unfiltered corpus that ranking
reverses. Fetal ultrasound methods papers are cited unusually heavily, so a citation threshold inflated their
share by roughly eight percentage points. The divergence from the previous review survives; the superlative does
not.

### The translational funnel

The methodological picture (Table 3, Fig. 5) is the central result. Of 3,494 included studies:

- **67.3%** reported internal validation only; a further **4.5%** reported no validation strategy at all.
- **18.7%** reported external or multi-center validation.
- **6.2%** included a reader study — a radiologist in the loop, with a measured effect.
- **3.3%** were prospective.
- **2.6%** (92 studies) provided a working code or model URL.
- **4.6%** involved a commercial product; **84.6%** said nothing about model availability.

On data, **39.1%** did not state the data source at all, **31.0%** used a single center, **20.1%** were
multi-center and **9.7%** used a public dataset. Where a dataset size could be parsed (2,005 studies, 57.4%), the
median was 548 subjects or images (IQR 204-2,022). A named model or product appeared in 23.4% of studies.

**Table 3** Methodological characteristics and their trajectory

| Characteristic | 2005-2014 (n=71) | 2015-2019 (n=295) | 2020-2022 (n=792) | 2023-2026 (n=2,336) | All (n=3,494) |
|:--|---:|---:|---:|---:|---:|
| Internal validation only | 81.7% | 74.9% | 71.1% | 64.6% | 67.3% |
| External / multi-center validation | 4.2% | 14.2% | 16.9% | **20.3%** | 18.7% |
| Reader study | 7.0% | 6.1% | 7.7% | 5.7% | 6.2% |
| Prospective | 2.8% | 2.4% | 1.6% | 4.0% | 3.3% |
| No validation stated | 4.2% | 2.4% | 2.7% | 5.4% | 4.5% |
| Single-center data | 22.5% | 33.6% | 37.8% | 28.7% | 31.0% |
| Multi-center data | 8.5% | 12.9% | 17.6% | **22.3%** | 20.1% |
| Open-source | 0.0% | 2.4% | 5.2% | 5.1% | 4.8% |
| Commercial product involved | 4.2% | 1.4% | 3.4% | 5.4% | 4.6% |
| Release status unclear | 95.8% | 94.9% | 88.4% | 81.6% | 84.6% |

*The 2023-2026 stratum is the largest because the field is growing, not because of any selection rule; 2026 is a
partial year. The 2005-2014 stratum is small (n=71) and its percentages are unstable.*

Two things are true at once. **Reporting rigor is improving**: external validation rose almost five-fold across
the eras, multi-center data nearly tripled, and the share of studies silent about model availability fell from
95.8% to 81.6%. And **the improvement is confined to what can be done retrospectively**: reader studies are no
more common now (5.7%) than in 2005-2014 (7.0%), prospective evaluation fell to 1.6% in 2020-2022 before reaching
4.0%, and code release has been flat at about 5% since 2020. Every axis that improved can be satisfied by
re-analyzing data already collected. The two that did not — putting a radiologist in the loop, and evaluating
prospectively — are the two that require new contact with patients. The field is getting better at what a
reviewer can demand in a revision and no better at what requires a different study design.

### What the non-primary literature says

The 456 in-scope records excluded as non-primary — reviews, editorials, guidelines and multi-society position
statements — are themselves a finding: **11.5% of the in-scope pediatric radiology AI literature is commentary
rather than primary research.** For a field with 3,494 primary studies, one commentary for every eight studies is a
high ratio, and it is concentrated in the last three years. This is the literature clinical leadership is most
likely to encounter, and it is not where the evidence is.

### Who writes this literature, and where a MEDLINE-only search stops

The Embase layer is not simply more of the same records. Of its 1,785 in-scope non-MEDLINE records, 998 were
already in the PubMed corpus — PubMed indexes a large Central-only population that Embase reports as non-MEDLINE —
leaving 777 genuinely new records, of which 426 were eligible and **365 entered the corpus as primary studies**.

The striking property of that material is authorship. For the 266 eligible new **journal articles**,
corresponding-author country was parsed from the Embase address field:

| Country | n | | Country | n |
|:--|--:|:-:|:--|--:|
| China | 129 | | Turkey | 6 |
| India | 24 | | Indonesia | 6 |
| United States | 14 | | Poland | 5 |
| Canada | 9 | | United Kingdom | 4 |
| Iran | 9 | | Russia | 4 |
| Germany | 7 | | Malaysia | 4 |

**189 of 266 (71%) have a corresponding author outside North America and Western Europe, against 14 (5%) from the
United States, across 34 countries.** 90 are not English-only and 67 carry no English at all. The whole PubMed
layer, by comparison, contains roughly 32 non-English records.

This is the concrete content of the no-language-restriction criterion. The previous review excluded non-English
articles and named this as a limitation likely to "disproportionately underrepresent Global South research" [1].
Dropping the restriction only answers that objection if the search reaches a non-English literature, and PubMed
alone does not: Embase is the mechanism, not the criterion. It is also better evidence than the criterion itself,
because country of correspondence is recorded in the record while language is only a proxy for it.

The **preprint** half of the same layer runs the other way — 160 eligible records, 26% non-Western, entirely in
English. medRxiv, bioRxiv and SSRN are North American and Western European venues. Combining the two halves
dilutes the finding, so they are reported separately.

### A sensitivity analysis a reader will ask for

The corpus contains a large body of work in which a machine-learning model is trained on pediatric brain MRI, fMRI,
DTI or connectome features to predict a psychiatric, cognitive or developmental outcome — ADHD, autism, depression,
IQ, treatment response. These meet every eligibility criterion (a trained model, a diagnostic radiology image, a
pediatric population) but are not what a radiologist would recognize as reporting. They are **916 of 3,494 studies
(26.2%)**, and they are the obvious candidate explanation for our MRI-first ranking.

They do not explain it. Removing the subgroup entirely leaves MRI first at **37.0%**, still well ahead of
radiography at 22.0% and against the previous review's radiography-first ordering. External validation is
**unchanged at 18.7%**, reader studies move from 6.2% to 6.1%, and prospective evaluation from 3.3% to 2.8%.
Neither headline result — the modality reversal or the narrowness of the funnel — depends on this literature.

### What never reaches a paper

2,168 conference records were retrieved and set aside by the publication-form criterion. They are worth reporting
as a count. **169 are SPR and ESPR meeting abstracts published as *Pediatric Radiology* supplements**, and from a
12% sample roughly 46% of the conference abstracts would meet this review's topic criteria. That is pediatric
radiology AI presented to this journal's own society and never converted into a full paper — a stage of the
translational funnel sitting *before* the first box this review measures, and invisible to any MEDLINE-only
search. We report it as a bounded observation from a sample, not as a corpus.

### Where the work is published

No venue dominates. *Scientific Reports* (133 studies) leads, followed by *Pediatric Radiology* (98),
*Medical Image Analysis* (65), *European Radiology* (57), *NeuroImage* (54) and *PLoS One* (52). Conference
proceedings account for 261 studies (7.9%), led by Lecture Notes in Computer Science (47) — lower than the 20.1%
we measured on the citation-filtered corpus, because proceedings papers are cited more heavily than the journal
median and were over-represented by the floor. Reviews restricted to MEDLINE, Embase, Web of Science and the
Cochrane Library, and excluding conference material, still miss roughly one included study in thirteen.

### The regulatory record narrows further

As of 2026-09-03, the FDA AI-enabled medical device list contained 1,524 devices, of which 1,164 (76.4%) fall under
the Radiology lead panel. Radiology clearances have accelerated sharply: 40 in 2018, 138 in 2022, 254 in 2025, and
69 in the first eight months of 2026. The list is dominated by the scanner manufacturers — GE HealthCare (107
devices), Siemens Healthineers (90), Philips (44), Canon Medical (43), United Imaging (40) — and by triage vendors,
led by Aidoc (34).

**Eleven radiology devices (0.9% of 1,164) carry a pediatric or fetal term in their device name**, from five
companies and covering three tasks (Table 4). Two further pediatric-named devices on the list are dental, not
radiologic, and are excluded here.

**Table 4** FDA-listed AI-enabled radiology devices with a pediatric or fetal device name

| Company | Device | Task | Clearances (year) |
|:--|:--|:--|:--|
| Gleamer | BoneView | Fracture detection on radiographs | 2 (2022, 2023) |
| AZmed | Rayvolve, Rayvolve LN, Rayvolve PTX-PE | Fracture and chest findings on radiographs | 4 (2022, 2024, 2025 ×2) |
| BrightHeart | Fetal EchoScan (v1.0, 1.1, 1.2) | Fetal echocardiography view and anomaly assist | 3 (2024, 2025 ×2) |
| Ever Fortune.AI | EFAI Bonesuite XR Bone Age Pro | Automated bone age | 1 (2024) |
| 16 Bit | Rho | Automated bone age | 1 (2024, De Novo) |

*Name-based identification is a lower bound: a device may carry a pediatric age range in its indication for use
without naming it. Visiana's BoneXpert, pediatric by design and CE-marked since 2009, does not appear on the FDA AI
list at all. Deep-learning CT and MR reconstruction products (GE TrueFidelity, Canon AiCE, Siemens Deep Resolve,
Philips Precise Image) are cleared without pediatric-specific labeling but are widely used for pediatric dose and
scan-time reduction.*

The tasks represented are exactly the three where pediatric-specific benchmarks or unambiguous pediatric populations
exist: bone age, which has had a public benchmark since the 2017 RSNA Pediatric Bone Age Challenge; fracture
detection, extended to children from mature adult products; and fetal echocardiography, where the population is
prenatal by definition. Nothing in the cleared set addresses neonatal chest imaging, congenital anomaly detection,
pediatric abdominal ultrasound, or pediatric oncology — the areas the literature is most active in.

Public attention tracks the regulatory picture rather than the research picture. Across seven trade-press archives
comprising 7,967 radiology AI stories, **161 (2.0%) concerned pediatric imaging**. The topics that dominate that
coverage — appendicitis and abdominal ultrasound (52 stories), fetal and neonatal brain MRI (39), funding and
business (37), regulatory clearance (29) — are only loosely related to what the literature emphasizes.

### Where the literature is thin

Within the pediatric bibliometric layer since 2023 (6,430 records), clinical problem clusters are strikingly
unequal. The largest are autism/ADHD/neurodevelopment (670 records), fetal anomalies and prenatal imaging (513),
brain tumors (284), congenital heart disease (283), fracture and non-accidental trauma (227), scoliosis and hip
dysplasia (224), epilepsy (189) and pneumonia/tuberculosis (182). The smallest, despite clinical importance and
clear imaging endpoints, are testicular and ovarian torsion (8 records, unchanged from the 2008-2022 era),
inflammatory bowel disease (22), lines and tubes in the NICU (54), neonatal jaundice and biliary atresia (56) and
craniosynostosis and craniofacial imaging (69).

Two patterns explain most of this distribution. Problems with a large public dataset attract work (bone age,
pneumonia, brain tumors, fetal standard planes); problems without one do not. And problems whose ground truth is a
number a machine can be scored against attract work more readily than problems whose ground truth requires clinical
follow-up.

---

## Discussion

### What this review adds

Three findings are, to our knowledge, new to the pediatric radiology AI literature.

**Pediatric AI is not catching up.** The absolute growth of pediatric radiology AI is genuinely impressive — a
40-fold increase in indexed records since 2008 — and both this review and Kamran et al. document it [1]. But growth
measured against the right denominator tells a different story. AI has penetrated pediatric radiology publishing at
roughly two-thirds the rate it has penetrated radiology publishing overall, and that ratio has been essentially
static since 2011, dipping during the deep-learning boom rather than rising. The deficit is structural. Framing
pediatric AI as "lagging but catching up" is not supported by the data; "growing in parallel, at a permanent
discount" fits better, and implies that the gap will not close on its own.

**A quarter of the field is fetal, and syntheses have been missing it.** Fetal and perinatal work is 22.5% of the
included corpus and is 68% ultrasound, making it the most internally coherent segment in the review; its share of
the most-cited work is higher still. This is a substantial divergence from Kamran et al., whose subspecialty taxonomy contains no fetal or
obstetric category and whose ten most common clinical applications include no fetal entry [1]. We believe the
explanation is a search-vocabulary effect rather than a disagreement about the field: a search built on pediatric
terminology (pediatric, child, infant, adolescent) under-captures a literature that describes itself as prenatal,
fetal and obstetric and that publishes in *Ultrasound in Obstetrics & Gynecology* and in MICCAI proceedings rather
than in pediatric radiology journals. Our queries include fetal and prenatal terms explicitly; the divergence is a
direct consequence.

This matters practically. Fetal ultrasound AI is where pediatric-relevant commercial activity is concentrated
(BrightHeart's three FDA clearances in two years; the fetal segment's prominence in the trade press), where the
first expert-level results were achieved, and where a children's hospital's imaging AI program is most likely to
encounter a cleared product with a genuinely pediatric indication. A review of pediatric radiology AI that omits
fetal imaging omits both its largest research segment and its most commercially advanced one.

**The funnel is much narrower than the count.** Of 3,494 included studies, 18.7% were validated outside the
developing institution, 6.2% put a radiologist in the loop, 3.3% were prospective, and 2.6% released code. Eleven
cleared devices carry a pediatric name. The distance between "pediatric radiology AI research is booming" and "a
child benefits" spans several order-of-magnitude reductions, each of them measurable. We would encourage that this
funnel, rather than the publication count, become the standard summary statistic for the field.

**Rigor is improving and prospective evidence is not.** This is the finding we did not expect and the one we would
most like others to check. Between 2005-2014 and 2023-2026 external validation rose from 4.2% to 20.3% and
multi-center data from 8.5% to 22.3% — real, sustained movement on exactly the axes that reviews and reporting
checklists have pressed. Over the same twenty years reader studies went from 7.0% to 5.7% — no improvement at
all — and prospective evaluation from 2.8% to 4.0%, having fallen to 1.6% in between. Retrospective external
validation is something an author can add during revision;
a prospective study is a different protocol, a different budget and a different year. The field has responded to
the critiques it can respond to cheaply.

### Where we differ from the existing synthesis, and why

Kamran et al.'s scoping review and this systematic review reach different conclusions on two axes. Because the two
appear in the same journal within a year, we think it is worth stating precisely where the difference comes from,
since in both cases the difference is methodological and both answers are defensible.

**Modality rank.** Kamran et al. found radiography first (37.8%), MRI second (33.0%), ultrasound third (14.5%) and
CT fourth (11.4%) [1]. We find MRI first (43.6%), ultrasound second (27.6%), radiography third (21.7%) and CT fourth
(8.4%). Three factors separate these. Their corpus is weighted toward musculoskeletal imaging (33.0% of articles),
where bone age and fracture radiographs dominate; ours includes the fetal ultrasound literature that theirs largely
does not; and our corpus includes the neurodevelopmental and psychiatric neuroimaging-ML literature, which is
disproportionately MRI-based
(neurodevelopmental cohorts, fetal and neonatal brain segmentation). Neither ranking is wrong. They answer "what has
been published on children" and "what pediatric imaging AI work the field has read", respectively.

**Task distribution, and what follows from it.** Kamran et al. report that 91.1% of articles address image
interpretation or diagnosis, with 5.6% on artifact and motion reduction and under 2% on acquisition, communication,
consultation, education and policy combined, and they recommend redirecting funding and protected time toward those
neglected non-interpretive areas [1]. Our product-based taxonomy gives detection/diagnosis 38.2%,
measurement/quantification 23.9%, outcome prediction 19.5%, segmentation 18.9%, reconstruction/imputation 7.9% and
workflow/non-interpretive 4.8%.

These are not contradictory measurements; they are different partitions of the same space. The Canadian Association
of Radiologists category "image interpretation/diagnosis" that Kamran et al. adopted absorbs segmentation,
quantification and prognostic modeling, which we count separately because they produce different things, are
validated differently, and reach the clinic by different routes. A model that outputs a Cobb angle, a model that
outputs an organ mask for dose calculation and a model that outputs "pneumonia present" are all "interpretation"
under the coarser scheme, and all three are counted inside the 91.1%.

The choice of partition changes the recommendation, which is why it is worth spelling out. Under a taxonomy in which
91% of the field is interpretation, the natural conclusion is that the field is monolithic and should diversify into
communication, education and policy. Under a taxonomy in which quantification, segmentation and reconstruction together account for
half of pediatric work, the field already has a substantial non-diagnostic wing, and the more actionable
observation is that this wing is where pediatric benefit is most immediate and most under-exploited relative to its
evidence base. Deep-learning reconstruction is on scanners in children's hospitals today; it cuts pediatric CT dose
roughly in half at equal or better image quality [16] and shortens pediatric brain MRI acquisitions by 29-41%
with lower noise and fewer artifacts, reducing sedation exposure [17]. It requires no diagnostic model in the loop, no new clearance pathway, and no pediatric dataset. It is, on
present evidence, the single largest available pediatric benefit from AI, and it is not what most pediatric
radiology AI research is about.

We do not disagree that communication, education, policy and stakeholder engagement are under-researched; our own
count of workflow and non-interpretive work (8.5%) supports that, and the near-absence of studies capturing patient
and family perspectives is a real gap. We would rank the priorities differently: datasets and validation first,
because they gate everything downstream; dose and throughput second, because the benefit is available now; and
non-interpretive research third, because although it is cheap and neglected, it does not by itself put a better tool
in front of a radiologist.

**Trajectory.** Kamran et al. characterize reporting quality largely as a static deficit — 88.8% of articles
discussed bias, but 11.2% showed reporting bias, 6.6% did not report their dataset, and 64.8% relied on local
hospital data [1]. Our era comparison shows measurable improvement, but not on every axis. External validation rose
from 4.2% to 20.3%, multi-center data from 8.5% to 22.3%, and the fraction of papers silent about model
availability fell from 95.8% to 81.6%. Reader studies did not improve at all (7.0% to 5.7%), and prospective
evaluation reached only 4.0% after falling to 1.6% in 2020-2022. The field is responding to precisely the critiques
that reviews like theirs have made — and the split is informative rather than incidental. Every axis that improved
can be satisfied by re-analyzing data already collected; the two that did not are the two requiring new contact
with patients. This is worth saying in both directions: a literature that only ever hears it is inadequate has no
way to tell whether its corrections are working, and a literature praised for improving in general will not notice
that its improvement stops exactly where cost begins.

*(These era figures supersede those in the first version of this database, which were computed on the
citation-filtered corpus and overstated every rigor measure — heavily cited papers are more likely to be externally
validated and to involve readers. The direction of the trend survived; the levels did not.)*

### Why a living database

The half-life of a bibliometric review in this field is short. Kamran et al.'s search closed in August 2024; in
2025 and 2026 to date alone, PubMed indexed a further 4,245 pediatric radiology AI records — more than five times
the size of their entire included corpus [1]. Any static synthesis of a field growing
at 24% per year is substantially out of date at the moment of publication, and its central estimates cannot be
checked without redoing the work.

We have therefore built this review as software. Every query string, screening rule, impact threshold, extraction
schema and figure specification is versioned in a public repository. The pipeline runs monthly under continuous
integration and opens a pull request containing regenerated counts, tables and figures. The paper database is
reproducible from committed data with no network access. Impact metrics refresh independently of extraction, so
citation counts and RCRs can be brought current without re-reading anything. Corrections live in an overrides file
keyed by PMID, so that every departure from the automated extraction is explicit, attributable and reversible.

This design has costs, which we state plainly. Automated screening and structured extraction are not equivalent to
dual independent human review, and the currency of the corpus is bounded by indexing lag, which is worst in exactly
the most recent year a reader cares about. But the design makes something possible that a static review cannot
offer: a reader who
doubts a number here can regenerate it, a reader who disagrees with the pediatric term list can change it and see
what happens, and a reader in 2028 can obtain the 2028 version rather than this one.

We would suggest that bibliometric syntheses in fast-moving areas of medical imaging should default to this form.
`[ACTION: insert the repository URL and an archived DOI (Zenodo) before submission.]`

### Implications for pediatric radiology practice and research

**For departments considering purchase.** The cleared pediatric-labeled set is small enough to enumerate (Table 4)
and covers three tasks. Everything else on the market that a children's hospital might deploy is adult-cleared,
which is not a bar to use but is a bar to assuming performance. The best available quantitative estimate of what
happens when an adult-derived tool meets pediatric anatomy comes from CT organ segmentation, where mean Dice fell
from 0.81 in adults to 0.73 in children and to 0.35-0.41 for the adrenal glands, and was recovered by pediatric
fine-tuning [2]. The best estimate of what happens in real pediatric practice comes from a pediatric emergency
department, where a CE-marked fracture detector achieved 92% stand-alone sensitivity but only 68% for radial condyle
fractures, and improved resident accuracy from 88% to 90% while causing residents to abandon a correct diagnosis in
2% of cases [3]. Both results argue for the same policy: local, age-stratified validation before clinical use, and
monitoring afterward.

**For research groups choosing a problem.** The distribution of research effort across pediatric clinical problems
is determined more by dataset availability than by clinical need. Testicular and ovarian torsion has attracted eight
papers since 2008 and none of the growth of the last three years. Inflammatory bowel disease, NICU line and tube
positioning, biliary atresia and craniofacial imaging are similarly thin. Each has an unambiguous imaging endpoint
and a clinically consequential decision attached to it. A children's hospital with an imaging archive and a
willingness to curate it is better placed to change these numbers than to add to the 670 papers on
neurodevelopmental imaging.

**For the field's data infrastructure.** Only two public pediatric radiograph datasets exceed 10,000 images; the
largest public pediatric-only CT set contains 359 patients; and no RSNA pediatric challenge has been run since bone
age in 2017. Adult benchmarks of comparable importance are one to two orders of magnitude larger (CheXpert 224,000
images; MIMIC-CXR 377,000) and exclude children entirely. Recent work has quantified the consequence directly: the
absence of children from public medical imaging data is producing measurable and growing age bias in deployed models
[4]. A curated, consented, age-stratified, multi-institutional pediatric dataset remains the single scarcest
resource in this field, and it is the contribution children's hospitals are uniquely positioned to make. It is also
the one intervention that would move every other number in this review.

### Limitations

Several limitations bear on how these results should be read.

**Automated screening and extraction.** Records were screened by query and impact threshold rather than by human
title and abstract review, and fields were extracted by a language model under a fixed schema rather than by two
independent human reviewers. The schema is validated, provenance is recorded per row, and release status is
cross-checked against external evidence, but this does not establish extraction accuracy.
`[ACTION: the human dual-extraction sample described in Methods must be completed and its agreement statistics
reported here.]`

**Three databases remain unsearched.** PubMed/MEDLINE and Embase are complete. Web of Science, Scopus and IEEE
Xplore have not been run; their translations are in Supplementary Table S1. The Embase layer gives a direct
estimate of what a second database adds — 365 included studies, an 11% increase — and of what it adds that PubMed
structurally cannot reach, so the remaining gap is bounded rather than unknown. IEEE Xplore is the one most likely
to matter, because it indexes the engineering literature (ISBI, TMI) that both PubMed and Embase cover unevenly,
and the direction of that bias is knowable: the missing layer is disproportionately methods work, so the true
share of segmentation, reconstruction and foundation-model studies is somewhat higher than Table 2 reports.

**Automated screening at scale.** Screening 6,600 records without dual human review is the principal
methodological risk of this design. A false include is corrected at extraction; a false exclude is invisible. The
sampling protocol in Methods is intended to bound that error, and the review should not be submitted before it is
executed and its recall reported.

**Database coverage.** The PubMed and Embase layers are complete and cross-validated against each other.
`[ACTION: Web of Science, Scopus and IEEE Xplore require institutional access and have not yet been run; their
translations are given in Supplementary Table S1.]`

**Geographic analysis is partial.** Corresponding-author country was parsed for the Embase layer only, because
that is the layer whose records carry a structured address field; it is not available corpus-wide, so we report it
for the Embase contribution rather than as a property of all 3,494 studies. Institutional and author-level
characteristics were not extracted at all, and we therefore cannot fully address the research-concentration
question Kamran et al. raise [1].

**Query dependence.** Every count here is a function of a query. We have made those queries explicit, audited
PubMed's term expansion, measured recall against landmark papers (86.7% overall, 100% for the pediatric subset) and
reported a precision proxy (71.8% of pediatric hits confirmed by explicit title/abstract wording), but a different
vocabulary would give different numbers. This is precisely why the queries are published and editable.

**Regulatory undercount.** Pediatric device identification is name-based, because the FDA list does not publish
indication text. The true count of cleared devices with a pediatric age range in their indication is higher than 11,
possibly substantially so; other analyses have put pediatric-targeted devices near 9% of radiology clearances [1].
Our figure should be read as a floor on *explicitly pediatric* products, not as an estimate of pediatric-usable ones.

**Trade press coverage.** Two significant outlets block automated access and are excluded, and newsletter archives
skew toward vendor announcements. Trade-press counts should be read as an indicator of commercial attention, not of
clinical adoption.

**Recency.** MEDLINE indexing, citation accrual and FDA list updates all lag. The 2025 and 2026 figures are
undercounts, and 2026 is a partial year throughout.

---

## Conclusion

Pediatric radiology AI has grown 40-fold since 2008, but it has never closed its relative gap with adult radiology
AI: measured as the AI share of each field's own publishing, pediatric radiology has been roughly one-third less
AI-saturated than radiology overall for fifteen years, and the gap widened rather than narrowed during the
deep-learning boom. Fetal imaging is a quarter of the included literature, is overwhelmingly ultrasound, and is
largely invisible to syntheses built on pediatric search vocabulary. Retrospective rigor is improving substantially
— external validation rose from 4.2% to 20.3% across the eras and multi-center data from 8.5% to 22.3% — while
prospective evaluation moved only from 2.8% to 3.8% and code release has been flat near 5% since 2020: the field
has answered the critiques that can be answered in a revision and not those that require a different study design.
The funnel from publication to deployment remains extremely narrow: fewer than one study in five is externally
validated, one in seventeen involves a radiologist reader, one in thirty-three is prospective, one in thirty-eight
releases code, and eleven of 1,164 cleared radiology AI devices carry a pediatric name. The most immediately
available pediatric benefit from AI — deep-learning reconstruction for dose and scan-time reduction — is not the
subject of most pediatric AI research, and the scarcest resource in the field remains a curated, age-stratified,
multi-institutional pediatric imaging dataset. We publish the analysis as an executable, monthly updated database
so that these estimates can be audited, corrected and carried forward rather than repeated.

---

## Declarations

**Data availability.** All queries, collection code, extracted records, figures and reports are available at
`[ACTION: repository URL]` and archived at `[ACTION: Zenodo DOI]`. The paper database is reproducible from committed
data with a single command and no network access.

**Funding.** `[ACTION]`

**Conflicts of interest.** `[ACTION]`

**Ethics approval.** Not applicable; this review analyzed published literature and public regulatory records and
collected no patient data.

**Author contributions.** `[ACTION]`

---

## References

*Provisional; every DOI below resolves through doi2bib into `reports/references.bib` per project convention. The
reference list will need expansion to roughly 60-80 entries for a full review — the entries here are those cited in
the body text above.*

1. Kamran R, Widjaja E, Sy A, et al. The current state of artificial intelligence research in pediatric radiology
   and recommendations for the future: a scoping review. *Pediatr Radiol*. 2026;56(9):2007-2020.
   doi:10.1007/s00247-025-06462-5
2. Chatterjee D, Kanhere A, Doo FX, et al. Children Are Not Small Adults: Addressing Limited Generalizability of an
   Adult Deep Learning CT Organ Segmentation Model to the Pediatric Population. *J Imaging Inform Med*.
   2025;38(3):1628-1641. doi:10.1007/s10278-024-01273-w
3. Ziegner M, Pape J, Lacher M, et al. Real-life benefit of artificial intelligence-based fracture detection in a
   pediatric emergency department. *Eur Radiol*. 2025;35(10):5881-5890. doi:10.1007/s00330-025-11554-9
4. Hua SBZ, et al. Lack of children in public medical imaging data points to growing age bias in biomedical AI.
   *medRxiv*. 2025. doi:10.1101/2025.06.06.25328913
5. Halabi SS, Prevedello LM, Kalpathy-Cramer J, et al. The RSNA Pediatric Bone Age Machine Learning Challenge.
   *Radiology*. 2019;290(2):498-503. doi:10.1148/radiol.2018180736
6. Larson DB, Chen MC, Lungren MP, et al. Performance of a Deep-Learning Neural Network Model in Assessing Skeletal
   Maturity on Pediatric Hand Radiographs. *Radiology*. 2018;287(1):313-322. doi:10.1148/radiol.2017170236
7. Rassmann S, Keller A, Skaf K, et al. Deeplasia: deep learning for bone age assessment validated on skeletal
   dysplasias. *Pediatr Radiol*. 2023;54(1):82-95. doi:10.1007/s00247-023-05789-1
8. Skaf K, Fardipour M, Schmidt P, et al. Automated bone age assessment in rare pediatric growth disorders: a
   comparative study using Deeplasia. *Front Endocrinol*. 2026;17. doi:10.3389/fendo.2026.1741927
9. Arnaout R, Curran L, Zhao Y, Levine JC, Chinn E, Moon-Grady AJ. An ensemble of neural networks provides
   expert-level prenatal detection of complex congenital heart disease. *Nat Med*. 2021;27(5):882-891.
   doi:10.1038/s41591-021-01342-5
10. Athalye C, van Nisselrooij A, Rizvi S, Haak MC, Moon-Grady AJ, Arnaout R. Deep-learning model for prenatal
    congenital heart disease screening generalizes to community setting and outperforms clinical detection.
    *Ultrasound Obstet Gynecol*. 2024;63(1):44-52. doi:10.1002/uog.27503
11. Zech JR, Badgeley MA, Liu M, Costa AB, Titano JJ, Oermann EK. Variable generalization performance of a deep
    learning model to detect pneumonia in chest radiographs: A cross-sectional study. *PLoS Med*.
    2018;15(11):e1002683. doi:10.1371/journal.pmed.1002683
12. Wasserthal J, Breit HC, Meyer MT, et al. TotalSegmentator: Robust Segmentation of 104 Anatomic Structures in
    CT Images. *Radiol Artif Intell*. 2023;5(5). doi:10.1148/ryai.230024
13. Irvin J, Rajpurkar P, Ko M, et al. CheXpert: A Large Chest Radiograph Dataset with Uncertainty Labels and
    Expert Comparison. *Proc AAAI Conf Artif Intell*. 2019;33(01):590-597. doi:10.1609/aaai.v33i01.3301590
14. Mongan J, Moy L, Kahn CE. Checklist for Artificial Intelligence in Medical Imaging (CLAIM): A Guide for Authors
    and Reviewers. *Radiol Artif Intell*. 2020;2(2):e200029. doi:10.1148/ryai.2020200029
15. Elliott JH, Synnot A, Turner T, et al. Living systematic review: 1. Introduction — the why, what, when, and how.
    *J Clin Epidemiol*. 2017;91:23-30. doi:10.1016/j.jclinepi.2017.08.010
16. Brady SL, Trout AT, Somasundaram E, Anton CG, Li Y, Dillman JR. Improving Image Quality and Reducing Radiation
    Dose for Pediatric CT by Using Deep Learning Reconstruction. *Radiology*. 2021;298(1):180-188.
    doi:10.1148/radiol.2020202317
17. Yoo H, Moon HE, Kim S, et al. Evaluation of Image Quality and Scan Time Efficiency in Accelerated 3D
    T1-Weighted Pediatric Brain MRI Using Deep Learning-Based Reconstruction. *Korean J Radiol*. 2025;26(2):180.
    doi:10.3348/kjr.2024.0701

---

## Suggested figures

All are already generated by the pipeline and live in `figures/`.

| # | Content | Source file |
|---|---|---|
| 1 | PRISMA 2020 flow | `review_prisma.png` |
| 2 | AI penetration of radiology vs pediatric radiology publishing, 2008-2026, with the ratio on a second axis | new; from `pubmed_yearly_counts.json` |
| 3 | Included studies by modality and year | `review_modality_year.png` |
| 4 | Clinical problem clusters, 2008-2022 vs 2023-present | `ped_problems.png` |
| 5 | The translational funnel: 3,494 studies → external validation → reader study → prospective → code → commercial | `review_funnel.png` |
| 6 | AI share of society flagship journals (RSNA, ECR, ACR, SPR), 2016-2026 | `society_ai_share.png` |

---

## Appendix: SPR scientific abstract (oral / poster)

*Formatted to the SPR requirement of Title, Purpose, Methods, Results, Conclusions.*

**Title:** From evidence to deployment: a systematic, continuously updated review of artificial intelligence in
pediatric radiology

**Purpose:** To measure the size, composition, methodological rigor and translational status of pediatric radiology
AI, to link the literature to the regulatory record, and to release the analysis as a database that updates monthly
rather than a fixed snapshot.

**Methods:** We combined a bibliometric layer (PubMed, 2008-2026, four fielded boolean queries with an arXiv
preprint layer, audited for term expansion; recall 26/30 landmark papers, 11/11 pediatric) with a structured-review
layer: a high-recall search of PubMed, Embase, Web of Science, Scopus, IEEE Xplore, preprint servers and a
prespecified list of conference venues, with no citation, language, publication-type or topic filter (PubMed layer
6,600 records screened from PubMed/MEDLINE and Embase, 2005-2026; 96.4% recall against the previous review's
789 included articles and 99.7% against 3,728 Embase records), screened against explicit eligibility
criteria and extracted under a fixed 20-field schema. Both were cross-linked to the FDA AI-enabled device list (1,164 radiology-panel devices) and to 7,967
radiology AI stories in seven trade-press archives. All code, queries and records are public and re-run monthly.

**Results:** Radiology AI publications grew from 715 (2008) to 20,831 (2025) PubMed records; pediatric records
from 58 to 2,348. AI reached 11.4% of all radiology publishing in 2025 but 7.4% of pediatric radiology publishing,
a penetration ratio of 0.65 that has not exceeded 0.81 in eighteen years. Of 6,600 records screened, 3,494 primary
studies were included — 4.4 times the previous scoping review's corpus. MRI (45.5%) and ultrasound (23.7%) led
radiography (19.3%); fetal imaging was 22.5% of studies and 71% of it was ultrasound, a segment absent from prior
pediatric syntheses. By model output, detection/diagnosis was 38.2%, measurement 23.9%, outcome prediction
19.5%, segmentation 18.9%. Validation was internal only in 67.3%, external/multi-center in 18.7%, a reader study in
6.2%, prospective in 3.3%; code was available for 2.6% and the data source was unstated in 39.1%. External
validation rose from 4.2% (2005-2014) to 20.3% (2023-2026) and multi-center data from 8.5% to 22.3%, while
reader studies fell from 7.0% to 5.7% and prospective evaluation reached only 4.0%. Embase contributed 365
studies PubMed does not index, 71% of whose eligible new journal articles had a corresponding author outside
North America and Western Europe. Of 1,164 cleared radiology AI devices, 11 (0.9%) carry a
pediatric device name, from five companies, covering bone age, fracture detection and fetal echocardiography.
Screening agreement between two independent automated screeners was 94.7% (kappa 0.885).

**Conclusions:** Pediatric radiology AI grows as fast as adult radiology AI but has never closed the relative gap.
Retrospective rigor is improving substantially while reader studies, prospective evaluation and code release have
not — the field has answered the critiques it can answer cheaply. Fetal imaging is a quarter
of the literature and is largely invisible to reviews built on pediatric search terms. The funnel from publication
to a tool a child benefits from is orders of magnitude narrower than publication counts imply. We release the
screened corpus and its code so these estimates can be audited and updated rather than re-derived.
