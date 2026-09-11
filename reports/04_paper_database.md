# Pediatric radiology AI: paper database

Generated 2026-09-11 from `data/processed/pedrad_paper_db.csv`.

This table is the corpus of the systematic review (`reports/05_review_manuscript.md`): the 3,496 included primary studies, of which 816 name a model or product. It is not a selection of the literature — no citation floor is applied — so every proportion here is a proportion of the review's corpus and can be quoted next to the manuscript without reconciliation.

6,995 records were retrieved and 393 conference proceedings set aside by the publication-form criterion, leaving 6,602 screened. 2,650 were screened out as adult-only, non-radiologic or without an AI component and 456 were in scope but were reviews, editorials or guidelines, which the eligibility criteria exclude. That leaves the 3,496 included primary studies in this table (3,122 from PubMed, 365 from Embase, 9 from OpenAlex).

Every screened record, including the excluded ones and the coded reason each was excluded, stays in `data/processed/pedrad_paper_db.json`; that store, not this table, is what an audit of the screening decisions reads.

Impact is reported five ways because no one measure covers the whole corpus. `citations` is the raw count and can only be compared within a year. `citations/yr` is that count divided by years since publication. `RCR` is iCite's relative citation ratio, where 1.0 is the median NIH-funded paper of the same field and year; it is undefined until a paper is about two years old and is computed for PubMed records only. `fwci` is OpenAlex's field-weighted citation impact, on the same 1.0-is-average scale, computed for anything with a DOI — including the Embase-only records, which have no PMID and therefore no RCR. `impact` is the column to sort on: FWCI where OpenAlex has it, RCR otherwise, blank until the paper has 5 raw citations (below that the ratio is dividing by a fraction of an expected citation and says nothing), with `impact_measure` naming which. 1,669 of 3,496 studies carry one. The top decile of those — 167 studies at or above 14.11x the average paper of their field and year — is the subset the slides name individually; the median included study sits near 2x.

Each row is read from the paper's abstract under a fixed schema, so a field is blank when the abstract does not state it — most notably the release column, which abstracts are usually silent about. Read "unclear" as "the paper does not say", not as "unavailable". Hand corrections in `data/paper_db_overrides.json` take precedence over the extracted value and are flagged in the `overridden_fields` column of the CSV.

## Counts

### Release status

| Status | Papers |
| --- | ---: |
| unclear | 2957 |
| unreleased | 212 |
| open-source | 168 |
| commercial | 159 |

### Modality

| Modality | Papers |
| --- | ---: |
| MRI | 1590 |
| ultrasound | 828 |
| x-ray / radiography | 676 |
| CT | 325 |
| nuclear / PET | 53 |
| other | 45 |
| multiple | 43 |
| fluoroscopy | 13 |

### Task

| Task | Papers |
| --- | ---: |
| detection / diagnosis | 1337 |
| measurement / quantification | 838 |
| outcome prediction | 683 |
| segmentation | 662 |
| reconstruction / imputation | 277 |
| workflow / non-interpretive | 167 |
| other | 123 |
| report generation / LLM | 28 |
| foundation model / vision-language | 26 |
| agent / autonomous | 2 |

### Age group

| Age group | Papers |
| --- | ---: |
| child | 1301 |
| adolescent | 889 |
| fetal | 786 |
| infant | 515 |
| pediatric (unspecified) | 498 |
| neonate | 346 |
| mixed pediatric and adult | 316 |

### Validation

| Strongest validation claimed | Papers |
| --- | ---: |
| internal only | 2352 |
| external / multi-center | 654 |
| reader study | 217 |
| none / not stated | 158 |
| prospective | 115 |

### Papers per year

| Year | Papers |
| --- | ---: |
| 2005 | 2 |
| 2006 | 2 |
| 2007 | 5 |
| 2008 | 9 |
| 2009 | 6 |
| 2010 | 2 |
| 2011 | 5 |
| 2012 | 14 |
| 2013 | 9 |
| 2014 | 17 |
| 2015 | 29 |
| 2016 | 32 |
| 2017 | 53 |
| 2018 | 68 |
| 2019 | 113 |
| 2020 | 167 |
| 2021 | 266 |
| 2022 | 361 |
| 2023 | 410 |
| 2024 | 555 |
| 2025 | 685 |
| 2026 | 686 |

### Database of record

| Search source | Papers |
| --- | ---: |
| PubMed | 3122 |
| Embase | 365 |
| OpenAlex | 9 |

## Named models (120 of highest impact)

Ranked by `impact` — FWCI where OpenAlex has computed it, RCR otherwise — so a 2025 paper and a 2018 one are compared on the same 1.0-is-average scale.

