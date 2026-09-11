# From evidence to deployment: a systematic, continuously updated review of artificial intelligence in pediatric radiology

**Article type:** Review

**Running title:** Pediatric radiology AI: from evidence to deployment

**Authors:** Joseph Rich, Amit Sura

**Affiliations:** [AUTHOR ACTION: add each author's institutional affiliation]

**Corresponding author:** [AUTHOR ACTION: add name, postal address, email address, and telephone number]

**Main-text word count:** 3,143 (Introduction through Conclusion, excluding headings; calculated 2026-09-11)

**Abstract word count:** 215

**Tables:** 4

**Figures:** 6

## Abstract

Artificial intelligence (AI) research in radiology is expanding rapidly, but its pediatric share and progression toward clinical use remain uncertain. We quantified the size, composition, methodological rigor, and translational status of pediatric radiology AI. A bibliometric analysis counted PubMed records from 2008 through 2026. A systematic search of PubMed/MEDLINE and Embase identified primary studies from 2005 onward; records were screened against prespecified criteria and 20 fields were extracted using constrained automated models. The search identified 13,510 records, of which 6,602 were screened and 3,496 primary studies included. Radiology AI records increased from 715 in 2008 to 20,831 in 2025, while pediatric records increased from 58 to 2,348. In 2025, AI represented 11.4% of radiology publishing and 7.4% of pediatric radiology publishing. MRI (45.5%) and ultrasound (23.7%) predominated. External or multicenter validation was reported in 18.7%, reader studies in 6.2%, prospective evaluation in 3.3%, and a working code or model URL in 2.6%. External validation increased from 4.2% in 2005–2014 to 20.3% in 2023–2026, whereas reader-study frequency did not improve. Eleven of 1,164 FDA-listed radiology AI devices had a pediatric or fetal term in their name. Pediatric radiology AI is growing but remains less AI-saturated than radiology overall. Local age-stratified validation, prospective evaluation, and multi-institutional pediatric datasets are priorities for translating publication growth into clinical benefit.

**Keywords:** Artificial Intelligence; Radiology; Pediatrics; Systematic Reviews as Topic

## Introduction

Artificial intelligence (AI) is now a sustained feature of radiology research and practice. In 2025, one in nine radiology records indexed in PubMed concerned AI, and the US Food and Drug Administration (FDA) had listed more than 1,100 AI-enabled devices under its Radiology panel. Children may benefit from these developments, but pediatric imaging presents distinct constraints: smaller datasets, age-dependent anatomy and normal ranges, rare diseases, deliberate limitation of ionizing radiation, and heightened consent and privacy requirements. Performance in adults therefore cannot be assumed to generalize to children.

Kamran et al. mapped 789 original pediatric radiology AI articles published from 2005 to August 2024 [1]. Their scoping review described countries, modalities, subspecialties, and application categories, but did not examine model-level dataset size, validation, performance, or availability. These variables determine whether a published model could progress toward clinical use. The literature also changes quickly enough that a static review becomes outdated soon after its search closes, making a living, reproducible approach attractive [15].

This review examined primary research in which an AI or machine-learning method was developed, applied, validated, or clinically evaluated using diagnostic radiologic imaging in people younger than 18 years or in fetal/prenatal imaging. Eligible modalities included radiography, fluoroscopy, CT, MRI, ultrasound and echocardiography, nuclear medicine, and angiography. Mixed-age studies required a separately analyzed pediatric subgroup or a pediatric-specific model. Reviews, editorials, case reports, conference abstracts and proceedings, non-radiologic imaging, and studies without a substantive AI component were excluded. No language restriction was applied.

Our objectives were to: (1) quantify pediatric radiology AI growth relative to radiology AI overall; (2) characterize the pediatric literature by modality, task, and age group; (3) measure validation, study design, data provenance, and model availability over time; (4) relate the literature to the regulatory record; and (5) provide an auditable database that can be updated as new evidence appears.

## Materials and methods

### Study design and reporting

We combined a bibliometric layer, which counted indexed records, with a structured systematic-review layer, which characterized individual eligible studies, and a translational layer based on the FDA device list. The review was designed with reference to PRISMA 2020. The protocol was versioned with the analysis code but was not prospectively registered. Full eligibility criteria and database strategies are provided in Supplementary Tables S1 and S2.

### Bibliometric analysis

For each year from 2008 through 2026, PubMed E-utilities was queried using publication-date fields for four concepts: radiology, radiology and AI, pediatric radiology, and pediatric radiology and AI. Modality and task terms were restricted to titles and abstracts because PubMed automatic term mapping broadened unfielded terms such as “ultrasound” and “tomography.” Task categories were defined by model output: detection/diagnosis, segmentation, measurement/quantification, outcome prediction, reconstruction/imputation, report generation, foundation or vision-language modeling, autonomous agents, and workflow/non-interpretive applications. Because PubMed does not comprehensively index arXiv, analogous arXiv counts were retained as a separate supplementary layer and were not merged silently with PubMed counts.

Query adequacy was evaluated against landmark papers and two external corpora. The structured-review search retrieved all 26 prespecified pediatric landmark papers, 639 of 663 (96.4%) PubMed-resolved articles from the previous scoping review [1], and 3,715 of 3,728 (99.7%) MEDLINE-indexed records returned when the strategy was translated to Embase. Missed records were reviewed to identify tokenization problems and noneligible material. Search vocabulary and validation procedures are reported in Supplementary Table S1 and the accompanying search protocol.

### Information sources and study selection

PubMed/MEDLINE and Embase were searched from January 1, 2005, to September 9, 2026. The search combined title/abstract terms for imaging modality, AI, and pediatric or fetal population without topic exclusions, publication-type filters, or language restrictions. Preprints identified through Embase and OpenAlex were eligible and deduplicated against journal versions. Reference lists of included reviews and the article list from the previous scoping review were checked for additional records. Web of Science, Scopus, and IEEE Xplore were not searched; their absence is addressed as a limitation.

Records were deduplicated by DOI, PMID, and then normalized title with first author and year. Conference abstracts and proceedings were removed before screening because they generally lacked enough information to appraise study design and could not be reliably linked to later full reports. Remaining titles and abstracts were screened against the prespecified eligibility criteria using a large language model constrained to return an include/exclude decision and coded reason. Records without sufficient abstract information were designated for full-text assessment.

A blinded random sample of 150 records was independently rescreened by a second automated model. Agreement was 94.7% (Cohen's κ=0.885); recall and precision of the first pass against the second were both 0.958. This comparison measures inter-model agreement, not accuracy against human reviewers. A prespecified dual-human validation sample had not been completed at this snapshot.

### Data extraction and classification

Each included abstract was processed under a fixed, versioned schema using constrained structured output. Extracted fields included model name and family, modality, body region, clinical problem, patient population and age groups, task, model description, release status and evidence, code URL, dataset size, data source, validation strategy, principal result, study design, and extraction confidence. Bibliographic fields came directly from source records. Controlled vocabularies were compiled into the schema so that categories were consistent across studies.

Release status was cross-checked against code-hosting URLs, the FDA list, and a curated list of products with public pediatric indications. “Unclear” means that availability was not stated in the abstract, not that the model was unavailable. Each row retained the exact source-text hash, prompt and schema version, and any manual override. Duplicate human extraction of the prespecified validation sample had not been completed at this snapshot.

The extracted rows are published as a single table containing exactly the included primary studies, so that the database, this manuscript, and the accompanying presentation describe one corpus. Records excluded at screening or on publication form remain in the versioned store with their coded reason and are the basis of any audit of those decisions.

### Citation measures

Each study also carried its citation record: counts, citations per year, and the relative citation ratio from NIH iCite for records with a PubMed identifier, and citation counts and field-weighted citation impact from OpenAlex, matched by DOI. OpenAlex coverage was necessary because Embase-only records have no PubMed identifier and therefore no relative citation ratio. Both normalized measures place the average article of the same field and year at 1.0. A normalized value was used only after a study had accumulated at least five citations, because the ratio otherwise divides by a fraction of an expected citation and becomes unstable for very recent work. Citation measures described the corpus and identified individual studies for presentation; they were not used to select the corpus, because a citation threshold would import language, geography, and positive-result bias into a systematic review.

### Translational analysis

The FDA AI-Enabled Medical Device List was downloaded on September 3, 2026, and filtered to the Radiology panel. Devices with pediatric or fetal terms in the device name were flagged and grouped by company and task. This name-based method provides a lower bound because the public list does not contain complete age-specific indication text. Commercial products with publicly stated pediatric indications were cross-checked separately.

### Statistical analysis and reproducibility

Counts, proportions, medians, interquartile ranges, and compound annual growth rates were calculated descriptively. Categories for modality, task, and age were multilabel and therefore could total more than 100%. Era comparisons used 2005–2014, 2015–2019, 2020–2022, and 2023–2026. Inferential tests were not applied because the reported denominators were enumerations of indexed records rather than samples drawn for population inference.

Queries, cached source records, screening decisions, extraction schema, and analysis code were versioned. The pipeline regenerated counts, tables, and figures monthly. Results in this manuscript are a snapshot collected on September 9, 2026; 2026 is year-to-date, and the most recent years remain susceptible to indexing lag.

## Results

### Publication growth and study selection

Radiology AI publications increased from 715 PubMed records in 2008 to 20,831 in 2025 (compound annual growth rate, 21.9%). Pediatric radiology AI increased from 58 to 2,348 records (24.3%). Absolute pediatric growth was therefore slightly faster, but the field did not close its relative gap. In 2025, AI represented 11.4% of radiology publishing and 7.4% of pediatric radiology publishing, giving a penetration ratio of 0.65 (Table 1). The ratio did not exceed 0.81 during the 18-year observation period.

The systematic search identified 13,510 records: 6,000 from PubMed/MEDLINE, 7,288 from Embase, and 222 from an earlier OpenAlex pass. Deduplication and removal of ineligible publication forms left 6,602 records for screening. Of these, 2,650 did not meet topic criteria and 456 were relevant but non-primary publications; 3,496 primary studies were included (Fig. 1). Embase contributed 365 included studies not indexed in PubMed. Study counts rose from 29 in 2015 to 167 in 2020, 555 in 2024, and 685 in 2025 (Fig. 2).

### Composition of the evidence base

MRI was reported in 1,590 studies (45.5%), ultrasound in 828 (23.7%), radiography in 676 (19.3%), and CT in 325 (9.3%) (Table 2; Fig. 3). Detection/diagnosis was the most common model output (38.2%), followed by measurement/quantification (24.0%), outcome prediction (19.5%), segmentation (18.9%), and reconstruction/imputation (7.9%). Children were represented in 37.2% of studies, adolescents in 25.4%, fetal populations in 22.5%, infants in 14.7%, and neonates in 9.9%.

Fetal or perinatal imaging accounted for 787 studies (22.5%). This segment was structurally distinct: 561 of 787 studies (71.3%) used ultrasound, compared with 23.7% in the overall corpus. Its task distribution was led by segmentation, detection, and measurement. Two post hoc sensitivity analyses removed the developmental-neuroscience MRI literature, which is eligible under our criteria but is not diagnostic radiology in the usual sense. Removing the 322 MRI studies that named an explicit neurodevelopmental or psychiatric diagnosis left MRI clearly first among the remaining 3,174 studies (39.9%, versus ultrasound 26.1% and radiography 21.3%). Removing the wider set of 768 studies that also used cognitive-neuroscience methods or reported cognitive or behavioral outcomes left MRI and ultrasound level among 2,728 studies (30.1% and 30.2%), with radiography at 24.6%. MRI's lead in this corpus is therefore substantially attributable to that literature, and whether MRI or ultrasound ranks first depends on where the boundary is drawn. External or multicenter validation was insensitive to both exclusions (18.7% and 18.5%, versus 18.7% overall).

### Methodological rigor and the translational funnel

Internal validation only was reported in 2,352 studies (67.3%), external or multicenter validation in 654 (18.7%), reader studies in 217 (6.2%), and prospective evaluation in 115 (3.3%) (Table 3; Figs. 4 and 5). No validation strategy was stated in 158 studies (4.5%). Data came from a single center in 31.1%, multiple centers in 20.1%, and a public dataset in 9.7%; source was unstated in 39.1%. Where dataset size was extractable (2,006 studies), the median was 547 subjects or images (interquartile range, 204–2,022). A working code or model URL was documented in 92 studies (2.6%).

Several retrospective indicators improved over time. External or multicenter validation increased from 4.2% in 2005–2014 to 20.3% in 2023–2026, and multicenter data use increased from 8.5% to 22.3%. Reader studies did not increase (7.0% to 5.7%). Prospective evaluation increased from 2.8% to 4.0% across the same eras after falling to 1.6% in 2020–2022. Code-release classification remained near 5% from 2020 onward. Thus, improvement was concentrated in retrospective practices rather than study designs requiring prospective clinical participation.

### Citation impact of the corpus

A normalized citation measure was available for 1,669 of 3,496 studies (47.7%); the remainder were too recent to have accumulated five citations. The median of those studies was cited 3.4 times the average article of its field and year, so this is a well-cited rather than a neglected literature. The most-cited decile comprised 167 studies at or above 14 times the field-and-year average, of which 158 came from PubMed, 6 from Embase, and 3 from the OpenAlex layer. Selecting on citations did not select strongly for methodological rigor: external or multicenter validation was reported by 22.8% of that decile versus 18.7% of the corpus, a reader study by 9.6% versus 6.2%, and 61.1% still reported internal validation only (Fig. 6).

### Regulatory translation

The FDA list contained 1,524 AI-enabled devices, including 1,164 (76.4%) assigned to the Radiology panel. Eleven radiology devices (0.9%) had a pediatric or fetal term in the device name (Table 4). They came from five companies and addressed three application areas: fracture or chest-finding detection on radiographs, bone-age assessment, and fetal echocardiography. Because identification was name-based, this is a floor for explicitly pediatric devices and not an estimate of all devices whose indications permit pediatric use.

## Discussion

### Principal findings

This review found rapid growth but limited progression toward clinical translation. Pediatric radiology AI expanded approximately 40-fold from 2008 to 2025, yet AI remained about one-third less prevalent within pediatric radiology publishing than within radiology publishing overall. Among 3,496 primary studies, fewer than one in five reported external or multicenter validation, approximately one in 16 included a reader study, one in 30 was prospective, and one in 38 supplied a working code or model URL. Only 11 FDA-listed radiology devices were explicitly pediatric or fetal by name.

The trajectory was mixed. External validation and multicenter data use improved substantially, consistent with attention to reporting and evaluation standards such as CLAIM [14]. Reader studies did not become more common, and prospective studies remained below 5%. Retrospective development can often be extended with additional datasets, whereas prospective evaluation requires a different protocol, clinical workflow, resources, and contact with patients. Publication growth and reporting improvement therefore should not be interpreted as equivalent growth in evidence of clinical benefit.

### Relationship to previous work

The previous scoping review found radiography first, followed by MRI and ultrasound, and categorized 91.1% of studies as image interpretation or diagnosis [1]. We found MRI first and ultrasound second. Two design choices explain much of this difference. First, our search explicitly included fetal, prenatal, neuroimaging, fMRI, connectome, and classical machine-learning vocabulary. Fetal imaging alone represented 22.5% of our corpus and was predominantly ultrasound, and the sensitivity analyses above show that MRI's lead depends on retaining the developmental-neuroscience literature that a narrower vocabulary does not reach. Our modality ranking should therefore be read as a property of the search vocabulary as much as of the field. Second, we classified studies by what the model produced. Segmentation masks, quantitative measurements, outcome predictions, and reconstructed images were therefore separated from diagnostic labels rather than grouped under interpretation.

The broader vocabulary revealed a substantial fetal literature that may not use child, infant, or pediatric terminology. Fetal echocardiography has also produced expert-level and community-validated AI studies [9,10] and the most clearly pediatric recent FDA activity. Bone age is another comparatively mature area, supported by a public challenge and external evaluations across common and rare growth disorders [5–8]. These examples show how pediatric benchmarks and unambiguous target populations can concentrate research and facilitate evaluation.

### Implications for practice and research

Departments should not assume that adult performance transfers to pediatric anatomy. An adult-derived CT segmentation model showed lower mean Dice performance in children and particularly poor performance for small structures before pediatric fine-tuning [2]. Site-dependent failure has also been demonstrated for adult chest radiograph models [11], despite the availability of robust general segmentation systems [12]. In a pediatric emergency department, a fracture detector improved resident accuracy modestly but performed unevenly by fracture type and sometimes caused readers to reverse a correct diagnosis [3]. These findings support local, age-stratified validation before deployment, subgroup monitoring afterward, and predefined procedures for discordance between clinicians and software.

Research investment should prioritize shared pediatric infrastructure and prospective evaluation. Public adult chest radiograph datasets contain hundreds of thousands of images [13], while pediatric datasets are fewer and smaller. The absence of children from public medical imaging data has been associated with measurable age bias [4]. Multi-institutional datasets should therefore record age, developmental stage, acquisition parameters, disease prevalence, and site, with governance that permits external evaluation. Challenge designs can build on the RSNA pediatric bone-age model [5] but should extend to neonatal chest imaging, pediatric abdominal ultrasound, congenital anomalies, oncology, and other clinically important areas with limited data.

AI benefits are not limited to diagnosis. Deep-learning reconstruction can reduce pediatric CT radiation exposure while maintaining image quality [16] and accelerate pediatric brain MRI while reducing noise and artifacts [17]. These applications may offer near-term benefit without requiring an autonomous diagnostic decision, although local validation and safety monitoring remain necessary. Funding priorities should balance diagnostic model development with reconstruction, workflow, human-factors studies, and outcomes measured in clinical practice.

### Living and reproducible review design

A living database addresses the short useful life of a static bibliometric review [15]. Here, each search, screening decision, schema version, and correction is retained, allowing estimates to be regenerated and disagreements to be audited. Updating does not remove indexing lag or the need for methodological validation, but it makes changes in the evidence base visible and permits corrected classifications to propagate consistently through tables and figures. The repository should be archived at each published version so that the manuscript remains linked to a fixed, citable snapshot.

### Limitations

The principal limitation is automated screening and extraction without completed dual-human validation. Agreement between two models does not exclude shared error, particularly for mixed-age cohorts, general-purpose methods tested on pediatric images, and studies using AI as a measurement instrument. The prespecified human screening and extraction studies must be completed before submission, and their results may change corpus counts.

Second, PubMed/MEDLINE and Embase were searched, but Web of Science, Scopus, and IEEE Xplore were not. Engineering methods and conference-derived work may therefore be underrepresented. Conversely, 2,168 conference records were excluded because their limited reports could not support the review's central appraisal; this may omit work that never reached full publication. Third, most extraction used abstracts. Missing information, including the data source in 39.1% of studies, may represent incomplete reporting rather than absent methods. Formal study-level risk-of-bias assessment was not feasible across the heterogeneous designs, so the reported measures assess selected aspects of rigor rather than overall validity.

Fourth, the review is query-dependent. Although recall was high against three validation sets, vocabulary choices influence modality and population estimates. Fifth, FDA identification relied on pediatric terms in device names because complete age-specific indication text was unavailable in the list; the device count is a lower bound. Finally, recent-year estimates are affected by indexing lag, and 2026 data are incomplete. These limitations make the direction and scale of the observed translational gap more secure than any single exact percentage.

## Conclusion

Pediatric radiology AI is growing rapidly but has not closed its relative publication gap with radiology overall, and evidence narrows sharply between model development and clinical use. Retrospective rigor improved: external validation and multicenter data use increased across eras. Reader studies and prospective evaluation, however, remained uncommon, and explicit code release and pediatric-named FDA devices were rare. Fetal imaging constituted more than one-fifth of the literature and illustrates the importance of inclusive pediatric search vocabulary.

The take-home message is that publication volume should not be used as a proxy for pediatric clinical readiness. Practice should require local age-stratified validation and post-deployment monitoring. Research policy should prioritize prospective reader and outcome studies, transparent reporting, and governed multi-institutional pediatric datasets, including underrepresented neonatal, abdominal, congenital, and oncologic applications. Completing human validation of this review and broadening database coverage are immediate methodological priorities. A versioned living database can then show whether these changes narrow the translational gap rather than merely enlarge the literature.

## Declarations

**Data availability.** All queries, collection code, extracted records, figures, and reports will be available at [AUTHOR ACTION: repository URL] and archived at [AUTHOR ACTION: Zenodo DOI]. The included primary studies are published as one table with all extracted fields; every screened record, including those excluded and the coded reason for each exclusion, is in the accompanying versioned store. The analysis is reproducible from the archived snapshot without model calls.

**Funding.** Not applicable.

**Conflicts of interest.** No conflicts of interests to disclose.

**Ethics approval.** Not applicable; this review analyzed published literature and public regulatory records and collected no patient data.

**Informed consent.** Not applicable.

**Author contributions.** [AUTHOR ACTION: provide a CRediT contribution statement for each author.]

**Acknowledgments.** None.

## References

1. Kamran R, Widjaja E, Sy A, et al. The current state of artificial intelligence research in pediatric radiology and recommendations for the future: a scoping review. Pediatr Radiol. 2026;56(9):2007–2020. doi:10.1007/s00247-025-06462-5
2. Chatterjee D, Kanhere A, Doo FX, et al. Children Are Not Small Adults: Addressing Limited Generalizability of an Adult Deep Learning CT Organ Segmentation Model to the Pediatric Population. J Imaging Inform Med. 2025;38(3):1628–1641. doi:10.1007/s10278-024-01273-w
3. Ziegner M, Pape J, Lacher M, et al. Real-life benefit of artificial intelligence-based fracture detection in a pediatric emergency department. Eur Radiol. 2025;35(10):5881–5890. doi:10.1007/s00330-025-11554-9
4. Hua SBZ, et al. Lack of children in public medical imaging data points to growing age bias in biomedical AI. medRxiv. 2025. doi:10.1101/2025.06.06.25328913
5. Halabi SS, Prevedello LM, Kalpathy-Cramer J, et al. The RSNA Pediatric Bone Age Machine Learning Challenge. Radiology. 2019;290(2):498–503. doi:10.1148/radiol.2018180736
6. Larson DB, Chen MC, Lungren MP, et al. Performance of a Deep-Learning Neural Network Model in Assessing Skeletal Maturity on Pediatric Hand Radiographs. Radiology. 2018;287(1):313–322. doi:10.1148/radiol.2017170236
7. Rassmann S, Keller A, Skaf K, et al. Deeplasia: deep learning for bone age assessment validated on skeletal dysplasias. Pediatr Radiol. 2024;54(1):82–95. doi:10.1007/s00247-023-05789-1
8. Skaf K, Fardipour M, Schmidt P, et al. Automated bone age assessment in rare pediatric growth disorders: a comparative study using Deeplasia. Front Endocrinol. 2026;17. doi:10.3389/fendo.2026.1741927
9. Arnaout R, Curran L, Zhao Y, Levine JC, Chinn E, Moon-Grady AJ. An ensemble of neural networks provides expert-level prenatal detection of complex congenital heart disease. Nat Med. 2021;27(5):882–891. doi:10.1038/s41591-021-01342-5
10. Athalye C, van Nisselrooij A, Rizvi S, Haak MC, Moon-Grady AJ, Arnaout R. Deep-learning model for prenatal congenital heart disease screening generalizes to community setting and outperforms clinical detection. Ultrasound Obstet Gynecol. 2024;63(1):44–52. doi:10.1002/uog.27503
11. Zech JR, Badgeley MA, Liu M, Costa AB, Titano JJ, Oermann EK. Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: a cross-sectional study. PLoS Med. 2018;15(11):e1002683. doi:10.1371/journal.pmed.1002683
12. Wasserthal J, Breit HC, Meyer MT, et al. TotalSegmentator: robust segmentation of 104 anatomic structures in CT images. Radiol Artif Intell. 2023;5(5):e230024. doi:10.1148/ryai.230024
13. Irvin J, Rajpurkar P, Ko M, et al. CheXpert: a large chest radiograph dataset with uncertainty labels and expert comparison. Proc AAAI Conf Artif Intell. 2019;33(01):590–597. doi:10.1609/aaai.v33i01.3301590
14. Mongan J, Moy L, Kahn CE. Checklist for Artificial Intelligence in Medical Imaging (CLAIM): a guide for authors and reviewers. Radiol Artif Intell. 2020;2(2):e200029. doi:10.1148/ryai.2020200029
15. Elliott JH, Synnot A, Turner T, et al. Living systematic review: 1. Introduction—the why, what, when, and how. J Clin Epidemiol. 2017;91:23–30. doi:10.1016/j.jclinepi.2017.08.010
16. Brady SL, Trout AT, Somasundaram E, Anton CG, Li Y, Dillman JR. Improving image quality and reducing radiation dose for pediatric CT by using deep learning reconstruction. Radiology. 2021;298(1):180–188. doi:10.1148/radiol.2020202317
17. Yoo H, Moon HE, Kim S, et al. Evaluation of image quality and scan time efficiency in accelerated 3D T1-weighted pediatric brain MRI using deep learning-based reconstruction. Korean J Radiol. 2025;26(2):180. doi:10.3348/kjr.2024.0701

## Tables

**Table 1. AI penetration of radiology and pediatric radiology publishing in PubMed**

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
| 2026 YTD | 138,306 | 11.92% | 23,662 | 8.02% | 0.67 |

Penetration ratio = (AI share of pediatric radiology)/(AI share of all radiology). A value of 1.0 would indicate equal AI representation. AI, artificial intelligence; YTD, year to date.

**Table 2. Composition of included primary studies (n=3,496)**

| Axis | Category | n | % |
|:--|:--|---:|---:|
| Modality | MRI | 1,590 | 45.5 |
| | Ultrasound | 827 | 23.7 |
| | Radiography | 676 | 19.3 |
| | CT | 325 | 9.3 |
| | Nuclear medicine/PET | 53 | 1.5 |
| | Other/multiple/fluoroscopy | 101 | 2.9 |
| Task | Detection/diagnosis | 1,337 | 38.2 |
| | Measurement/quantification | 838 | 24.0 |
| | Outcome prediction | 683 | 19.5 |
| | Segmentation | 662 | 18.9 |
| | Reconstruction/imputation | 277 | 7.9 |
| | Workflow/non-interpretive | 167 | 4.8 |
| | Other | 123 | 3.5 |
| | Report generation/large language model | 28 | 0.8 |
| | Foundation/vision-language model | 26 | 0.7 |
| Age group | Child | 1,301 | 37.2 |
| | Adolescent | 889 | 25.4 |
| | Fetal | 786 | 22.5 |
| | Infant | 515 | 14.7 |
| | Pediatric, unspecified | 498 | 14.2 |
| | Neonate | 346 | 9.9 |
| | Mixed pediatric and adult | 316 | 9.0 |

Modality, task, and age group were multilabel; percentages within an axis can exceed 100%. CT, computed tomography; MRI, magnetic resonance imaging; PET, positron emission tomography.

**Table 3. Methodological characteristics by publication era**

| Characteristic | 2005–2014 (n=71) | 2015–2019 (n=295) | 2020–2022 (n=794) | 2023–2026 (n=2,336) | All (n=3,496) |
|:--|---:|---:|---:|---:|---:|
| Internal validation only | 81.7% | 74.9% | 71.2% | 64.6% | 67.3% |
| External/multicenter validation | 4.2% | 14.2% | 16.9% | 20.3% | 18.7% |
| Reader study | 7.0% | 6.1% | 7.7% | 5.7% | 6.2% |
| Prospective | 2.8% | 2.4% | 1.6% | 4.0% | 3.3% |
| No validation stated | 4.2% | 2.4% | 2.6% | 5.4% | 4.5% |
| Single-center data | 22.5% | 33.6% | 37.9% | 28.7% | 31.1% |
| Multicenter data | 8.5% | 12.9% | 17.5% | 22.3% | 20.1% |
| Open-source classification | 0.0% | 2.4% | 5.2% | 5.1% | 4.8% |
| Commercial product involved | 4.2% | 1.4% | 3.4% | 5.4% | 4.5% |
| Release status unclear | 95.8% | 94.9% | 88.4% | 81.6% | 84.6% |

The 2026 interval is incomplete. The 2005–2014 stratum is small and its percentages should be interpreted cautiously.

**Table 4. FDA-listed radiology AI devices with a pediatric or fetal term in the device name**

| Company | Device | Task | Clearances (year) |
|:--|:--|:--|:--|
| Gleamer | BoneView | Fracture detection on radiographs | 2 (2022, 2023) |
| AZmed | Rayvolve, Rayvolve LN, Rayvolve PTX-PE | Fracture and chest findings on radiographs | 4 (2022, 2024, 2025 ×2) |
| BrightHeart | Fetal EchoScan (v1.0, 1.1, 1.2) | Fetal echocardiography view and anomaly assistance | 3 (2024, 2025 ×2) |
| Ever Fortune.AI | EFAI Bonesuite XR Bone Age Pro | Automated bone age | 1 (2024) |
| 16 Bit | Rho | Automated bone age | 1 (2024, De Novo) |

Device identification was name-based and is a lower bound for explicitly pediatric products. AI, artificial intelligence; FDA, US Food and Drug Administration.

## Figure legends

**Fig. 1 PRISMA flow diagram.** Identification, deduplication, screening, and inclusion of records from PubMed/MEDLINE, Embase, and OpenAlex. Of 13,510 identified records, 6,602 were screened and 3,496 primary studies were included.

**Fig. 2 Included studies by publication year.** Annual number of primary pediatric radiology AI studies included from 2005 through September 9, 2026. The 2026 value is year-to-date and is affected by indexing lag.

**Fig. 3 Modality composition over time.** Annual number of included primary studies by imaging modality. Studies could receive more than one modality label.

**Fig. 4 Validation strategy by publication era.** Proportions of studies reporting internal validation only, external or multicenter validation, a reader study, prospective evaluation, or no stated validation strategy. Categories are mutually exclusive in the extraction schema.

**Fig. 5 Translational funnel.** Number and proportion of included studies reporting external or multicenter validation, a reader study, prospective evaluation, a working code or model URL, or involvement of a commercial product. These indicators are displayed against the full corpus to show the narrowing path toward clinical use; they are not necessarily nested subsets. Explicitly pediatric or fetal FDA-listed devices are reported separately in Table 4.

**Fig. 6 Citation impact and validation.** Strongest validation strategy reported by all included studies and by the most-cited decile, the decile being defined on citation impact normalized to the average article of the same field and year. Percentages are within each group.
