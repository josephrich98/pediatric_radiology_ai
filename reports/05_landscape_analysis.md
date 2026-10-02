# Landscape analysis: reproducible supplementary tables

Generated 2026-09-30 from **3,528 included primary-study records**; search cutoff September 9, 2026.

Run `PYTHONPATH=. python scripts/review_stats.py` then `PYTHONPATH=. python scripts/build_landscape_review.py`. The latter verifies exact membership against the shared cohort and writes the source CSV SHA-256 to `data/processed/review_landscape_stats.json`.

Topic counts below are exploratory matches to the title and extracted clinical question. Dataset counts are name mentions across the title and extracted clinical question, population, model description, and dataset size. They cannot establish whether a dataset was used for training, testing, or mentioned as context. No-match does not mean no use. All rules and row-level matches are exported in the JSON and `review_landscape_audit.csv`.

There are 983 records with no match to the selected topic rules; these remain in every whole-cohort denominator. Categories overlap; counts are records, not independent datasets, models, or patients.

## Table L1. Modality, task, and age by era

| Axis / label | All | 2005–2014 (n=71) | 2015–2019 (n=295) | 2020–2022 (n=794) | 2023–2024 (n=965) | 2025 (n=685) | 2026 YTD (n=718) |
|:--|--:|--:|--:|--:|--:|--:|--:|
| modality: MRI | 1,604 (45.5%) | 43 (60.6%) | 172 (58.3%) | 371 (46.7%) | 428 (44.4%) | 301 (43.9%) | 289 (40.3%) |
| modality: ultrasound | 837 (23.7%) | 12 (16.9%) | 60 (20.3%) | 179 (22.5%) | 229 (23.7%) | 178 (26.0%) | 179 (24.9%) |
| modality: x-ray / radiography | 685 (19.4%) | 9 (12.7%) | 45 (15.3%) | 152 (19.1%) | 186 (19.3%) | 132 (19.3%) | 161 (22.4%) |
| modality: CT | 326 (9.2%) | 3 (4.2%) | 19 (6.4%) | 83 (10.5%) | 94 (9.7%) | 52 (7.6%) | 75 (10.4%) |
| modality: nuclear / PET | 53 (1.5%) | 0 (0.0%) | 1 (0.3%) | 14 (1.8%) | 23 (2.4%) | 7 (1.0%) | 8 (1.1%) |
| modality: other | 46 (1.3%) | 0 (0.0%) | 6 (2.0%) | 5 (0.6%) | 13 (1.3%) | 10 (1.5%) | 12 (1.7%) |
| modality: multiple | 43 (1.2%) | 3 (4.2%) | 0 (0.0%) | 6 (0.8%) | 9 (0.9%) | 12 (1.8%) | 13 (1.8%) |
| modality: fluoroscopy | 13 (0.4%) | 0 (0.0%) | 0 (0.0%) | 4 (0.5%) | 4 (0.4%) | 3 (0.4%) | 2 (0.3%) |
| modality: mammography | 1 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 1 (0.1%) |
| task: detection / diagnosis | 1,353 (38.4%) | 41 (57.7%) | 126 (42.7%) | 287 (36.1%) | 378 (39.2%) | 248 (36.2%) | 273 (38.0%) |
| task: measurement / quantification | 849 (24.1%) | 15 (21.1%) | 63 (21.4%) | 190 (23.9%) | 234 (24.2%) | 156 (22.8%) | 191 (26.6%) |
| task: outcome prediction | 686 (19.4%) | 7 (9.9%) | 50 (16.9%) | 148 (18.6%) | 181 (18.8%) | 150 (21.9%) | 150 (20.9%) |
| task: segmentation | 668 (18.9%) | 6 (8.5%) | 55 (18.6%) | 171 (21.5%) | 184 (19.1%) | 117 (17.1%) | 135 (18.8%) |
| task: reconstruction / imputation | 278 (7.9%) | 0 (0.0%) | 13 (4.4%) | 77 (9.7%) | 63 (6.5%) | 66 (9.6%) | 59 (8.2%) |
| task: workflow / non-interpretive | 167 (4.7%) | 3 (4.2%) | 18 (6.1%) | 38 (4.8%) | 39 (4.0%) | 41 (6.0%) | 28 (3.9%) |
| task: other | 124 (3.5%) | 4 (5.6%) | 12 (4.1%) | 21 (2.6%) | 26 (2.7%) | 36 (5.3%) | 25 (3.5%) |
| task: report generation / LLM | 28 (0.8%) | 0 (0.0%) | 3 (1.0%) | 3 (0.4%) | 5 (0.5%) | 5 (0.7%) | 12 (1.7%) |
| task: foundation model / vision-language | 26 (0.7%) | 0 (0.0%) | 1 (0.3%) | 3 (0.4%) | 6 (0.6%) | 8 (1.2%) | 8 (1.1%) |
| task: agent / autonomous | 2 (0.1%) | 0 (0.0%) | 1 (0.3%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 1 (0.1%) |
| age_groups: child | 1,313 (37.2%) | 33 (46.5%) | 101 (34.2%) | 311 (39.2%) | 368 (38.1%) | 257 (37.5%) | 243 (33.8%) |
| age_groups: adolescent | 900 (25.5%) | 20 (28.2%) | 76 (25.8%) | 181 (22.8%) | 246 (25.5%) | 182 (26.6%) | 195 (27.2%) |
| age_groups: fetal | 795 (22.5%) | 12 (16.9%) | 70 (23.7%) | 171 (21.5%) | 225 (23.3%) | 156 (22.8%) | 161 (22.4%) |
| age_groups: infant | 518 (14.7%) | 10 (14.1%) | 40 (13.6%) | 102 (12.8%) | 138 (14.3%) | 114 (16.6%) | 114 (15.9%) |
| age_groups: pediatric (unspecified) | 504 (14.3%) | 4 (5.6%) | 40 (13.6%) | 115 (14.5%) | 131 (13.6%) | 91 (13.3%) | 123 (17.1%) |
| age_groups: neonate | 348 (9.9%) | 8 (11.3%) | 33 (11.2%) | 75 (9.4%) | 109 (11.3%) | 67 (9.8%) | 56 (7.8%) |
| age_groups: mixed pediatric and adult | 319 (9.0%) | 8 (11.3%) | 27 (9.2%) | 68 (8.6%) | 93 (9.6%) | 62 (9.1%) | 61 (8.5%) |

## Table L2. Selected clinical topic mentions

| Topic | All | 2023–2024 | 2025 | 2026 YTD |
|:--|--:|--:|--:|--:|
| Fetal assessment / prenatal | 764 (21.7%) | 220 (22.8%) | 151 (22.0%) | 149 (20.8%) |
| Brain development / cognition | 357 (10.1%) | 96 (9.9%) | 71 (10.4%) | 63 (8.8%) |
| Autism / ADHD / psychiatric | 314 (8.9%) | 73 (7.6%) | 65 (9.5%) | 59 (8.2%) |
| Cardiac / congenital heart | 242 (6.9%) | 75 (7.8%) | 47 (6.9%) | 61 (8.5%) |
| Bone age / skeletal maturation | 178 (5.0%) | 51 (5.3%) | 26 (3.8%) | 27 (3.8%) |
| Brain / CNS tumors | 165 (4.7%) | 52 (5.4%) | 32 (4.7%) | 33 (4.6%) |
| Pulmonary infection | 162 (4.6%) | 43 (4.5%) | 31 (4.5%) | 39 (5.4%) |
| Scoliosis / spine deformity | 144 (4.1%) | 37 (3.8%) | 39 (5.7%) | 36 (5.0%) |
| Fracture / trauma / abuse | 139 (3.9%) | 37 (3.8%) | 19 (2.8%) | 40 (5.6%) |
| Epilepsy | 82 (2.3%) | 13 (1.3%) | 14 (2.0%) | 14 (1.9%) |
| Liver / biliary | 71 (2.0%) | 27 (2.8%) | 19 (2.8%) | 8 (1.1%) |
| Renal / urinary | 70 (2.0%) | 26 (2.7%) | 11 (1.6%) | 12 (1.7%) |
| Hip dysplasia | 60 (1.7%) | 17 (1.8%) | 12 (1.8%) | 12 (1.7%) |
| Acute abdomen | 44 (1.2%) | 14 (1.5%) | 11 (1.6%) | 13 (1.8%) |
| Chronic lung / airway | 39 (1.1%) | 12 (1.2%) | 7 (1.0%) | 11 (1.5%) |
| Hydrocephalus | 37 (1.0%) | 6 (0.6%) | 6 (0.9%) | 12 (1.7%) |
| Neonatal brain injury | 32 (0.9%) | 12 (1.2%) | 9 (1.3%) | 4 (0.6%) |
| Inflammatory bowel disease | 5 (0.1%) | 1 (0.1%) | 1 (0.1%) | 2 (0.3%) |

## Table L3. Named dataset mentions

| Resource | All | 2025 | 2026 YTD |
|:--|--:|--:|--:|
| ABCD | 83 | 22 | 14 |
| ABIDE | 42 | 9 | 8 |
| RSNA bone age | 42 | 7 | 5 |
| dHCP | 39 | 9 | 3 |
| ADHD-200 | 33 | 8 | 2 |
| CBTN | 17 | 5 | 2 |
| GRAZPEDWRI-DX | 15 | 5 | 6 |
| Guangzhou / Kermany | 13 | 3 | 2 |
| BraTS-PEDs | 12 | 7 | 3 |
| PediCXR / VinDr-PCXR | 5 | 2 | 1 |
| FETAL_PLANES_DB | 5 | 2 | 1 |
| CheXpert (general resource) | 5 | 1 | 0 |
| FeTA | 4 | 0 | 0 |
| Regensburg appendicitis | 3 | 1 | 2 |
| Pediatric-CT-SEG | 2 | 0 | 2 |

## Table L4. Publication status

| Period | Records | Preprint flag |
|:--|--:|--:|
| 2005–2014 | 71 | 0 (0.0%) |
| 2015–2019 | 295 | 3 (1.0%) |
| 2020–2022 | 794 | 29 (3.7%) |
| 2023–2024 | 965 | 81 (8.4%) |
| 2025 | 685 | 62 (9.1%) |
| 2026 YTD | 718 | 56 (7.8%) |

The preprint flag follows the stored source record; online-first and issue dates are not harmonized. Annual counts use the exported publication year. The clinical examples in the manuscript identify earlier online publication where relevant.

## Table L5. Unresolved publication-version candidates

Exact normalized-title matching identified 81 groups (165 records). These are candidates for adjudication, not automatic exclusions. The analysis preserves the shared cohort; the record count is not a verified count of unique investigations. Different titles for different versions will escape this audit.

| Group | Record | Year | Title | DOI |
|--:|:--|--:|:--|:--|
| 1 | 40920305 | 2026 | FetalMLOps: operationalizing machine learning models for standard fetal ultrasound plane classification. | 10.1007/s11517-025-03436-5 |
| 1 | emb:L2036028779 | 2026 | FetalMLOps: operationalizing machine learning models for standard fetal ultrasound plane classification | 10.1007/s11517-025-03436-5 |
| 2 | 41066289 | 2026 | Detailed Delineation of the Fetal Brain in Diffusion MRI via Multi-Task Learning. | 10.1109/TMI.2025.3619809 |
| 2 | 39257731 | 2024 | Detailed delineation of the fetal brain in diffusion MRI via multi-task learning. | 10.1101/2024.08.29.609697 |
| 2 | 39314513 | 2024 | Detailed delineation of the fetal brain in diffusion MRI via multi-task learning. |  |
| 3 | 41068314 | 2026 | Prediction of motor developmental outcomes based on MRI radiomics in premature infants. | 10.1038/s41390-025-04377-3 |
| 3 | emb:L2036664225 | 2024 | Prediction of Motor Developmental Outcomes Based on MRI Radiomics in Premature Infants | 10.2139/ssrn.5068600 |
| 4 | 41238791 | 2026 | Towards automated fetal brain biometry reporting for 3-dimensional T2-weighted 0.55-3T magnetic resonance imaging at 20-40 weeks gestational age range. | 10.1007/s00247-025-06403-2 |
| 4 | emb:L2037732607 | 2025 | Towards automated fetal brain biometry reporting for 3-dimensional T2-weighted 0.55-3T magnetic resonance imaging at 20-40 weeks gestational age range | 10.1101/2025.02.06.25321808 |
| 5 | 41494544 | 2026 | Adolescents with non-suicidal self-injury exhibit increased pain empathic neural reactivity and personal distress to physical but not affective pain. | 10.1016/j.jad.2025.121145 |
| 5 | emb:L2042570799 | 2025 | Adolescents with non-suicidal self-injury exhibit increased pain empathic neural reactivity and personal distress to physical but not affective pain | 10.1101/2025.09.10.25335218 |
| 6 | 41530498 | 2026 | AI-powered segmentation and prognosis with missing MRI in pediatric brain tumors. | 10.1038/s41698-025-01269-x |
| 6 | emb:L2039912979 | 2025 | AI-Powered Segmentation and Prognosis with Missing MRI in Pediatric Brain Tumors | 10.1101/2025.07.14.25331187 |
| 7 | 41571797 | 2026 | Aperiodic parameters of the fMRI power spectrum associate with preterm birth and neonatal age. | 10.1038/s42003-025-09488-5 |
| 7 | emb:L2036917606 | 2024 | Aperiodic parameters of the fMRI power spectrum associate with preterm birth and neonatal age | 10.1101/2024.12.16.24318785 |
| 8 | 41646737 | 2026 | Automated Echocardiographic Detection of Congenital Heart Disease Using Artificial Intelligence. | 10.64898/2026.01.24.26344771 |
| 8 | 41902792 | 2026 | Automated Echocardiographic Detection of Congenital Heart Disease Using Artificial Intelligence. | 10.1161/CIRCULATIONAHA.126.079781 |
| 9 | 41727084 | 2026 | When attention falters: brain, breathing, and behavioral signals of lapses in interoceptive attention. | 10.64898/2026.02.07.704566 |
| 9 | 42332286 | 2026 | When attention falters: Brain, breathing, and behavioral signals of lapses in interoceptive attention. | 10.3758/s13415-026-01467-5 |
| 10 | 41876706 | 2026 | Neuroanatomy reflects individual variability in impulsivity in youth. | 10.1038/s41380-026-03526-2 |
| 10 | 40909792 | 2025 | Neuroanatomy Reflects Individual Variability in Impulsivity in Youth. | 10.21203/rs.3.rs-6520460/v1 |
| 11 | 42013743 | 2026 | BIBSNet: A deep learning baby image brain segmentation network for MRI scans. | 10.1016/j.dcn.2026.101706 |
| 11 | 36993540 | 2025 | BIBSNet: A Deep Learning Baby Image Brain Segmentation Network for MRI Scans. | 10.1101/2023.03.22.533696 |
| 12 | 42040958 | 2026 | Silent Verb Generation during fMRI Reveals Post-Radiotherapy Alterations in Cerebellar-Cerebral Language Regions in Patients Treated for Medulloblastoma. | 10.21203/rs.3.rs-9372156/v1 |
| 12 | 42738316 | 2026 | Silent Verb Generation During fMRI Reveals Post-Radiotherapy Alterations in Cerebellar-Cerebral Language Regions in Patients Treated for Medulloblastoma. | 10.3390/cancers18172795 |
| 13 | 42190896 | 2026 | Classification of familial and non-familial ADHD using auto-encoding network and binary hypothesis testing. | 10.1016/j.brainresbull.2026.111966 |
| 13 | 40894124 | 2025 | Classification of familial and non-familial ADHD using auto-encoding network and binary hypothesis testing. | 10.1101/2025.08.15.25333792 |
| 14 | 42386757 | 2026 | An MRI Atlas of the Human Fetal Brain: Reference and Segmentation Tools for Fetal Brain MRI Analysis. | 10.1038/s41597-026-07608-2 |
| 14 | 40900685 | 2025 | An MRI Atlas of the Human Fetal Brain: Reference and Segmentation Tools for Fetal Brain MRI Analysis. |  |
| 15 | 42501730 | 2026 | Multivariate environmental exposures are reflected in whole-brain functional connectivity and cognition in youth. | 10.1016/j.dcn.2026.101788 |
| 15 | 41292958 | 2025 | Multivariate environmental exposures are reflected in whole-brain functional connectivity and cognition in youth. | 10.1101/2025.11.13.688261 |
| 16 | 42517220 | 2026 | A Multitask Deep Learning Model for Pediatric Echocardiography Analysis. | 10.1161/CIRCULATIONAHA.126.080619 |
| 16 | 41282661 | 2025 | A Multi-Task Deep Learning Model for Pediatric Echocardiography Analysis. | 10.1101/2025.10.27.25338912 |
| 17 | 42774684 | 2026 | Deep learning-based detection of focal cortical dysplasia in children: External validation of the MELD Graph and 3D-nnUNet pipelines. | 10.1016/j.ynirp.2026.100410 |
| 17 | emb:L2045422626 | 2026 | Deep Learning-Based Detection of Focal Cortical Dysplasia in Children: External Validation of the MELD Graph and 3D-nnUNet pipelines | 10.64898/2026.04.21.26351368 |
| 18 | emb:L2040009264 | 2026 | PedVision: A manual-annotation-free and age scalable segmentation pipeline for bone analysis in hand X-ray images | 10.1016/j.bspc.2025.108569 |
| 18 | emb:L2036531047 | 2024 | Pedvision: A Manual-Annotation-Free and Age Scalable Segmentation Pipeline for Bone Analysis in Hand X-Ray Images | 10.2139/ssrn.5050535 |
| 19 | emb:L2042500034 | 2026 | Automated right ventricular assessment in pediatric echocardiography via deep learning improves measurement reliability and reduces variability | 10.1016/j.ibmed.2026.100344 |
| 19 | emb:L2039914104 | 2025 | Automated Right Ventricular Assessment in Pediatric Echocardiography via Deep Learning Improves Measurement Reliability and Reduces Variability | 10.2139/ssrn.5365887 |
| 19 | emb:L2040562547 | 2025 | Automated right ventricular assessment in pediatric echocardiography via deep learning improves measurement reliability and reduces variability | 10.2139/ssrn.5418051 |
| 20 | emb:L2043746724 | 2026 | Intersecting effects of social circumstances and transcendent thinking on mid-adolescents’ longitudinal functional connectome development | 10.2139/ssrn.6233118 |
| 20 | emb:L2039217866 | 2025 | Intersecting effects of social circumstances and transcendent thinking on mid-adolescents’ longitudinal functional connectome development | 10.1101/2025.05.20.654735 |
| 21 | emb:L2043761891 | 2026 | Distal Radial Epiphyseal Fusion Timing in Northwest Europeans and Middle Eastern Asylum Seekers: An Automated Ultrasound and Machine Learning Approach | 10.2139/ssrn.6258351 |
| 21 | emb:L2045356674 | 2026 | Distal radial epiphyseal fusion timing in Northwest Europeans and Middle Eastern asylum seekers: An automated ultrasound and machine learning approach | 10.1016/j.fsir.2026.100479 |
| 22 | 38313196 | 2025 | IVIM-Morph: Motion-compensated quantitative Intra-voxel Incoherent Motion (IVIM) analysis for functional fetal lung maturity assessment from diffusion-weighted MRI data. |  |
| 22 | 39756266 | 2025 | IVIM-Morph: Motion-compensated quantitative Intra-voxel Incoherent Motion (IVIM) analysis for functional fetal lung maturity assessment from diffusion-weighted MRI data. | 10.1016/j.media.2024.103445 |
| 23 | 38570368 | 2025 | Deep Learning for Automated Measurement of Total Cardiac Volume for Heart Transplantation Size Matching. | 10.1007/s00246-024-03470-4 |
| 23 | 38234758 | 2023 | Deep Learning for Automated Measurement of Total Cardiac Volume for Heart Transplantation Size Matching. | 10.21203/rs.3.rs-3788726/v1 |
| 24 | 39152359 | 2025 | Validity of machine learning algorithms for automatically extract growing rod length on radiographs in children with early-onset scoliosis. | 10.1007/s11517-024-03181-1 |
| 24 | emb:L2031007817 | 2025 | Validity of machine learning algorithms for automatically extract growing rod length on radiographs in children with early-onset scoliosis | 10.1007/s11517-024-03181-1 |
| 25 | 39253637 | 2025 | Integrated Brain Connectivity Analysis with fMRI, DTI, and sMRI Powered by Interpretable Graph Neural Networks. |  |
| 25 | 40250104 | 2025 | Integrated brain connectivity analysis with fMRI, DTI, and sMRI powered by interpretable graph neural networks. | 10.1016/j.media.2025.103570 |
| 26 | 39655476 | 2025 | Automated Neuroprognostication Via Machine Learning in Neonates with Hypoxic-Ischemic Encephalopathy. | 10.1002/ana.27154 |
| 26 | emb:L2032645587 | 2024 | Automated Neuroprognostication via Machine Learning in Neonates with Hypoxic-Ischemic Encephalopathy | 10.1101/2024.05.07.24306996 |
| 27 | 39674995 | 2025 | A fully automated measurement of migration percentage on ultrasound images in children with cerebral palsy. | 10.1007/s11517-024-03259-w |
| 27 | emb:L2032606294 | 2025 | A fully automated measurement of migration percentage on ultrasound images in children with cerebral palsy | 10.1007/s11517-024-03259-w |
| 28 | 39777258 | 2025 | Pediatric brain tumor classification using deep learning on MR images with age fusion. | 10.1093/noajnl/vdae205 |
| 28 | emb:L2034988463 | 2024 | Pediatric brain tumor classification using deep learning on MR-images with age fusion | 10.1101/2024.09.05.24313109 |
| 29 | 39838221 | 2025 | Automatic skeletal maturity grading from pelvis radiographs by deep learning for adolescent idiopathic scoliosis. | 10.1007/s11517-025-03283-4 |
| 29 | emb:L2033079723 | 2025 | Automatic skeletal maturity grading from pelvis radiographs by deep learning for adolescent idiopathic scoliosis | 10.1007/s11517-025-03283-4 |
| 30 | 40061352 | 2025 | Quantitative T1 mapping indicates elevated white matter myelin in children with RASopathies. | 10.1101/2025.02.25.25322881 |
| 30 | 40316128 | 2025 | Quantitative T1 Mapping Indicates Elevated White Matter Myelin in Children With RASopathies. | 10.1016/j.biopsych.2025.04.014 |
| 31 | 40172789 | 2025 | An efficient network with state space model under evidential training for fetal echocardiography standard view recognition. | 10.1007/s11517-025-03347-5 |
| 31 | emb:L2034103015 | 2025 | An efficient network with state space model under evidential training for fetal echocardiography standard view recognition | 10.1007/s11517-025-03347-5 |
| 32 | 40304583 | 2025 | Deep Learning Model for Real-Time Nuchal Translucency Assessment at Prenatal US. | 10.1148/ryai.240498 |
| 32 | emb:L2036995633 | 2025 | Deep Learning Model for Real-Time Nuchal Translucency Assessment at Prenatal US | 10.1148/ryai.240498 |
| 33 | 40321262 | 2025 | Automated cervix biometry, volumetry and normative models for 3D motion-corrected T2-weighted 0.55-3T fetal MRI during 2nd and 3rd trimesters. | 10.1101/2025.04.16.25325947 |
| 33 | 41326549 | 2025 | Automated cervix biometry, volumetry and normative models for 3D motion-corrected T2-weighted 0.55-3T fetal MRI during 2nd and 3rd trimesters. | 10.1038/s41598-025-29744-2 |
| 34 | 40372847 | 2025 | CLIF-Net: Intersection-Guided Cross-View Fusion Network for Infection Detection From Cranial Ultrasound. | 10.1109/TMI.2025.3570316 |
| 34 | 40778164 | 2025 | CLIF-Net: Intersection-guided Cross-view Fusion Network for Infection Detection from Cranial Ultrasound. | 10.1101/2025.07.21.25331887 |
| 35 | 40535328 | 2025 | Longitudinal Risk Prediction for Pediatric Glioma with Temporal Deep Learning. | 10.1056/aioa2400703 |
| 35 | 38978642 | 2024 | Longitudinal risk prediction for pediatric glioma with temporal deep learning. | 10.1101/2024.06.04.24308434 |
| 36 | 40612716 | 2025 | A graph neural network approach to investigate brain critical states over neurodevelopment. | 10.1162/netn_a_00451 |
| 36 | emb:L2035793475 | 2024 | A Graph Neural Network Approach to Investigate Brain Critical States Over Neurodevelopment | 10.1101/2024.10.09.617395 |
| 37 | 40654936 | 2025 | Using deep learning to predict internalizing problems from brain structure in youth. | 10.1101/2024.11.28.625869 |
| 37 | 40883286 | 2025 | Using deep learning to predict internalizing problems from brain structure in youth. | 10.1038/s41398-025-03565-3 |
| 38 | 40684513 | 2025 | Integrating multilevel, multidomain and multimodal neuroimaging factors to predict early alcohol exposure trajectories using explainable AI. | 10.1016/j.dcn.2025.101597 |
| 38 | emb:L2038239913 | 2025 | Integrating Multilevel, Multidomain and Multimodal Neuroimaging Factors to Predict Early Alcohol Exposure Trajectories Using Explainable AI | 10.1101/2025.03.12.25323356 |
| 38 | emb:L2038321162 | 2025 | Integrating Multilevel, Multidomain and Multimodal Neuroimaging Factors to Predict Early Alcohol Exposure Trajectories Using Explainable Ai | 10.2139/ssrn.5195030 |
| 39 | 40800807 | 2025 | Streamline tractography of the fetal brain in utero with machine learning. | 10.1162/imag_a_00537 |
| 39 | 39253631 | 2024 | Streamline tractography of the fetal brain in utero with machine learning. |  |
| 40 | 40945816 | 2025 | Neurodevelopmental deviations in schizophrenia: Evidences from multimodal connectome-based brain ages. | 10.1016/j.pnpbp.2025.111498 |
| 40 | emb:L2037149829 | 2024 | Neurodevelopmental deviations in schizophrenia: Evidences from multimodal connectome-based brain ages | 10.1101/2024.12.22.629311 |
| 41 | 40949947 | 2025 | Limited generalizability of dynamic fMRI correlates of adolescent rumination. | 10.1101/2025.08.29.673124 |
| 41 | 41541224 | 2025 | Limited generalizability of dynamic fMRI correlates of adolescent rumination. | 10.1038/s44220-025-00525-0 |
| 42 | 40960398 | 2025 | A Deep Learning Framework for Synthesizing Longitudinal Infant Brain MRI during Early Development. | 10.1148/ryai.240708 |
| 42 | emb:L2037448182 | 2025 | A Deep Learning Framework for Synthesizing Longitudinal Infant Brain MRI during Early Development | 10.1148/ryai.240708 |
| 43 | 40991626 | 2025 | Detection of pneumonia in children through chest radiographs using artificial intelligence in a low-resource setting: A pilot study. | 10.1371/journal.pdig.0000713 |
| 43 | emb:L2036917276 | 2024 | Detection of Pneumonia in Children through Chest Radiographs using Artificial Intelligence in a Low-Resource Setting: A Pilot Study | 10.1101/2024.12.01.24318269 |
| 44 | 40993183 | 2025 | NeoCLIP: a self-supervised foundation model for the interpretation of neonatal radiographs. | 10.1038/s41746-025-01922-6 |
| 44 | emb:L2036917369 | 2024 | NeoCLIP: A Self-Supervised Foundation Model for the Interpretation of Neonatal Radiographs | 10.1101/2024.12.03.24318410 |
| 45 | 41206361 | 2025 | Auto-segmentation of thoraco-abdominal organs in pediatric dynamic MRI. | 10.1002/mp.70104 |
| 45 | 38766023 | 2024 | Auto-segmentation of thoraco-abdominal organs in pediatric dynamic MRI. | 10.1101/2024.05.04.24306582 |
| 46 | 41310360 | 2025 | Segmentation-free pretherapeutic assessment of BRAF-status in pediatric low-grade gliomas. | 10.1038/s43856-025-01204-y |
| 46 | emb:L2037732324 | 2025 | Segmentation-Free Pretherapeutic Assessment of BRAF-Status in Pediatric Low-Grade Gliomas | 10.1101/2025.01.30.25321339 |
| 47 | emb:L2032795091 | 2025 | Ultra-Low-Field Paediatric MRI in Low- and Middle-Income Countries: Super-Resolution Using a Multi-Orientation U-Net | 10.1002/hbm.70112 |
| 47 | emb:L2030896484 | 2024 | Ultra-low-field paediatric MRI in low- and middle-income countries: super-resolution using a multi-orientation U-Net | 10.1101/2024.02.16.580639 |
| 48 | emb:L2037671087 | 2025 | Automatic diagnosis of early pregnancy fetal nasal bone development based on complex mid-sagittal section ultrasound imaging | 10.1016/j.neucom.2025.129773 |
| 48 | emb:L2036242142 | 2024 | Automatic Diagnosis of Early Pregnancy Fetal Nasal Bone Development Based on Complex Mid-Sagittal Section Ultrasound Imaging | 10.2139/ssrn.5033502 |
| 49 | 37961086 | 2024 | Early prognostication of overall survival for pediatric diffuse midline gliomas using MRI radiomics and machine learning: a two-center study. | 10.1101/2023.11.01.23297935 |
| 49 | 39027132 | 2024 | Early prognostication of overall survival for pediatric diffuse midline gliomas using MRI radiomics and machine learning: A two-center study. | 10.1093/noajnl/vdae108 |
| 50 | 38232121 | 2024 | Uncovering the effects of model initialization on deep model generalization: A study with adult and pediatric chest X-ray images. | 10.1371/journal.pdig.0000286 |
| 50 | emb:L2025488478 | 2023 | Uncovering the effects of model initialization on deep model generalization: A study with adult and pediatric chest X-ray images | 10.1101/2023.05.31.23290789 |
| 51 | 38339954 | 2024 | Estimating cortical thickness trajectories in children across different scanners using transfer learning from normative models. | 10.1002/hbm.26565 |
| 51 | emb:L2024392459 | 2023 | Estimating cortical thickness trajectories in children across different scanners using transfer learning from normative models | 10.1101/2023.03.02.530742 |
| 52 | 38446044 | 2024 | Noninvasive Molecular Subtyping of Pediatric Low-Grade Glioma with Self-Supervised Transfer Learning. | 10.1148/ryai.230333 |
| 52 | 37609311 | 2023 | Noninvasive molecular subtyping of pediatric low-grade glioma with self-supervised transfer learning. | 10.1101/2023.08.04.23293673 |
| 53 | 38532493 | 2024 | Menarche, pubertal timing and the brain: female-specific patterns of brain maturation beyond age-related development. | 10.1186/s13293-024-00604-4 |
| 53 | emb:L2026946495 | 2023 | Menarche, pubertal timing and the brain: female-specific patterns of brain maturation beyond age-related development | 10.1101/2023.08.31.23294880 |
| 54 | 38547665 | 2024 | Sensorless volumetric reconstruction of fetal brain freehand ultrasound scans with deep implicit representation. | 10.1016/j.media.2024.103147 |
| 54 | emb:L2031290881 | 2024 | Sensorless volumetric reconstruction of fetal brain freehand ultrasound scans with deep implicit representation | 10.1016/j.media.2024.103147 |
| 55 | 38603863 | 2024 | Predicting depression risk in early adolescence via multimodal brain imaging. | 10.1016/j.nicl.2024.103604 |
| 55 | 37162823 | 2023 | PREDICTING DEPRESSION RISK IN EARLY ADOLESCENCE VIA MULTIMODAL BRAIN IMAGING. | 10.1101/2023.04.10.536286 |
| 56 | 38701657 | 2024 | Deep learning microstructure estimation of developing brains from diffusion MRI: A newborn and fetal study. | 10.1016/j.media.2024.103186 |
| 56 | 37425859 | 2023 | Deep learning microstructure estimation of developing brains from diffusion MRI: a newborn and fetal study. | 10.1101/2023.07.01.547351 |
| 57 | 38712238 | 2024 | Brain age prediction and deviations from normative trajectories in the neonatal connectome. | 10.1101/2024.04.23.590811 |
| 57 | 39592647 | 2024 | Brain age prediction and deviations from normative trajectories in the neonatal connectome. | 10.1038/s41467-024-54657-5 |
| 58 | 38875769 | 2024 | Longitudinal associations between language network characteristics in the infant brain and school-age reading abilities are mediated by early-developing phonological skills. | 10.1016/j.dcn.2024.101405 |
| 58 | 38895379 | 2024 | Longitudinal associations between language network characteristics in the infant brain and school-age reading abilities are mediated by early-developing phonological skills. | 10.1101/2023.06.22.546194 |
| 59 | 38961684 | 2024 | XRAInet: AI-based decision support for pneumothorax and pleural effusion management. | 10.1002/ppul.27133 |
| 59 | emb:L2030471497 | 2024 | XRAInet: AI-based decision support for pneumothorax and pleural effusion management | 10.1002/ppul.27133 |
| 60 | 39182418 | 2024 | Identifying developmental changes in functional brain connectivity associated with cognitive functioning in children and adolescents with ADHD. | 10.1016/j.dcn.2024.101439 |
| 60 | emb:L2029578380 | 2023 | Identifying Developmental Changes in Functional Brain Connectivity Associated with Cognitive Functioning in Children and Adolescents with ADHD | 10.1101/2023.12.20.572617 |
| 61 | 39655845 | 2024 | Ultrasound imaging based recognition of prenatal anomalies: a systematic clinical engineering review. | 10.1088/2516-1091/ad3a4b |
| 61 | emb:L2032183259 | 2024 | Ultrasound imaging based recognition of prenatal anomalies: a systematic clinical engineering review | 10.1088/2516-1091/ad3a4b |
| 62 | 39717438 | 2024 | Automated pediatric brain tumor imaging assessment tool from CBTN: Enhancing suprasellar region inclusion and managing limited data with deep learning. | 10.1093/noajnl/vdae190 |
| 62 | emb:L2033953749 | 2024 | Automated Pediatric Brain Tumor Imaging Assessment Tool from CBTN: Enhancing Suprasellar Region Inclusion and Managing Limited Data with Deep Learning | 10.1101/2024.07.29.24311006 |
| 63 | 40800341 | 2024 | Diffusion deep learning for brain age prediction and longitudinal tracking in children through adulthood. | 10.1162/imag_a_00114 |
| 63 | emb:L2028194741 | 2023 | Diffusion Deep Learning for Brain Age Prediction and Longitudinal Tracking in Children Through Adulthood | 10.1101/2023.10.17.23297166 |
| 64 | 36093915 | 2023 | Accelerated two-dimensional phase-contrast for cardiovascular MRI using deep learning-based reconstruction with complex difference estimation. | 10.1002/mrm.29441 |
| 64 | emb:L2019064810 | 2023 | Accelerated two-dimensional phase-contrast for cardiovascular MRI using deep learning-based reconstruction with complex difference estimation | 10.1002/mrm.29441 |
| 65 | 36515219 | 2023 | 3D-MASNet: 3D mixed-scale asymmetric convolutional segmentation network for 6-month-old infant brain MR images. | 10.1002/hbm.26174 |
| 65 | emb:L2012991291 | 2021 | 3D-MASNet: 3D Mixed-scale Asymmetric Convolutional Segmentation Network for 6-month-old Infant Brain MR Images | 10.1101/2021.05.23.445294 |
| 66 | 36711966 | 2023 | Automated Tumor Segmentation and Brain Tissue Extraction from Multiparametric MRI of Pediatric Brain Tumors: A Multi-Institutional Study. | 10.1101/2023.01.02.22284037 |
| 66 | 37051331 | 2023 | Automated tumor segmentation and brain tissue extraction from multiparametric MRI of pediatric brain tumors: A multi-institutional study. | 10.1093/noajnl/vdad027 |
| 67 | 37205412 | 2023 | Neuro-Environmental Interactions: a time sensitive matter. | 10.1101/2023.05.04.539456 |
| 67 | 38260714 | 2023 | Neuro-environmental interactions: a time sensitive matter. | 10.3389/fncom.2023.1302010 |
| 68 | 37417801 | 2023 | The future of neonatal lung ultrasound: Validation of an artificial intelligence model for interpreting lung scans. A multicentre prospective diagnostic study. | 10.1002/ppul.26563 |
| 68 | emb:L2024275090 | 2023 | The future of neonatal lung ultrasound: Validation of an artificial intelligence model for interpreting lung scans. A multicentre prospective diagnostic study | 10.1002/ppul.26563 |
| 69 | 37707410 | 2023 | Prediction of MYCN Gene Amplification in Pediatric Neuroblastomas: Development of a Deep Learning-Based Tool for Automatic Tumor Segmentation and Comparative Analysis of Computed Tomography-Based Radiomics Features Harmonization. | 10.1097/RCT.0000000000001480 |
| 69 | emb:L2027304409 | 2023 | Prediction of MYCN Gene Amplification in Pediatric Neuroblastomas: Development of a Deep Learning-Based Tool for Automatic Tumor Segmentation and Comparative Analysis of Computed Tomography-Based Radiomics Features Harmonization | 10.1097/RCT.0000000000001480 |
| 70 | 34795038 | 2022 | Using chest computed tomography and unsupervised machine learning for predicting and evaluating response to lumacaftor-ivacaftor in people with cystic fibrosis. | 10.1183/13993003.01344-2021 |
| 70 | emb:L636766776 | 2022 | Using chest computed tomography and unsupervised machine learning for predicting and evaluating response to lumacaftor-ivacaftor in people with cystic fibrosis | 10.1183/13993003.01344-2021 |
| 71 | 35585848 | 2022 | Through-Plane Super-Resolution With Autoencoders in Diffusion Magnetic Resonance Imaging of the Developing Human Brain. | 10.3389/fneur.2022.827816 |
| 71 | emb:L2016436618 | 2021 | Through-plane super-resolution with autoencoders in diffusion magnetic resonance imaging of the developing human brain | 10.1101/2021.12.06.471406 |
| 72 | 35616520 | 2022 | Structural differences in adolescent brains can predict alcohol misuse. | 10.7554/eLife.77545 |
| 72 | emb:L2017166020 | 2022 | Structural differences in adolescent brains can predict alcohol misuse | 10.1101/2022.01.31.22269833 |
| 73 | 35649314 | 2022 | Automated 3D reconstruction of the fetal thorax in the standard atlas space from motion-corrupted MRI stacks for 21-36 weeks GA range. | 10.1016/j.media.2022.102484 |
| 73 | emb:L2015042740 | 2021 | Automated 3D reconstruction of the fetal thorax in the standard atlas space from motion-corrupted MRI stacks for 21-36 weeks GA range | 10.1101/2021.09.22.461335 |
| 74 | 35797364 | 2022 | Identifying neuroanatomical and behavioral features for autism spectrum disorder diagnosis in children using machine learning. | 10.1371/journal.pone.0269773 |
| 74 | emb:L2010333989 | 2020 | Identifying Neuroanatomical and Behavioral Features for Autism Spectrum Disorder Diagnosis in Children using Machine Learning | 10.1101/2020.11.09.20227843 |
| 75 | 35852028 | 2022 | Systematic evaluation of machine learning algorithms for neuroanatomically-based age prediction in youth. | 10.1002/hbm.26010 |
| 75 | emb:L2015898396 | 2021 | Systematic Evaluation of Machine Learning Algorithms for Neuroanatomically-Based Age Prediction in Youth | 10.1101/2021.11.24.469888 |
| 76 | 35958478 | 2022 | Temporal bone CT-based deep learning models for differential diagnosis of primary ciliary dyskinesia related otitis media and simple otitis media with effusion. |  |
| 76 | emb:L2019706419 | 2022 | Temporal bone CT-based deep learning models for differential diagnosis of primary ciliary dyskinesia related otitis media and simple otitis media with effusion |  |
| 77 | 34026587 | 2021 | Bone Age Assessment of Iranian Children in an Automatic Manner. | 10.4103/jmss.JMSS_9_20 |
| 77 | emb:L634106700 | 2021 | Bone age assessment of iranian children in an automatic manner | 10.4103/jmss.JMSS-9-20 |
| 78 | 34405049 | 2021 | A comparison of machine learning classifiers for pediatric epilepsy using resting-state functional MRI latency data. | 10.3892/br.2021.1453 |
| 78 | emb:L2013097559 | 2021 | A comparison of machine learning classifiers for pediatric epilepsy using resting-state functional MRI latency data |  |
| 79 | 32975706 | 2020 | Automated measurement network for accurate segmentation and parameter modification in fetal head ultrasound images. | 10.1007/s11517-020-02242-5 |
| 79 | emb:L2006794605 | 2020 | Automated measurement network for accurate segmentation and parameter modification in fetal head ultrasound images | 10.1007/s11517-020-02242-5 |
| 80 | 25540897 | 2015 | Comparison on three classification techniques for sex estimation from the bone length of Asian children below 19 years old: an analysis using different group of ages. | 10.1016/j.forsciint.2014.11.007 |
| 80 | emb:L601043471 | 2014 | Comparison on three classification techniques for sex estimation from the bone length of Asian children below 19 years old: An analysis using different group of ages | 10.1016/j.forsciint.2014.11.007 |
| 81 | 25910262 | 2015 | Standard Plane Localization in Fetal Ultrasound via Domain Transferred Deep Neural Networks. | 10.1109/JBHI.2015.2425041 |
| 81 | emb:L605898293 | 2015 | Standard Plane Localization in Fetal Ultrasound via Domain Transferred Deep Neural Networks | 10.1109/JBHI.2015.2425041 |

## Table L6. Sensitivity to retaining one record per normalized title

Prefer a record without a preprint flag, then a PubMed record, then the latest publication year. This heuristic tests composition stability; it is not a replacement for version adjudication. Different titles can still represent the same investigation.

The sensitivity set contains 3,444 records, compared with 3,528 in the shared cohort.

| Modality | Shared cohort | One record per title |
|:--|--:|--:|
| MRI | 1,604 (45.5%) | 1,549 (45.0%) |
| ultrasound | 837 (23.7%) | 821 (23.8%) |
| x-ray / radiography | 685 (19.4%) | 676 (19.6%) |
| CT | 326 (9.2%) | 322 (9.3%) |
| nuclear / PET | 53 (1.5%) | 53 (1.5%) |
| fluoroscopy | 13 (0.4%) | 13 (0.4%) |
