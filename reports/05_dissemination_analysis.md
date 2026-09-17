# Supplementary dissemination analysis

Offline analysis of archived source snapshots, September 16, 2026. These descriptive searches are separate from the 3,496 included primary-study records. No source totals are pooled or interpreted as unique studies, adoption, or clinical benefit.

## Source inventory

| File | Recorded collection date | SHA-256 |
|:--|:--|:--|
| `data/processed/pubmed_yearly_counts.json` | See companion pubmed_summary (2026-09-07) | `7ec7d4654694424f1d5672d326071ee10f735447bb9c62e3730e7bdeaba8ff19` |
| `data/processed/pubmed_summary.json` | 2026-09-07 | `1e9df03a774b4a41d67f32a00a9c2749799ae686990465f8496a86965c5905fa` |
| `data/processed/preprint_counts.json` | 2026-09-16 | `521752df935916a91c3b1b2c0a943740c7bd4338dccf9e21bce96753ed85714e` |
| `data/processed/journal_impact.json` | Not recorded; archived snapshot analyzed 2026-09-16 | `268f7c12ca82b0ce5ef7b4f537f455d518797d720b0955b52a655713083807b1` |
| `data/processed/conference_works.json` | Not recorded; archived snapshot analyzed 2026-09-16 | `baa436e0a2a1c8374a9a9744c7297673754cb1211d823cd32fc4b037888bfd3a` |
| `data/processed/newsletter_summary.json` | 2026-09-09 | `ccbef244a24370aa2ab70d1fec9dd231d1c384c788804468d469df1b657ef65f` |

Collection dates describe metadata, not necessarily the dates of every cached API response. The screened cohort retains its September 9 search cutoff. The current collector rules and source URLs are frozen in `data/processed/review_context_manifest.json`; rule snapshots are not evidence that all historical retrievals used identical code.

## Table D1. Publication-source counts

| Year | PubMed, all ages | PubMed, pediatric | arXiv, all ages | arXiv, pediatric | medRxiv, all ages | medRxiv, pediatric |
|--:|--:|--:|--:|--:|--:|--:|
| 2008 | 715 | 58 | 11 | 0 | 0 | 0 |
| 2009 | 723 | 58 | 18 | 0 | 0 | 0 |
| 2010 | 557 | 48 | 28 | 0 | 0 | 0 |
| 2011 | 492 | 62 | 39 | 1 | 0 | 0 |
| 2012 | 569 | 63 | 61 | 0 | 0 | 0 |
| 2013 | 680 | 72 | 76 | 0 | 0 | 0 |
| 2014 | 769 | 113 | 97 | 2 | 0 | 0 |
| 2015 | 873 | 134 | 135 | 1 | 0 | 0 |
| 2016 | 1045 | 155 | 247 | 0 | 0 | 0 |
| 2017 | 1556 | 203 | 514 | 13 | 0 | 0 |
| 2018 | 2632 | 340 | 972 | 16 | 0 | 0 |
| 2019 | 4342 | 515 | 1424 | 32 | 16 | 3 |
| 2020 | 6928 | 682 | 2110 | 37 | 215 | 4 |
| 2021 | 10174 | 947 | 2101 | 35 | 162 | 12 |
| 2022 | 12469 | 1038 | 2361 | 49 | 154 | 9 |
| 2023 | 13901 | 1227 | 3017 | 46 | 187 | 11 |
| 2024 | 16222 | 1695 | 3736 | 84 | 293 | 26 |
| 2025 | 20831 | 2348 | 4426 | 104 | 351 | 26 |
| 2026 YTD | 16481 | 1897 | 3198 | 59 | 287 | 26 |

PubMed includes multiple publication types and is not a journal-only primary-study cohort. Preprints can overlap PubMed and later journal versions; sources have not been linked at record level. medRxiv counts before 2019 are structural zeros and are not plotted. Approximate translated queries have different field and indexing behavior.

## Table D2. Twelve highest-output journals in the separate search

| Journal | 2015–2025 | 2026 YTD | Total |
|:--|--:|--:|--:|
| Pediatric Radiology | 141 | 55 | 196 |
| Scientific Reports | 128 | 27 | 155 |
| European Radiology | 76 | 24 | 100 |
| NeuroImage | 83 | 6 | 89 |
| Diagnostics | 67 | 19 | 86 |
| Medical Image Analysis | 70 | 6 | 76 |
| Journal of Imaging Informatics in Medicine | 46 | 20 | 66 |
| Frontiers in Pediatrics | 46 | 14 | 60 |
| IEEE Journal of Biomedical and Health Informatics | 46 | 8 | 54 |
| PLoS ONE | 49 | 5 | 54 |
| Computers in Biology and Medicine | 49 | 2 | 51 |
| Frontiers in Neuroscience | 44 | 6 | 50 |

The underlying source inventory contains 5,099 records across 1,061 source labels, including a small number of proceedings/preprint labels. The displayed twelve are journals and account for 1,037 records. Journal aliases already matched to the same OpenAlex source were merged by the collector. No citedness threshold was used for this figure.

## Table D3. Conference title matches

