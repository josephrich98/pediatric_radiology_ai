# Pediatric radiology AI: paper database

Generated 2026-09-09 from `data/processed/pedrad_paper_db.csv`.

325 papers, 73 of which name a model or product, screened from 585 PubMed records matching the pediatric radiology-AI query (title/abstract fielded) for 2015-2026 (260 were screened out as adult-only, non-radiologic, or non-AI).

Candidates are papers meeting at least 20 citations in NIH iCite or at least 10 citations per year or a relative citation ratio of at least 5, which keeps the database to work the field has actually engaged with. A raw citation floor is also a recency filter — a paper published this year has had no time to accrue citations — which is why the rate and ratio clauses exist; even so the current year is thin by construction, and the trend figures, not this table, are the place to read growth.

Impact is reported four ways because no one measure works across the whole range. `citations` is the raw count and can only be compared within a year. `citations/yr` is that count divided by years since publication. `RCR` is iCite's relative citation ratio, where 1.0 is the median NIH-funded paper of the same field and year, and is the column to use when comparing a 2016 paper with a 2024 one; it is undefined until a paper is about two years old. `fwci` is OpenAlex's field-weighted citation impact, on the same 1.0-is-average scale, and covers some of what RCR does not.

Each row is read from the paper's abstract under a fixed schema, so a field is blank when the abstract does not state it — most notably the release column, which abstracts are usually silent about. Read "unclear" as "the paper does not say", not as "unavailable". Hand corrections in `data/paper_db_overrides.json` take precedence over the extracted value and are flagged in the `overridden_fields` column of the CSV.

## Counts

### Release status

| Status | Papers |
| --- | ---: |
| unclear | 265 |
| commercial | 32 |
| open-source | 24 |
| unreleased | 4 |

### Modality

| Modality | Papers |
| --- | ---: |
| MRI | 140 |
| x-ray / radiography | 78 |
| ultrasound | 73 |
| CT | 35 |
| multiple | 10 |
| nuclear / PET | 7 |
| other | 5 |

### Task

| Task | Papers |
| --- | ---: |
| detection / diagnosis | 142 |
| measurement / quantification | 85 |
| segmentation | 73 |
| outcome prediction | 56 |
| workflow / non-interpretive | 32 |
| reconstruction / imputation | 32 |
| other | 8 |
| report generation / LLM | 3 |
| agent / autonomous | 1 |
| foundation model / vision-language | 1 |

### Age group

| Age group | Papers |
| --- | ---: |
| pediatric (unspecified) | 98 |
| fetal | 85 |
| child | 75 |
| adolescent | 53 |
| mixed pediatric and adult | 41 |
| infant | 28 |
| neonate | 21 |

### Validation

| Strongest validation claimed | Papers |
| --- | ---: |
| internal only | 151 |
| external / multi-center | 78 |
| none / not stated | 46 |
| reader study | 39 |
| prospective | 11 |

### Papers per year

| Year | Papers |
| --- | ---: |
| 2015 | 8 |
| 2016 | 10 |
| 2017 | 21 |
| 2018 | 28 |
| 2019 | 47 |
| 2020 | 43 |
| 2021 | 44 |
| 2022 | 38 |
| 2023 | 19 |
| 2024 | 35 |
| 2025 | 28 |
| 2026 | 4 |

