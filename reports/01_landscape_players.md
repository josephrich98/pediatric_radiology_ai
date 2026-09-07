# The Biggest Players in Radiology AI (and Pediatric Radiology AI)

_Most-cited papers from OpenAlex; most-starred open-source tools from GitHub. Citation and star counts are snapshots at collection time._

## Most-cited radiology AI papers

**How obtained.** OpenAlex was searched with a *union* of modality- and task-specific queries (e.g. `CT deep learning segmentation`, `chest radiograph deep learning`, `radiomics machine learning`, `anatomical structures segmentation CT`), the results deduplicated by work id and ranked by citation count. The union matters: a single `radiology deep learning` query misses landmark papers whose title/abstract never use the word "radiology" — TotalSegmentator and nnU-Net, for instance, are framed purely as CT segmentation and only surface through the modality/task queries.

| Rank | Citations | Year | Title | Venue |
|---:|---:|---:|:--|:--|
| 1 | 15110 | 2017 | A survey on deep learning in medical image analysis | Medical Image Analysis |
| 2 | 9364 | 2020 | nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation | Nature Methods |
| 3 | 6709 | 2017 | Computational Radiomics System to Decode the Radiographic Phenotype | Cancer Research |
| 4 | 4917 | 2017 | Deep Learning in Medical Image Analysis | Annual Review of Biomedical Engineering |
| 5 | 4868 | 2018 | Identifying Medical Diagnoses and Treatable Diseases by Image-Based Deep Learning | Cell |
| 6 | 4700 | 2018 | Convolutional neural networks: an overview and application in radiology | Insights into Imaging |
| 7 | 3762 | 2018 | Artificial intelligence in radiology | Nature reviews. Cancer |
| 8 | 3187 | 2020 | COVID-Net: a tailored deep convolutional neural network design for detection of COVID-19 cases from chest X-ray images | Scientific Reports |
| 9 | 2687 | 2019 | CheXpert: A Large Chest Radiograph Dataset with Uncertainty Labels and Expert Comparison | AAAI Publications (The Association for the Advancement of Artificial Intelligence (AAAI)) |
| 10 | 2432 | 2020 | Covid-19: automatic detection from X-ray images utilizing transfer learning with convolutional neural networks | Physical and Engineering Sciences in Medicine |
| 11 | 2377 | 2020 | A Survey on Explainable Artificial Intelligence (XAI): Toward Medical XAI | IEEE Transactions on Neural Networks and Learning Systems |
| 12 | 2369 | 2018 | Deep Learning Techniques for Automatic MRI Cardiac Multi-Structures Segmentation and Diagnosis: Is the Problem Solved? | IEEE Transactions on Medical Imaging |
| 13 | 2334 | 2019 | MultiResUNet : Rethinking the U-Net architecture for multimodal biomedical image segmentation | Neural Networks |
| 14 | 2268 | 2019 | CE-Net: Context Encoder Network for 2D Medical Image Segmentation | IEEE Transactions on Medical Imaging |
| 15 | 2161 | 2019 | End-to-end lung cancer screening with three-dimensional deep learning on low-dose chest computed tomography | Nature Medicine |
| 16 | 2037 | 2018 | An overview of deep learning in medical imaging focusing on MRI | Zeitschrift für Medizinische Physik |
| 17 | 1976 | 2018 | GAN-based synthetic medical image augmentation for increased CNN performance in liver lesion classification | Neurocomputing |
| 18 | 1946 | 2020 | Can AI Help in Screening Viral and COVID-19 Pneumonia? | IEEE Access |
| 19 | 1945 | 2021 | U-Net and Its Variants for Medical Image Segmentation: A Review of Theory and Applications | IEEE Access |
| 20 | 1885 | 2017 | Low-Dose CT With a Residual Encoder-Decoder Convolutional Neural Network | IEEE Transactions on Medical Imaging |
| 21 | 1752 | 2017 | Learning a variational network for reconstruction of accelerated MRI data | Magnetic Resonance in Medicine |
| 22 | 1668 | 2017 | Machine Learning for Medical Imaging | Radiographics |
| 23 | 1652 | 2018 | Low-Dose CT Image Denoising Using a Generative Adversarial Network With Wasserstein Distance and Perceptual Loss | IEEE Transactions on Medical Imaging |
| 24 | 1646 | 2019 | Deep Learning Techniques for Medical Image Segmentation: Achievements and Challenges | Journal of Imaging Informatics in Medicine |
| 25 | 1633 | 2018 | Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study | PLoS Medicine |
| 26 | 1497 | 2017 | Deep Learning Applications in Medical Image Analysis | IEEE Access |
| 27 | 1453 | 2018 | Deep learning for chest radiograph diagnosis: A retrospective comparison of the CheXNeXt algorithm to practicing radiologists | PLoS Medicine |
| 28 | 1425 | 2023 | TotalSegmentator: Robust Segmentation of 104 Anatomic Structures in CT Images | Radiology Artificial Intelligence |
| 29 | 1379 | 2021 | Deep learning-enabled medical computer vision | npj Digital Medicine |
| 30 | 1360 | 2020 | CoroNet: A deep neural network for detection and diagnosis of COVID-19 from chest x-ray images | Computer Methods and Programs in Biomedicine |

