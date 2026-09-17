## FDA pediatric-use inventory (source-exhaustive screen)

This appendix screens **all 1,230 records in the Radiology lead panel** of the FDA AI-enabled-device CSV downloaded 2026-09-16. Each linked FDA decision-summary PDF was downloaded when available and its intended-use text searched for pediatric, fetal, infant, neonatal, child, adolescent, and pregnancy terms. A *label-positive candidate* has a direct patient-population or intended-use statement; a *needs label review* record contains a conflicting, exclusionary, validation-only, or ambiguous mention. This is exhaustive for the dated FDA-list snapshot, not a claim that the FDA list itself captures every AI device. See the [screening dataset](../data/processed/fda_pediatric_inventory.json) and [collector](../scripts/collect_fda_pediatric_inventory.py).

- 283 records had a pediatric/fetal keyword in extracted evidence.
- 230 are label-positive candidates; 53 require manual label review.
- Evidence text was available for 1,588 records; 1 need OCR and 25 linked documents were unavailable.
- 1,230 Radiology-panel records were in the source CSV; data/raw/fda_pediatric_inventory/2026-09-16/ai_devices.csv.

### Label-positive candidates

| Submission | Decision date | Company | Device | Product code | Evidence pages |
|:--|:--|:--|:--|:--|:--:|
| DEN250007 | 02/11/2026 | Ultrasound AI | Delivery Date AI | SHE | 1, 2 |
| K163253 | 01/05/2017 | ARTERYS INC. | Arterys Cardio DL | LLZ | 5 |
| K172356 | 09/15/2017 | Verathon Incorporated | BladderScan Prime PLUS System | IYO | 4, 5 |
| K172385 | 09/14/2017 | Clarius Mobile Health Corp. | Clarius Ultrasound System | IYN | 4, 6 |
| K180799 | 05/14/2018 | Clarius Mobile Health Corp. | Clarius Ultrasound Scanner | IYN | 4, 5 |
| K181574 | 07/10/2018 | EchoNous, Inc. | Uscan | IYO | 3, 4 |
| K181685 | 10/25/2018 | GE Medical Systems Ultrasound and Primary Care Diagnostics, | Vivid E80, Vivid E90, Vivid E95 | IYN | 3, 5 |
| K191171 | 11/13/2019 | Ultromics Ltd | EchoGo Core | QIH | 5, 6 |
| K191278 | 11/19/2019 | MultiModal Imaging Services Corporation (dba HealthLytix) | RSI-MRI+ | LLZ | 3, 5 |
| K192107 | 08/29/2019 | Clarius Mobile Health Corp. | Clarius Ultrasound Scanner | IYN | 3, 4 |
| K192377 | 02/10/2020 | Varian Medical Systems, Inc. | Ethos Treatment Management, Ethos Treatment Planning, Ethos Radiotherapy System, Halcyon | IYE | 3, 5 |
| K193518 | 03/26/2020 | EchoNous, Inc. | KOSMOS | IYN | 3, 5 |
| K200232 | 06/23/2020 | DiA Imaging Analysis Ltd | LVivo Software Application | QIH | 5 |
| K200356 | 06/11/2020 | Medo.ai | MEDO ARIA | QIH | 3, 5 |
| K200980 | 06/11/2020 | Butterfly Network, Inc. | Auto 3D Bladder Volume Tool | IYO | 6 |
| K201012 | 05/01/2020 | Philips Ultrasound, Inc. | EPIQ Diagnostic Ultrasound System Series, Affiniti Diagnostic Ultrasound System Series, CX50 Diagnostic Ultrasound System, Sparq Diagnostic Ultrasound System, Lumify Diagnostic Ultrasound System | IYN | 3, 4 |
| K201039 | 12/07/2020 | Resonance Health Analysis Services Pty Ltd | HepaFat-AI | LNH | 9 |
| K201632 | 08/14/2020 | TOMTEC Imaging Systems GmbH | TOMTEC-ARENA | LLZ | 6, 12 |
| K210426 | 05/13/2021 | Samsung Medison CO., LTD. | HS40 Diagnostic Ultrasound System | IYN | 3, 5 |
| K210556 | 04/21/2021 | Genesis Software Innovations | Preview Shoulder | QIH | 9 |
| K210760 | 01/14/2022 | Philips Medical Systems Nederland, B.V. | Precise Image | JAK | 5 |
| K211597 | 09/08/2021 | Philips Medical Systems | EPIQ Series Diagnostic Ultrasound System, Affiniti Series Diagnostic Ultrasound System | IYN | 7 |
| K211611 | 09/30/2022 | CASIS Cardiac Simulation & Imaging Software | QIR Suite | QIH | 7, 10 |
| K211824 | 09/09/2021 | Samsung Medison Co., Ltd. | HERA W9, HERA W10 Diagnostic Ultrasound System | IYN | 3, 5 |
| K211945 | 09/08/2021 | Samsung Medison CO., LTD. | V8 Diagnostic Ultrasound System | IYN | 3, 5 |
| K211966 | 05/06/2022 | Medviso AB | Segment 3DPrint | LLZ | 3, 5 |
| K212012 | 01/19/2022 | Cycle Clarity | Follicle Clarity | QIH | 5 |
| K212100 | 08/06/2021 | EchoNous, Inc. | Kosmos | IYN | 6, 7 |
| K212265 | 11/16/2021 | Shenzhen Mindray Bio-Medical Electronics Co.,LTD | TEX20/TEX20 Pro/TEX20S/TEX20T/TEX20 Exp/TEX20 Elite Diagnostic Ultrasound System, TEX10/ TEX10 Pro/TEX10S/TEX10T/TEX10 Exp/TEX10 Elite/TE X/TE X Lite Diagnostic Ultrasound System | IYN | 3, 5 |
| K212269 | 09/17/2021 | Canon Inc. | Intelligent NR | MQB | 5 |
| K212336 | 11/17/2021 | Omega Medical Imaging, LLC | Soteria.AI | OWB | 4 |
| K212616 | 12/16/2021 | Koios Medical, Inc. | Koios DS | POK | 13 |
| K212654 | 02/04/2022 | OXOS Medical, Inc. | Micro C Medical Imaging System, M01 | IZL | 6, 7 |
| K212704 | 09/24/2021 | Philips Medical Systems | Philips EPIQ Diagnostic Ultrasound System, Philips Affiniti Diagnostic Ultrasound System | IYN | 3, 4 |
| K213272 | 03/31/2023 | Formus Labs, Ltd | Formus Hip | QIH | 6 |
| K213436 | 11/15/2021 | Clarius Mobile Health Corp. | Clarius Ultrasound Scanner | IYN | 5, 6 |
| K213544 | 01/06/2022 | TOMTEC Imaging Systems GmbH | TOMTEC-ARENA | QIH | 8 |
| K213689 | 02/17/2022 | GE Healthcare | Voluson P6, Voluson P8 | IYN | 3, 5 |
| K213886 | 04/26/2022 | Aidoc Medical, Ltd. | BriefCase | QAS | 3, 5 |
| K214043 | 03/14/2022 | Aidoc Medical, Ltd. | BriefCase | QFM | 3, 5 |
| K220043 | 04/05/2022 | Samsung Medison Co., LTD | HERA W10 Diagnostic Ultrasound System, HERA W9 Diagnostic Ultrasound System | IYN | 5 |
| K220068 | 03/31/2023 | Butterfly Network, Inc. | Butterfly iQ/iQ+ Ultrasound System | IYO | 3, 5 |
| K220358 | 06/06/2022 | GE Medical Systems Ultrasound and Primary Care Diagnostics, | Voluson Expert 22, Voluson Expert 20, Voluson Expert 18 | IYN | 5 |
| K220497 | 06/23/2022 | Smart Soft Healthcare AD | CoLumbo | QIH | 3, 6 |
| K220709 | 10/07/2022 | Aidoc Medical, Ltd. | BriefCase | QAS | 3, 5 |
| K220813 | 06/17/2022 | TheraPanacea | ART-PLAN | QKB | 30 |
| K220848 | 06/27/2022 | GE Medical Systems | Venue Fit | IYN | 7 |
| K220851 | 06/27/2022 | GE Medical Systems | Venue | IYN | 7 |
| K220975 | 06/29/2022 | Samsung Medison Co., Ltd. | V8 Diagnostic Ultrasound System, V7 Diagnostic Ultrasound System | IYN | 3, 5 |
| K221240 | 05/17/2022 | Aidoc Medical, Ltd. | BriefCase | QAS | 3, 5 |
| K221314 | 06/03/2022 | Aidoc Medical, Ltd. | BriefCase | QAS | 3, 5 |
| K221330 | 11/18/2022 | Aidoc Medical, Ltd. | BriefCase | QAS | 3, 5 |
| K221393 | 06/10/2022 | Hyperfine, Inc. | Swoop Portable MR Imaging System | LNH | 5 |
| K221599 | 08/22/2022 | Samsung Medison Co., Ltd. | HS40 Diagnostic Ultrasound System | IYN | 3, 5 |
| K221923 | 07/28/2022 | Hyperfine, Inc. | Swoop Portable MR Imaging System | LNH | 5 |
| K222176 | 03/02/2023 | Gleamer | BoneView | QBS | 5, 7 |
| K222277 | 08/26/2022 | Aidoc Medical, Ltd. | BriefCase | QAS | 3, 5 |
| K222329 | 09/28/2022 | Aidoc Medical, Ltd. | BriefCase | QAS | 3, 5 |
| K222406 | 01/23/2023 | Clarius Mobile Health Corp. | Clarius AI | QIH | 9 |
| K222428 | 11/14/2022 | Siemens Medical Solutions USA, Inc. | Syngo Dynamics (Version VA40F) | QIH | 5 |
| K222755 | 02/16/2023 | Shanghai United Imaging Intelligence Co., Ltd. | uMR 680 | LNH | 8 |
| K223268 | 12/16/2022 | Hyperfine, Inc. | BrainInsight | QIH | 5 |
| K223387 | 02/13/2023 | Samsung Medison Co., Ltd. | V8 Diagnostic Ultrasound System, V7 Diagnostic Ultrasound System | IYN | 3, 5 |
| K223491 | 05/25/2023 | GE Medical Systems, LLC | Critical Care Suite with Pneumothorax Detection AI Algorithm, Critical Care Suite 2.1, Critical Care Suite | QBS | 5, 6 |
| K223771 | 05/04/2023 | Philips Ultrasound | Lumify Diagnostic Ultrasound System | IYN | 5, 8 |
| K223830 | 04/11/2023 | BK Medical Aps | Ultrasound System 2300 | IYN | 3, 12 |
| K230020 | 02/01/2023 | Aidoc Medical, Ltd. | BriefCase | QFM | 3, 4 |
| K230084 | 04/21/2023 | Samsung Medison CO., LTD. | HERA W10 Diagnostic Ultrasound System; HERA W9 Diagnostic Ultrasound System | IYN | 3, 5 |
| K230112 | 06/13/2023 | Imbio, Inc. | CAC Software | JAK | 8 |
| K230179 | 11/29/2023 | Esaote S.p.A. | 6440 MyLabX90 | IYN | 7 |
| K230208 | 02/22/2023 | Hyperfine, Inc. | Swoop® Portable MR Imaging System | LNH | 5 |
| K230209 | 10/20/2023 | Ontact Health Co., Ltd. | Sonix Health | QIH | 6 |
| K230346 | 06/20/2023 | GE Medical Systems Ultrasound & Primary Care Diagnostic, LLC | Voluson SWIFT; Voluson SWIFT+ | IYN | 3, 5 |
| K230365 | 07/25/2023 | Sonio | Sonio Detect | IYN | 3, 5 |
| K231001 | 10/05/2023 | DeepTek Medical Imaging Pvt Ltd | DeepTek CXR Analyzer v1.0 | MYN | 3, 6 |
| K231190 | 05/12/2023 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound System | IYN | 3 |
| K231677 | 03/06/2024 | Edgecare Inc. | EdgeFlow UH10 | IYO | 8 |
| K231764 | 10/23/2023 | BK Medical Aps | Ultrasound System 1300 | IYN | 11, 12 |
| K231772 | 10/03/2023 | Samsung Medison Co., Ltd. | V8/H8 Diagnostic Ultrasound System, V7/H7 Diagnostic Ultrasound System, V6/H6 Diagnostic Ultrasound System | IYN | 3, 5 |
| K231917 | 01/05/2024 | EOS imaging | VEA Align | QIH | 3, 5 |
| K231965 | 10/30/2023 | GE Medical Systems Ultrasound and Primary Care Diagnostics, | Voluson Expert 22, Voluson Expert 20, Voluson Expert 18 | IYN | 3, 5 |
| K231966 | 11/07/2023 | GE Medical Systems Ultrasound and Primary care Diagnostics, | LOGIQ E10 | IYN | 5 |
| K232083 | 11/13/2023 | Aidoc Medical, Ltd. | BriefCase-Quantification | QIH | 3, 4 |
| K232145 | 10/30/2023 | Siemens Medical Solutions USA, Inc. | ACUSON Sequoia Diagnostic Ultrasound System, ACUSON Sequoia Select Diagnostic Ultrasound System, ACUSON Origin Diagnostic Ultrasound System | IYN | 6, 7 |
| K232231 | 12/13/2023 | Quibim S.L. | QP-Brain® | QIH | 4, 6 |
| K232257 | 11/13/2023 | Clarius Mobile Health Corp. | Clarius Bladder AI | QIH | 10 |
| K232384 | 12/15/2023 | VideaHealth, Inc. | Videa Dental Assist | MYN | 9, 17 |
| K232410 | 05/10/2024 | Milvue | SmartChest | QFM | 6 |
| K232500 | 10/26/2023 | Philips Ultrasound | Lumify Diagnostic Ultrasound System | IYN | 5 |
| K232613 | 02/28/2024 | Innolitics, LLC | CT Cardiomegaly | QIH | 3, 6 |
| K232698 | 01/18/2024 | Software Nemotec S.L. | NemoScan | QIH | 3, 5 |
| K232704 | 10/05/2023 | Clarius Mobile Health Corp. | Clarius Ultrasound Scanner | IYN | 5, 6 |
| K232751 | 10/30/2023 | Aidoc Medical, Ltd. | BriefCase-Triage | QAS | 4, 6 |
| K232760 | 10/06/2023 | Hyperfine, Inc. | Swoop® Portable MR Imaging System® | LNH | 6 |
| K232808 | 01/04/2024 | Butterfly Network, Inc. | Butterfly iQ3 Ultrasound System | IYN | 3, 5 |
| K233030 | 03/01/2024 | MRIguidance B.V | BoneMRI | QIH | 7, 9 |
| K233247 | 05/15/2024 | Heuron Co., Ltd. | Heuron ICH | QAS | 3, 4 |
| K233457 | 07/12/2024 | Hutom Inc. | RUS | QIH | 7 |
| K233543 | 05/21/2024 | Siemens Medical Solutions | YSIO X.pree | KPR | 7 |
| K233545 | 11/30/2023 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound System | IYN | 3, 5 |
| K233738 | 03/04/2024 | Overjet, Inc | Overjet Caries Assist-Pediatric | MYN | 4, 5 |
| K233788 | 02/13/2024 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound System, Affiniti Series Diagnostic Ultrasound System | IYN | 6, 7 |
| K233955 | 06/14/2024 | Clarius Mobile Health Corp. | Clarius OB AI | IYN | 4, 6 |
| K233968 | 03/13/2024 | Avicenna.AI | CINA-iPE | QAS | 3, 6 |
| K233977 | 09/04/2024 | Sonic Incytes | Velacur | IYO | 3, 5 |
| K234042 | 06/07/2024 | Ever Fortune.AI Co., Ltd. | EFAI Bonesuite XR Bone Age Pro Assessment System (BAP-XR-100) | QIH | 5, 6 |
| K240291 | 04/08/2024 | Ever Fortune.AI, Co., Ltd. | EFAI CARDIOSUITE CTA ACUTE AORTIC SYNDROME ASSESSMENT SYSTEM | QAS | 6 |
| K240406 | 04/26/2024 | Sonio | Sonio Detect | IYN | 3, 5 |
| K240516 | 06/12/2024 | Samsung Medison Co., Ltd. | RS85 Diagnostic Ultrasound System | IYN | 3 |
| K240582 | 06/25/2024 | EOS imaging | VEA Align; spineEOS | QIH | 3, 6 |
| K240631 | 06/21/2024 | Samsung Medison Co., Ltd. | V8/XV8/XH8, V7/XV7/XH7, V6/XV6/XH6 Diagnostic Ultrasound System | IYN | 3 |
| K240704 | 07/22/2024 | Siemens Medical Solutions, USA, Inc. | ACUSON Sequoia Diagnostic Ultrasound System, ACUSON Sequoia Select Diagnostic Ultrasound System, ACUSON Origin Diagnostic Ultrasound System, ACUSON Origin ICE  Diagnostic Ultrasound System | IYN | 3, 7 |
| K240793 | 12/16/2024 | MSKai | MSKai | QIH | 4, 7 |
| K240845 | 07/17/2024 | AZmed SAS | Rayvolve | QBS | 3, 7 |
| K240850 | 04/24/2024 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound Systems; Affiniti Series Diagnostic Ultrasound Systems | IYN | 6, 7 |
| K240944 | 07/16/2024 | Hyperfine, Inc. | Swoop® Portable MR Imaging® System | LNH | 5 |
| K240980 | 10/07/2024 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound System | IYN | 6 |
| K241029 | 10/07/2024 | Verdure Imaging | SpineUs System | IYO | 7 |
| K241108 | 10/30/2024 | Remedy Logic Inc. | RemedyLogic AI MRI Lumbar Spine Reader | QIH | 4, 6 |
| K241112 | 05/15/2024 | Aidoc Medical, Ltd. | BriefCase-Quantification | QIH | 5, 6 |
| K241211 | 08/15/2024 | Smart Soft Healthcare | CoLumbo | QIH | 3, 5 |
| K241331 | 10/01/2024 | Springbok, Inc. | MuscleView | LNH | 15 |
| K241380 | 09/11/2024 | Diagnoly | FETOLY-HEART | IYN | 4, 6 |
| K241659 | 02/10/2025 | Philips Ultrasound LLC | Ultrasound Workspace (UWS 6.0) | QIH | 5, 7 |
| K241727 | 07/12/2024 | Aidoc Medical, Ltd. | BriefCase-Triage | QAS | 3, 5 |
| K241949 | 01/17/2025 | Sonoscape Medical Corp. | Digital Color Doppler Ultrasound System (P60 Series) | IYN | 4, 6 |
| K241971 | 10/11/2024 | Samsung Medison Co., Ltd. | HERA Z20, R20, HERA Z30, R30 Diagnostic Ultrasound System | IYN | 4 |
| K242020 | 12/12/2024 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound System; Affiniti Series Diagnostic Ultrasound System | IYN | 3, 6 |
| K242062 | 11/15/2024 | Mycardium AI Limited | 1CMR Pro | LLZ | 4, 6 |
| K242168 | 12/20/2024 | GE Medical Systems Ultrasound and Primary care Diagnostics | Voluson Expert 18; Voluson Expert 20; Voluson Expert 22 | IYN | 5 |
| K242171 | 01/17/2025 | Milvue | TechCare Trauma | QBS | 8, 9 |
| K242203 | 11/22/2024 | Aidoc Medical, Ltd. | BriefCase-Quantification | QIH | 4, 6 |
| K242342 | 11/14/2024 | BrightHeart | Fetal EchoScan | POK | 3, 5 |
| K242444 | 11/27/2024 | Samsung Medison Co., Ltd. | HERA W10 Diagnostic Ultrasound System; HERA W9 Diagnostic Ultrasound System | IYN | 4, 6 |
| K242488 | 01/06/2025 | Omega Medical Imaging, LLC | Soteria E-View | JAA | 4, 6 |
| K242511 | 12/10/2024 | Samsung Medison Co., Ltd. | V5 Diagnostic Ultrasound System, H5 Diagnostic Ultrasound System, XV5 Diagnostic Ultrasound System, XH5 Diagnostic Ultrasound System, V4 Diagnostic Ultrasound System, H4 Diagnostic Ultrasound System, XV4 Diagnostic Ultrasound System, XH4 Diagnostic Ultrasound System | IYN | 6 |
| K242523 | 11/19/2024 | Siemens Medical Solutions USA, Inc. | ACUSON Sequoia Diagnostic Ultrasound System; ACUSON Sequoia Select Diagnostic Ultrasound System; ACUSON Origin Diagnostic Ultrasound System; ACUSON Origin ICE Diagnostic Ultrasound System | IYN | 4, 5 |
| K242551 | 04/03/2025 | Siemens Healthcare GmbH | syngo Dynamics (Version VA41D) | QIH | 6 |
| K242594 | 05/23/2025 | DeepEcho | DEEPECHO | IYN | 4, 6 |
| K242607 | 02/21/2025 | ScanDiags AG | ScanDiags Ortho L-Spine MR-Q | QIH | 4, 7 |
| K242800 | 11/15/2024 | Philips Ultrasound LLC | The 5000 Compact Series Ultrasound Systems | IYN | 4, 6 |
| K242821 | 02/20/2025 | Ever Fortune.AI, Co., Ltd. | EFAI Chestsuite XR Malpositioned ETT Assessment System (ETT-XR-100) | QAS | 7 |
| K242837 | 10/18/2024 | Aidoc Medical, Ltd. | BriefCase-Triage | QAS | 6, 7 |
| K243548 | 12/11/2024 | Aidoc Medical, Ltd. | BriefCase-Triage | QFM | 3, 5 |
| K243614 | 02/21/2025 | Sonio | Sonio Suspect | POK | 4, 8 |
| K243684 | 05/07/2025 | BrightHeart | BrightHeart View Classifier | QIH | 4, 5 |
| K243702 | 02/12/2025 | Samsung Medison Co., Ltd. | V8 Diagnostic Ultrasound System; cV8 Diagnostic Ultrasound System; V7 Diagnostic Ultrasound System; cV7 Diagnostic Ultrasound System; V6 Diagnostic Ultrasound System; cV6 Diagnostic Ultrasound System | IYN | 4, 6 |
| K243779 | 07/01/2025 | BunkerHill Health | Bunkerhill Abdominal Aortic Quantification (AAQ) | QIH | 6 |
| K243793 | 05/21/2025 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound System; Affiniti Series Diagnostic Ultrasound System | IYN | 7, 8 |
| K243794 | 02/06/2025 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound System; Affiniti Series Diagnostic Ultrasound System | IYN | 4, 7 |
| K243859 | 08/29/2025 | Nurea | PRAEVAorta®2 | QIH | 8, 10 |
| K243893 | 05/05/2025 | Pearl, Inc. | Second Opinion® Pediatric | MYN | 6, 9 |
| K250177 | 04/10/2025 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound System; Affiniti Series Diagnostic Ultrasound System | IYN | 4, 7 |
| K250236 | 05/30/2025 | Hyperfine, Inc. | Swoop® Portable MR Imaging® System (V2) | LNH | 6 |
| K250237 | 09/15/2025 | Beijing Infervision Healthcare Medical Technology Co., Ltd. | InferOperate Suite | QIH | 7 |
| K250248 | 02/14/2025 | Aidoc Medical, Ltd. | BriefCase-Triage | QAS | 3, 5 |
| K250367 | 05/28/2025 | Smart Soft Healthcare AD | CoLumboX | QIH | 4, 6 |
| K250370 | 05/20/2025 | FUJIFILM Corporation | SCENARIA View Phase 5.0 | JAK | 11 |
| K250416 | 04/11/2025 | Galileo CDS, Inc | GBrain MRI | QIH | 7, 8 |
| K250660 | 07/14/2025 | Siemens Medical Solutions | LUMINOS Q.namix T; LUMINOS Q.namix R | OWB | 4, 7 |
| K250670 | 06/30/2025 | Mycardium AI Limited | EchoConfidence (USA) | QIH | 4, 6 |
| K250686 | 07/22/2025 | NeuroSpectrum Insights Corp. | GyriCalc (Version 1.0.0) | LLZ | 4, 8 |
| K250886 | 06/18/2025 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound Systems; Affiniti Series Diagnostic Ultrasound Systems | IYN | 4, 8 |
| K250914 | 12/18/2025 | Crescom Co., Ltd. | MediAI-BA | QIH | 6, 7 |
| K250959 | 12/22/2025 | Bioticsai, Inc. | BioticsAI | IYN | 4, 6 |
| K250999 | 07/18/2025 | Samsung Medison Co., Ltd. | V8 Diagnostic Ultrasound System; cV8 Diagnostic Ultrasound System; V7 Diagnostic Ultrasound System; cV7 Diagnostic Ultrasound System; V6 Diagnostic Ultrasound System; cV6 Diagnostic Ultrasound System; V5 Diagnostic Ultrasound System; cV5 Diagnostic Ultrasound System; V4 Diagnostic Ultrasound System; cV4 Diagnostic Ultrasound System | IYN | 4, 6 |
| K251002 | 09/19/2025 | VideaHealth Inc. | Videa Dental AI | MYN | 10 |
| K251071 | 05/02/2025 | BrightHeart | Fetal EchoScan (v1.1) | POK | 4, 5 |
| K251078 | 11/14/2025 | Eos Imaging | AutoDensity | QIH | 8, 9 |
| K251110 | 05/09/2025 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound Systems; Affiniti Series Diagnostic Ultrasound Systems | IYN | 4, 6 |
| K251167 | 09/19/2025 | Shanghai United Imaging Healthcare Co., Ltd. | uDR Aurora CX | KPR | 7 |
| K251195 | 01/27/2026 | Aidoc Medical , Ltd. | BriefCase-Triage | QAS | 4, 6 |
| K251276 | 05/21/2025 | Hyperfine, Inc. | Swoop® Portable MR Imaging® System | LNH | 6 |
| K251322 | 07/25/2025 | GE Medical Systems Ultrasound and Primary care Diagnostics, | Venue; Venue Go; Venue Fit; Venue Sprint | IYN | 7, 8 |
| K251368 | 09/12/2025 | Diagnoly | FETOLY | IYN | 6, 10 |
| K251370 | 12/01/2025 | Canon Medical Systems Corporation | Cartesion Prime (PCD-1000A/3) V10.21 | KPS | 8 |
| K251406 | 05/30/2025 | Aidoc Medical, Ltd. | BriefCase-Triage | QAS | 4, 6 |
| K251455 | 07/24/2025 | Philips Ultrasound LLC | EPIQ Series Diagnostic Ultrasound System; Affiniti Series Diagnostic Ultrasound System | IYN | 4, 8 |
| K251456 | 06/05/2025 | BrightHeart | BrightHeart View Classifier | QIH | 5, 6 |
| K251481 | 08/20/2025 | Siemens Medical Solutions USA, Inc. | ACUSON Sequoia Diagnostic Ultrasound System; ACUSON Sequoia Select Diagnostic Ultrasound System; ACUSON Origin Diagnostic Ultrasound System; ACUSON Origin ICE Diagnostic Ultrasound System | IYN | 8, 9 |
| K251514 | 12/05/2025 | Overjet, Inc. | Overjet CBCT Assist | QIH | 7 |
| K251532 | 11/03/2025 | Mighty Oak Medical | Acorn 3D Software (AC-SEG-4009); Acorn 3DP Model (AC-101-XX) | LLZ | 7 |
| K251651 | 10/09/2025 | Philips Ultrasound, LLC | EPIQ Series Diagnostic Ultrasound System; Affiniti Series Diagnostic Ultrasound System | IYN | 4, 7 |
| K251673 | 10/17/2025 | X9, Inc. | X9 Ultrasound System | SGH | 4, 6 |
| K251682 | 09/09/2025 | Springbok, Inc. (dba Springbok Analytics) | MuscleView 2.0 | LNH | 5, 8 |
| K251747 | 08/15/2025 | EOS imaging | VEA Align; spineEOS | QIH | 4, 6 |
| K251963 | 10/29/2025 | Ge Medical Systems Ultrasound and Primary Care Diagnostics | LOGIQ E10s | IYN | 4, 6 |
| K251985 | 10/29/2025 | Ge Medical Systems Ultrasound and Primary Care Diagnostics | LOGIQ E10 | IYN | 4, 6 |
| K252103 | 12/02/2025 | Mighty Oak Medical | Acorn 3D Software (AC-SEG-4009); Acorn 3DP Model (AC-101-XX) | QIH | 4, 7 |
| K252148 | 03/27/2026 | Butterfly Network, Inc. | Butterfly Gestational Age Tool | IYN | 4, 7 |
| K252188 | 01/15/2026 | Elekta Solutions AB | EMLA (Elekta Evo); EMLA (VersaHD); EMLA (Elekta Harmony Pro); EMLA (Elekta Infintiy); EMLA (Elekta Harmony); EMLA (Elekta Synergy) | IYE | 7 |
| K252237 | 04/17/2026 | Edgecare, Inc. | EdgeFlow UW20 | IYO | 8 |
| K252294 | 12/08/2025 | Brightheart | Fetal EchoScan (v1.2) | POK | 4, 5 |
| K252328 | 11/24/2025 | Ge Medical Systems Ultrasound and Primary Care Diagnostics | Voluson Expert 18; Voluson Expert 20; Voluson Expert 22 | IYN | 4, 6 |
| K252362 | 08/22/2025 | Galileo CDS, Inc | GBrain MRI | QIH | 7 |
| K252433 | 03/16/2026 | Sonio | Sonio Detect  (v3) | IYN | 4, 6 |
| K252503 | 04/30/2026 | Canon, Inc. | Intelligent NR | OWB | 4, 6 |
| K252538 | 03/05/2026 | Orca Dental AI , Ltd. | CEPHX3D | QIH | 13 |
| K252539 | 09/03/2025 | Arterys, Inc. | Tempus Pixel | QIH | 7 |
| K252557 | 12/22/2025 | Philips Ultrasound, LLC | Lumify Diagnostic Ultrasound System | IYN | 4, 8 |
| K252558 | 05/05/2026 | Philips Ultrasound, LLC | Lumify Diagnostic Ultrasound System | IYN | 4, 7 |
| K252954 | 05/04/2026 | Neurocareai, Inc. (Dba Savelife.Ai) | MammoSightAI | QFM | 4 |
| K252970 | 01/07/2026 | Aidoc Medical , Ltd. | BriefCase-Triage: CARE Multi-triage CT Body | QAS | 4, 6 |
| K253265 | 11/06/2025 | Aidoc Medical , Ltd. | BriefCase-Triage | QAS | 4, 6 |
| K253269 | 11/26/2025 | Ge Hualun Medical Systems Co. , Ltd. | OEC One CFD | OXO | 4, 7 |
| K253366 | 01/07/2026 | GE Medical Systems Ultrasound and Primary Care Diagnostics | LOGIQ Fortis | IYN | 4, 6 |
| K253370 | 01/08/2026 | GE Medical Systems Ultrasound and Primary Care Diagnostics | LOGIQ Totus | IYN | 4, 6 |
| K253489 | 12/12/2025 | Hyperfine, Inc. | Swoop® Portable MR Imaging® System | LNH | 6 |
| K253502 | 04/14/2026 | Ge Medical Systems, LLC | Critical Care Suite with Enteric Tube Positioning AI Algorithm | QIH | 4, 6 |
| K253578 | 02/26/2026 | Aidoc Medical , Ltd. | BriefCase-Triage: CARE Multi-Triage CT for Pneumothorax; Pericardial effusion; Large aortic aneurysm; Shoulder fracture or dislocation device | QAS | 6, 7 |
| K253595 | 03/27/2026 | Philips Ultrasound, LLC | EPIQ Series Diagnostic Ultrasound System, Affiniti Series Diagnostic Ultrasound System | IYN | 8 |
| K253649 | 03/27/2026 | Philips Medical Systems Technologies , Ltd. | Spectral CT Verida Family | JAK | 4, 8 |
| K253689 | 04/10/2026 | Siemens Healthcare GmbH | syngo Dynamics (VA41F) | QIH | 6 |
| K253818 | 03/03/2026 | Harrison-AI Medical Pty, Ltd. | Annalise Enterprise | QAS | 11, 12 |
| K254015 | 04/01/2026 | Smart Soft Healthcare AD | CoLumbo C-Spine | QIH | 8 |
| K260123 | 05/27/2026 | Philips Ultrasound, LLC | EPIQ Series Diagnostic Ultrasound System | IYN | 6, 7 |
| K260300 | 06/15/2026 | Anumana, Inc. | WatchMate Software | QIH | 9 |
| K260322 | 06/11/2026 | Mighty Oak Medical | Acorn 3D Software (AC-SEG-4009); Acorn 3DP Model (AC-101-XX) | QIH | 4, 7 |
| K260378 | 05/12/2026 | AZmed | Rayvolve | QBS | 8, 10 |
| K260497 | 06/04/2026 | Keya Medical Technology Co., Ltd. | DEEPVESSEL Plaque | QIH | 4 |
| K260509 | 03/19/2026 | Radformation, Inc. | AutoContour (RADAC V5) | QKB | 4 |
| K260667 | 06/29/2026 | Philips Ultrasound, LLC | Alturion Series Diagnostic Ultrasound System | IYN | 4, 6 |
| K260673 | 03/24/2026 | GE Medical Systems Ultrasound and Primary Care Diagnostics | LOGIQ Vita; LOGIQ Vita Pro; LOGIQ Vita Express; LOGIQ Vita Plus; LOGIQ Vita Power; LOGIQ S20; LOGIQ S20 Pro; LOGIQ S20 Express; LOGIQ S20 Plus; LOGIQ S20 Power | IYN | 4, 6 |
| K260680 | 05/27/2026 | Philips Ultrasound, LLC | EPIQ Series Diagnostic Ultrasound Systems; Affiniti Series Diagnostic Ultrasound Systems | IYN | 4, 7 |
| K260729 | 06/18/2026 | GuideAI Health | Vascular Assist Occlusion Triage (VAOT) (v1.0) | QAS | 7, 9 |
| K260844 | 06/16/2026 | Siemens Medical Solutions USA, Inc. | ACUSON Sequoia Diagnostic Ultrasound System;ACUSON Sequoia Select Diagnostic Ultrasound System;ACUSON Origin Diagnostic Ultrasound System;ACUSON Origin ICE Diagnostic Ultrasound System | IYN | 4, 5 |
| K261273 | 05/15/2026 | Neurophet., Inc. | Neurophet AQUA | QIH | 4 |
| K261317 | 05/14/2026 | Aidoc Medical , Ltd. | BriefCase-Triage | QAS | 6, 7 |
| K261519 | 06/04/2026 | Sonio | Sonio Suspect | POK | 7 |
| P150043 | 11/09/2016 | QView Medical, Inc. | QVCAD System | MYN | 23 |