| Venue | Year | Retrieved accepted titles | Radiology-AI matches | Pediatric matches |
|:--|--:|--:|--:|--:|
| MICCAI | 2023 | 733 | 236 | 8 |
| MICCAI | 2024 | 856 | 298 | 8 |
| MICCAI | 2025 | 1027 | 320 | 10 |
| MICCAI | 2026 | NA | NA | NA |
| MIDL | 2023 | 112 | 47 | 1 |
| MIDL | 2024 | 117 | 39 | 1 |
| MIDL | 2025 | 109 | 40 | 2 |
| MIDL | 2026 | 221 | 74 | 5 |
| CVPR | 2023 | 2353 | 18 | 0 |
| CVPR | 2024 | 2716 | 35 | 1 |
| CVPR | 2025 | 2871 | 42 | 0 |
| CVPR | 2026 | 4042 | 59 | 0 |
| NeurIPS | 2023 | 3584 | 12 | 0 |
| NeurIPS | 2024 | 4538 | 17 | 0 |
| NeurIPS | 2025 | 5858 | 29 | 0 |
| NeurIPS | 2026 | NA | NA | NA |
| ICLR | 2023 | 1584 | 6 | 0 |
| ICLR | 2024 | 2296 | 3 | 0 |
| ICLR | 2025 | 3830 | 7 | 0 |
| ICLR | 2026 | 5468 | 26 | 1 |
| ICML | 2023 | 1865 | 2 | 0 |
| ICML | 2024 | 2634 | 3 | 0 |
| ICML | 2025 | 3339 | 7 | 0 |
| ICML | 2026 | 6646 | 15 | 0 |

Counts use the meetings' own accepted-paper lists, not the older DBLP samples or the citation-ranked Semantic Scholar example tables. A title must match medical, imaging, and AI terms and avoid excluded domains; the pediatric subset additionally matches pediatric terms. Missing lists are NA, not zero. Proceedings remain excluded from the primary review cohort. RSNA/SPR journal proxies are omitted from this conference analysis.

## Table D4. News archive coverage and pediatric story matches

| Source | Retrieved date range | 2023 | 2024 | 2025 | 2026 YTD |
|:--|:--|--:|--:|--:|--:|
| The Imaging Wire | 2018-03-22 to 2026-09-02 | 17 | 19 | 17 | 9 |
| RSNA News | 2014-01-01 to 2026-09-01 | 3 | 2 | 2 | 2 |
| TLDR AI | 2024-01-02 to 2026-09-09 | NA | 0 | 1 | 0 |
| TLDR Tech | 2024-01-02 to 2026-09-09 | NA | 0 | 0 | 0 |
| Signify Research | 2017-05-16 to 2026-08-10 | 1 | 0 | 0 | 0 |
| ESR / ECR | 2019-02-14 to 2026-08-31 | 2 | 4 | 2 | 2 |
| Radiology Business | 2026-08-11 to 2026-09-09 | NA | NA | NA | 0 |

These are automated story matches, not adjudicated pediatric-AI stories or unique research events. Archive depth, source selection, sponsor text, and repeated coverage prevent comparisons of popularity or market share. Blocked sources: AuntMinnie; Diagnostic Imaging; Health Imaging; RSNA AI newsletter / journal e-alerts.

## Queries and collector provenance

### Journal search stored with the source snapshot

```text
(radiology[tiab] OR radiological[tiab] OR radiograph*[tiab] OR "medical imaging"[tiab] OR tomography[tiab] OR "magnetic resonance"[tiab] OR MRI[tiab] OR "computed tomography"[tiab] OR CT[tiab] OR ultrasound[tiab] OR ultrasonograph*[tiab] OR sonograph*[tiab] OR mammograph*[tiab] OR "chest x-ray"[tiab]) AND ("artificial intelligence"[tiab] OR "machine learning"[tiab] OR "deep learning"[tiab] OR "convolutional neural network"[tiab] OR "convolutional neural networks"[tiab] OR "neural network"[tiab] OR "neural networks"[tiab] OR "computer-aided diagnosis"[tiab] OR radiomics[tiab] OR "computer vision"[tiab]) AND (pediatric*[tiab] OR paediatric*[tiab] OR child*[tiab] OR infant*[tiab] OR neonat*[tiab] OR adolescen*[tiab] OR fetal[tiab] OR foetal[tiab] OR newborn*[tiab] OR preterm[tiab] OR "children's hospital"[tiab]) NOT ("Retracted Publication"[pt] OR "Retraction of Publication"[pt])
```

### Broad publication queries and preprint translations

The following reproduce the current collector definitions used for the contextual count analysis; the annual aggregate JSON does not retain individual query responses. PubMed uses annual [pdat] restrictions; arXiv uses submittedDate and medRxiv uses PUB_YEAR through Europe PMC. These are distinct from the review eligibility search.

**all_radiology**

