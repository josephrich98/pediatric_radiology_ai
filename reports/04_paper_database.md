# Pediatric radiology AI: paper database

Generated 2026-09-10 from `data/processed/pedrad_paper_db.csv`.

3658 papers, 767 of which name a model or product, screened from 5904 records matching the pediatric radiology-AI query (title/abstract fielded) for 2015-2026 (2246 were screened out as adult-only, non-radiologic, or non-AI). Candidates come from three sources: PubMed, OpenAlex preprints, and conference proceedings (MICCAI, ISBI, SPIE Medical Imaging, NeurIPS and the rest), deduplicated against each other.

Candidates are papers meeting at least 20 citations in NIH iCite or at least 10 citations per year or a relative citation ratio of at least 5, which keeps the database to work the field has actually engaged with. A raw citation floor is also a recency filter — a paper published this year has had no time to accrue citations — which is why the rate and ratio clauses exist; even so the current year is thin by construction, and the trend figures, not this table, are the place to read growth.

Impact is reported four ways because no one measure works across the whole range. `citations` is the raw count and can only be compared within a year. `citations/yr` is that count divided by years since publication. `RCR` is iCite's relative citation ratio, where 1.0 is the median NIH-funded paper of the same field and year, and is the column to use when comparing a 2016 paper with a 2024 one; it is undefined until a paper is about two years old. `fwci` is OpenAlex's field-weighted citation impact, on the same 1.0-is-average scale, and covers some of what RCR does not.

Each row is read from the paper's abstract under a fixed schema, so a field is blank when the abstract does not state it — most notably the release column, which abstracts are usually silent about. Read "unclear" as "the paper does not say", not as "unavailable". Hand corrections in `data/paper_db_overrides.json` take precedence over the extracted value and are flagged in the `overridden_fields` column of the CSV.

## Counts

### Release status

| Status | Papers |
| --- | ---: |
| unclear | 3280 |
| open-source | 157 |
| commercial | 149 |
| unreleased | 72 |

### Modality

| Modality | Papers |
| --- | ---: |
| MRI | 1605 |
| ultrasound | 922 |
| x-ray / radiography | 664 |
| CT | 347 |
| multiple | 95 |
| nuclear / PET | 64 |
| other | 59 |
| fluoroscopy | 11 |

### Task

| Task | Papers |
| --- | ---: |
| detection / diagnosis | 1427 |
| measurement / quantification | 798 |
| segmentation | 715 |
| outcome prediction | 683 |
| reconstruction / imputation | 290 |
| other | 204 |
| workflow / non-interpretive | 203 |
| foundation model / vision-language | 34 |
| report generation / LLM | 31 |
| agent / autonomous | 6 |

### Age group

| Age group | Papers |
| --- | ---: |
| child | 1274 |
| fetal | 884 |
| adolescent | 830 |
| pediatric (unspecified) | 590 |
| infant | 551 |
| neonate | 358 |
| mixed pediatric and adult | 303 |

### Validation

| Strongest validation claimed | Papers |
| --- | ---: |
| internal only | 2279 |
| external / multi-center | 613 |
| none / not stated | 478 |
| reader study | 188 |
| prospective | 100 |

### Papers per year

| Year | Papers |
| --- | ---: |
| 2005 | 1 |
| 2006 | 2 |
| 2007 | 3 |
| 2008 | 8 |
| 2009 | 6 |
| 2010 | 4 |
| 2011 | 7 |
| 2012 | 15 |
| 2013 | 8 |
| 2014 | 18 |
| 2015 | 45 |
| 2016 | 43 |
| 2017 | 67 |
| 2018 | 104 |
| 2019 | 139 |
| 2020 | 195 |
| 2021 | 279 |
| 2022 | 383 |
| 2023 | 410 |
| 2024 | 555 |
| 2025 | 682 |
| 2026 | 684 |

## Named models (120 most cited)