## Named models (73 most cited)

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
| DeepCut | 2017 | 138 | 15.33 | 6.62 | MRI | fetuses in a fetal MRI dataset | segmenting fetal brain and lung on MRI without pi… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2016.2621185) |
| iBEAT V2.0 | 2023 | 106 | 35.33 | 15.28 | MRI | infants from birth to 6 years of age, across many imaging sites, prot… | measuring cortical development in infants, whose… | open-source | Nature protocols | [doi](https://doi.org/10.1038/s41596-023-00806-x) |
| BR-Net | 2020 | 97 | 16.17 | 5.03 | MRI; x-ray / radiography | adolescents in the NCANDA alcohol and neurodevelopment cohort, childr… | stopping a model from learning a confounder inste… | open-source | Nature communications | [doi](https://doi.org/10.1038/s41467-020-19784-9) |
| Functional Random Forest | 2018 | 91 | 11.38 | 4.52 | MRI | 47 children with autism and 58 typically developing children aged 9-13 | whether autism spectrum disorder contains distinc… | unclear | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2017.12.044) |
| FUIQA | 2017 | 91 | 10.11 | 5.08 | ultrasound | fetuses undergoing obstetric ultrasound examination | automatic quality control of obstetric ultrasound… | unclear | IEEE transactions on cybernetics | [doi](https://doi.org/10.1109/TCYB.2017.2671898) |
| Auto-Net | 2017 | 90 | 10.0 | 4.82 | MRI | public adult benchmark datasets plus reconstructed fetal brain MRI | extracting the brain from surrounding tissue on M… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2017.2721362) |
| time-dependent deep image prior | 2021 | 86 | 17.2 | 8.17 | MRI | fetuses in retrospective and real fetal cardiac MRI datasets | reconstructing a moving fetal heart from sparsely… | unclear | IEEE transactions on medical im… | [doi](https://doi.org/10.1109/TMI.2021.3084288) |
| DPA-HNN | 2019 | 86 | 12.29 | 5.4 | CT | adult and pediatric patients whose thoracic CT reports were collected… | extracting whether a CT report says there is a pu… | unclear | Artificial intelligence in medi… | [doi](https://doi.org/10.1016/j.artmed.2018.11.004) |
| DeepUTE | 2018 | 81 | 11.57 | 4.88 | nuclear / PET; MRI | 79 pediatric brain tumor examinations, 36 with active tumor volume ab… | quantitatively accurate FET-PET/MRI in children w… | unclear | Frontiers in neuroscience | [doi](https://doi.org/10.3389/fnins.2018.01005) |
| DeepFMRI | 2020 | 72 | 12.0 | 4.89 | MRI | children in the public ADHD-200 dataset, contributed by several imagi… | diagnosing ADHD, which currently rests entirely o… | unclear | Journal of neuroscience methods | [doi](https://doi.org/10.1016/j.jneumeth.2019.108506) |
| Rayvolve | 2022 | 71 | 17.75 | 8.64 | x-ray / radiography | 2,549 children aged 0-17 (mean 8.5 years) referred from a pediatric e… | detecting fractures on radiographs of children pr… | commercial | Diagnostic and interventional i… | [doi](https://doi.org/10.1016/j.diii.2021.10.007) |
| DeepWMA | 2020 | 71 | 11.83 | 5.11 | MRI | 597 diffusion MRI scans from six independently acquired populations s… | identifying named white matter tracts consistentl… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2020.101761) |
| MF R-CNN | 2019 | 63 | 9.0 | 4.43 | ultrasound | fetuses undergoing prenatal ultrasound | deciding whether a fetal head ultrasound image is… | unclear | Medical image analysis | [doi](https://doi.org/10.1016/j.media.2019.101548) |
| ARVBNet | 2020 | 60 | 10.0 | 3.89 | ultrasound | fetuses undergoing cardiac screening ultrasound | deciding whether a fetal cardiac four-chamber vie… | unclear | IEEE journal of biomedical and… | [doi](https://doi.org/10.1109/JBHI.2019.2948316) |
| quantusFLM | 2015 | 60 | 5.45 | 2.89 | ultrasound | 144 neonates delivered between 28 and 39 weeks, imaged within 48 hour… | predicting neonatal respiratory morbidity before… | commercial | Ultrasound in obstetrics & gyne… | [doi](https://doi.org/10.1002/uog.13441) |
| BoneView | 2022 | 55 | 13.75 | 7.05 | x-ray / radiography | 300 radiographic examinations from patients aged 2-21 (167 boys, 133… | detecting acute appendicular fractures in children | commercial | Skeletal radiology | [doi](https://doi.org/10.1007/s00256-022-04070-0) |
| deepee | 2021 | 53 | 10.6 | 3.46 | x-ray / radiography | children in the public pediatric pneumonia chest radiograph dataset,… | training diagnostic models on children's images w… | open-source | Scientific reports | [doi](https://doi.org/10.1038/s41598-021-93030-0) |
| CHN-PD | 2019 | 53 | 7.57 | 2.66 | MRI | 328 cognitively normal Chinese children aged 6-12, with two independe… | whether a pediatric brain atlas built on one popu… | open-source | NeuroImage | [doi](https://doi.org/10.1016/j.neuroimage.2019.01.006) |
| Appendicitis Prediction Tool | 2021 | 52 | 10.4 | 5.4 | ultrasound | 430 children and adolescents aged 0-18 with suspected appendicitis | three separate decisions in suspected pediatric a… | open-source | Frontiers in pediatrics | [doi](https://doi.org/10.3389/fped.2021.662183) |
| AutoRAPNO | 2022 | 49 | 12.25 | 4.44 | MRI | 794 children with preoperative MRI and 122 with serial postoperative… | measuring tumor burden reproducibly across serial… | unclear | Neuro-oncology | [doi](https://doi.org/10.1093/neuonc/noab151) |
| DAG V-Net | 2021 | 49 | 9.8 | 4.78 | ultrasound | fetuses across trimesters in the public HC18 challenge dataset (355 t… | measuring head circumference from a fetal ultraso… | open-source | Journal of digital imaging | [doi](https://doi.org/10.1007/s10278-020-00410-5) |
| DW-Net | 2020 | 47 | 7.83 | 3.94 | ultrasound | 895 apical four-chamber views from fetal echocardiography | outlining the seven key structures of the apical… | unclear | Computerized medical imaging an… | [doi](https://doi.org/10.1016/j.compmedimag.2019.101690) |
| Cropping-Segmentation-Calibration (CSC) | 2020 | 47 | 7.83 | 2.54 | ultrasound | 615 annotated frames from 421 normal fetal cardiac ultrasound videos… | delineating the ventricular septum during fetal c… | unclear | Biomolecules | [doi](https://doi.org/10.3390/biom10111526) |
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
| Deeplasia | 2024 | 25 | 12.5 | 6.53 | x-ray / radiography | the public RSNA challenge set for training, plus 568 radiographs from… | bone age in children with skeletal dysplasia, whe… | open-source | Pediatric radiology | [doi](https://doi.org/10.1007/s00247-023-05789-1) |
| childfx | 2024 | 24 | 12.0 | 8.19 | x-ray / radiography | 240 patients (mean age 11.3 years, range 0-22, 37.9% female) with elb… | upper extremity fractures missed by residents and… | open-source | Skeletal radiology | [doi](https://doi.org/10.1007/s00256-024-04698-0) |
| BIBSNet | 2025 | 19 | 19.0 | 6.83 | MRI | 90 participants aged 0-8 months (median 4.6 months) | segmenting the infant brain in the first months o… | open-source | bioRxiv : the preprint server f… | [doi](https://doi.org/10.1101/2023.03.22.533696) |
| ChatGPT-4 | 2024 | 19 | 9.5 | 5.68 | ultrasound | 103 randomly selected anonymized ultrasound and operative records fro… | turning free-text ultrasound and operative report… | commercial | Journal of pediatric surgery | [doi](https://doi.org/10.1016/j.jpedsurg.2024.01.033) |
| BoneXpert, PANDA, BoneView | 2025 | 13 | 13.0 | 5.28 | x-ray / radiography | 306 children aged 1-18, stratified by sex and age, at a Central Europ… | which of the bone age products approved for the E… | commercial | European radiology | [doi](https://doi.org/10.1007/s00330-024-11169-6) |
| TotalSegmentator | 2025 | 12 | 12.0 | 3.65 | CT | 300 adult and 359 pediatric abdominal CT scans from external datasets | whether the field's default open organ segmentati… | open-source | Journal of imaging informatics… | [doi](https://doi.org/10.1007/s10278-024-01273-w) |
| BoneMetrics | 2025 | 11 | 11.0 | 4.35 | x-ray / radiography | 345 patients (mean age 33, range over 2 years), of whom 179 were unde… | measuring Cobb angles on full spine radiographs,… | commercial | Skeletal radiology | [doi](https://doi.org/10.1007/s00256-024-04853-7) |
| BoneView, RBfracture | 2025 | 11 | 11.0 | 4.69 | x-ray / radiography | 998 emergency musculoskeletal radiographs (585 normal, 413 abnormal)… | choosing between competing commercial fracture de… | commercial | Emergency radiology | [doi](https://doi.org/10.1007/s10140-025-02353-2) |
| TrueLung | 2025 | 10 | 10.0 | 3.61 | MRI | 75 children with cystic fibrosis imaged at 1.5 T | measuring regional ventilation and perfusion in c… | unclear | Zeitschrift fur medizinische Ph… | [doi](https://doi.org/10.1016/j.zemedi.2024.08.001) |
| LAS-Net | 2025 | 10 | 10.0 | 3.44 | nuclear / PET; CT | 297 children in two Children's Oncology Group trials (median age 15.4… | deciding from the interim PET whether a child's H… | unclear | Radiology. Artificial intellige… | [doi](https://doi.org/10.1148/ryai.240229) |
| ChatGPT-o4-mini-high, ChatGPT-4.5, Gemini 2.5 Pro | 2025 | 10 | 10.0 | 3.93 | x-ray / radiography | 180 left-hand wrist radiographs of children aged 0-18 from the RSNA P… | whether a general-purpose chatbot can substitute… | commercial | Academic radiology | [doi](https://doi.org/10.1016/j.acra.2025.07.058) |
| MONAIfbs | 2021 | — | — | — | MRI | fetuses with suspected pathology, particularly spina bifida | brain masking for super-resolution reconstruction… | open-source | arXiv (preprint) | [doi](https://doi.org/10.48550/arxiv.2103.13314) |

## Most-cited-per-year work from 2024 onward (40)

Ranked by citations per year rather than raw count, because a paper from this year has had no time to accumulate one. `RCR` is iCite's relative citation ratio (1.0 is the median NIH-funded paper of the same field and year) and falls back to OpenAlex's field-weighted citation impact where iCite has not computed it, which is most of the last two years.

| Title | Year | Cites | /yr | RCR/FWCI | Type | Clinical problem | Link |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| Multimodal deep learning improves recurrence risk prediction in… | 2025 | 26 | 26.0 | 7.84 | journal | predicting which children will recur after su… | [doi](https://doi.org/10.1093/neuonc/noae173) |
| Lack of children in public medical imaging data points to growi… | 2025 | 22 | 22.0 | 8.08 | preprint | whether children are represented at all in th… | [doi](https://doi.org/10.1101/2025.06.06.25328913) |
| Predicting pediatric patient rehabilitation outcomes after spin… | 2025 | 21 | 21.0 | 7.96 | journal | telling an adolescent before scoliosis surger… | [doi](https://doi.org/10.1038/s43856-024-00726-1) |
| BIBSNet | 2025 | 19 | 19.0 | 6.83 | preprint | segmenting the infant brain in the first mont… | [doi](https://doi.org/10.1101/2023.03.22.533696) |
| Multiparametric MRI along with machine learning predicts progno… | 2025 | 18 | 18.0 | 4.63 | journal | identifying which children with low-grade gli… | [doi](https://doi.org/10.1038/s41467-024-55659-z) |
| Assessment of glymphatic function and white matter integrity in… | 2025 | 17 | 17.0 | 5.78 | journal | detecting autism spectrum disorder on imaging… | [doi](https://doi.org/10.1007/s00330-025-11359-w) |
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
| AI-Assisted X-ray Fracture Detection in Residency Training: Eva… | 2024 | 24 | 12.0 | 7.5 | journal | whether AI assistance helps radiology residen… | [doi](https://doi.org/10.3390/diagnostics14060596) |
| childfx | 2024 | 24 | 12.0 | 8.19 | journal | upper extremity fractures missed by residents… | [doi](https://doi.org/10.1007/s00256-024-04698-0) |
| TotalSegmentator | 2025 | 12 | 12.0 | 3.65 | journal | whether the field's default open organ segmen… | [doi](https://doi.org/10.1007/s10278-024-01273-w) |
| Artificial intelligence (AI) in radiological paediatric fractur… | 2025 | 12 | 12.0 | 4.81 | journal | detecting bone injury in children, now that b… | [doi](https://doi.org/10.1007/s00330-025-11449-9) |
| Advances in Artificial Intelligence and Machine Learning for Pr… | 2025 | 12 | 12.0 | 4.67 | journal | predicting and diagnosing necrotizing enteroc… | [doi](https://doi.org/10.3390/children12040498) |
| MRI-based synthetic CT for assessment of the bony elements of t… | 2024 | 22 | 11.0 | 6.69 | journal | assessing the bony sacroiliac joints in child… | [doi](https://doi.org/10.1186/s13244-023-01603-6) |
| Towards consistency in pediatric brain tumor measurements: Chal… | 2024 | 22 | 11.0 | 3.46 | journal | why two readers measuring the same pediatric… | [doi](https://doi.org/10.1093/neuonc/noae093) |
| Radiomics and artificial intelligence applications in pediatric… | 2024 | 22 | 11.0 | 4.19 | journal | characterizing, grading and prognosticating c… | [doi](https://doi.org/10.1007/s12519-024-00823-0) |
| Out-of-Distribution Detection and Radiological Data Monitoring… | 2025 | 11 | 11.0 | 3.49 | journal | knowing when a deployed model is being shown… | [doi](https://doi.org/10.1007/s10278-024-01212-9) |
| BoneMetrics | 2025 | 11 | 11.0 | 4.35 | journal | measuring Cobb angles on full spine radiograp… | [doi](https://doi.org/10.1007/s00256-024-04853-7) |
| Clinical validation of explainable AI for fetal growth scans th… | 2025 | 11 | 11.0 | 3.82 | journal | giving the sonographer usable feedback during… | [doi](https://doi.org/10.1038/s41598-025-86536-4) |
| Review of the Current State of Artificial Intelligence in Pedia… | 2025 | 11 | 11.0 | 3.96 | journal | cardiac MRI in congenital heart disease is sl… | [doi](https://doi.org/10.3390/children12040416) |
| BoneView, RBfracture | 2025 | 11 | 11.0 | 4.69 | journal | choosing between competing commercial fractur… | [doi](https://doi.org/10.1007/s10140-025-02353-2) |

The full table, including the model description, dataset size, validation and headline result for every paper, is `data/processed/pedrad_paper_db.csv`.