```text
PubMed: (((radiology OR radiological OR radiograph* OR "medical imaging" OR "diagnostic imaging"[tiab] OR "tomography, x-ray computed"[MeSH Terms] OR "tomography, emission-computed"[MeSH Terms] OR tomograph*[tiab] OR "magnetic resonance" OR MRI OR "computed tomography" OR CT[tiab] OR ultrasound[tiab] OR ultrasonograph*[tiab] OR sonograph*[tiab] OR echocardiograph*[tiab] OR "ultrasonography"[MeSH Terms] OR mammograph* OR "chest x-ray") NOT ("optical coherence"[tiab] OR fundus[tiab] OR retina*[tiab] OR dental[tiab] OR histopatholog*[tiab] OR "whole slide"[tiab] OR dermoscop*[tiab] OR endoscop*[tiab] OR colonoscop*[tiab] OR microscop*[tiab]))) AND YYYY:YYYY[pdat]
arXiv: (((all:radiology OR all:radiological OR (all:radiograph OR all:radiographs OR all:radiographic OR all:radiography) OR all:"medical imaging" OR all:"diagnostic imaging" OR all:"computed tomography" OR all:"emission tomography" OR (all:tomography OR all:tomographic) OR all:"magnetic resonance" OR all:MRI OR all:"computed tomography" OR all:CT OR all:ultrasound OR (all:ultrasonography OR all:ultrasonographic) OR (all:sonography OR all:sonographic) OR (all:echocardiography OR all:echocardiographic) OR all:ultrasonography OR (all:mammography OR all:mammographic OR all:mammogram OR all:mammograms) OR all:"chest x-ray") ANDNOT (all:"optical coherence" OR all:fundus OR (all:retina OR all:retinal) OR all:dental OR (all:histopathology OR all:histopathological OR all:histopathologic) OR all:"whole slide" OR (all:dermoscopy OR all:dermoscopic) OR (all:endoscopy OR all:endoscopic) OR (all:colonoscopy OR all:colonoscopic) OR (all:microscopy OR all:microscopic)))) AND submittedDate:[YYYY01010000 TO YYYY12312359]
medRxiv / Europe PMC: SRC:PPR AND PUBLISHER:"medRxiv" AND ((((TITLE:radiology OR ABSTRACT:radiology) OR (TITLE:radiological OR ABSTRACT:radiological) OR ((TITLE:radiograph OR ABSTRACT:radiograph) OR (TITLE:radiographs OR ABSTRACT:radiographs) OR (TITLE:radiographic OR ABSTRACT:radiographic) OR (TITLE:radiography OR ABSTRACT:radiography)) OR (TITLE:"medical imaging" OR ABSTRACT:"medical imaging") OR (TITLE:"diagnostic imaging" OR ABSTRACT:"diagnostic imaging") OR (TITLE:"computed tomography" OR ABSTRACT:"computed tomography") OR (TITLE:"emission tomography" OR ABSTRACT:"emission tomography") OR ((TITLE:tomography OR ABSTRACT:tomography) OR (TITLE:tomographic OR ABSTRACT:tomographic)) OR (TITLE:"magnetic resonance" OR ABSTRACT:"magnetic resonance") OR (TITLE:MRI OR ABSTRACT:MRI) OR (TITLE:"computed tomography" OR ABSTRACT:"computed tomography") OR (TITLE:CT OR ABSTRACT:CT) OR (TITLE:ultrasound OR ABSTRACT:ultrasound) OR ((TITLE:ultrasonography OR ABSTRACT:ultrasonography) OR (TITLE:ultrasonographic OR ABSTRACT:ultrasonographic)) OR ((TITLE:sonography OR ABSTRACT:sonography) OR (TITLE:sonographic OR ABSTRACT:sonographic)) OR ((TITLE:echocardiography OR ABSTRACT:echocardiography) OR (TITLE:echocardiographic OR ABSTRACT:echocardiographic)) OR (TITLE:ultrasonography OR ABSTRACT:ultrasonography) OR ((TITLE:mammography OR ABSTRACT:mammography) OR (TITLE:mammographic OR ABSTRACT:mammographic) OR (TITLE:mammogram OR ABSTRACT:mammogram) OR (TITLE:mammograms OR ABSTRACT:mammograms)) OR (TITLE:"chest x-ray" OR ABSTRACT:"chest x-ray")) NOT ((TITLE:"optical coherence" OR ABSTRACT:"optical coherence") OR (TITLE:fundus OR ABSTRACT:fundus) OR ((TITLE:retina OR ABSTRACT:retina) OR (TITLE:retinal OR ABSTRACT:retinal)) OR (TITLE:dental OR ABSTRACT:dental) OR ((TITLE:histopathology OR ABSTRACT:histopathology) OR (TITLE:histopathological OR ABSTRACT:histopathological) OR (TITLE:histopathologic OR ABSTRACT:histopathologic)) OR (TITLE:"whole slide" OR ABSTRACT:"whole slide") OR ((TITLE:dermoscopy OR ABSTRACT:dermoscopy) OR (TITLE:dermoscopic OR ABSTRACT:dermoscopic)) OR ((TITLE:endoscopy OR ABSTRACT:endoscopy) OR (TITLE:endoscopic OR ABSTRACT:endoscopic)) OR ((TITLE:colonoscopy OR ABSTRACT:colonoscopy) OR (TITLE:colonoscopic OR ABSTRACT:colonoscopic)) OR ((TITLE:microscopy OR ABSTRACT:microscopy) OR (TITLE:microscopic OR ABSTRACT:microscopic))))) AND PUB_YEAR:[YYYY TO YYYY]
```

**pediatric_radiology**