| Model | Year | Cites | /yr | Impact | Modality | Population | Clinical problem | Release | Journal | Link |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| CA-Net | 2021 | 269 | 53.8 | 93.26 (FWCI) | MRI | fetuses imaged with MRI; a second application uses dermoscopic skin l… | segmenting the placenta and fetal brain on fetal… | open-source | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2020.3035253) |
| Attention Gate (Attention U-Net) | 2019 | 701 | 100.14 | 82.77 (FWCI) | ultrasound; CT | fetuses undergoing mid-pregnancy screening ultrasound; the segmentati… | identifying the correct standard views during fet… | open-source | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2019.01.012) |
| iBEAT V2.0 | 2023 | 106 | 35.33 | 69.13 (FWCI) | MRI | infants from birth to 6 years of age, across many imaging sites, prot… | measuring cortical development in infants, whose… | open-source | Nature protocols | [doi](https://doi.org/10.1038/s41596-023-00806-x) |
| DeepIGeoS | 2019 | 185 | 26.43 | 65.79 (FWCI) | MRI | fetal MRI studies; brain tumor FLAIR MRI is the second test case | producing clinically usable placental contours on… | unclear | IEEE transactions on pattern an… | [doi](https://doi.org/10.1109/TPAMI.2018.2840695) |
| BrainNetCNN | 2017 | 370 | 41.11 | 62.95 (FWCI) | MRI | infants born preterm, scanned between 27 and 46 weeks postmenstrual a… | predicting neurodevelopmental outcome after prete… | unclear | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2016.09.046) |
| ChatGPT-o4-mini-high, ChatGPT-4.5, Gemini 2.5 Pro | 2025 | 10 | 10.0 | 53.76 (FWCI) | x-ray / radiography | 180 left-hand wrist radiographs of children aged 0-18 from the RSNA P… | whether a general-purpose chatbot can substitute… | commercial | Academic radiology | [doi](https://doi.org/10.1016/j.acra.2025.07.058) |
| BIFSeg | 2018 | 277 | 34.62 | 51.2 (FWCI) | MRI | fetuses imaged with MRI; a second application uses brain tumor MRI | outlining fetal organs on MRI when only some orga… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2018.2791721) |
| GANCS | 2019 | 230 | 32.86 | 51.16 (FWCI) | MRI | pediatric patients undergoing contrast-enhanced abdominal MRI | shortening contrast-enhanced MRI in children by r… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2018.2858752) |
| 2017 RSNA Pediatric Bone Age Challenge ensembles | 2019 | 37 | 5.29 | 48.17 (FWCI) | x-ray / radiography | 12 611 pediatric hand radiographs for development and a 200-radiograp… | automated skeletal age estimation from hand radio… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.2019190053) |
| SonoNet | 2017 | 193 | 21.44 | 42.18 (FWCI) | ultrasound | fetuses undergoing routine mid-pregnancy anomaly screening ultrasound | finding and labelling the standard views required… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2017.2712367) |
| Auto-Net | 2017 | 90 | 10.0 | 41.77 (FWCI) | MRI | public adult benchmark datasets plus reconstructed fetal brain MRI | extracting the brain from surrounding tissue on M… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2017.2721362) |
| LINKS | 2015 | 147 | 13.36 | 38.57 (FWCI) | MRI | 119 infants | Segmenting infant brain MRI into gray matter, whi… | unclear | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2014.12.042) |
| BoneXpert, PANDA, BoneView | 2025 | 13 | 13.0 | 32.04 (FWCI) | x-ray / radiography | 306 children aged 1-18, stratified by sex and age, at a Central Europ… | which of the bone age products approved for the E… | commercial | European radiology | [doi](https://doi.org/10.1007/s00330-024-11169-6) |
| TW3-AI | 2020 | 26 | 4.33 | 31.86 (FWCI) | x-ray / radiography | 9059 clinical left hand radiographs from PACS between January 2012 an… | bone age assessment by the Tanner-Whitehouse 3 me… | unclear | Quantitative imaging in medicin… | [doi](https://doi.org/10.21037/qims.2020.02.20) |
| TDL-BAAM | 2020 | 26 | 4.33 | 30.33 (FWCI) | x-ray / radiography | 15 129 frontal pediatric trauma hand radiographs from Children's Hosp… | whether bone age assessment should still be ancho… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.2020190198) |
| FeTA | 2023 | 39 | 13.0 | 29.74 (FWCI) | MRI | fetuses in the open FeTA dataset of reconstructed brain MRI segmented… | segmenting the developing fetal brain into tissue… | open-source | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2023.102833) |
| FUIQA | 2017 | 91 | 10.11 | 27.17 (FWCI) | ultrasound | fetuses undergoing obstetric ultrasound examination | automatic quality control of obstetric ultrasound… | unclear | IEEE transactions on cybernetics | [doi](https://doi.org/10.1109/TCYB.2017.2671898) |
| FetalBrainAwareNet | 2024 | 17 | 8.5 | 23.76 (FWCI) | ultrasound | — | Synthesizing anatomically accurate fetal head sta… | unclear | Computerized medical imaging an… | [doi](https://doi.org/10.1016/j.compmedimag.2024.102405) |
| DAG V-Net | 2021 | 49 | 9.8 | 23.29 (FWCI) | ultrasound | fetuses across trimesters in the public HC18 challenge dataset (355 t… | measuring head circumference from a fetal ultraso… | open-source | Journal of digital imaging | [doi](https://doi.org/10.1007/s10278-020-00410-5) |
| DPA-HNN | 2019 | 86 | 12.29 | 20.62 (FWCI) | CT | adult and pediatric patients whose thoracic CT reports were collected… | extracting whether a CT report says there is a pu… | unclear | Artificial intelligence in medi… | [doi](https://doi.org/10.1016/j.artmed.2018.11.004) |
| TW3 AI bone age assessment system | 2024 | 9 | 4.5 | 20.58 (FWCI) | x-ray / radiography | 744 patients aged 1-20 years (378 boys, 366 girls) from 9 children's… | validating an AI system for Tanner-Whitehouse 3 b… | unclear | Quantitative imaging in medicin… | [doi](https://doi.org/10.21037/qims-23-715) |
| DenseNet169 | 2023 | 21 | 7.0 | 20.17 (FWCI) | ultrasound | fetal ultrasound images from two datasets from different regions, rec… | identifying which fetal organ an ultrasound image… | unclear | Scientific reports | [doi](https://doi.org/10.1038/s41598-023-44689-0) |
| DeepCut | 2017 | 138 | 15.33 | 19.28 (FWCI) | MRI | fetuses in a fetal MRI dataset | segmenting fetal brain and lung on MRI without pi… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2016.2621185) |
| MF R-CNN | 2019 | 63 | 9.0 | 18.99 (FWCI) | ultrasound | fetuses undergoing prenatal ultrasound | deciding whether a fetal head ultrasound image is… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2019.101548) |
| AI-OPiNE | 2024 | 17 | 8.5 | 18.43 (FWCI) | MRI | 414 term neonates from the HEAL trial across 17 institutions | Predicting 2-year neurodevelopmental outcome (dea… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.240076) |
| FUVAI | 2022 | 31 | 7.75 | 17.65 (FWCI) | ultrasound | 50 freehand fetal ultrasound video scans, compared against five exper… | fetal biometry - head circumference, biparietal d… | unclear | Physics in medicine and biology | [doi](https://doi.org/10.1088/1361-6560/ac4d85) |
| ImplicitVol | 2024 | 19 | 6.33 | 16.12 (FWCI) | ultrasound | fetuses imaged with freehand 2D ultrasound sweeps, natively-acquired… | 3D reconstruction of fetal brain anatomy from fre… | unclear | Medical Image Analysis | [doi](https://doi.org/10.1016/j.media.2024.103147) |
| ImplicitVol | 2024 | 11 | 5.5 | 16.12 (FWCI) | ultrasound | fetal freehand 2D ultrasound video sequences from multiple manufactur… | reconstructing 3D fetal brain volumes from freeha… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2024.103147) |
| ABAIs (automatic bone age identification system) | 2021 | 13 | 2.6 | 16.03 (FWCI) | x-ray / radiography | 8,061 hand radiographs, ages 0-18 years | Automatically assessing bone age from pediatric l… | unclear | BioMedicine | [doi](https://doi.org/10.37796/2211-8039.1256) |
| icobrain-dl | 2024 | 14 | 7.0 | 15.08 (FWCI) | MRI | 390 patients (ages 2-81) for training across four datasets; 280 patie… | Can a single brain segmentation model work accura… | unclear | Scientific reports | [doi](https://doi.org/10.1038/s41598-024-61798-6) |
| ANUBEX | 2024 | 8 | 4.0 | 15.08 (FWCI) | MRI | 433 participants from the HEAL (High-dose Erythropoietin for Asphyxia… | automatically extracting (skull-stripping) the ne… | unclear | Scientific reports | [doi](https://doi.org/10.1038/s41598-024-54436-8) |
| RTSeg-Net | 2024 | 15 | 7.5 | 15.07 (FWCI) | ultrasound | two intrapartum ultrasound image datasets | real-time segmentation of the fetal head and pubi… | unclear | Computers in biology and medici… | [doi](https://doi.org/10.1016/j.compbiomed.2024.108501) |
| Cropping-Segmentation-Calibration (CSC) | 2020 | 47 | 7.83 | 14.97 (FWCI) | ultrasound | 615 annotated frames from 421 normal fetal cardiac ultrasound videos… | delineating the ventricular septum during fetal c… | unclear | Biomolecules | [doi](https://doi.org/10.3390/biom10111526) |
| Attention MFP-Unet | 2021 | 22 | 4.4 | 14.97 (FWCI) | ultrasound | the public HC18 grand challenge dataset plus clinical data from 1334… | measuring biparietal diameter, head circumference… | unclear | Physica medica : PM : an intern… | [doi](https://doi.org/10.1016/j.ejmp.2021.06.020) |
| ALFA (Accurate Learning with Few Atlases) | 2016 | 24 | 2.4 | 14.61 (FWCI) | MRI | multi-modal brain MRI of 50 newborns | brain extraction from neonatal MRI - the first st… | unclear | Scientific reports | [doi](https://doi.org/10.1038/srep23470) |
| ScolioNets | 2023 | 35 | 11.67 | 14.48 (FWCI) | other | adolescent patients attending spine clinics, with radiographs and sma… | classifying severity and curve type in adolescent… | commercial | JAMA network open | [doi](https://doi.org/10.1001/jamanetworkopen.2023.30617) |
| AI-IQA | 2025 | 5 | 5.0 | 14.39 (FWCI) | ultrasound | 567 clinical validation cases scanned by 4 radiologists; large multic… | automated quality auditing of first-trimester fet… | unclear | BMC pregnancy and childbirth | [doi](https://doi.org/10.1186/s12884-025-07485-4) |
| Fetal-BET | 2024 | 8 | 4.0 | 14.24 (FWCI) | MRI | approximately 72,000 2D fetal brain MRI images (T2-weighted, diffusio… | automatically extracting (skull-stripping) the fe… | unclear | IEEE open journal of engineerin… | [doi](https://doi.org/10.1109/OJEMB.2024.3426969) |
| Pgds-ResNet | 2023 | 17 | 5.67 | 14.12 (FWCI) | ultrasound | — | Screening for high-risk fetuses with common and r… | unclear | Biomedicines | [doi](https://doi.org/10.3390/biomedicines11061756) |
| SAP-UNet (Squeeze Atrous Pooling UNet) | 2025 | 16 | 8.0 | 13.58 (FWCI) | ultrasound | fetuses undergoing prenatal ultrasound (public HC18 dataset) | fetal head circumference measurement on prenatal… | unclear | Biomedical Signal Processing an… | [doi](https://doi.org/10.1016/j.bspc.2024.107434) |
| deepee | 2021 | 53 | 10.6 | 13.2 (FWCI) | x-ray / radiography | children in the public pediatric pneumonia chest radiograph dataset,… | training diagnostic models on children's images w… | open-source | Scientific reports | [doi](https://doi.org/10.1038/s41598-021-93030-0) |
| ECAU-Net | 2022 | 41 | 8.2 | 13.14 (FWCI) | ultrasound | fetuses in the second trimester of pregnancy | fetal cerebellum segmentation for CNS assessment | unclear | Biomedical Signal Processing an… | [doi](https://doi.org/10.1016/j.bspc.2022.103528) |
| FB-ZWUNet | 2025 | 7 | 3.5 | 13.1 (FWCI) | ultrasound | fetuses at 18-32 weeks gestation undergoing brain ultrasound | assessment of fetal brain development via corpus… | unclear | Biomedical Signal Processing an… | [doi](https://doi.org/10.1016/j.bspc.2025.107499) |
| PAICS | 2022 | 39 | 9.75 | 12.64 (FWCI) | ultrasound | 16,297 pregnancies at 18-40 weeks from two tertiary Chinese hospitals… | screening for congenital central nervous system m… | unclear | Ultrasound in obstetrics & gyne… | [doi](https://doi.org/10.1002/uog.24843) |
| FetMRQC | 2024 | 10 | 5.0 | 12.54 (FWCI) | MRI | >1600 manually rated fetal brain T2-weighted images from four clinica… | automated image quality assessment/control for fe… | open-source | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2024.103282) |
| ASD-HNet | 2025 | 6 | 6.0 | 12.51 (FWCI) | MRI | ABIDE-I, ABIDE-II and ADHD-200 public datasets | Improving objective diagnosis of autism spectrum… | open-source | Neural networks : the official… | [doi](https://doi.org/10.1016/j.neunet.2025.107450) |
| BoneXpert | 2024 | 11 | 5.5 | 12.43 (FWCI) | x-ray / radiography | 1,173 participants aged 5-18 years in Mexico | adult height prediction from bone age assessment | commercial | Pediatric research | [doi](https://doi.org/10.1038/s41390-023-02821-w) |
| EchoNet-Peds | 2023 | 45 | 15.0 | 12.26 (FWCI) | ultrasound | pediatric patients undergoing echocardiography (4,467 echocardiogram… | automated assessment of left ventricular ejection… | unclear | Journal of the American Society… | [doi](https://doi.org/10.1016/j.echo.2023.01.015) |
| YOLOv5 | 2023 | 17 | 5.67 | 12.2 (FWCI) | ultrasound | — | Classifying normal versus abnormal fetal heart ul… | unclear | Journal of perinatal medicine | [doi](https://doi.org/10.1515/jpm-2023-0041) |
| DeepFMRI | 2020 | 72 | 12.0 | 11.96 (FWCI) | MRI | children in the public ADHD-200 dataset, contributed by several imagi… | diagnosing ADHD, which currently rests entirely o… | unclear | Journal of neuroscience methods | [doi](https://doi.org/10.1016/j.jneumeth.2019.108506) |
| HRINet (Hemispheric Relation Inference Network) | 2024 | 7 | 3.5 | 11.88 (FWCI) | MRI | 531 preterm and full-term neonates from the Developing Human Connecto… | estimating perinatal brain age / maturity from co… | unclear | IEEE journal of biomedical and… | [doi](https://doi.org/10.1109/JBHI.2024.3411620) |
| ARVBNet | 2020 | 60 | 10.0 | 11.82 (FWCI) | ultrasound | fetuses undergoing cardiac screening ultrasound | deciding whether a fetal cardiac four-chamber vie… | unclear | IEEE journal of biomedical and… | [doi](https://doi.org/10.1109/JBHI.2019.2948316) |
| PSFFGAN | 2023 | 20 | 6.67 | 11.64 (FWCI) | ultrasound | fetal four-chamber ultrasound views, healthy and with congenital hear… | the shortage of large, high-quality fetal four-ch… | unclear | IEEE journal of biomedical and… | [doi](https://doi.org/10.1109/JBHI.2022.3143319) |
| PAICS (Prenatal Ultrasound Diagnosis Artificial Intelligence Conduct System) | 2023 | 16 | 5.33 | 11.59 (FWCI) | ultrasound | 709 fetal neurosonographic images/videos read by 36 sonologists of va… | detecting fetal intracranial malformations on pre… | unclear | NPJ digital medicine | [doi](https://doi.org/10.1038/s41746-023-00932-6) |
| DeepUTE | 2018 | 81 | 11.57 | 11.32 (FWCI) | nuclear / PET; MRI | 79 pediatric brain tumor examinations, 36 with active tumor volume ab… | quantitatively accurate FET-PET/MRI in children w… | unclear | Frontiers in neuroscience | [doi](https://doi.org/10.3389/fnins.2018.01005) |
| AF-net | 2021 | 25 | 5.0 | 11.32 (FWCI) | ultrasound | antenatal ultrasound examinations, sizes not stated | measuring the amniotic fluid index, which informs… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2020.101951) |
| ETLM (Ensemble Transfer Learning Model) | 2022 | 19 | 4.75 | 11.23 (FWCI) | ultrasound | fetuses undergoing obstetric ultrasound (public HC18 dataset) | segmenting the fetal head on ultrasound and estim… | unclear | Diagnostics (Basel, Switzerland) | [doi](https://doi.org/10.3390/diagnostics12092229) |
| Appendicitis Prediction Tool | 2021 | 52 | 10.4 | 11.22 (FWCI) | ultrasound | 430 children and adolescents aged 0-18 with suspected appendicitis | three separate decisions in suspected pediatric a… | open-source | Frontiers in pediatrics | [doi](https://doi.org/10.3389/fped.2021.662183) |
| FHUSP-NET | 2024 | 14 | 7.0 | 11.19 (FWCI) | ultrasound | 3,360 ultrasound images of five fetal heart standard planes from 1,30… | Can the fetal heart ultrasound standard planes ne… | unclear | Computers in biology and medici… | [doi](https://doi.org/10.1016/j.compbiomed.2023.107741) |
| FTSPD (First-Trimester Standard Plane Detection) | 2023 | 12 | 4.0 | 11.19 (FWCI) | ultrasound | 220 first-trimester ultrasound videos from two scanners | Automatically locating standard anatomical planes… | unclear | Ultrasound in medicine & biology | [doi](https://doi.org/10.1016/j.ultrasmedbio.2023.05.005) |
| BoneXpert | 2020 | 10 | 1.67 | 11.11 (FWCI) | x-ray / radiography | 611 children (3-17 years) presenting for trauma | establishing bone-age reference standards for Tai… | commercial | The Kaohsiung journal of medica… | [doi](https://doi.org/10.1002/kjm2.12268) |
| DLBAA (deep learning-based bone age assessment) | 2022 | 13 | 3.25 | 11.1 (FWCI) | x-ray / radiography | 485 hand radiographs from healthy Korean children aged 2-17 years (26… | Assessing whether Greulich-Pyle bone age standard… | unclear | Yonsei medical journal | [doi](https://doi.org/10.3349/ymj.2022.63.7.683) |
| DUnet / ResDUnet | 2019 | 26 | 3.71 | 10.74 (FWCI) | MRI | infant brain MRI | segmenting hippocampal subfields in infants, wher… | unclear | Frontiers in neuroinformatics | [doi](https://doi.org/10.3389/fninf.2019.00030) |
| D-ProtoPNet | 2025 | 6 | 6.0 | 10.49 (FWCI) | x-ray / radiography | 5,856 CXR images from pediatric patients ages 1-5 years (public Kaggl… | Providing an interpretable ('white-box') pneumoni… | unclear | Journal of medical imaging and… | [doi](https://doi.org/10.1016/j.jmir.2025.102023) |
| DBSN (double branch segmentation network) | 2022 | 16 | 4.0 | 10.14 (FWCI) | ultrasound | private dataset of 313 transperineal ultrasound images; public datase… | assessing fetal head descent during labor via ang… | unclear | Frontiers in physiology | [doi](https://doi.org/10.3389/fphys.2022.940150) |
| MTSE U-Net | 2022 | 30 | 6.0 | 10.11 (FWCI) | MRI | — | fetal brain segmentation, classifying pathologica… | unclear | Network Modeling Analysis in He… | [doi](https://doi.org/10.1007/s13721-022-00394-y) |
| APPSTACK | 2024 | 10 | 5.0 | 9.77 (FWCI) | ultrasound | pediatric patients evaluated for appendicitis | diagnosing pediatric appendicitis using machine l… | unclear | Scientific reports | [doi](https://doi.org/10.1038/s41598-024-75896-y) |
| Deeplasia | 2024 | 25 | 12.5 | 9.58 (FWCI) | x-ray / radiography | the public RSNA challenge set for training, plus 568 radiographs from… | bone age in children with skeletal dysplasia, whe… | open-source | Pediatric radiology | [doi](https://doi.org/10.1007/s00247-023-05789-1) |
| BoneXpert; VUNO Med-Bone Age | 2025 | 5 | 5.0 | 9.43 (FWCI) | x-ray / radiography | 292 Turkish children aged 1-15 years | bone age assessment | commercial | Diagnostic and interventional r… | [doi](https://doi.org/10.4274/dir.2024.242790) |
| uAI DR scoliosis analysis system | 2025 | 7 | 7.0 | 9.25 (FWCI) | x-ray / radiography | 3,192 patients aged 8-18 years with AIS; 2,092 cases included after s… | AI-based rapid measurement of x-ray coronal imagi… | commercial | Journal of orthopaedic surgery… | [doi](https://doi.org/10.1186/s13018-024-05383-7) |
| MEDO-Hip | 2023 | 29 | 9.67 | 9.17 (FWCI) | ultrasound | 369 scans in 306 infants, scanned by nurses or family physicians at t… | universal newborn screening for developmental dys… | commercial | Scientific reports | [doi](https://doi.org/10.1038/s41598-023-35603-9) |
| Heartassist™ | 2023 | 12 | 4.0 | 9.15 (FWCI) | ultrasound | 120 consecutive singleton low-risk pregnant women, 19-23 weeks gestat… | Automatically assessing image quality/adequacy of… | commercial | Journal of perinatal medicine | [doi](https://doi.org/10.1515/jpm-2023-0052) |
| SSLDEC | 2019 | 27 | 3.86 | 9.15 (FWCI) | MRI | isointense-phase infant brain MRI, alongside MNIST and SVHN benchmark… | the cost of expert annotation in medical image se… | unclear | IEEE access : practical innovat… | [doi](https://doi.org/10.1109/ACCESS.2019.2891970) |
| SupWMA | 2023 | 40 | 13.33 | 8.96 (FWCI) | MRI | six independently acquired datasets spanning ages and health conditio… | parcellating the superficial white matter, which… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2023.102759) |
| HeteroSync Learning (HSL) | 2025 | 6 | 6.0 | 8.95 (FWCI) | ultrasound | Multi-center thyroid cancer imaging study, including an out-of-distri… | Enabling accurate multi-institution AI models for… | unclear | Nature communications | [doi](https://doi.org/10.1038/s41467-025-64459-y) |
| Smartplanes | 2018 | 43 | 5.38 | 8.87 (FWCI) | ultrasound | 30 fetuses at 17-30 weeks gestation, each with two 3D volumes and a c… | finding the transthalamic plane and measuring bip… | commercial | Diagnostic and interventional i… | [doi](https://doi.org/10.1016/j.diii.2018.08.001) |
| PSFHSP-Net | 2024 | 10 | 5.0 | 8.65 (FWCI) | ultrasound | intrapartum ultrasound imaging (patient numbers not stated) | automatically identifying the pubic symphysis-fet… | unclear | Medical & biological engineerin… | [doi](https://doi.org/10.1007/s11517-024-03111-1) |
| DeepGA | 2023 | 15 | 5.0 | 8.64 (FWCI) | ultrasound | 7,113 subjects, 10,413 ultrasound images | Can fetal gestational age be estimated automatica… | unclear | Artificial intelligence in medi… | [doi](https://doi.org/10.1016/j.artmed.2022.102453) |
| DenseNet-PAS / DenseNet-PP | 2024 | 11 | 5.5 | 8.57 (FWCI) | MRI | 540 pregnant women with suspected placenta accreta spectrum from two… | diagnosing placenta accreta spectrum antenatally… | unclear | Journal of magnetic resonance i… | [doi](https://doi.org/10.1002/jmri.28770) |
| SpineTK | 2023 | 21 | 7.0 | 8.54 (FWCI) | x-ray / radiography | 1310 anterior-posterior low-dose stereoradiographic images and radiog… | Cobb angle measurement, the definitional measurem… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.220158) |
| SMANet | 2022 | 7 | 1.75 | 8.54 (FWCI) | x-ray / radiography | 4,861 left-hand radiographs, Beijing Jishuitan Hospital | Can an interpretable, race/geography-independent… | unclear | Quantitative imaging in medicin… | [doi](https://doi.org/10.21037/qims-21-1158) |
| pTBLightNet | 2025 | 5 | 5.0 | 8.53 (FWCI) | x-ray / radiography | 918 pediatric CXRs from three pediatric TB cohorts (external test), p… | detecting pediatric pulmonary tuberculosis-compat… | unclear | Nature communications | [doi](https://doi.org/10.1038/s41467-025-64391-1) |
| Multi-Frame + Cylinder method (MFCY) | 2020 | 27 | 4.5 | 8.42 (FWCI) | ultrasound | 538 four-chamber-view ultrasound frames from 256 normal cases, five-f… | segmenting the fetal thoracic wall on the four-ch… | unclear | Biomolecules | [doi](https://doi.org/10.3390/biom10121691) |
| FetalGAN | 2022 | 14 | 3.5 | 8.26 (FWCI) | MRI | fetal resting-state functional MRI scans | Can fetal brain tissue be separated from non-brai… | unclear | Frontiers in neuroscience | [doi](https://doi.org/10.3389/fnins.2022.887634) |
| COMFormer | 2023 | 12 | 4.0 | 8.07 (FWCI) | ultrasound | 1792 subjects, 12,400 images (BCNatal public dataset) | Classifying maternal-fetal anatomical structures… | unclear | IEEE transactions on ultrasonic… | [doi](https://doi.org/10.1109/TUFFC.2023.3311879) |
| SepUNet | 2022 | 32 | 8.0 | 8.02 (FWCI) | MRI | more than 80 000 osteosarcoma MRI images from three hospitals in Chin… | segmenting osteosarcoma on MRI and computing tumo… | unclear | Computational and mathematical… | [doi](https://doi.org/10.1155/2022/7703583) |
| UPL-SFDA | 2023 | 21 | 7.0 | 7.99 (FWCI) | MRI | validated on a multi-site cardiac MRI dataset, a cross-modality fetal… | adapting a segmentation model to a new hospital w… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2023.3318364) |
| TransferX | 2024 | 33 | 16.5 | 7.89 (FWCI) | MRI | 214 children at Dana-Farber/Boston Children's for development and 112… | determining BRAF mutational status in pediatric l… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.230333) |
| IS-YOLOX | 2024 | 10 | 5.0 | 7.88 (FWCI) | ultrasound | fetal echocardiography (congenital heart disease screening) | automated localization and segmentation of cardia… | unclear | IEEE/ACM transactions on comput… | [doi](https://doi.org/10.1109/TCBB.2022.3222356) |
| Fetus Framework | 2022 | 15 | 3.75 | 7.88 (FWCI) | ultrasound | 1,519 pregnant women (weeks 10-14) across two centers (Shenzhen Peopl… | Can AI identify fetal intracranial structures in… | unclear | Computer methods and programs i… | [doi](https://doi.org/10.1016/j.cmpb.2022.107170) |
| SpineHRNet+ | 2022 | 30 | 7.5 | 7.86 (FWCI) | x-ray / radiography | 1542 consecutive patients with scoliosis at two Hong Kong clinics fro… | automatic measurement of spine alignment in scoli… | unclear | EClinicalMedicine | [doi](https://doi.org/10.1016/j.eclinm.2021.101252) |
| TractGraphFormer | 2025 | 9 | 9.0 | 7.75 (FWCI) | MRI | children (n=9,345) and young adults (n=1,065) from large diffusion MR… | predicting sex and age from diffusion MRI tractog… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2025.103476) |
| MABAL | 2018 | 42 | 5.25 | 7.74 (FWCI) | x-ray / radiography | 10,289 skeletal age examinations, 8,909 from one institution's archiv… | bone age assessment, which is tedious and time co… | unclear | Journal of digital imaging | [doi](https://doi.org/10.1007/s10278-018-0053-3) |
| IT-UNet | 2024 | 10 | 5.0 | 7.73 (FWCI) | ultrasound | two developmental dysplasia of the hip (DDH) ultrasound datasets, inf… | automated landmark detection on hip ultrasound to… | unclear | IEEE journal of biomedical and… | [doi](https://doi.org/10.1109/JBHI.2024.3390241) |
| MI-CB-DLM | 2021 | 17 | 3.4 | 7.65 (FWCI) | MRI | 271 MR exams from 211 fetuses (mean gestational age 30.9+/-5.5 weeks) | Automatically assessing image quality of reconstr… | unclear | Journal of magnetic resonance i… | [doi](https://doi.org/10.1002/jmri.27649) |
| Mask-R2CNN | 2021 | 15 | 3.0 | 7.65 (FWCI) | ultrasound | HC18 Challenge dataset | Can fetal head circumference, a key measure of fe… | unclear | International journal of comput… | [doi](https://doi.org/10.1007/s11548-021-02430-0) |
| GPT-4V; Gemini Pro Vision | 2024 | 82 | 41.0 | 7.63 (FWCI) | multiple | 190 'Diagnosis Please' teaching cases published in Radiology (Jan 200… | generate differential diagnoses directly from rad… | commercial | Radiology | [doi](https://doi.org/10.1148/radiol.240273) |
| PDFF-CNN | 2024 | 8 | 4.0 | 7.63 (FWCI) | MRI | 1,327 routine clinical T2-weighted MRI images from 157 subjects | predicting gestational age from fetal brain MRI t… | unclear | Medical physics | [doi](https://doi.org/10.1002/mp.16875) |
| AAPSO (adaptive and altruistic particle swarm optimization) feature selection framework | 2022 | 15 | 3.75 | 7.63 (FWCI) | x-ray / radiography | publicly available chest x-ray pneumonia dataset (pediatric-motivated… | Can a low-cost, computer-aided diagnosis system a… | open-source | Applied soft computing | [doi](https://doi.org/10.1016/j.asoc.2022.109464) |
| CUPID | 2024 | 8 | 4.0 | 7.53 (FWCI) | ultrasound | 642 fetuses, mean gestational age 22±2.82 weeks, prospective study at… | automatically measuring fetal biometric parameter… | unclear | BMC pregnancy and childbirth | [doi](https://doi.org/10.1186/s12884-024-06336-y) |
| AI-SPS | 2025 | 5 | 5.0 | 7.25 (FWCI) | ultrasound | 2,737 annotated frames from 45 clinical ultrasound videos (training)… | real-time detection of the standard imaging plane… | unclear | Journal of orthopaedic research… | [doi](https://doi.org/10.1002/jor.70020) |
| SonoCNS Fetal Brain | 2021 | 28 | 5.6 | 7.2 (FWCI) | ultrasound | 143 women at routine anatomical survey between 18+0 and 22+6 weeks, e… | obtaining the five standard fetal intracranial me… | commercial | Ultrasound in obstetrics & gyne… | [doi](https://doi.org/10.1002/uog.22171) |
| FaBiAN | 2022 | 10 | 2.5 | 7.11 (FWCI) | MRI | simulated fetal brain data, modeling in utero brain maturation, compl… | providing a realistic simulated fetal brain MRI d… | open-source | Scientific reports | [doi](https://doi.org/10.1038/s41598-022-10335-4) |
| CLP-Net | 2025 | 11 | 11.0 | 7.04 (FWCI) | ultrasound | 418 3D ultrasound volumes (394 normal, 24 CLP) from 288 pregnant women | automated localization of standard ultrasound pla… | unclear | BMC pregnancy and childbirth | [doi](https://doi.org/10.1186/s12884-024-07108-4) |
| Fracture Detection Using YOLOv8 App | 2023 | 58 | 19.33 | 6.96 (FWCI) | x-ray / radiography | children presenting with wrist trauma (public GRAZPEDWRI-DX pediatric… | detecting wrist fractures on trauma radiographs | unclear | Scientific reports | [doi](https://doi.org/10.1038/s41598-023-47460-7) |
| Functional Random Forest | 2018 | 91 | 11.38 | 6.92 (FWCI) | MRI | 47 children with autism and 58 typically developing children aged 9-13 | whether autism spectrum disorder contains distinc… | unclear | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2017.12.044) |
| BIBSNet | 2025 | 19 | 19.0 | 6.83 (RCR) | MRI | 90 participants aged 0-8 months (median 4.6 months) | segmenting the infant brain in the first months o… | open-source | bioRxiv : the preprint server f… | [doi](https://doi.org/10.1101/2023.03.22.533696) |
| VP-Nets | 2018 | 26 | 3.25 | 6.83 (FWCI) | ultrasound | 3D fetal neurosonography volumes | locating key brain structures in 3D fetal neuroso… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2018.04.004) |
| JoCoRank | 2024 | 6 | 3.0 | 6.79 (FWCI) | MRI | 157 healthy fetuses between 22 and 34 weeks gestation (1,327 MRI imag… | Accurately estimating fetal brain age from MRI su… | unclear | Computers in biology and medici… | [doi](https://doi.org/10.1016/j.compbiomed.2024.108111) |
| FOAC-Net (Fetal Organ Anomaly Classification Network) | 2022 | 7 | 1.75 | 6.76 (FWCI) | MRI | 36 participants; fetal 3D SSFP MRI sequences | Can a deep learning classification network automa… | unclear | Frontiers in artificial intelli… | [doi](https://doi.org/10.3389/frai.2022.832485) |
| Hydronephrosis Severity Index (HSI) | 2024 | 11 | 5.5 | 6.69 (FWCI) | ultrasound | pediatric patients with antenatal hydronephrosis across four quaterna… | predicting need for surgical intervention in ante… | unclear | Scientific reports | [doi](https://doi.org/10.1038/s41598-024-72271-9) |
| DLCRN (deep learning clinical-radiomics nomogram) | 2023 | 11 | 3.67 | 6.67 (FWCI) | MRI | 186 HIE patients and 219 healthy controls, from two medical centers | diagnosing hypoxic-ischemic encephalopathy in ful… | unclear | Neonatology | [doi](https://doi.org/10.1159/000530352) |
| quantusFLM | 2019 | 38 | 5.43 | 6.59 (FWCI) | ultrasound | 790 fetal lung ultrasound images obtained between 24 and 39 weeks ges… | predicting neonatal respiratory morbidity from ul… | commercial | Scientific reports | [doi](https://doi.org/10.1038/s41598-019-38576-w) |
| TrueFidelity | 2022 | 22 | 5.5 | 6.57 (FWCI) | CT | 120 pediatric patients (mean age 8.7 +/- 5.2 years, 60 male) who had… | image quality in pediatric abdominopelvic CT, whe… | commercial | Korean journal of radiology | [doi](https://doi.org/10.3348/kjr.2021.0466) |
| LAS-Net | 2025 | 10 | 10.0 | 6.56 (FWCI) | nuclear / PET; CT | 297 children in two Children's Oncology Group trials (median age 15.4… | deciding from the interim PET whether a child's H… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.240229) |
| RadiologyNET | 2025 | 8 | 8.0 | 6.56 (FWCI) | multiple | public benchmark datasets including RSNA Pediatric Bone Age Challenge… | whether pretraining on a large heterogeneous radi… | open-source | Scientific reports | [doi](https://doi.org/10.1038/s41598-025-05009-w) |
| LiviaNET / HyperDense-Net | 2020 | 22 | 3.67 | 6.55 (FWCI) | MRI | 24 pairs of neonatal T1 and T2 data from the Developing Human Connect… | segmenting gray matter, white matter and cerebros… | open-source | Frontiers in neuroscience | [doi](https://doi.org/10.3389/fnins.2020.00207) |
| Fgds-EL | 2023 | 10 | 3.33 | 6.55 (FWCI) | ultrasound | fetuses undergoing prenatal ultrasound | screening for fetal genetic diseases using facial… | unclear | International journal of enviro… | [doi](https://doi.org/10.3390/ijerph20032377) |
| nnU-Net | 2024 | 11 | 5.5 | 6.5 (FWCI) | MRI | fetuses with congenital diaphragmatic hernia (registered clinical tri… | automatically quantifying fetal lung volume and p… | open-source | European journal of pediatrics | [doi](https://doi.org/10.1007/s00431-024-05476-9) |
| AutoRAPNO | 2022 | 49 | 12.25 | 6.42 (FWCI) | MRI | 794 children with preoperative MRI and 122 with serial postoperative… | measuring tumor burden reproducibly across serial… | unclear | Neuro-oncology | [doi](https://doi.org/10.1093/neuonc/noab151) |

## Highest-impact work from 2024 onward (40)

A raw citation count cannot rank the last two years — a paper from this year has had no time to accumulate one — so these are ranked on the normalized `impact` column, which is FWCI for most of this window because RCR is not yet computed. Studies with fewer than 5 citations have no normalized value and rank below those that do, on citations per year. The source column marks the records that reached the corpus through Embase rather than PubMed.

| Title | Year | Cites | /yr | Impact | Type | Source | Clinical problem | Link |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| ChatGPT-o4-mini-high, ChatGPT-4.5, Gemini 2.5 Pro | 2025 | 10 | 10.0 | 53.76 (FWCI) | journal | PubMed | whether a general-purpose chatbot can substit… | [doi](https://doi.org/10.1016/j.acra.2025.07.058) |
| Prediction of mental health risk in adolescents. | 2025 | 34 | 34.0 | 52.07 (FWCI) | journal | PubMed | predicting future risk of general psychiatric… | [doi](https://doi.org/10.1038/s41591-025-03560-7) |
| Infants have rich visual categories in ventrotemporal cortex at… | 2026 | 7 | 7.0 | 45.99 (FWCI) | journal | PubMed | characterizing the development of visual cate… | [doi](https://doi.org/10.1038/s41593-025-02187-8) |
| BoneXpert, PANDA, BoneView | 2025 | 13 | 13.0 | 32.04 (FWCI) | journal | PubMed | which of the bone age products approved for t… | [doi](https://doi.org/10.1007/s00330-024-11169-6) |
| Automated bone age assessment in a German pediatric cohort: agr… | 2024 | 16 | 8.0 | 29.42 (FWCI) | journal | PubMed | whether a bone age product can be swapped in… | [doi](https://doi.org/10.1007/s00330-023-10543-0) |
| A Dempster-Shafer Approach to Trustworthy AI With Application t… | 2024 | 16 | 8.0 | 29.27 (FWCI) | journal | PubMed | detecting and correcting failures in automate… | [doi](https://doi.org/10.1109/TPAMI.2023.3346330) |
| Whole examination AI estimation of fetal biometrics from 20-wee… | 2025 | 10 | 10.0 | 29.04 (FWCI) | journal | PubMed | fetal biometry currently rests on a handful o… | [doi](https://doi.org/10.1038/s41746-024-01406-z) |
| Uncovering ethical biases in publicly available fetal ultrasoun… | 2025 | 8 | 8.0 | 28.78 (FWCI) | journal | PubMed | whether publicly available fetal ultrasound i… | [doi](https://doi.org/10.1038/s41746-025-01739-3) |
| Scanner-based real-time three-dimensional brain + body slice-to… | 2025 | 13 | 13.0 | 27.93 (FWCI) | journal | PubMed | motion-corrected 3D fetal MRI has stayed a re… | [doi](https://doi.org/10.1007/s00247-025-06165-x) |
| HFSCCD: A Hybrid Neural Network for Fetal Standard Cardiac Cycl… | 2024 | 12 | 6.0 | 26.3 (FWCI) | journal | PubMed | Automatically detecting standard cardiac cycl… | [doi](https://doi.org/10.1109/JBHI.2024.3370507) |
| Predicting pediatric patient rehabilitation outcomes after spin… | 2025 | 21 | 21.0 | 26.15 (FWCI) | journal | PubMed | telling an adolescent before scoliosis surger… | [doi](https://doi.org/10.1038/s43856-024-00726-1) |
| Three-dimensional markerless surface topography approach with c… | 2025 | 10 | 10.0 | 24.29 (FWCI) | journal | PubMed | screening adolescents for scoliosis without t… | [doi](https://doi.org/10.1038/s41598-025-92551-2) |
| Assessment of Bone Age Based on Hand Radiographs Using Regressi… | 2024 | 5 | 2.5 | 24.16 (FWCI) | journal | PubMed | estimating bone age from hand radiographs | [doi](https://doi.org/10.3390/life14060774) |
| FetalBrainAwareNet | 2024 | 17 | 8.5 | 23.76 (FWCI) | journal | PubMed | Synthesizing anatomically accurate fetal head… | [doi](https://doi.org/10.1016/j.compmedimag.2024.102405) |
| On the use of contrastive learning for standard-plane classific… | 2024 | 16 | 8.0 | 23.76 (FWCI) | journal | PubMed | automated identification of standard imaging… | [doi](https://doi.org/10.1016/j.compbiomed.2024.108430) |
| Advancing prenatal healthcare by explainable AI enhanced fetal… | 2025 | 5 | 5.0 | 23.38 (FWCI) | journal | PubMed | automated, explainable segmentation of fetal… | [doi](https://doi.org/10.1038/s41598-025-04631-y) |
| Transformer based multi-modal MRI fusion for prediction of post… | 2024 | 12 | 6.0 | 22.06 (FWCI) | journal | PubMed | Estimating post-menstrual age and assessing b… | [doi](https://doi.org/10.1016/j.media.2024.103140) |
| Longitudinal twin growth discordance patterns and adverse perin… | 2025 | 9 | 9.0 | 21.07 (FWCI) | journal | PubMed | identifying patterns of twin fetal growth dis… | [doi](https://doi.org/10.1016/j.ajog.2024.12.029) |
| TW3 AI bone age assessment system | 2024 | 9 | 4.5 | 20.58 (FWCI) | journal | PubMed | validating an AI system for Tanner-Whitehouse… | [doi](https://doi.org/10.21037/qims-23-715) |
| Artificial intelligence assisted common maternal fetal planes p… | 2024 | 11 | 5.5 | 19.51 (FWCI) | journal | PubMed | automatically classifying standard maternal-f… | [doi](https://doi.org/10.3389/fmed.2024.1486995) |
| Estimating cortical thickness trajectories in children across d… | 2024 | 24 | 12.0 | 19.27 (FWCI) | journal | PubMed | estimating individual cortical thickness deve… | [doi](https://doi.org/10.1002/hbm.26565) |
| Interaction between clinicians and artificial intelligence to d… | 2024 | 13 | 6.5 | 19.27 (FWCI) | journal | PubMed | Detecting fetal atrioventricular septal defec… | [doi](https://doi.org/10.1002/uog.27577) |
| Integrated brain connectivity analysis with fMRI, DTI, and sMRI… | 2025 | 17 | 17.0 | 18.99 (FWCI) | journal | PubMed | Integrating multimodal brain imaging (fMRI, D… | [doi](https://doi.org/10.1016/j.media.2025.103570) |
| AI-OPiNE | 2024 | 17 | 8.5 | 18.43 (FWCI) | journal | PubMed | Predicting 2-year neurodevelopmental outcome… | [doi](https://doi.org/10.1148/ryai.240076) |
| Automated body organ segmentation, volumetry and population-ave… | 2024 | 15 | 7.5 | 18.38 (FWCI) | journal | PubMed | volumetry of fetal organs, which is currently… | [doi](https://doi.org/10.1038/s41598-024-57087-x) |
| Using Artificial Intelligence for Rheumatic Heart Disease Detec… | 2024 | 34 | 17.0 | 18 (FWCI) | journal | PubMed | detecting rheumatic heart disease via mitral… | [doi](https://doi.org/10.1161/JAHA.123.031257) |
| Diagnostic Accuracy of an Integrated AI Tool to Estimate Gestat… | 2024 | 32 | 16.0 | 17.04 (FWCI) | journal | PubMed | dating a pregnancy where no trained sonograph… | [doi](https://doi.org/10.1001/jama.2024.10770) |
| Automated Neuroprognostication Via Machine Learning in Neonates… | 2025 | 14 | 14.0 | 16.72 (FWCI) | journal | PubMed | predicting neurodevelopmental outcome after n… | [doi](https://doi.org/10.1002/ana.27154) |
| Artificial intelligence-assisted approach to assessing bowel wa… | 2025 | 16 | 16.0 | 16.71 (FWCI) | journal | PubMed | measuring bowel wall thickness on intestinal… | [doi](https://doi.org/10.1093/ecco-jcc/jjaf037) |
| Deep Learning-based Brain Age Prediction Using MRI to Identify… | 2025 | 7 | 7.0 | 16.19 (FWCI) | journal | PubMed | using a fetal brain age prediction model to i… | [doi](https://doi.org/10.1148/ryai.240115) |
| ImplicitVol | 2024 | 19 | 6.33 | 16.12 (FWCI) | journal | Embase | 3D reconstruction of fetal brain anatomy from… | [doi](https://doi.org/10.1016/j.media.2024.103147) |
| ImplicitVol | 2024 | 11 | 5.5 | 16.12 (FWCI) | journal | PubMed | reconstructing 3D fetal brain volumes from fr… | [doi](https://doi.org/10.1016/j.media.2024.103147) |
| Interpretable and intervenable ultrasonography-based machine le… | 2024 | 26 | 13.0 | 16.09 (FWCI) | journal | PubMed | diagnosis, management and severity of suspect… | [doi](https://doi.org/10.1016/j.media.2023.103042) |
| Deep learning denoising reconstruction for improved image quali… | 2024 | 11 | 5.5 | 15.87 (FWCI) | journal | PubMed | improving fetal cardiac MRI image quality for… | [doi](https://doi.org/10.3389/fcvm.2024.1323443) |
| Ultrasound imaging based recognition of prenatal anomalies: a s… | 2024 | 18 | 6.0 | 15.27 (FWCI) | journal | Embase | recognition of prenatal structural anomalies… | [doi](https://doi.org/10.1088/2516-1091/ad3a4b) |
| Ultrasound imaging based recognition of prenatal anomalies: a s… | 2024 | 6 | 3.0 | 15.27 (FWCI) | journal | PubMed | automated detection of prenatal structural an… | [doi](https://doi.org/10.1088/2516-1091/ad3a4b) |
| icobrain-dl | 2024 | 14 | 7.0 | 15.08 (FWCI) | journal | PubMed | Can a single brain segmentation model work ac… | [doi](https://doi.org/10.1038/s41598-024-61798-6) |
| ANUBEX | 2024 | 8 | 4.0 | 15.08 (FWCI) | journal | PubMed | automatically extracting (skull-stripping) th… | [doi](https://doi.org/10.1038/s41598-024-54436-8) |
| RTSeg-Net | 2024 | 15 | 7.5 | 15.07 (FWCI) | journal | PubMed | real-time segmentation of the fetal head and… | [doi](https://doi.org/10.1016/j.compbiomed.2024.108501) |
| Validation of an AI-Powered Automated X-ray Bone Age Analyzer i… | 2024 | 6 | 3.0 | 14.87 (FWCI) | journal | PubMed | Validating a commercially available AI-powere… | [doi](https://doi.org/10.1007/s12325-024-02944-4) |

The full table, including the model description, dataset size, validation and headline result for every study, is `data/processed/pedrad_paper_db.csv`; the screened-out records and their reasons are in `data/processed/pedrad_paper_db.json`.