| Model | Year | Cites | /yr | RCR | Modality | Population | Clinical problem | Release | Journal | Link |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| Attention Gate (Attention U-Net) | 2019 | 701 | 100.14 | 41.92 | ultrasound; CT | fetuses undergoing mid-pregnancy screening ultrasound; the segmentati… | identifying the correct standard views during fet… | open-source | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2019.01.012) |
| BrainNetCNN | 2017 | 370 | 41.11 | 17.62 | MRI | infants born preterm, scanned between 27 and 46 weeks postmenstrual a… | predicting neurodevelopmental outcome after prete… | unclear | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2016.09.046) |
| SynthStrip | 2022 | 320 | 80.0 | 33.97 | MRI | subjects from newborn to adult, across a range of acquisitions includ… | removing non-brain signal (skull-stripping) as a… | open-source | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2022.119474) |
| BIFSeg | 2018 | 277 | 34.62 | 15.58 | MRI | fetuses imaged with MRI; a second application uses brain tumor MRI | outlining fetal organs on MRI when only some orga… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2018.2791721) |
| CA-Net | 2021 | 269 | 53.8 | 22.45 | MRI | fetuses imaged with MRI; a second application uses dermoscopic skin l… | segmenting the placenta and fetal brain on fetal… | open-source | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2020.3035253) |
| GANCS | 2019 | 230 | 32.86 | 14.69 | MRI | pediatric patients undergoing contrast-enhanced abdominal MRI | shortening contrast-enhanced MRI in children by r… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2018.2858752) |
| SonoNet | 2017 | 193 | 21.44 | 10.91 | ultrasound | fetuses undergoing routine mid-pregnancy anomaly screening ultrasound | finding and labelling the standard views required… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2017.2712367) |
| DeepIGeoS | 2019 | 185 | 26.43 | 10.13 | MRI | fetal MRI studies; brain tumor FLAIR MRI is the second test case | producing clinically usable placental contours on… | unclear | IEEE transactions on pattern an… | [doi](https://doi.org/10.1109/TPAMI.2018.2840695) |
| LINKS | 2015 | 147 | 13.36 | 6.72 | MRI | 119 infants | Segmenting infant brain MRI into gray matter, whi… | unclear | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2014.12.042) |
| DeepCut | 2017 | 138 | 15.33 | 6.62 | MRI | fetuses in a fetal MRI dataset | segmenting fetal brain and lung on MRI without pi… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2016.2621185) |
| iBEAT V2.0 | 2023 | 106 | 35.33 | 15.28 | MRI | infants from birth to 6 years of age, across many imaging sites, prot… | measuring cortical development in infants, whose… | open-source | Nature protocols | [doi](https://doi.org/10.1038/s41596-023-00806-x) |
| BR-Net | 2020 | 97 | 16.17 | 5.03 | MRI; x-ray / radiography | adolescents in the NCANDA alcohol and neurodevelopment cohort, childr… | stopping a model from learning a confounder inste… | open-source | Nature communications | [doi](https://doi.org/10.1038/s41467-020-19784-9) |
| Functional Random Forest | 2018 | 91 | 11.38 | 4.52 | MRI | 47 children with autism and 58 typically developing children aged 9-13 | whether autism spectrum disorder contains distinc… | unclear | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2017.12.044) |
| FUIQA | 2017 | 91 | 10.11 | 5.08 | ultrasound | fetuses undergoing obstetric ultrasound examination | automatic quality control of obstetric ultrasound… | unclear | IEEE transactions on cybernetics | [doi](https://doi.org/10.1109/TCYB.2017.2671898) |
| Auto-Net | 2017 | 90 | 10.0 | 4.82 | MRI | public adult benchmark datasets plus reconstructed fetal brain MRI | extracting the brain from surrounding tissue on M… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2017.2721362) |
| time-dependent deep image prior | 2021 | 86 | 17.2 | 8.17 | MRI | fetuses in retrospective and real fetal cardiac MRI datasets | reconstructing a moving fetal heart from sparsely… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2021.3084288) |
| DPA-HNN | 2019 | 86 | 12.29 | 5.4 | CT | adult and pediatric patients whose thoracic CT reports were collected… | extracting whether a CT report says there is a pu… | unclear | Artificial intelligence in medi… | [doi](https://doi.org/10.1016/j.artmed.2018.11.004) |
| GPT-4V; Gemini Pro Vision | 2024 | 82 | 41.0 | 14.3 | multiple | 190 'Diagnosis Please' teaching cases published in Radiology (Jan 200… | generate differential diagnoses directly from rad… | commercial | Radiology | [doi](https://doi.org/10.1148/radiol.240273) |
| DeepUTE | 2018 | 81 | 11.57 | 4.88 | nuclear / PET; MRI | 79 pediatric brain tumor examinations, 36 with active tumor volume ab… | quantitatively accurate FET-PET/MRI in children w… | unclear | Frontiers in neuroscience | [doi](https://doi.org/10.3389/fnins.2018.01005) |
| DeepFMRI | 2020 | 72 | 12.0 | 4.89 | MRI | children in the public ADHD-200 dataset, contributed by several imagi… | diagnosing ADHD, which currently rests entirely o… | unclear | Journal of neuroscience methods | [doi](https://doi.org/10.1016/j.jneumeth.2019.108506) |
| Rayvolve | 2022 | 71 | 17.75 | 8.64 | x-ray / radiography | 2,549 children aged 0-17 (mean 8.5 years) referred from a pediatric e… | detecting fractures on radiographs of children pr… | commercial | Diagnostic and interventional i… | [doi](https://doi.org/10.1016/j.diii.2021.10.007) |
| DeepWMA | 2020 | 71 | 11.83 | 5.11 | MRI | 597 diffusion MRI scans from six independently acquired populations s… | identifying named white matter tracts consistentl… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2020.101761) |
| MF R-CNN | 2019 | 63 | 9.0 | 4.43 | ultrasound | fetuses undergoing prenatal ultrasound | deciding whether a fetal head ultrasound image is… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2019.101548) |
| ARVBNet | 2020 | 60 | 10.0 | 3.89 | ultrasound | fetuses undergoing cardiac screening ultrasound | deciding whether a fetal cardiac four-chamber vie… | unclear | IEEE journal of biomedical and… | [doi](https://doi.org/10.1109/JBHI.2019.2948316) |
| quantusFLM | 2015 | 60 | 5.45 | 2.89 | ultrasound | 144 neonates delivered between 28 and 39 weeks, imaged within 48 hour… | predicting neonatal respiratory morbidity before… | commercial | Ultrasound in obstetrics & gyne… | [doi](https://doi.org/10.1002/uog.13441) |
| Fracture Detection Using YOLOv8 App | 2023 | 58 | 19.33 | 12.59 | x-ray / radiography | children presenting with wrist trauma (public GRAZPEDWRI-DX pediatric… | detecting wrist fractures on trauma radiographs | unclear | Scientific reports | [doi](https://doi.org/10.1038/s41598-023-47460-7) |
| BoneView | 2022 | 55 | 13.75 | 7.05 | x-ray / radiography | 300 radiographic examinations from patients aged 2-21 (167 boys, 133… | detecting acute appendicular fractures in children | commercial | Skeletal radiology | [doi](https://doi.org/10.1007/s00256-022-04070-0) |
| deepee | 2021 | 53 | 10.6 | 3.46 | x-ray / radiography | children in the public pediatric pneumonia chest radiograph dataset,… | training diagnostic models on children's images w… | open-source | Scientific reports | [doi](https://doi.org/10.1038/s41598-021-93030-0) |
| CHN-PD | 2019 | 53 | 7.57 | 2.66 | MRI | 328 cognitively normal Chinese children aged 6-12, with two independe… | whether a pediatric brain atlas built on one popu… | open-source | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2019.01.006) |
| Appendicitis Prediction Tool | 2021 | 52 | 10.4 | 5.4 | ultrasound | 430 children and adolescents aged 0-18 with suspected appendicitis | three separate decisions in suspected pediatric a… | open-source | Frontiers in pediatrics | [doi](https://doi.org/10.3389/fped.2021.662183) |
| AutoRAPNO | 2022 | 49 | 12.25 | 4.44 | MRI | 794 children with preoperative MRI and 122 with serial postoperative… | measuring tumor burden reproducibly across serial… | unclear | Neuro-oncology | [doi](https://doi.org/10.1093/neuonc/noab151) |
| DAG V-Net | 2021 | 49 | 9.8 | 4.78 | ultrasound | fetuses across trimesters in the public HC18 challenge dataset (355 t… | measuring head circumference from a fetal ultraso… | open-source | Journal of digital imaging | [doi](https://doi.org/10.1007/s10278-020-00410-5) |
| DGACNN | 2020 | 49 | 8.17 | 3.78 | ultrasound | fetuses undergoing echocardiographic screening for congenital heart d… | screening for fetal congenital heart disease on e… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2019.2946059) |
| DW-Net | 2020 | 47 | 7.83 | 3.94 | ultrasound | 895 apical four-chamber views from fetal echocardiography | outlining the seven key structures of the apical… | unclear | Computerized medical imaging an… | [doi](https://doi.org/10.1016/j.compmedimag.2019.101690) |
| Cropping-Segmentation-Calibration (CSC) | 2020 | 47 | 7.83 | 2.54 | ultrasound | 615 annotated frames from 421 normal fetal cardiac ultrasound videos… | delineating the ventricular septum during fetal c… | unclear | Biomolecules | [doi](https://doi.org/10.3390/biom10111526) |
| EchoNet-Peds | 2023 | 45 | 15.0 | 5.7 | ultrasound | pediatric patients undergoing echocardiography (4,467 echocardiogram… | automated assessment of left ventricular ejection… | unclear | Journal of the American Society… | [doi](https://doi.org/10.1016/j.echo.2023.01.015) |
| Smartplanes | 2018 | 43 | 5.38 | 2.6 | ultrasound | 30 fetuses at 17-30 weeks gestation, each with two 3D volumes and a c… | finding the transthalamic plane and measuring bip… | commercial | Diagnostic and interventional i… | [doi](https://doi.org/10.1016/j.diii.2018.08.001) |
| childfx | 2023 | 42 | 14.0 | 8.58 | x-ray / radiography | 58,846 upper extremity radiographs from 14,873 pediatric and young ad… | pediatric upper extremity fractures, which respon… | open-source | Pediatric radiology | [doi](https://doi.org/10.1007/s00247-023-05754-y) |
| MABAL | 2018 | 42 | 5.25 | 2.96 | x-ray / radiography | 10,289 skeletal age examinations, 8,909 from one institution's archiv… | bone age assessment, which is tedious and time co… | unclear | Journal of digital imaging | [doi](https://doi.org/10.1007/s10278-018-0053-3) |
| CAD4Kids | 2020 | 41 | 6.83 | 2.93 | x-ray / radiography | 858 interpretable pediatric chest radiographs, 39% with primary-endpo… | identifying WHO-defined primary-endpoint pneumoni… | unclear | Pediatric radiology | [doi](https://doi.org/10.1007/s00247-019-04593-0) |
| SupWMA | 2023 | 40 | 13.33 | 7.14 | MRI | six independently acquired datasets spanning ages and health conditio… | parcellating the superficial white matter, which… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2023.102759) |
| PRIMAGE | 2020 | 40 | 6.67 | 2.52 | multiple | children with neuroblastoma or diffuse intrinsic pontine glioma acros… | phenotyping, treatment allocation and prognosis i… | unclear | European radiology experimental | [doi](https://doi.org/10.1186/s41747-020-00150-9) |
| Spherical U-Net | 2019 | 40 | 5.71 | 2.2 | MRI | infants | parcellating the infant cortical surface and pred… | unclear | Information processing in medic… | [doi](https://doi.org/10.1007/978-3-030-20351-1_67) |
| FeTA | 2023 | 39 | 13.0 | 6.59 | MRI | fetuses in the open FeTA dataset of reconstructed brain MRI segmented… | segmenting the developing fetal brain into tissue… | open-source | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2023.102833) |
| PAICS | 2022 | 39 | 9.75 | 5.12 | ultrasound | 16,297 pregnancies at 18-40 weeks from two tertiary Chinese hospitals… | screening for congenital central nervous system m… | unclear | Ultrasound in obstetrics & gyne… | [doi](https://doi.org/10.1002/uog.24843) |
| quantusFLM | 2019 | 38 | 5.43 | 2.54 | ultrasound | 790 fetal lung ultrasound images obtained between 24 and 39 weeks ges… | predicting neonatal respiratory morbidity from ul… | commercial | Scientific reports | [doi](https://doi.org/10.1038/s41598-019-38576-w) |
| BoneXpert | 2022 | 37 | 9.25 | 4.4 | x-ray / radiography | 97 radiologists across 18 European countries already using the softwa… | what actually happens when an AI tool designed to… | commercial | Pediatric radiology | [doi](https://doi.org/10.1007/s00247-022-05295-w) |
| GRAZPEDWRI-DX | 2022 | 37 | 9.25 | 4.78 | x-ray / radiography | 6,091 children treated for wrist trauma at one pediatric surgery depa… | the absence of an annotated public pediatric frac… | open-source | Scientific data | [doi](https://doi.org/10.1038/s41597-022-01328-z) |
| CarMEN | 2019 | 37 | 5.29 | 2.48 | MRI | trained and tested on 150 cardiac MRI patients, then validated on a s… | estimating three-dimensional deformable cardiac m… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.2019180080) |
| 2017 RSNA Pediatric Bone Age Challenge ensembles | 2019 | 37 | 5.29 | 2.51 | x-ray / radiography | 12 611 pediatric hand radiographs for development and a 200-radiograp… | automated skeletal age estimation from hand radio… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.2019190053) |
| 2017 RSNA Bone Age Challenge winning model | 2023 | 36 | 12.0 | 5.34 | x-ray / radiography | trained on 12 611 pediatric hand radiographs from two U.S. hospitals;… | whether an expert-level bone age model holds up o… | unclear | Radiology | [doi](https://doi.org/10.1148/radiol.220505) |
| PN-UNet (Pyramid Non-local UNet) | 2020 | 36 | 6.0 | 3.19 | x-ray / radiography | infants and young children undergoing pelvis radiography for suspecte… | detecting misshapen pelvis anatomical landmarks t… | open-source | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2020.3008382) |
| ScolioNets | 2023 | 35 | 11.67 | 8.13 | other | adolescent patients attending spine clinics, with radiographs and sma… | classifying severity and curve type in adolescent… | commercial | JAMA network open | [doi](https://doi.org/10.1001/jamanetworkopen.2023.30617) |
| DLIR (deep learning image reconstruction) | 2021 | 35 | 7.0 | 2.97 | CT | 46 children (mean age 5.9 +/- 4.2 years) scanned at 70 kVp with 0.8-1… | cutting both radiation and iodinated contrast dos… | commercial | La Radiologia medica | [doi](https://doi.org/10.1007/s11547-021-01384-2) |
| DeepMedic | 2020 | 34 | 5.67 | 1.67 | nuclear / PET | 100 pediatric Hodgkin lymphoma patients with baseline 18F-FDG PET/CT,… | extracting metabolic tumor volume and the other b… | open-source | EJNMMI physics | [doi](https://doi.org/10.1186/s40658-020-00346-3) |
| TransferX | 2024 | 33 | 16.5 | 5.96 | MRI | 214 children at Dana-Farber/Boston Children's for development and 112… | determining BRAF mutational status in pediatric l… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.230333) |
| PediCXR | 2023 | 33 | 11.0 | 5.21 | x-ray / radiography | 9125 studies retrospectively collected from a major pediatric hospita… | the shortage of physician-annotated pediatric che… | open-source | Scientific data | [doi](https://doi.org/10.1038/s41597-023-02102-5) |
| HBN-POD2 quality control network | 2022 | 33 | 8.25 | 3.46 | MRI | 2747 diffusion MRI datasets from children and adolescents in the Heal… | quality control of diffusion MRI at a scale where… | open-source | Scientific data | [doi](https://doi.org/10.1038/s41597-022-01695-7) |
| DLIR (deep learning image reconstruction) | 2021 | 33 | 6.6 | 3.11 | CT | 33 children scanned at 70 kVp with automatic tube current modulation… | keeping thin-slice pediatric chest CT angiography… | commercial | Quantitative imaging in medicin… | [doi](https://doi.org/10.21037/qims-20-1158) |
| DeepSSM | 2018 | 33 | 4.12 | 2.56 | CT; MRI | three applications, the first of which is pediatric cranial CT for ch… | building statistical shape models straight from r… | unclear | Shape in medical imaging : Inte… | [doi](https://doi.org/10.1007/978-3-030-04747-4_23) |
| SepUNet | 2022 | 32 | 8.0 | 3.63 | MRI | more than 80 000 osteosarcoma MRI images from three hospitals in Chin… | segmenting osteosarcoma on MRI and computing tumo… | unclear | Computational and mathematical… | [doi](https://doi.org/10.1155/2022/7703583) |
| FUVAI | 2022 | 31 | 7.75 | 3.93 | ultrasound | 50 freehand fetal ultrasound video scans, compared against five exper… | fetal biometry - head circumference, biparietal d… | unclear | Physics in medicine and biology | [doi](https://doi.org/10.1088/1361-6560/ac4d85) |
| graph chart diagram | 2022 | 31 | 7.75 | 3.53 | ultrasound | fetal cardiac ultrasound screening read by experts, fellows and resid… | screening for congenital heart disease on fetal c… | unclear | Biomedicines | [doi](https://doi.org/10.3390/biomedicines10030551) |
| BoneView | 2024 | 30 | 15.0 | 10.15 | x-ray / radiography | up to 1,000 radiographs per body part from a single emergency departm… | which pediatric fracture types a marketed AI tool… | commercial | Pediatric radiology | [doi](https://doi.org/10.1007/s00247-023-05822-3) |
| CortexODE | 2023 | 30 | 10.0 | 4.81 | MRI | large-scale neuroimaging datasets across age groups including neonate… | reconstructing cortical surfaces from brain MRI,… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2022.3206221) |
| SpineHRNet+ | 2022 | 30 | 7.5 | 3.87 | x-ray / radiography | 1542 consecutive patients with scoliosis at two Hong Kong clinics fro… | automatic measurement of spine alignment in scoli… | unclear | EClinicalMedicine | [doi](https://doi.org/10.1016/j.eclinm.2021.101252) |
| MEDO-Hip | 2023 | 29 | 9.67 | 6.08 | ultrasound | 369 scans in 306 infants, scanned by nurses or family physicians at t… | universal newborn screening for developmental dys… | commercial | Scientific reports | [doi](https://doi.org/10.1038/s41598-023-35603-9) |
| Brain Maturation Index | 2015 | 29 | 2.64 | 1.13 | MRI | 303 healthy subjects aged 4.88-18.35 years (115 rescanned after 2 yea… | predicting individual brain maturation (biologica… | unclear | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2015.05.071) |
| Pediatric-CT-SEG | 2022 | 28 | 7.0 | 3.23 | CT | 359 pediatric chest-abdomen-pelvis or abdomen-pelvis CT exams (180 ma… | organ autosegmentation has been developed almost… | open-source | Medical physics | [doi](https://doi.org/10.1002/mp.15485) |
| SonoCNS Fetal Brain | 2021 | 28 | 5.6 | 2.78 | ultrasound | 143 women at routine anatomical survey between 18+0 and 22+6 weeks, e… | obtaining the five standard fetal intracranial me… | commercial | Ultrasound in obstetrics & gyne… | [doi](https://doi.org/10.1002/uog.22171) |
| Temporal SonoEyeNet (TSEN) | 2020 | 28 | 4.67 | 2.36 | ultrasound | 280 video clips of 3-7 seconds each, one per biometry plane, with sim… | how an experienced sonographer navigates to a sta… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2020.101762) |
| StrainNet | 2023 | 27 | 9.0 | 3.88 | MRI | 161 patients with various heart diseases, 99 healthy adults, and 45 h… | measuring myocardial strain from ordinary cine MR… | unclear | Radiology. Cardiothoracic imagi… | [doi](https://doi.org/10.1148/ryct.220196) |
| Multi-Frame + Cylinder method (MFCY) | 2020 | 27 | 4.5 | 1.29 | ultrasound | 538 four-chamber-view ultrasound frames from 256 normal cases, five-f… | segmenting the fetal thoracic wall on the four-ch… | unclear | Biomolecules | [doi](https://doi.org/10.3390/biom10121691) |
| SSLDEC | 2019 | 27 | 3.86 | 1.48 | MRI | isointense-phase infant brain MRI, alongside MNIST and SVHN benchmark… | the cost of expert annotation in medical image se… | unclear | IEEE access : practical innovat… | [doi](https://doi.org/10.1109/ACCESS.2019.2891970) |
| FBNetGen | 2022 | 26 | 6.5 | 2.65 | MRI | the Adolescent Brain Cognitive Development (ABCD) cohort and the Phil… | clinical prediction from functional brain network… | open-source | Proceedings of machine learning… | [pubmed](https://pubmed.ncbi.nlm.nih.gov/37377881/) |
| DLR (deep learning reconstruction) | 2021 | 26 | 5.2 | 2.67 | CT | 51 children aged 1-18 years (34 boys, 17 girls) scanned February to O… | reducing radiation dose in pediatric body CT, whe… | commercial | BMC medical imaging | [doi](https://doi.org/10.1186/s12880-021-00677-2) |
| TW3-AI | 2020 | 26 | 4.33 | 2.31 | x-ray / radiography | 9059 clinical left hand radiographs from PACS between January 2012 an… | bone age assessment by the Tanner-Whitehouse 3 me… | unclear | Quantitative imaging in medicin… | [doi](https://doi.org/10.21037/qims.2020.02.20) |
| TDL-BAAM | 2020 | 26 | 4.33 | 1.74 | x-ray / radiography | 15 129 frontal pediatric trauma hand radiographs from Children's Hosp… | whether bone age assessment should still be ancho… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.2020190198) |
| DUnet / ResDUnet | 2019 | 26 | 3.71 | 1.47 | MRI | infant brain MRI | segmenting hippocampal subfields in infants, wher… | unclear | Frontiers in neuroinformatics | [doi](https://doi.org/10.3389/fninf.2019.00030) |
| VP-Nets | 2018 | 26 | 3.25 | 1.25 | ultrasound | 3D fetal neurosonography volumes | locating key brain structures in 3D fetal neuroso… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2018.04.004) |
| Pneumo-CAD | 2008 | 26 | 1.44 | 0.84 | x-ray / radiography | children with clinical suspicion of pneumonia, chest radiographs clas… | computer-aided diagnosis of pneumonia in children… | unclear | International journal of medica… | [doi](https://doi.org/10.1016/j.ijmedinf.2007.10.010) |
| Deeplasia | 2024 | 25 | 12.5 | 6.53 | x-ray / radiography | the public RSNA challenge set for training, plus 568 radiographs from… | bone age in children with skeletal dysplasia, whe… | open-source | Pediatric radiology | [doi](https://doi.org/10.1007/s00247-023-05789-1) |
| CAD4TB | 2023 | 25 | 8.33 | 3.64 | x-ray / radiography | 620 children under 13 years with presumptive tuberculosis in South Af… | computer-aided detection of intrathoracic tubercu… | commercial | PLOS global public health | [doi](https://doi.org/10.1371/journal.pgph.0001799) |
| AF-net | 2021 | 25 | 5.0 | 2.32 | ultrasound | antenatal ultrasound examinations, sizes not stated | measuring the amniotic fluid index, which informs… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2020.101951) |
| H-DenseUNet | 2021 | 25 | 5.0 | 2.71 | MRI | T1-weighted lower leg MRI of 20 children, six of them with cerebral p… | segmenting individual lower leg muscles and bones… | unclear | NMR in biomedicine | [doi](https://doi.org/10.1002/nbm.4609) |
| childfx | 2024 | 24 | 12.0 | 8.19 | x-ray / radiography | 240 patients (mean age 11.3 years, range 0-22, 37.9% female) with elb… | upper extremity fractures missed by residents and… | open-source | Skeletal radiology | [doi](https://doi.org/10.1007/s00256-024-04698-0) |
| DeepMNF | 2023 | 24 | 8.0 | 4.27 | MRI | the ABIDE-1 repository, including data from all available screening s… | computer-aided diagnosis of autism spectrum disor… | unclear | Artificial intelligence in medi… | [doi](https://doi.org/10.1016/j.artmed.2022.102475) |
| S3Reg | 2021 | 24 | 4.8 | 1.93 | MRI | two datasets covering adult and infant multimodal cortical features | cortical surface registration, the prerequisite f… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2021.3069645) |
| Multi-task SonoEyeNet (M-SEN) | 2018 | 24 | 3.0 | 1.55 | ultrasound | fetal ultrasound video frames with sonographer gaze tracking data | detecting the standardized abdominal circumferenc… | unclear | Medical image computing and com… | [doi](https://doi.org/10.1007/978-3-030-00928-1_98) |
| ALFA (Accurate Learning with Few Atlases) | 2016 | 24 | 2.4 | 1.15 | MRI | multi-modal brain MRI of 50 newborns | brain extraction from neonatal MRI - the first st… | unclear | Scientific reports | [doi](https://doi.org/10.1038/srep23470) |
| NEOCIVET 2.0 | 2021 | 23 | 4.6 | 1.74 | MRI | three independent datasets comprising 736 pre-term and 97 term neonat… | measuring cortical thickness in neonates, where s… | open-source | Frontiers in neuroscience | [doi](https://doi.org/10.3389/fnins.2021.650082) |
| BOUNTI | 2023 | 22 | 7.33 | 3.64 | MRI | trained on 360 fetal MRI datasets with different acquisition paramete… | fetal brain volumetry has no universally accepted… | open-source | bioRxiv : the preprint server f… | [doi](https://doi.org/10.1101/2023.04.18.537347) |
| TrueFidelity | 2022 | 22 | 5.5 | 2.66 | CT | 120 pediatric patients (mean age 8.7 +/- 5.2 years, 60 male) who had… | image quality in pediatric abdominopelvic CT, whe… | commercial | Korean journal of radiology | [doi](https://doi.org/10.3348/kjr.2021.0466) |
| msResNet | 2022 | 22 | 5.5 | 2.42 | MRI | children with drug-resistant epilepsy undergoing clinically acquired… | localizing the seizure onset zone non-invasively… | unclear | IEEE journal of biomedical and… | [doi](https://doi.org/10.1109/JBHI.2022.3196330) |
| APPLAUSE | 2021 | 22 | 4.4 | 2.1 | MRI | 108 placental datasets at 3 T including 20 high-risk pregnancies with… | assessing placental maturation and health from T2… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2021.102145) |
| Attention MFP-Unet | 2021 | 22 | 4.4 | 1.96 | ultrasound | the public HC18 grand challenge dataset plus clinical data from 1334… | measuring biparietal diameter, head circumference… | unclear | Physica medica : PM : an intern… | [doi](https://doi.org/10.1016/j.ejmp.2021.06.020) |
| LiviaNET / HyperDense-Net | 2020 | 22 | 3.67 | 1.53 | MRI | 24 pairs of neonatal T1 and T2 data from the Developing Human Connect… | segmenting gray matter, white matter and cerebros… | open-source | Frontiers in neuroscience | [doi](https://doi.org/10.3389/fnins.2020.00207) |
| TL-CNN | 2020 | 22 | 3.67 | 1.53 | MRI | 110 very preterm infants (≤32 weeks gestational age) | early prediction of cognitive deficit at 2 years… | unclear | Frontiers in neuroscience | [doi](https://doi.org/10.3389/fnins.2020.00858) |
| US-GuideNet | 2020 | 22 | 3.67 | 1.76 | ultrasound | 464 routine clinical scans by 17 accredited sonographers, with real-w… | the operator expertise required to find standard… | unclear | Medical image computing and com… | [doi](https://doi.org/10.1007/978-3-030-59716-0_56) |
| PIN (Patch-based Iterative Network) | 2018 | 22 | 2.75 | 1.49 | ultrasound | 72 3D ultrasound images from fetal screening examinations | locating anatomical landmarks in 3D fetal screeni… | unclear | Medical image computing and com… | [doi](https://doi.org/10.1007/978-3-030-00928-1_64) |
| SpineTK | 2023 | 21 | 7.0 | 4.65 | x-ray / radiography | 1310 anterior-posterior low-dose stereoradiographic images and radiog… | Cobb angle measurement, the definitional measurem… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.220158) |
| UPL-SFDA | 2023 | 21 | 7.0 | 4.14 | MRI | validated on a multi-site cardiac MRI dataset, a cross-modality fetal… | adapting a segmentation model to a new hospital w… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2023.3318364) |
| DenseNet169 | 2023 | 21 | 7.0 | 4.59 | ultrasound | fetal ultrasound images from two datasets from different regions, rec… | identifying which fetal organ an ultrasound image… | unclear | Scientific reports | [doi](https://doi.org/10.1038/s41598-023-44689-0) |
| Light_U-Net | 2022 | 21 | 5.25 | 2.89 | MRI; CT | 39 pediatric and adult patients with both bone MRI and CT of the head… | generating CT-equivalent images from bone MRI so… | unclear | AJNR. American journal of neuro… | [doi](https://doi.org/10.3174/ajnr.A7588) |
| dilated-dense U-Net | 2019 | 21 | 3.0 | 1.18 | MRI | infants at risk of autism spectrum disorder scanned at 6, 12 and 24 m… | measuring amygdala and hippocampal subfield volum… | unclear | Graph Learning in Medical Imagi… | [doi](https://doi.org/10.1007/978-3-030-35817-4_20) |
| PSFFGAN | 2023 | 20 | 6.67 | 3.94 | ultrasound | fetal four-chamber ultrasound views, healthy and with congenital hear… | the shortage of large, high-quality fetal four-ch… | unclear | IEEE journal of biomedical and… | [doi](https://doi.org/10.1109/JBHI.2022.3143319) |
| LungQ bronchus-artery analysis | 2023 | 20 | 6.67 | 2.81 | CT | 113 baseline and 102 48-week chest CT scans from 115 children aged 3-… | measuring bronchial wall thickening and bronchial… | commercial | Journal of cystic fibrosis : of… | [doi](https://doi.org/10.1016/j.jcf.2023.05.013) |
| MEDO-Hip | 2023 | 20 | 6.67 | 3.91 | ultrasound | 306 infants (369 scans) screened at routine 6-10 week well-child visi… | screening every infant for developmental dysplasi… | commercial | Paediatrics & child health | [doi](https://doi.org/10.1093/pch/pxad013) |
| phasrGAN / phasrresnet | 2022 | 20 | 5.0 | 2.05 | MRI | 28 fetuses at a median gestational week of 36 (IQR 33-38), imaged at… | fetal cardiac MRI improves diagnosis of congenita… | unclear | Journal of magnetic resonance i… | [doi](https://doi.org/10.1002/jmri.27956) |
| PTNet3D | 2022 | 20 | 5.0 | 2.43 | MRI | the high-resolution Developing Human Connectome Project and the longi… | infants sleep irregularly, cannot follow instruct… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2022.3174827) |
| TTTS-GPS | 2019 | 20 | 2.86 | 1.38 | MRI; ultrasound | pregnancies with twin-to-twin transfusion syndrome, imaged with MRI a… | planning minimally invasive fetoscopic laser surg… | unclear | Computer methods and programs i… | [doi](https://doi.org/10.1016/j.cmpb.2019.104993) |
| BIBSNet | 2025 | 19 | 19.0 | 6.83 | MRI | 90 participants aged 0-8 months (median 4.6 months) | segmenting the infant brain in the first months o… | open-source | bioRxiv : the preprint server f… | [doi](https://doi.org/10.1101/2023.03.22.533696) |
| ChatGPT-4 | 2024 | 19 | 9.5 | 5.68 | ultrasound | 103 randomly selected anonymized ultrasound and operative records fro… | turning free-text ultrasound and operative report… | commercial | Journal of pediatric surgery | [doi](https://doi.org/10.1016/j.jpedsurg.2024.01.033) |
| SynthSR | 2024 | 19 | 9.5 | 4.46 | MRI | 70 individuals, mean age 20.39 years (range 9-26 years) | improving correspondence between low-field and hi… | unclear | Frontiers in neurology | [doi](https://doi.org/10.3389/fneur.2024.1339223) |
| TorchXRayVision | 2023 | 19 | 6.33 | 2.98 | x-ray / radiography | pediatric patients aged 1 to 5 years (publicly available pediatric ch… | detecting pneumonia on pediatric chest radiograph… | unclear | Journal of the American College… | [doi](https://doi.org/10.1016/j.jacr.2023.07.004) |
| Medo Hip | 2022 | 19 | 4.75 | 2.44 | ultrasound | 240 infant hips (120 single 2D images, 120 sweeps) spanning normal to… | detecting developmental dysplasia of the hip on i… | commercial | Journal of pediatric orthopedics | [doi](https://doi.org/10.1097/BPO.0000000000002065) |
| ST-DAG-Att | 2022 | 19 | 4.75 | 1.96 | MRI | Adolescent Brain Cognitive Development cohort (n=7,693, children) and… | predicting cognition and age from resting-state f… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2022.102370) |
| BA-GCA Net | 2022 | 19 | 4.75 | 2.33 | MRI | adolescents with osteosarcoma | segmenting osteosarcoma tumor boundaries on MRI | unclear | Computational intelligence and… | [doi](https://doi.org/10.1155/2022/3881833) |
| ETLM (Ensemble Transfer Learning Model) | 2022 | 19 | 4.75 | 2.76 | ultrasound | fetuses undergoing obstetric ultrasound (public HC18 dataset) | segmenting the fetal head on ultrasound and estim… | unclear | Diagnostics (Basel, Switzerland) | [doi](https://doi.org/10.3390/diagnostics12092229) |
| MA-Net | 2020 | 19 | 3.17 | 1.39 | ultrasound; MRI; CT | not specifically described; evaluated on several public/benchmark ult… | general-purpose segmentation of ultrasound images… | unclear | Medical physics | [doi](https://doi.org/10.1002/mp.14512) |

## Most-cited-per-year work from 2024 onward (40)

Ranked by citations per year rather than raw count, because a paper from this year has had no time to accumulate one. `RCR` is iCite's relative citation ratio (1.0 is the median NIH-funded paper of the same field and year) and falls back to OpenAlex's field-weighted citation impact where iCite has not computed it, which is most of the last two years.

| Title | Year | Cites | /yr | RCR/FWCI | Type | Clinical problem | Link |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| GPT-4V; Gemini Pro Vision | 2024 | 82 | 41.0 | 14.3 | journal | generate differential diagnoses directly from… | [doi](https://doi.org/10.1148/radiol.240273) |
| A foundation model for enhancing magnetic resonance images and… | 2025 | 34 | 34.0 | 10.8 | journal | improving MR image quality (motion artifact,… | [doi](https://doi.org/10.1038/s41551-024-01283-7) |
| Prediction of mental health risk in adolescents. | 2025 | 34 | 34.0 | 11.34 | journal | predicting future risk of general psychiatric… | [doi](https://doi.org/10.1038/s41591-025-03560-7) |
| Multimodal deep learning improves recurrence risk prediction in… | 2025 | 26 | 26.0 | 7.84 | journal | predicting which children will recur after su… | [doi](https://doi.org/10.1093/neuonc/noae173) |
| Artificial Intelligence for Neuroimaging in Pediatric Cancer. | 2025 | 24 | 24.0 | 8.3 | journal | use of AI to improve pediatric cancer neuroim… | [doi](https://doi.org/10.3390/cancers17040622) |
| Lack of children in public medical imaging data points to growi… | 2025 | 22 | 22.0 | 8.08 | preprint | whether children are represented at all in th… | [doi](https://doi.org/10.1101/2025.06.06.25328913) |
| Predicting pediatric patient rehabilitation outcomes after spin… | 2025 | 21 | 21.0 | 7.96 | journal | telling an adolescent before scoliosis surger… | [doi](https://doi.org/10.1038/s43856-024-00726-1) |
| BIBSNet | 2025 | 19 | 19.0 | 6.83 | preprint | segmenting the infant brain in the first mont… | [doi](https://doi.org/10.1101/2023.03.22.533696) |
| Multiparametric MRI along with machine learning predicts progno… | 2025 | 18 | 18.0 | 4.63 | journal | identifying which children with low-grade gli… | [doi](https://doi.org/10.1038/s41467-024-55659-z) |
| Using Artificial Intelligence for Rheumatic Heart Disease Detec… | 2024 | 34 | 17.0 | 7.32 | journal | detecting rheumatic heart disease via mitral… | [doi](https://doi.org/10.1161/JAHA.123.031257) |
| Cognitive Impairment Is Related to Glymphatic System Dysfunctio… | 2024 | 34 | 17.0 | 6.92 | journal | predicting cognitive impairment in pediatric… | [doi](https://doi.org/10.1002/ana.26911) |
| Assessment of glymphatic function and white matter integrity in… | 2025 | 17 | 17.0 | 5.78 | journal | detecting autism spectrum disorder on imaging… | [doi](https://doi.org/10.1007/s00330-025-11359-w) |
| Integrated brain connectivity analysis with fMRI, DTI, and sMRI… | 2025 | 17 | 17.0 | 6.01 | journal | Integrating multimodal brain imaging (fMRI, D… | [doi](https://doi.org/10.1016/j.media.2025.103570) |
| Deep-learning model for prenatal congenital heart disease scree… | 2024 | 33 | 16.5 | 8.72 | journal | congenital heart defects missed at the routin… | [doi](https://doi.org/10.1002/uog.27503) |
| TransferX | 2024 | 33 | 16.5 | 5.96 | journal | determining BRAF mutational status in pediatr… | [doi](https://doi.org/10.1148/ryai.230333) |
| Diagnostic Accuracy of an Integrated AI Tool to Estimate Gestat… | 2024 | 32 | 16.0 | 7.17 | journal | dating a pregnancy where no trained sonograph… | [doi](https://doi.org/10.1001/jama.2024.10770) |
| AI implementation in pediatric radiology for patient safety: a… | 2026 | 16 | 16.0 | 13.34 | journal | how a children's hospital should buy, deploy,… | [doi](https://doi.org/10.1007/s00247-025-06386-0) |
| Artificial intelligence-assisted approach to assessing bowel wa… | 2025 | 16 | 16.0 | 5.79 | journal | measuring bowel wall thickness on intestinal… | [doi](https://doi.org/10.1093/ecco-jcc/jjaf037) |
| BoneView | 2024 | 30 | 15.0 | 10.15 | journal | which pediatric fracture types a marketed AI… | [doi](https://doi.org/10.1007/s00247-023-05822-3) |
| Toward governance of artificial intelligence in pediatric healt… | 2025 | 15 | 15.0 | 5.26 | journal | who is accountable when AI is used on a child… | [doi](https://doi.org/10.1038/s41746-025-02000-7) |
| Advances in the Application of Artificial Intelligence in Fetal… | 2024 | 29 | 14.5 | 8.16 | journal | operator dependence in fetal echocardiography… | [doi](https://doi.org/10.1016/j.echo.2023.12.013) |
| The unintended consequences of artificial intelligence in paedi… | 2024 | 28 | 14.0 | 7.26 | journal | the harms AI can cause in a pediatric setting… | [doi](https://doi.org/10.1007/s00247-023-05746-y) |
| Automated Neuroprognostication Via Machine Learning in Neonates… | 2025 | 14 | 14.0 | 5.23 | journal | predicting neurodevelopmental outcome after n… | [doi](https://doi.org/10.1002/ana.27154) |
| Development and validation of fully automated robust deep learn… | 2025 | 14 | 14.0 | 5.43 | journal | having organ masks on a child's CT, which pat… | [doi](https://doi.org/10.1016/j.ejmp.2025.104911) |
| Applications of artificial intelligence and advanced imaging in… | 2025 | 14 | 14.0 | 4.41 | journal | characterizing diffuse midline glioma, a fata… | [doi](https://doi.org/10.1093/neuonc/noaf058) |
| MRI-Based End-To-End Pediatric Low-Grade Glioma Segmentation an… | 2024 | 27 | 13.5 | 7.35 | journal | predicting BRAF status in pediatric low-grade… | [doi](https://doi.org/10.1177/08465371231184780) |
| Interpretable and intervenable ultrasonography-based machine le… | 2024 | 26 | 13.0 | 7.06 | journal | diagnosis, management and severity of suspect… | [doi](https://doi.org/10.1016/j.media.2023.103042) |
| Stepwise Transfer Learning for Expert-level Pediatric Brain Tum… | 2024 | 26 | 13.0 | 5.8 | journal | segmenting pediatric brain tumors for volumet… | [doi](https://doi.org/10.1148/ryai.230254) |
| BoneXpert, PANDA, BoneView | 2025 | 13 | 13.0 | 5.28 | journal | which of the bone age products approved for t… | [doi](https://doi.org/10.1007/s00330-024-11169-6) |
| Scanner-based real-time three-dimensional brain + body slice-to… | 2025 | 13 | 13.0 | 5.03 | journal | motion-corrected 3D fetal MRI has stayed a re… | [doi](https://doi.org/10.1007/s00247-025-06165-x) |
| Real-life benefit of artificial intelligence-based fracture det… | 2025 | 13 | 13.0 | 5.36 | journal | whether a bought AI tool actually helps the i… | [doi](https://doi.org/10.1007/s00330-025-11554-9) |
| Deeplasia | 2024 | 25 | 12.5 | 6.53 | journal | bone age in children with skeletal dysplasia,… | [doi](https://doi.org/10.1007/s00247-023-05789-1) |
| Using brain structural neuroimaging measures to predict psychos… | 2024 | 25 | 12.5 | 4.82 | journal | predicting which clinically high-risk individ… | [doi](https://doi.org/10.1038/s41380-024-02426-7) |
| Role of artificial-intelligence-assisted automated cardiac biom… | 2024 | 25 | 12.5 | 7.51 | journal | coarctation of the aorta, which is missed bef… | [doi](https://doi.org/10.1002/uog.27608) |
| Training and Comparison of nnU-Net and DeepMedic Methods for Au… | 2024 | 25 | 12.5 | 6.21 | journal | automated segmentation of pediatric brain tum… | [doi](https://doi.org/10.3174/ajnr.A8293) |
| Estimating cortical thickness trajectories in children across d… | 2024 | 24 | 12.0 | 4.94 | journal | estimating individual cortical thickness deve… | [doi](https://doi.org/10.1002/hbm.26565) |
| AI-Assisted X-ray Fracture Detection in Residency Training: Eva… | 2024 | 24 | 12.0 | 7.5 | journal | whether AI assistance helps radiology residen… | [doi](https://doi.org/10.3390/diagnostics14060596) |
| childfx | 2024 | 24 | 12.0 | 8.19 | journal | upper extremity fractures missed by residents… | [doi](https://doi.org/10.1007/s00256-024-04698-0) |
| TotalSegmentator | 2025 | 12 | 12.0 | 3.65 | journal | whether the field's default open organ segmen… | [doi](https://doi.org/10.1007/s10278-024-01273-w) |
| Artificial intelligence (AI) in radiological paediatric fractur… | 2025 | 12 | 12.0 | 4.81 | journal | detecting bone injury in children, now that b… | [doi](https://doi.org/10.1007/s00330-025-11449-9) |

The full table, including the model description, dataset size, validation and headline result for every paper, is `data/processed/pedrad_paper_db.csv`.