```text
PubMed: (((radiology OR radiological OR radiograph* OR "medical imaging" OR "diagnostic imaging"[tiab] OR "tomography, x-ray computed"[MeSH Terms] OR "tomography, emission-computed"[MeSH Terms] OR tomograph*[tiab] OR "magnetic resonance" OR MRI OR "computed tomography" OR CT[tiab] OR ultrasound[tiab] OR ultrasonograph*[tiab] OR sonograph*[tiab] OR echocardiograph*[tiab] OR "ultrasonography"[MeSH Terms] OR mammograph* OR "chest x-ray") NOT ("optical coherence"[tiab] OR fundus[tiab] OR retina*[tiab] OR dental[tiab] OR histopatholog*[tiab] OR "whole slide"[tiab] OR dermoscop*[tiab] OR endoscop*[tiab] OR colonoscop*[tiab] OR microscop*[tiab])) AND (pediatric* OR paediatric* OR child* OR infant* OR neonat* OR adolescen* OR "children's hospital")) AND YYYY:YYYY[pdat]
arXiv: (((all:radiology OR all:radiological OR (all:radiograph OR all:radiographs OR all:radiographic OR all:radiography) OR all:"medical imaging" OR all:"diagnostic imaging" OR all:"computed tomography" OR all:"emission tomography" OR (all:tomography OR all:tomographic) OR all:"magnetic resonance" OR all:MRI OR all:"computed tomography" OR all:CT OR all:ultrasound OR (all:ultrasonography OR all:ultrasonographic) OR (all:sonography OR all:sonographic) OR (all:echocardiography OR all:echocardiographic) OR all:ultrasonography OR (all:mammography OR all:mammographic OR all:mammogram OR all:mammograms) OR all:"chest x-ray") ANDNOT (all:"optical coherence" OR all:fundus OR (all:retina OR all:retinal) OR all:dental OR (all:histopathology OR all:histopathological OR all:histopathologic) OR all:"whole slide" OR (all:dermoscopy OR all:dermoscopic) OR (all:endoscopy OR all:endoscopic) OR (all:colonoscopy OR all:colonoscopic) OR (all:microscopy OR all:microscopic))) AND ((all:pediatric OR all:pediatrics) OR (all:paediatric OR all:paediatrics) OR (all:child OR all:children OR all:childhood) OR (all:infant OR all:infants OR all:infancy) OR (all:neonatal OR all:neonate OR all:neonates OR all:neonatology) OR (all:adolescent OR all:adolescents OR all:adolescence) OR all:"children's hospital")) AND submittedDate:[YYYY01010000 TO YYYY12312359]
medRxiv / Europe PMC: SRC:PPR AND PUBLISHER:"medRxiv" AND ((((TITLE:radiology OR ABSTRACT:radiology) OR (TITLE:radiological OR ABSTRACT:radiological) OR ((TITLE:radiograph OR ABSTRACT:radiograph) OR (TITLE:radiographs OR ABSTRACT:radiographs) OR (TITLE:radiographic OR ABSTRACT:radiographic) OR (TITLE:radiography OR ABSTRACT:radiography)) OR (TITLE:"medical imaging" OR ABSTRACT:"medical imaging") OR (TITLE:"diagnostic imaging" OR ABSTRACT:"diagnostic imaging") OR (TITLE:"computed tomography" OR ABSTRACT:"computed tomography") OR (TITLE:"emission tomography" OR ABSTRACT:"emission tomography") OR ((TITLE:tomography OR ABSTRACT:tomography) OR (TITLE:tomographic OR ABSTRACT:tomographic)) OR (TITLE:"magnetic resonance" OR ABSTRACT:"magnetic resonance") OR (TITLE:MRI OR ABSTRACT:MRI) OR (TITLE:"computed tomography" OR ABSTRACT:"computed tomography") OR (TITLE:CT OR ABSTRACT:CT) OR (TITLE:ultrasound OR ABSTRACT:ultrasound) OR ((TITLE:ultrasonography OR ABSTRACT:ultrasonography) OR (TITLE:ultrasonographic OR ABSTRACT:ultrasonographic)) OR ((TITLE:sonography OR ABSTRACT:sonography) OR (TITLE:sonographic OR ABSTRACT:sonographic)) OR ((TITLE:echocardiography OR ABSTRACT:echocardiography) OR (TITLE:echocardiographic OR ABSTRACT:echocardiographic)) OR (TITLE:ultrasonography OR ABSTRACT:ultrasonography) OR ((TITLE:mammography OR ABSTRACT:mammography) OR (TITLE:mammographic OR ABSTRACT:mammographic) OR (TITLE:mammogram OR ABSTRACT:mammogram) OR (TITLE:mammograms OR ABSTRACT:mammograms)) OR (TITLE:"chest x-ray" OR ABSTRACT:"chest x-ray")) NOT ((TITLE:"optical coherence" OR ABSTRACT:"optical coherence") OR (TITLE:fundus OR ABSTRACT:fundus) OR ((TITLE:retina OR ABSTRACT:retina) OR (TITLE:retinal OR ABSTRACT:retinal)) OR (TITLE:dental OR ABSTRACT:dental) OR ((TITLE:histopathology OR ABSTRACT:histopathology) OR (TITLE:histopathological OR ABSTRACT:histopathological) OR (TITLE:histopathologic OR ABSTRACT:histopathologic)) OR (TITLE:"whole slide" OR ABSTRACT:"whole slide") OR ((TITLE:dermoscopy OR ABSTRACT:dermoscopy) OR (TITLE:dermoscopic OR ABSTRACT:dermoscopic)) OR ((TITLE:endoscopy OR ABSTRACT:endoscopy) OR (TITLE:endoscopic OR ABSTRACT:endoscopic)) OR ((TITLE:colonoscopy OR ABSTRACT:colonoscopy) OR (TITLE:colonoscopic OR ABSTRACT:colonoscopic)) OR ((TITLE:microscopy OR ABSTRACT:microscopy) OR (TITLE:microscopic OR ABSTRACT:microscopic)))) AND (((TITLE:pediatric OR ABSTRACT:pediatric) OR (TITLE:pediatrics OR ABSTRACT:pediatrics)) OR ((TITLE:paediatric OR ABSTRACT:paediatric) OR (TITLE:paediatrics OR ABSTRACT:paediatrics)) OR ((TITLE:child OR ABSTRACT:child) OR (TITLE:children OR ABSTRACT:children) OR (TITLE:childhood OR ABSTRACT:childhood)) OR ((TITLE:infant OR ABSTRACT:infant) OR (TITLE:infants OR ABSTRACT:infants) OR (TITLE:infancy OR ABSTRACT:infancy)) OR ((TITLE:neonatal OR ABSTRACT:neonatal) OR (TITLE:neonate OR ABSTRACT:neonate) OR (TITLE:neonates OR ABSTRACT:neonates) OR (TITLE:neonatology OR ABSTRACT:neonatology)) OR ((TITLE:adolescent OR ABSTRACT:adolescent) OR (TITLE:adolescents OR ABSTRACT:adolescents) OR (TITLE:adolescence OR ABSTRACT:adolescence)) OR (TITLE:"children's hospital" OR ABSTRACT:"children's hospital"))) AND PUB_YEAR:[YYYY TO YYYY]
```