### Needs label review

| Submission | Decision date | Company | Device | Why retained |
|:--|:--|:--|:--|:--|
| DEN170022 | 07/19/2017 | Quantitative Insights, Inc | QuantX | conflicting / non-indication keyword context |
| DEN190040 | 02/07/2020 | Bay Labs, Inc. | Caption Guidance | conflicting / non-indication keyword context |
| DEN220040 | 01/12/2024 | Imvaria, Inc | Fibresolve | conflicting / non-indication keyword context |
| DEN230023 | 04/09/2024 | 16 Bit Inc | Rho | conflicting / non-indication keyword context |
| DEN240047 | 05/30/2025 | Clairity, Inc. | Allix5 | conflicting / non-indication keyword context |
| K111776 | 12/28/2011 | RIVERAIN MEDICAL GROUP,LLC | DELTAVIEW MODEL 2.1 | conflicting / non-indication keyword context |
| K123526 | 12/27/2012 | RIVERAIN TECHNOLOGIES | CLEARREAD +CONFIRM | conflicting / non-indication keyword context |
| K163138 | 11/30/2016 | Clarius Mobile Health Corp. | Clarius Ultrasound System | conflicting / non-indication keyword context |
| K180589 | 04/05/2018 | Agfa HealthCare N.V. | DR 800 with MUSICA Dynamic | conflicting / non-indication keyword context |
| K180599 | 05/02/2018 | GE Medical Systems Ultrasound and Primary Care Diagnostics, | Venue | conflicting / non-indication keyword context |
| K193170 | 12/13/2019 | GE Healthcare Japan Corporation | Deep Learning Image Reconstruction | conflicting / non-indication keyword context |
| K200497 | 07/16/2020 | GE Medical Systems Ultrasound and Primary Care Diagnostics | Vivid S60N, Vivid S70N | conflicting / non-indication keyword context |
| K200708 | 09/09/2020 | GE Medical Systems Ultrasound and | Vivid iq | conflicting / non-indication keyword context |
| K200743 | 07/23/2020 | GE Medical Systems Ultrasound and | Vivid E80/ Vivid E90/ Vivid E95 | conflicting / non-indication keyword context |
| K200851 | 09/09/2020 | GE Medical Systems Ultrasound and Primary Care Diagnostics | Vivid T8, Vivid T9 | conflicting / non-indication keyword context |
| K200852 | 09/18/2020 | GE Medical Systems Ultrasound and Primary Care Diagnostics | EchoPAC Software Only, EchoPAC Plug-In | conflicting / non-indication keyword context |
| K210438 | 09/10/2021 | GE Medical Systems Ultrasound and Primary Care Diagnostics, | Versana Premier | conflicting / non-indication keyword context |
| K212067 | 09/17/2021 | GE Healthcare Japan Corporation | Deep Learning Image Reconstruction | conflicting / non-indication keyword context |
| K212333 | 01/24/2022 | Canon Medical Systems Corporation | Aplio i900/i800/i700 Diagnostic Ultrasound System, Software V6.5 | conflicting / non-indication keyword context |
| K212690 | 12/21/2021 | Qure.ai Technologies | qXR-BT | conflicting / non-indication keyword context |
| K212960 | 03/22/2022 | Canon Medical Systems Corporation | Aplio a550, Aplio a450, and Aplio a, Diagnostic Ultrasound System, Software V6.5 | conflicting / non-indication keyword context |
| K213642 | 01/13/2022 | GE Healthcare | Voluson S6, Voluson S8, Voluson S8t, Voluson S10, Voluson S10 Expert | conflicting / non-indication keyword context |
| K213999 | 02/18/2022 | GE Medical Systems, LLC. | Deep Learning Image Reconstruction | conflicting / non-indication keyword context |
| K220446 | 05/11/2022 | GE Medical Systems Ultrasound and Primary Care Diagnostics, | Versana Balance | conflicting / non-indication keyword context |
| K220619 | 07/15/2022 | GE Medical Systems Ultrasound and Primary Care Diagnostics, | Vivid S60N, Vivid S70N | conflicting / non-indication keyword context |
| K220882 | 07/22/2022 | GE Medical Systems Ultrasound and | Vivid E80, Vivid E90, Vivid E95 | conflicting / non-indication keyword context |
| K220940 | 07/22/2022 | GE Medical Systems Ultrasound and Primary Care Diagnostics, | EchoPAC Software Only, EchoPAC Plug-in | conflicting / non-indication keyword context |
| K221147 | 07/18/2022 | GE Medical Systems Ultrasound and Primary Care Diagnostics, | Vivid T8, Vivid T9 | conflicting / non-indication keyword context |
| K221148 | 07/18/2022 | GE Medical Systems Ultrasound & Primary Care Diagnostics LLC | Vivid iq | conflicting / non-indication keyword context |
| K230807 | 04/20/2023 | GE Healthcare Japan Corporation | Deep Learning Image Reconstruction | conflicting / non-indication keyword context |
| K231989 | 11/07/2023 | GE Medical Systems Ultrasound and Primary Care Diagnostic, | LOGIQ E10s, LOGIQ Fortis | conflicting / non-indication keyword context |
| K232381 | 12/07/2023 | GE Medical Systems Ultrasound and Primary care Diagnostics, | LOGIQ Totus | conflicting / non-indication keyword context |
| K233195 | 01/24/2024 | Canon Medical Systems Corporation | Aplio i900, Aplio i800 and Aplio i700 Software V8.1 Diagnostic Ultrasound System | conflicting / non-indication keyword context |
| K233692 | 03/07/2024 | GE Medical Systems Ultrasound and Primary care Diagnostics, | Voluson Signature 20, Voluson Signature 18 | conflicting / non-indication keyword context |
| K241582 | 09/12/2024 | Canon Medical Systems Corporation | Aplio i900/i800/i700 Diagnostic Ultrasound System, Software V7.0 (TUS-AI900, TUS-AI800, TUS-AI700) | conflicting / non-indication keyword context |
| K241593 | 02/05/2025 | Gleamer SAS | BoneMetrics (US) | conflicting / non-indication keyword context |
| K241671 | 05/16/2025 | Esaote S.p.A. | 6450 Ultrasound System (MyLabE80); 6450 Ultrasound System (MyLabE85) | conflicting / non-indication keyword context |
| K242005 | 10/02/2024 | GE Medical Systems Ultrasound and Primary Care Diagnostics | Versana Premier; Versana Premier Lotus; LOGIQ F | conflicting / non-indication keyword context |
| K243620 | 02/11/2025 | GE Medical Systems Ultrasound and Primary Care Diagnostics | Vivid iq | conflicting / non-indication keyword context |
| K243628 | 02/11/2025 | GE Medical Systems Ultrasound and Primary Care Diagnostics | Vivid T9/Vivid T8 | conflicting / non-indication keyword context |
| K250330 | 11/03/2025 | Pie Medical Imaging BV | 3mensio Workstation | conflicting / non-indication keyword context |
| K250543 | 05/29/2025 | GE Medical Systems Ultrasound and Primary care Diagnostics | Voluson Performance 16; Voluson Performance 18 | conflicting / non-indication keyword context |
| K251106 | 08/29/2025 | Fujifilm Sonosite Inc | Sonosite LX and Sonosite PX Ultrasound Systems | conflicting / non-indication keyword context |
| K251169 | 07/10/2025 | GE Medical Systems Ultrasound and Primary Care Diagnostics | Vivid Pioneer | conflicting / non-indication keyword context |
| K251342 | 07/16/2025 | GE Medical Systems Ultrasound and Primary Care Diagnostics | EchoPAC Software Only / EchoPAC Plug-in | conflicting / non-indication keyword context |
| K252074 | 10/31/2025 | Canon Medical Systems Corporation | Aplio i900, Aplio i800 and Aplio i700 Software V9.0 Diagnostic Ultrasound System | conflicting / non-indication keyword context |
| K253050 | 06/18/2026 | Informai | RadOncAI | conflicting / non-indication keyword context |
| K253288 | 04/06/2026 | Esaote, S.p.A. | 6450 Ultrasound System (MyLabE80); 6450 Ultrasound System (MyLabE85) | conflicting / non-indication keyword context |
| K253720 | 05/21/2026 | Wuhan United Imaging Healthcare Co.,Ltd | uSONIQUE Nova, uSONIQUE Nova Elite, uSONIQUE Vita, uSONIQUE Vita Elite, uSONIQUE Grace, uSONIQUE Grace Elite | conflicting / non-indication keyword context |
| K254013 | 05/14/2026 | Subtle Medical, Inc. | SubtleHD-PET (1.x) | conflicting / non-indication keyword context |
| K254120 | 05/15/2026 | Subtle Medical, Inc. | SubtleHD-CT (1.x) | conflicting / non-indication keyword context |
| P160009 | 03/24/2017 | iCAD Inc | PowerLook® Tomo Detection Software | conflicting / non-indication keyword context |
| P200003 | 01/11/2021 | Seno Medical Instruments, Inc. | Imagio Breast Imaging System | conflicting / non-indication keyword context |

The inventory intentionally includes scanner, ultrasound, radiation-therapy, dental, fetal, and software products because the FDA Radiology panel includes all of these. Repeated submissions are retained so the result is auditable; use the submission number to collapse versions into product families. Confirm the current 510(k), De Novo, or PMA labeling before purchase.