### What the papers above 1,500 citations answer

| Citations | Paper | Topic | Clinical question |
|---:|:--|:--|:--|
| 15110 | A survey on deep learning in medical image analysis (2017) | survey | What can deep learning do across medical imaging? (the field's reference survey) |
| 9364 | nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation (2020) | segmentation | Can one self-configuring method segment any organ or lesion without hand tuning? (nnU-Net) |
| 6709 | Computational Radiomics System to Decode the Radiographic Phenotype (2017) | radiomics | Can standardized image features (radiomics) be extracted reproducibly? (PyRadiomics) |
| 4917 | Deep Learning in Medical Image Analysis (2017) | survey | How does deep learning apply to medical image analysis? (review) |
| 4868 | Identifying Medical Diagnoses and Treatable Diseases by Image-Based Deep Learning (2018) | classification | Can transfer learning diagnose pediatric pneumonia on chest X-ray and retinal disease on OCT? |
| 4700 | Convolutional neural networks: an overview and application in radiology (2018) | tutorial | What is a convolutional neural network, explained for radiologists? |
| 3762 | Artificial intelligence in radiology (2018) | review | How will AI change radiology practice? (Hosny et al.) |
| 3187 | COVID-Net: a tailored deep convolutional neural network design for detection of COVID-19 cases from chest X-ray images (2020) | classification | Can a CNN detect COVID-19 on chest X-ray? (COVID-Net) |
| 2687 | CheXpert: A Large Chest Radiograph Dataset with Uncertainty Labels and Expert Comparison (2019) | dataset | A 224k chest-radiograph dataset with uncertainty labels for training and benchmarking (CheXpert) |
| 2432 | Covid-19: automatic detection from X-ray images utilizing transfer learning with convolutional neural networks (2020) | classification | Can transfer learning detect COVID-19 on X-ray with small data? |
| 2377 | A Survey on Explainable Artificial Intelligence (XAI): Toward Medical XAI (2020) | explainability | How can AI decisions in medicine be made explainable? |
| 2369 | Deep Learning Techniques for Automatic MRI Cardiac Multi-Structures Segmentation and Diagnosis: Is the Problem Solved? (2018) | segmentation | Is automatic cardiac MRI segmentation solved? (ACDC challenge) |
| 2334 | MultiResUNet : Rethinking the U-Net architecture for multimodal biomedical image segmentation (2019) | segmentation | Architecture variant of U-Net for multimodal segmentation |
| 2268 | CE-Net: Context Encoder Network for 2D Medical Image Segmentation (2019) | segmentation | Architecture variant for 2D medical image segmentation (CE-Net) |
| 2161 | End-to-end lung cancer screening with three-dimensional deep learning on low-dose chest computed tomography (2019) | screening | Can AI read low-dose CT for lung-cancer screening as well as radiologists? (Google) |
| 2037 | An overview of deep learning in medical imaging focusing on MRI (2018) | review | Deep learning in MRI: acquisition to interpretation (overview) |
| 1976 | GAN-based synthetic medical image augmentation for increased CNN performance in liver lesion classification (2018) | synthesis | Can GAN-generated synthetic lesions improve training with scarce data? |
| 1946 | Can AI Help in Screening Viral and COVID-19 Pneumonia? (2020) | classification | Can AI screen viral vs COVID-19 pneumonia on X-ray? |
| 1945 | U-Net and Its Variants for Medical Image Segmentation: A Review of Theory and Applications (2021) | survey | U-Net and its variants: a review |
| 1885 | Low-Dose CT With a Residual Encoder-Decoder Convolutional Neural Network (2017) | reconstruction | Can a CNN denoise low-dose CT to standard-dose quality? (RED-CNN) |
| 1752 | Learning a variational network for reconstruction of accelerated MRI data (2017) | reconstruction | Can a learned reconstruction accelerate MRI 4x without losing diagnostic quality? |
| 1668 | Machine Learning for Medical Imaging (2017) | tutorial | Machine learning for medical imaging: a primer for radiologists |
| 1652 | Low-Dose CT Image Denoising Using a Generative Adversarial Network With Wasserstein Distance and Perceptual Loss (2018) | reconstruction | Can a GAN denoise low-dose CT while keeping texture natural? |
| 1646 | Deep Learning Techniques for Medical Image Segmentation: Achievements and Challenges (2019) | survey | Segmentation methods: achievements and challenges (review) |
| 1633 | Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study (2018) | generalization | Does a pneumonia model trained at one hospital work at another? (often not) |

## Most-cited pediatric radiology AI papers

**How obtained.** Same union-of-queries method with pediatric terms (bone age, fetal/neonatal MRI, pediatric CT/fracture/pneumonia), additionally requiring a pediatric signal in the title so the list stays genuinely pediatric.

| Rank | Citations | Year | Title | Venue |
|---:|---:|---:|:--|:--|
| 1 | 472 | 2018 | The RSNA Pediatric Bone Age Machine Learning Challenge | Radiology |
| 2 | 469 | 2017 | Performance of a Deep-Learning Neural Network Model in Assessing Skeletal Maturity on Pediatric Hand Radiographs | Radiology |
| 3 | 454 | 2017 | Fully Automated Deep Learning System for Bone Age Assessment | Journal of Imaging Informatics in Medicine |
| 4 | 434 | 2016 | Deep learning for automated skeletal bone age assessment in X-ray images | Medical Image Analysis |
| 5 | 203 | 2020 | Improving Image Quality and Reducing Radiation Dose for Pediatric CT by Using Deep Learning Reconstruction | Radiology |
| 6 | 166 | 2017 | Computerized Bone Age Estimation Using Deep Learning Based Program: Evaluation of the Accuracy and Efficiency | American Journal of Roentgenology |
| 7 | 133 | 2018 | Regression Convolutional Neural Network for Automated Pediatric Bone Age Assessment From Hand Radiograph | IEEE Journal of Biomedical and Health Informatics |
| 8 | 126 | 2018 | Artificial intelligence-assisted interpretation of bone age radiographs improves accuracy and decreases variability | Skeletal Radiology |
| 9 | 116 | 2019 | Deep Learning Based Attenuation Correction of PET/MRI in Pediatric Brain Tumor Patients: Evaluation in a Clinical Setting | Frontiers in Neuroscience |
| 10 | 107 | 2019 | Using a Dual-Input Convolutional Neural Network for Automated Detection of Pediatric Supracondylar Fracture on Conventional Radiography | Investigative Radiology |
| 11 | 94 | 2021 | Deep Learning–based Reconstruction for Lower-Dose Pediatric CT: Technical Principles, Image Characteristics, and Clinical Implementations | Radiographics |
| 12 | 89 | 2018 | MABAL: a Novel Deep-Learning Architecture for Machine-Assisted Bone Age Labeling | Journal of Imaging Informatics in Medicine |
| 13 | 87 | 2019 | Incorporated region detection and classification using deep convolutional networks for bone age assessment | Artificial Intelligence in Medicine |
| 14 | 84 | 2020 | Bone Age Assessment Empowered with Deep Learning: A Survey, Open Research Challenges and Future Directions | Diagnostics |
| 15 | 83 | 2019 | Automatic feature extraction in X-ray image based on deep learning approach for determination of bone age | Future Generation Computer Systems |
| 16 | 79 | 2019 | TW3-Based Fully Automated Bone Age Assessment System Using Deep Neural Networks | IEEE Access |
| 17 | 79 | 2021 | Automated detection of pneumonia cases using deep transfer learning with paediatric chest X-ray images | British Journal of Radiology |
| 18 | 77 | 2020 | Deep Learning for Pediatric Posterior Fossa Tumor Detection and Classification: A Multi-Institutional Study | American Journal of Neuroradiology |
| 19 | 76 | 2021 | Deep learning-based automatic tumor burden assessment of pediatric high-grade gliomas, medulloblastomas, and other leptomeningeal seeding tumors | Neuro-Oncology |
| 20 | 76 | 2020 | A Deep Attentive Convolutional Neural Network for Automatic Cortical Plate Segmentation in Fetal MRI | IEEE Transactions on Medical Imaging |

### What the papers above 100 citations answer

| Citations | Paper | Topic | Clinical question |
|---:|:--|:--|:--|
| 472 | The RSNA Pediatric Bone Age Machine Learning Challenge (2018) | bone age | How well can crowdsourced AI estimate bone age? (RSNA challenge, 260 teams) |
| 469 | Performance of a Deep-Learning Neural Network Model in Assessing Skeletal Maturity on Pediatric Hand Radiographs (2017) | bone age | Can a CNN assess skeletal maturity as accurately as radiologists? |
| 454 | Fully Automated Deep Learning System for Bone Age Assessment (2017) | bone age | Fully automated bone age from hand radiographs |
| 434 | Deep learning for automated skeletal bone age assessment in X-ray images (2016) | bone age | Deep learning for automated bone age (BoNet) |
| 203 | Improving Image Quality and Reducing Radiation Dose for Pediatric CT by Using Deep Learning Reconstruction (2020) | reconstruction | Can deep-learning reconstruction cut pediatric CT dose while improving image quality? |
| 166 | Computerized Bone Age Estimation Using Deep Learning Based Program: Evaluation of the Accuracy and Efficiency (2017) | bone age | Is a commercial deep-learning bone-age program accurate and faster in practice? |
| 133 | Regression Convolutional Neural Network for Automated Pediatric Bone Age Assessment From Hand Radiograph (2018) | bone age | Regression CNN for pediatric bone age |
| 126 | Artificial intelligence-assisted interpretation of bone age radiographs improves accuracy and decreases variability (2018) | bone age | Does AI assistance make radiologists' bone-age reads more accurate and consistent? |
| 116 | Deep Learning Based Attenuation Correction of PET/MRI in Pediatric Brain Tumor Patients: Evaluation in a Clinical Setting (2019) | reconstruction | Can deep learning replace CT for PET/MRI attenuation correction in children? |
| 107 | Using a Dual-Input Convolutional Neural Network for Automated Detection of Pediatric Supracondylar Fracture on Conventional Radiography (2019) | fracture | Can a CNN detect supracondylar fractures on pediatric elbow radiographs? |

## Commercial players: the FDA AI-enabled device list

**How obtained.** The FDA publishes a spreadsheet of every AI-enabled device it has authorized ([source](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices)). Restricting to the *Radiology* lead panel gives products per year and clearances per company. The list carries no pediatric flag; device names were matched against pediatric terms and a curated list of products with pediatric indications was cross-checked against it.

- 1,164 of 1,524 AI-enabled devices (76.4%) are in the Radiology panel (snapshot 2026-09-03).

| Company | Radiology AI devices | Years | Examples |
|:--|---:|:--|:--|
| GE HealthCare | 107 | 2014–2026 | Automated Aortic Stenosis Software (AutoAS); LOGIQ Vita; LOGIQ Vita Pro; LOGIQ Vita Express; LOGIQ Vita Plus; LOGIQ Vita Power; LOGIQ S20; LOGIQ S20 Pro; LOGIQ S20 Express; LOGIQ S20 Plus; LOGIQ S20 Power; True Definition DL |
| Siemens Healthineers | 90 | 2014–2026 | SOMATOM X.cite; SOMATOM X.ceed; MAGNETOM Flow.Ace; MAGNETOM Flow.Plus; MI View&GO |
| Philips | 44 | 2018–2026 | Spectral CT Verida Family; EPIQ Series Diagnostic Ultrasound System, Affiniti Series Diagnostic Ultrasound System; CT Rembra RT; CT Areta RT; CT Rembra |
| Canon Medical | 43 | 2019–2026 | Vantage Fortian/Orian 1.5T, MRT-1550, V10.0 with AiCE Reconstruction Processing Unit for MR; Aquilion ServeSP (TSX-307B) V2.0; Alphenix, INFX-8000V/B, INFX-8000V/S, V9.6 with aEvolve Imaging (FOV Extension) |
| United Imaging | 40 | 2020–2026 | uMI Panvivo (uMI Panvivo); uMI Panvivo (uMI Panvivo S); uMI Panvivo (uMI Panvivo EX); uMI Panvivo (uMI Panvivo ES); uCT 780 with uWS-CT-Dual Energy Analysis; uMR 680 |
| Aidoc | 34 | 2018–2026 | BriefCase-Triage: CARE Multi-Triage CT for Pneumothorax; Pericardial effusion; Large aortic aneurysm; Shoulder fracture or dislocation device; BriefCase-Triage; BriefCase-Triage: CARE Multi-triage CT Body |
| Samsung | 19 | 2021–2026 | HERA Z20 Diagnostic Ultrasound System; HERA Z20e Diagnostic Ultrasound System; HERA Z20s Diagnostic Ultrasound System; R20 Diagnostic Ultrasound System; HERA Z30 Diagnostic Ultrasound System; R30 Diagnostic Ultrasound System; V8 Diagnostic Ultrasound System; cV8 Diagnostic Ultrasound System; V7 Diagnostic Ultrasound System; cV7 Diagnostic Ultrasound System; V6 Diagnostic Ultrasound System; cV6 Diagnostic Ultrasound System; V5 Diagnostic Ultrasound System; cV5 Diagnostic Ultrasound System; V4 Diagnostic Ultrasound System; cV4 Diagnostic Ultrasound System; V8 Diagnostic Ultrasound System; cV8 Diagnostic Ultrasound System; V7 Diagnostic Ultrasound System; cV7 Diagnostic Ultrasound System; V6 Diagnostic Ultrasound System; cV6 Diagnostic Ultrasound System |
| iSchemaView (RapidAI) | 17 | 2018–2025 | Rapid Aortic Measurements; Rapid Obstructive Hydrocephalus, Rapid OH; Rapid CTA 360 |
| Hyperfine | 13 | 2021–2025 | Swoop® Portable MR Imaging® System; Swoop® Portable MR Imaging® System (V2); Swoop® Portable MR Imaging® System |
| Clarius Mobile Health | 12 | 2016–2026 | Clarius Ejection Fraction AI; Clarius Median Nerve AI; Clarius Prostate AI |
| Viz.ai | 11 | 2018–2025 | Viz Subdural+, Viz SUBDURAL PLUS; Viz HDS, Viz Volume Plus, Viz ICH+; Viz AAA |
| Circle CVI | 10 | 2014–2025 | cvi42 Coronary Plaque Software Application; StrokeSENS ASPECTS Software Application; cvi42 Software Application |
| Coreline | 10 | 2020–2025 | AVIEW Lung Nodule CAD; AVIEW; AVIEW CAC |
| DiA Imaging Analysis | 10 | 2020–2025 | LVivo Software Application; LVivo Seamless; LVivo Software Application |
| Overjet | 10 | 2021–2025 | Overjet CBCT Assist; Overjet Image Enhancement Assist; Overjet Charting Assist |
| Fujifilm | 9 | 2021–2025 | ECHELON Synergy; Sonosite LX and Sonosite PX Ultrasound Systems; Synapse PACS (7.5) |
| Qure.ai | 9 | 2020–2026 | qXR-Detect; qER-CTA (v1.0); qCT LN Quant |
| Zebra Medical | 9 | 2018–2021 | HealthPPT; HealthCCSng; HealthJOINT |
| Annalise.ai | 8 | 2022–2025 | Annalise Enterprise; Annalise Enterprise CTB Triage Trauma; Annalise Enterprise CTB Triage Trauma |
| Ever FortuneAI | 8 | 2022–2025 | EFAI Chestsuite XR Malpositioned ETT Assessment System (ETT-XR-100); EFAI Neurosuite CT Midline Shift Assessment System (MLS-CT-100); EFAI Bonesuite XR Bone Age Pro Assessment System (BAP-XR-100) |

![FDA AI devices per year](../figures/fda_devices_per_year.png)

![Companies with the most FDA radiology AI devices](../figures/fda_companies.png)

### Devices whose names carry a pediatric term

| Year | Company | Device |
|---:|:--|:--|
| 2025 | Brightheart | Fetal EchoScan (v1.2) |
| 2025 | Pearl, Inc. | Second Opinion® Pediatric |
| 2025 | BrightHeart | Fetal EchoScan (v1.1) |
| 2025 | AZmed | Rayvolve LN |
| 2025 | AZmed | Rayvolve PTX-PE |
| 2024 | BrightHeart | Fetal EchoScan |
| 2024 | AZmed SAS | Rayvolve |
| 2024 | Ever Fortune.AI Co., Ltd. | EFAI Bonesuite XR Bone Age Pro Assessment System (BAP-XR-100) |
| 2024 | 16 Bit Inc | Rho |
| 2024 | Overjet, Inc | Overjet Caries Assist-Pediatric |
| 2023 | Gleamer | BoneView |
| 2022 | AZmed SAS | Rayvolve |
| 2022 | Gleamer | BoneView |

### Commercial software with a pediatric angle (curated)

| Vendor | Product | Task | Pediatric status | On FDA list |
|:--|:--|:--|:--|:--|
| Gleamer | BoneView | fracture detection on radiographs | pediatric indication (age 2+) cleared 2023 | 4 device(s), 2022–2025 |
| AZmed | Rayvolve | fracture (and chest) findings on radiographs | pediatric fracture indication cleared 2024 | 4 device(s), 2022–2025 |
| Visiana | BoneXpert | automated bone age (GP / TW) | pediatric by design; CE-marked since 2009 (not on the FDA AI list) | not listed |
| 16 Bit | Rho | automated bone age | pediatric by design | 1 device(s), 2024–2024 |
| Ever Fortune.AI | EFAI Bonesuite Bone Age Pro | automated bone age | pediatric by design | 11 device(s), 2022–2026 |
| BrightHeart | Fetal EchoScan | fetal echocardiography view / anomaly assist | prenatal (fetal) by design | 5 device(s), 2024–2025 |
| GE HealthCare / Canon / Siemens / Philips | TrueFidelity, AiCE, Deep Resolve, Precise Image | deep-learning CT / MR reconstruction (lower dose, faster scans) | adult-cleared scanner software, widely used for pediatric dose reduction | 307 device(s), 2014–2026 |
| Subtle Medical / AIRS Medical | SubtleMR, SwiftMR | accelerated MRI via deep-learning denoising | adult-cleared; pediatric scan-time studies | 13 device(s), 2018–2026 |
| Qure.ai | qXR / qER | chest radiograph and head CT triage / quantification | adult indications; pediatric TB-screening evidence only | 9 device(s), 2020–2026 |
| Aidoc / Viz.ai | BriefCase, Viz LVO / ICH | worklist triage (hemorrhage, LVO, PE, pneumothorax) | adult-only indications; the largest deployed category | 43 device(s), 2018–2026 |

## Most-starred open-source radiology / imaging AI tools

| Rank | Stars | Repository | Language | Description |
|---:|---:|:--|:--|:--|
| 1 | 8849 | [MIC-DKFZ/nnUNet](https://github.com/MIC-DKFZ/nnUNet) | Python |  |
| 2 | 8652 | [Project-MONAI/MONAI](https://github.com/Project-MONAI/MONAI) | Python | AI Toolkit for Healthcare Imaging |
| 3 | 4385 | [bowang-lab/MedSAM](https://github.com/bowang-lab/MedSAM) | Jupyter Notebook | Segment Anything in Medical Images |
| 4 | 4317 | [OHIF/Viewers](https://github.com/OHIF/Viewers) | TypeScript | OHIF zero-footprint DICOM viewer and oncology specific Lesion Tracker, plus shared extensi |
| 5 | 3234 | [Beckschen/TransUNet](https://github.com/Beckschen/TransUNet) | Python | This repository includes the official project of TransUNet, presented in our paper: TransU |
| 6 | 2962 | [wasserth/TotalSegmentator](https://github.com/wasserth/TotalSegmentator) | Python | Tool for robust segmentation of >100 important anatomical structures in CT and MR images |
| 7 | 2612 | [Slicer/Slicer](https://github.com/Slicer/Slicer) | C++ | Multi-platform, free open source software for visualization and image computing. |
| 8 | 2439 | [TorchIO-project/torchio](https://github.com/TorchIO-project/torchio) | Python | Medical imaging processing for AI applications. |
| 9 | 2418 | [HuCaoFighting/Swin-Unet](https://github.com/HuCaoFighting/Swin-Unet) | Python | [ECCVW 2022] The codes for the work "Swin-Unet: Unet-like Pure Transformer for Medical Ima |
| 10 | 2258 | [Tencent/MedicalNet](https://github.com/Tencent/MedicalNet) | Python | Many studies have shown that the performance on deep learning is significantly affected by |
| 11 | 2231 | [microsoft/LLaVA-Med](https://github.com/microsoft/LLaVA-Med) | Python | Large Language-and-Vision Assistant for Biomedicine, built towards multimodal GPT-4 level  |
| 12 | 2227 | [ellisdg/3DUnetCNN](https://github.com/ellisdg/3DUnetCNN) | Python | Pytorch 3D U-Net Convolution Neural Network (CNN) designed for medical image segmentation |
| 13 | 2203 | [pydicom/pydicom](https://github.com/pydicom/pydicom) | Python | Read, modify and write DICOM files with python code |
| 14 | 2064 | [ozan-oktay/Attention-Gated-Networks](https://github.com/ozan-oktay/Attention-Gated-Networks) | Python | Use of Attention Gates in a Convolutional Neural Network / Medical Image Classification an |
| 15 | 1918 | [black0017/MedicalZooPytorch](https://github.com/black0017/MedicalZooPytorch) | Python | A pytorch-based deep learning framework for multi-modal 2D/3D medical image segmentation |
| 16 | 1652 | [InsightSoftwareConsortium/ITK](https://github.com/InsightSoftwareConsortium/ITK) | C++ | Insight Toolkit (ITK) -- Official Repository.  ITK builds on a proven, spatially-oriented  |
| 17 | 1533 | [facebookresearch/fastMRI](https://github.com/facebookresearch/fastMRI) | Python | A large-scale dataset of both raw MRI measurements and clinical MRI images. |
| 18 | 1497 | [ANTsX/ANTs](https://github.com/ANTsX/ANTs) | C++ | Advanced Normalization Tools (ANTs) |
| 19 | 1399 | [MedMNIST/MedMNIST](https://github.com/MedMNIST/MedMNIST) | Python | [pip install medmnist] 18x Standardized Datasets for 2D and 3D Biomedical Image Classifica |
| 20 | 1223 | [bowang-lab/MedRAX](https://github.com/bowang-lab/MedRAX) | Python | MedRAX: Medical Reasoning Agent for Chest X-ray - ICML 2025 |
| 21 | 1190 | [mlmed/torchxrayvision](https://github.com/mlmed/torchxrayvision) | Jupyter Notebook | TorchXRayVision: A library of chest X-ray datasets and models. Classifiers, segmentation,  |
| 22 | 1133 | [cornerstonejs/cornerstone3D](https://github.com/cornerstonejs/cornerstone3D) | TypeScript | Cornerstone is a set of JavaScript libraries that can be used to build web-based medical i |
| 23 | 1084 | [SimpleITK/SimpleITK](https://github.com/SimpleITK/SimpleITK) | C++ | SimpleITK: a layer built on top of the Insight Toolkit (ITK), intended to simplify and fac |
| 24 | 1042 | [Xiaoqi-Zhao-DLUT/MSNet-M2SNet](https://github.com/Xiaoqi-Zhao-DLUT/MSNet-M2SNet) | Python | (MIR 2026 [M2SNet] & MICCAI 2022 GOALS Challenge & MICCAI 2021 [MSNet]) Multi-scale in Mul |
| 25 | 954 | [uni-medical/SAM-Med3D](https://github.com/uni-medical/SAM-Med3D) | Python | SAM-Med3D: An Efficient General-purpose Promptable Segmentation Model for 3D Volumetric Me |

## Pediatric-specific open-source tools

| Stars | Repository | Description |
|---:|:--|:--|
| 19 | [thevishalagarwal/BoneAgeEstimation](https://github.com/thevishalagarwal/BoneAgeEstimation) | Deep Learning aproach for estimating bone age from hand x-ray images |
| 19 | [aimi-bonn/Deeplasia](https://github.com/aimi-bonn/Deeplasia) | Prior-free deep learning for pediatric bone age assessment robust to skeletal dysplasias |
| 15 | [Hzzone/Bone-Age-Assessment](https://github.com/Hzzone/Bone-Age-Assessment) | Deep Learning and Training dicom file with Caffe and Regression Prediction by age label. |
| 9 | [tana0101/Hip-Joint-Keypoint-Detection](https://github.com/tana0101/Hip-Joint-Keypoint-Detection) | A research-oriented deep learning pipeline for automatic hip joint keypoint detection, ace |
| 7 | [Giammarco07/DeePRAC_project](https://github.com/Giammarco07/DeePRAC_project) | Learning anatomical digital twins in pediatric 3D imaging for renal cancer surgery. A proj |
| 6 | [i-pan/boneage](https://github.com/i-pan/boneage) | Code and models for automated pediatric bone age evaluation with deep learning |
| 6 | [pazadeh/BAAM](https://github.com/pazadeh/BAAM) | A deep learning-based Bone Age Assessment Model (BAAM) |
| 5 | [RichardChangCA/Deep-Contrastive-Metric-Learning-Method-to-Detect-Polymicrogyria-in-Pediatric-Brain-MRI](https://github.com/RichardChangCA/Deep-Contrastive-Metric-Learning-Method-to-Detect-Polymicrogyria-in-Pediatric-Brain-MRI) | [Journal Paper: Computerized Medical Imaging and Graphics] A Novel Center-based Deep Contr |
| 5 | [dani-capellan/pTB_LungRegionExtractor](https://github.com/dani-capellan/pTB_LungRegionExtractor) | Multi-view deep learning-based solution that extracts lung and mediastinal regions of inte |
| 4 | [karelbecerra/sam-x-ray-medical-images-hand-sex-classification](https://github.com/karelbecerra/sam-x-ray-medical-images-hand-sex-classification) | Deep learning and segmentation in sex classification from left hand X-ray images in pediat |
| 4 | [bryanoliveira/bone-age-regression](https://github.com/bryanoliveira/bone-age-regression) | A Deep Learning approach to solve the bone age regression problem. |
| 3 | [ardranirwan28/bone-age-assessment](https://github.com/ardranirwan28/bone-age-assessment) | Bone Age Assessment project using deep learning from hand x-rays |
| 3 | [abdm149/GraduationProject](https://github.com/abdm149/GraduationProject) | This repository contains the code and resources for my graduation project on bone age esti |
| 2 | [nikshak/Pneumonia-Detection-using-Image-Classification](https://github.com/nikshak/Pneumonia-Detection-using-Image-Classification) | The implementation of clinical-decision support algorithms for medical imaging faces chall |
| 2 | [afiosman/deep-learning-based-bone-age-estimation](https://github.com/afiosman/deep-learning-based-bone-age-estimation) | Develop a deep learning-based model utilizing a fully connected convolutional neural netwo |