**radiology_ai**

```text
PubMed: (((radiology OR radiological OR radiograph* OR "medical imaging" OR "diagnostic imaging"[tiab] OR "tomography, x-ray computed"[MeSH Terms] OR "tomography, emission-computed"[MeSH Terms] OR tomograph*[tiab] OR "magnetic resonance" OR MRI OR "computed tomography" OR CT[tiab] OR ultrasound[tiab] OR ultrasonograph*[tiab] OR sonograph*[tiab] OR echocardiograph*[tiab] OR "ultrasonography"[MeSH Terms] OR mammograph* OR "chest x-ray") NOT ("optical coherence"[tiab] OR fundus[tiab] OR retina*[tiab] OR dental[tiab] OR histopatholog*[tiab] OR "whole slide"[tiab] OR dermoscop*[tiab] OR endoscop*[tiab] OR colonoscop*[tiab] OR microscop*[tiab])) AND ("artificial intelligence" OR "machine learning" OR "deep learning" OR "convolutional neural network" OR "neural network" OR "computer-aided diagnosis" OR radiomics OR "computer vision")) AND YYYY:YYYY[pdat]
arXiv: (((all:radiology OR all:radiological OR (all:radiograph OR all:radiographs OR all:radiographic OR all:radiography) OR all:"medical imaging" OR all:"diagnostic imaging" OR all:"computed tomography" OR all:"emission tomography" OR (all:tomography OR all:tomographic) OR all:"magnetic resonance" OR all:MRI OR all:"computed tomography" OR all:CT OR all:ultrasound OR (all:ultrasonography OR all:ultrasonographic) OR (all:sonography OR all:sonographic) OR (all:echocardiography OR all:echocardiographic) OR all:ultrasonography OR (all:mammography OR all:mammographic OR all:mammogram OR all:mammograms) OR all:"chest x-ray") ANDNOT (all:"optical coherence" OR all:fundus OR (all:retina OR all:retinal) OR all:dental OR (all:histopathology OR all:histopathological OR all:histopathologic) OR all:"whole slide" OR (all:dermoscopy OR all:dermoscopic) OR (all:endoscopy OR all:endoscopic) OR (all:colonoscopy OR all:colonoscopic) OR (all:microscopy OR all:microscopic))) AND (all:"artificial intelligence" OR all:"machine learning" OR all:"deep learning" OR all:"convolutional neural network" OR all:"neural network" OR all:"computer-aided diagnosis" OR all:radiomics OR all:"computer vision")) AND submittedDate:[YYYY01010000 TO YYYY12312359]
medRxiv / Europe PMC: SRC:PPR AND PUBLISHER:"medRxiv" AND ((((TITLE:radiology OR ABSTRACT:radiology) OR (TITLE:radiological OR ABSTRACT:radiological) OR ((TITLE:radiograph OR ABSTRACT:radiograph) OR (TITLE:radiographs OR ABSTRACT:radiographs) OR (TITLE:radiographic OR ABSTRACT:radiographic) OR (TITLE:radiography OR ABSTRACT:radiography)) OR (TITLE:"medical imaging" OR ABSTRACT:"medical imaging") OR (TITLE:"diagnostic imaging" OR ABSTRACT:"diagnostic imaging") OR (TITLE:"computed tomography" OR ABSTRACT:"computed tomography") OR (TITLE:"emission tomography" OR ABSTRACT:"emission tomography") OR ((TITLE:tomography OR ABSTRACT:tomography) OR (TITLE:tomographic OR ABSTRACT:tomographic)) OR (TITLE:"magnetic resonance" OR ABSTRACT:"magnetic resonance") OR (TITLE:MRI OR ABSTRACT:MRI) OR (TITLE:"computed tomography" OR ABSTRACT:"computed tomography") OR (TITLE:CT OR ABSTRACT:CT) OR (TITLE:ultrasound OR ABSTRACT:ultrasound) OR ((TITLE:ultrasonography OR ABSTRACT:ultrasonography) OR (TITLE:ultrasonographic OR ABSTRACT:ultrasonographic)) OR ((TITLE:sonography OR ABSTRACT:sonography) OR (TITLE:sonographic OR ABSTRACT:sonographic)) OR ((TITLE:echocardiography OR ABSTRACT:echocardiography) OR (TITLE:echocardiographic OR ABSTRACT:echocardiographic)) OR (TITLE:ultrasonography OR ABSTRACT:ultrasonography) OR ((TITLE:mammography OR ABSTRACT:mammography) OR (TITLE:mammographic OR ABSTRACT:mammographic) OR (TITLE:mammogram OR ABSTRACT:mammogram) OR (TITLE:mammograms OR ABSTRACT:mammograms)) OR (TITLE:"chest x-ray" OR ABSTRACT:"chest x-ray")) NOT ((TITLE:"optical coherence" OR ABSTRACT:"optical coherence") OR (TITLE:fundus OR ABSTRACT:fundus) OR ((TITLE:retina OR ABSTRACT:retina) OR (TITLE:retinal OR ABSTRACT:retinal)) OR (TITLE:dental OR ABSTRACT:dental) OR ((TITLE:histopathology OR ABSTRACT:histopathology) OR (TITLE:histopathological OR ABSTRACT:histopathological) OR (TITLE:histopathologic OR ABSTRACT:histopathologic)) OR (TITLE:"whole slide" OR ABSTRACT:"whole slide") OR ((TITLE:dermoscopy OR ABSTRACT:dermoscopy) OR (TITLE:dermoscopic OR ABSTRACT:dermoscopic)) OR ((TITLE:endoscopy OR ABSTRACT:endoscopy) OR (TITLE:endoscopic OR ABSTRACT:endoscopic)) OR ((TITLE:colonoscopy OR ABSTRACT:colonoscopy) OR (TITLE:colonoscopic OR ABSTRACT:colonoscopic)) OR ((TITLE:microscopy OR ABSTRACT:microscopy) OR (TITLE:microscopic OR ABSTRACT:microscopic)))) AND ((TITLE:"artificial intelligence" OR ABSTRACT:"artificial intelligence") OR (TITLE:"machine learning" OR ABSTRACT:"machine learning") OR (TITLE:"deep learning" OR ABSTRACT:"deep learning") OR (TITLE:"convolutional neural network" OR ABSTRACT:"convolutional neural network") OR (TITLE:"neural network" OR ABSTRACT:"neural network") OR (TITLE:"computer-aided diagnosis" OR ABSTRACT:"computer-aided diagnosis") OR (TITLE:radiomics OR ABSTRACT:radiomics) OR (TITLE:"computer vision" OR ABSTRACT:"computer vision"))) AND PUB_YEAR:[YYYY TO YYYY]
```

