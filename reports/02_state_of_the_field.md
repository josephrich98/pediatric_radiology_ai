# Radiology AI: What It Does Well, the Bleeding Edge, and the Unresolved

_A synthesis for clinical leadership. The quantitative companions are
`00_popularity_trends.md` (how fast the field is growing and how much is
pediatric) and `01_landscape_players.md` (the most-cited papers and most-used
open-source tools). References are collected in `references.bib`._

## One-paragraph orientation

The "radiologists will be obsolete" claim is roughly a decade old (Geoffrey
Hinton's 2016 remark is the usual marker) and has not borne out. What did happen
is a steady, large expansion of *narrow, task-specific* tools: detection,
triage, segmentation, and measurement aids that sit inside the existing
workflow. Adult, high-volume, single-modality problems (chest radiograph
findings, screening mammography, stroke and pulmonary-embolism triage on CT) are
where the technology is most mature. Pediatric radiology is a small fraction of
the literature and an even smaller fraction of cleared products, for reasons
that are structural rather than temporary: less data, more anatomical variation
with age, and higher regulatory caution.

## What radiology AI already does well

- **Worklist triage / prioritization.** Flagging likely-positive studies
  (intracranial hemorrhage, large-vessel occlusion, pulmonary embolism,
  pneumothorax) so they are read first. This is the most clinically validated
  and most widely deployed category, because it improves time-to-treatment
  without removing the radiologist from the decision.
- **Detection and measurement aids on high-volume adult exams.** Lung-nodule
  detection on chest CT, breast-density and lesion flagging on mammography, bone
  measurements, and organ/lesion volumetry. These reduce missed findings and
  manual measurement time.
- **Image quality and acquisition.** Deep-learning reconstruction and denoising
  now ship on commercial CT and MRI scanners, enabling lower radiation dose and
  shorter scan times. For pediatrics this is arguably the *most valuable* mature
  application, because dose reduction and shorter (often sedation-free) scans
  matter more in children.
- **Quantification and standardization.** Automated segmentation for radiation
  planning, longitudinal tumor measurement, and reproducible volumetrics, where
  consistency beats human inter-reader variability.

## The bleeding edge

- **Foundation models and vision-language models for imaging.** Large
  pretrained models adapted to radiology, and report-generation / draft-report
  systems built on large language models. Promising for efficiency, but
  hallucination and verifiability are unresolved (see below).
- **Opportunistic and population screening.** Extracting incidental but
  prognostic signals (bone density, coronary calcium, body composition,
  "biological age") from scans acquired for other reasons.
- **Multimodal and longitudinal models.** Combining imaging with the electronic
  health record, genomics, and prior studies rather than reading a single image
  in isolation.
- **Self-supervised and label-efficient learning.** Reducing the dependence on
  large expert-annotated datasets — the single biggest practical bottleneck, and
  especially acute in pediatrics.
- **Pediatric-specific frontiers.** Automated bone-age assessment is the one
  pediatric task with a mature, benchmarked literature (the RSNA Pediatric Bone
  Age Challenge). Active frontiers include fetal and neonatal brain MRI
  segmentation, congenital anomaly detection, scoliosis/Cobb-angle measurement,
  and growth-aware models that account for changing anatomy across ages.

## What remains unresolved

- **Generalization and dataset shift.** Models trained at one site routinely
  degrade at another (different scanners, protocols, populations). External
  validation remains the exception, not the rule.
- **Pediatric data scarcity and age dependence.** Children are not small adults:
  anatomy, normal ranges, and disease spectra change with age, so adult models
  transfer poorly and pediatric datasets are small and fragmented across rare
  conditions. This is the core reason pediatric AI lags.
- **Prospective clinical benefit.** Most evidence is retrospective accuracy on
  curated test sets. Randomized or prospective evidence that AI improves patient
  *outcomes* (not just reader metrics) is thin.
- **Report generation trust.** LLM-generated reports can be fluent and wrong;
  there is no robust, deployed mechanism to guarantee a generated report is
  faithful to the image.
- **Regulatory and liability fit for pediatrics.** Most cleared radiology-AI
  devices are validated on adults; pediatric labeling is rare, leaving
  children's hospitals to validate tools locally before use.
- **Workflow integration, monitoring, and drift.** Even accurate models fail in
  practice without PACS/reporting integration, alerting that fits the read, and
  ongoing performance monitoring as scanners and populations change.
- **Equity and bias.** Performance can vary by sex, body habitus, scanner, and
  for children by developmental stage; systematic subgroup evaluation is
  uncommon.

## Implications for a children's hospital

1. **Buy maturity, build for the gaps.** Adopt mature, FDA-cleared adult-derived
   tools where they transfer (triage, reconstruction/dose reduction), and treat
   pediatric-specific tasks (bone age, fetal/neonatal MRI, congenital anomalies)
   as local validation or research collaborations.
2. **Demand local validation.** Because most tools are validated on adults,
   require evidence on a pediatric population — ideally your own — before
   clinical use.
3. **Prioritize dose and throughput.** Deep-learning reconstruction and
   scan-time reduction deliver the clearest pediatric benefit today.
4. **Plan for monitoring.** Any deployed model needs ongoing performance
   tracking; pediatric drift (growth, protocol changes) is faster than in adults.

_See `references.bib` for landmark papers; all DOIs were resolved through
doi2bib per project convention._