**pediatric_radiology_ai**

```text
PubMed: (((radiology OR radiological OR radiograph* OR "medical imaging" OR "diagnostic imaging"[tiab] OR "tomography, x-ray computed"[MeSH Terms] OR "tomography, emission-computed"[MeSH Terms] OR tomograph*[tiab] OR "magnetic resonance" OR MRI OR "computed tomography" OR CT[tiab] OR ultrasound[tiab] OR ultrasonograph*[tiab] OR sonograph*[tiab] OR echocardiograph*[tiab] OR "ultrasonography"[MeSH Terms] OR mammograph* OR "chest x-ray") NOT ("optical coherence"[tiab] OR fundus[tiab] OR retina*[tiab] OR dental[tiab] OR histopatholog*[tiab] OR "whole slide"[tiab] OR dermoscop*[tiab] OR endoscop*[tiab] OR colonoscop*[tiab] OR microscop*[tiab])) AND ("artificial intelligence" OR "machine learning" OR "deep learning" OR "convolutional neural network" OR "neural network" OR "computer-aided diagnosis" OR radiomics OR "computer vision") AND (pediatric* OR paediatric* OR child* OR infant* OR neonat* OR adolescen* OR "children's hospital")) AND YYYY:YYYY[pdat]
arXiv: (((all:radiology OR all:radiological OR (all:radiograph OR all:radiographs OR all:radiographic OR all:radiography) OR all:"medical imaging" OR all:"diagnostic imaging" OR all:"computed tomography" OR all:"emission tomography" OR (all:tomography OR all:tomographic) OR all:"magnetic resonance" OR all:MRI OR all:"computed tomography" OR all:CT OR all:ultrasound OR (all:ultrasonography OR all:ultrasonographic) OR (all:sonography OR all:sonographic) OR (all:echocardiography OR all:echocardiographic) OR all:ultrasonography OR (all:mammography OR all:mammographic OR all:mammogram OR all:mammograms) OR all:"chest x-ray") ANDNOT (all:"optical coherence" OR all:fundus OR (all:retina OR all:retinal) OR all:dental OR (all:histopathology OR all:histopathological OR all:histopathologic) OR all:"whole slide" OR (all:dermoscopy OR all:dermoscopic) OR (all:endoscopy OR all:endoscopic) OR (all:colonoscopy OR all:colonoscopic) OR (all:microscopy OR all:microscopic))) AND (all:"artificial intelligence" OR all:"machine learning" OR all:"deep learning" OR all:"convolutional neural network" OR all:"neural network" OR all:"computer-aided diagnosis" OR all:radiomics OR all:"computer vision") AND ((all:pediatric OR all:pediatrics) OR (all:paediatric OR all:paediatrics) OR (all:child OR all:children OR all:childhood) OR (all:infant OR all:infants OR all:infancy) OR (all:neonatal OR all:neonate OR all:neonates OR all:neonatology) OR (all:adolescent OR all:adolescents OR all:adolescence) OR all:"children's hospital")) AND submittedDate:[YYYY01010000 TO YYYY12312359]
medRxiv / Europe PMC: SRC:PPR AND PUBLISHER:"medRxiv" AND ((((TITLE:radiology OR ABSTRACT:radiology) OR (TITLE:radiological OR ABSTRACT:radiological) OR ((TITLE:radiograph OR ABSTRACT:radiograph) OR (TITLE:radiographs OR ABSTRACT:radiographs) OR (TITLE:radiographic OR ABSTRACT:radiographic) OR (TITLE:radiography OR ABSTRACT:radiography)) OR (TITLE:"medical imaging" OR ABSTRACT:"medical imaging") OR (TITLE:"diagnostic imaging" OR ABSTRACT:"diagnostic imaging") OR (TITLE:"computed tomography" OR ABSTRACT:"computed tomography") OR (TITLE:"emission tomography" OR ABSTRACT:"emission tomography") OR ((TITLE:tomography OR ABSTRACT:tomography) OR (TITLE:tomographic OR ABSTRACT:tomographic)) OR (TITLE:"magnetic resonance" OR ABSTRACT:"magnetic resonance") OR (TITLE:MRI OR ABSTRACT:MRI) OR (TITLE:"computed tomography" OR ABSTRACT:"computed tomography") OR (TITLE:CT OR ABSTRACT:CT) OR (TITLE:ultrasound OR ABSTRACT:ultrasound) OR ((TITLE:ultrasonography OR ABSTRACT:ultrasonography) OR (TITLE:ultrasonographic OR ABSTRACT:ultrasonographic)) OR ((TITLE:sonography OR ABSTRACT:sonography) OR (TITLE:sonographic OR ABSTRACT:sonographic)) OR ((TITLE:echocardiography OR ABSTRACT:echocardiography) OR (TITLE:echocardiographic OR ABSTRACT:echocardiographic)) OR (TITLE:ultrasonography OR ABSTRACT:ultrasonography) OR ((TITLE:mammography OR ABSTRACT:mammography) OR (TITLE:mammographic OR ABSTRACT:mammographic) OR (TITLE:mammogram OR ABSTRACT:mammogram) OR (TITLE:mammograms OR ABSTRACT:mammograms)) OR (TITLE:"chest x-ray" OR ABSTRACT:"chest x-ray")) NOT ((TITLE:"optical coherence" OR ABSTRACT:"optical coherence") OR (TITLE:fundus OR ABSTRACT:fundus) OR ((TITLE:retina OR ABSTRACT:retina) OR (TITLE:retinal OR ABSTRACT:retinal)) OR (TITLE:dental OR ABSTRACT:dental) OR ((TITLE:histopathology OR ABSTRACT:histopathology) OR (TITLE:histopathological OR ABSTRACT:histopathological) OR (TITLE:histopathologic OR ABSTRACT:histopathologic)) OR (TITLE:"whole slide" OR ABSTRACT:"whole slide") OR ((TITLE:dermoscopy OR ABSTRACT:dermoscopy) OR (TITLE:dermoscopic OR ABSTRACT:dermoscopic)) OR ((TITLE:endoscopy OR ABSTRACT:endoscopy) OR (TITLE:endoscopic OR ABSTRACT:endoscopic)) OR ((TITLE:colonoscopy OR ABSTRACT:colonoscopy) OR (TITLE:colonoscopic OR ABSTRACT:colonoscopic)) OR ((TITLE:microscopy OR ABSTRACT:microscopy) OR (TITLE:microscopic OR ABSTRACT:microscopic)))) AND ((TITLE:"artificial intelligence" OR ABSTRACT:"artificial intelligence") OR (TITLE:"machine learning" OR ABSTRACT:"machine learning") OR (TITLE:"deep learning" OR ABSTRACT:"deep learning") OR (TITLE:"convolutional neural network" OR ABSTRACT:"convolutional neural network") OR (TITLE:"neural network" OR ABSTRACT:"neural network") OR (TITLE:"computer-aided diagnosis" OR ABSTRACT:"computer-aided diagnosis") OR (TITLE:radiomics OR ABSTRACT:radiomics) OR (TITLE:"computer vision" OR ABSTRACT:"computer vision")) AND (((TITLE:pediatric OR ABSTRACT:pediatric) OR (TITLE:pediatrics OR ABSTRACT:pediatrics)) OR ((TITLE:paediatric OR ABSTRACT:paediatric) OR (TITLE:paediatrics OR ABSTRACT:paediatrics)) OR ((TITLE:child OR ABSTRACT:child) OR (TITLE:children OR ABSTRACT:children) OR (TITLE:childhood OR ABSTRACT:childhood)) OR ((TITLE:infant OR ABSTRACT:infant) OR (TITLE:infants OR ABSTRACT:infants) OR (TITLE:infancy OR ABSTRACT:infancy)) OR ((TITLE:neonatal OR ABSTRACT:neonatal) OR (TITLE:neonate OR ABSTRACT:neonate) OR (TITLE:neonates OR ABSTRACT:neonates) OR (TITLE:neonatology OR ABSTRACT:neonatology)) OR ((TITLE:adolescent OR ABSTRACT:adolescent) OR (TITLE:adolescents OR ABSTRACT:adolescents) OR (TITLE:adolescence OR ABSTRACT:adolescence)) OR (TITLE:"children's hospital" OR ABSTRACT:"children's hospital"))) AND PUB_YEAR:[YYYY TO YYYY]
```

### Classification rules and conference source URLs

```json
{
  "rules": {
    "PAPER_MEDICAL_SIGNAL": [
      "radiology",
      "radiological",
      "radiograph",
      "radiographs",
      "x-ray",
      "xray",
      "chest x-ray",
      "mri",
      "magnetic resonance",
      "ct scan",
      "ultrasound",
      "mammography",
      "mammographic",
      "tomography",
      "radiomics",
      "lesion",
      "tumor",
      "tumour",
      "nodule",
      "medical image",
      "medical imaging",
      "clinical imaging",
      "pathology image",
      "histopathology",
      "ct",
      "mri",
      "imaging",
      "radiograph",
      "tumor",
      "tumour",
      "lesion",
      "nodule",
      "cancer",
      "disease",
      "diagnosis",
      "diagnostic",
      "medical",
      "clinical",
      "biomedical",
      "segment",
      "radiomics",
      "pneumonia",
      "fracture",
      "bone age",
      "covid",
      "chest",
      "u-net",
      "unet",
      "nnu-net",
      "brain",
      "cardiac",
      "abdominal",
      "anatomic",
      "anatomical",
      "pulmonary",
      "fetal",
      "fmri",
      "echocardiography",
      "ultrasound",
      "x-ray",
      "pet"
    ],
    "PAPER_AI_SIGNAL": [
      "deep learning",
      "neural network",
      "convolutional",
      "machine learning",
      "transformer",
      "self-supervised",
      "segmentation",
      "classification",
      "diffusion model",
      "foundation model",
      "representation learning",
      "generative",
      "attention",
      "learning",
      "artificial intelligence",
      "ai",
      "ai-based",
      "ai-assisted",
      "model",
      "models",
      "network",
      "networks",
      "automated",
      "automatic",
      "algorithm",
      "algorithms",
      "segment",
      "detection",
      "prediction",
      "predicting",
      "radiomics",
      "radiomic",
      "reconstruction",
      "u-net",
      "unet",
      "nnu-net",
      "gpt",
      "chatgpt",
      "language model",
      "language models",
      "computer-aided",
      "computer aided",
      "vision-language",
      "vision language",
      "foundation model",
      "diffusion",
      "mamba",
      "large-scale",
      "benchmark",
      "dataset",
      "challenge",
      "synthesis",
      "denoising",
      "super-resolution",
      "registration",
      "classification",
      "quantification",
      "estimation",
      "software",
      "computational",
      "computer vision"
    ],
    "PAPER_IMAGING_SIGNAL": [
      "radiology",
      "radiological",
      "radiologist",
      "radiologists",
      "mri",
      "mr",
      "magnetic resonance",
      "x-ray",
      "x-rays",
      "xray",
      "radiograph",
      "radiographs",
      "radiography",
      "ultrasound",
      "ultrasonography",
      "echocardiography",
      "computed tomography",
      "tomography",
      "ct",
      "cta",
      "pet",
      "pet/ct",
      "spect",
      "mammography",
      "mammogram",
      "mammograms",
      "mammographic",
      "dxa",
      "angiography",
      "fluoroscopy",
      "chest",
      "bone age",
      "fetal",
      "medical image",
      "medical images",
      "medical imaging",
      "medical volumetric",
      "medical segmentation",
      "3d medical",
      "radiotherapy",
      "lesion segmentation",
      "tumor segmentation",
      "tumour segmentation",
      "brain imaging",
      "nodule"
    ],
    "PAPER_PEDIATRIC_SIGNAL": [
      "pediatric",
      "paediatric",
      "child",
      "infant",
      "neonat",
      "adolescent",
      "fetal",
      "foetal",
      "newborn",
      "bone age",
      "bone age",
      "pediatrics",
      "paediatrics",
      "kawasaki",
      "scoliosis",
      "preterm",
      "premature",
      "congenital",
      "young adult"
    ],
    "PAPER_EXCLUDE_DOMAIN": [
      "retinopathy",
      "fundus",
      "ophthalmolog",
      "retinal",
      "dermatolog",
      "skin lesion",
      "skin cancer",
      "histopath",
      "whole slide",
      "whole-slide",
      "microscop",
      "cytolog",
      "genomic",
      "electrocardiogram",
      "endoscop",
      "eeg",
      "electroencephalogra",
      "practice guideline",
      "encephalopathy",
      "wearable",
      "ecg",
      "gaussian splatting",
      "prohibited item",
      "baggage",
      "security screening",
      "dental",
      "tooth",
      "teeth",
      "cbct",
      "maxillofacial",
      "blood cell",
      "omics",
      "big data analytics",
      "wearable sensor",
      "speech",
      "protein",
      "brain decoding",
      "fmri-to-image",
      "connectom",
      "brain activit",
      "brain signals",
      "pathology image",
      "pathology images",
      "clinical text",
      "text summarization"
    ],
    "NEWS_PEDIATRIC_PATTERNS": [
      "p(a)?ediatric",
      "(?<!poster )child(?!-pugh)",
      "infant",
      "neonat",
      "newborn",
      "adolescen",
      "f(o)?etal",
      "fetus",
      "bone age",
      "preterm",
      "\\bnicu\\b",
      "toddler",
      "kids\\b",
      "in utero",
      "prenatal"
    ],
    "NEWS_AI_PATTERNS": [
      "artificial intelligence",
      "\\bai\\b",
      "\\bai-",
      "machine learning",
      "deep learning",
      "neural net",
      "algorithm",
      "large language model",
      "\\bllms?\\b",
      "chatgpt",
      "\\bgpt-",
      "foundation model",
      "computer-aided",
      "radiomics",
      "generative",
      "convolutional",
      "\\bcad\\b"
    ],
    "NEWS_RADIOLOGY_PATTERNS": [
      "radiolog",
      "imaging",
      "x-ray",
      "xray",
      "\\bmri\\b",
      "\\bct\\b",
      "ultrasound",
      "sonograph",
      "mammogra",
      "tomograph",
      "radiograph",
      "\\bpet\\b",
      "\\bpacs\\b",
      "scanner"
    ]
  },
  "conference_sources": {
    "NeurIPS": {
      "kind": "json",
      "url": "https://neurips.cc/static/virtual/data/neurips-{year}-orals-posters.json"
    },
    "ICLR": {
      "kind": "json",
      "url": "https://iclr.cc/static/virtual/data/iclr-{year}-orals-posters.json"
    },
    "ICML": {
      "kind": "json",
      "url": "https://icml.cc/static/virtual/data/icml-{year}-orals-posters.json"
    },
    "CVPR": {
      "kind": "cvf",
      "url": "https://openaccess.thecvf.com/CVPR{year}?day=all"
    },
    "MICCAI": {
      "kind": "miccai",
      "url": "https://papers.miccai.org/miccai-{year}/",
      "urls": {
        "2023": "https://conferences.miccai.org/2023/papers/"
      }
    },
    "MIDL": {
      "kind": "pmlr",
      "urls": {
        "2023": "https://proceedings.mlr.press/v227/",
        "2024": "https://proceedings.mlr.press/v250/",
        "2025": "https://proceedings.mlr.press/v301/",
        "2026": "https://proceedings.mlr.press/v315/"
      }
    }
  }
}
```

Rebuild with `PYTHONPATH=. python scripts/build_review_context.py`. It writes four PNG/PDF figures, this report, and the source manifest without network requests. Rebuilding from refreshed inputs requires editorial review of the manuscript's numbers and snapshot dates.
