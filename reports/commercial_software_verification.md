# Commercial software slide: verification and sources

Checked 2026-09-16 against manufacturer pages and FDA summaries; the scanner-maker rows were split per vendor and their links re-checked 2026-09-17. This review covers all 19 companies in the slide's rows; GE HealthCare, Canon, Siemens and Philips are listed one per row rather than as a combined scanner-maker row. The slide describes selected products, rather than each company's entire portfolio. Product functions outside the US are distinguished from FDA indications.

## What the FDA column means

**Company-wide FDA AI entries (n; years)** counts radiology-panel entries associated with the named companies in `data/processed/fda_ai_devices.json`, saved 2026-09-17. Parentheses give the earliest and latest decision years. Grouped companies are summed. Entries include different versions, submissions and unrelated products; they are not counts of unique algorithms, the selected products, pediatric indications, installations or clinical adoption. The [FDA describes its AI-enabled device list as noncomprehensive](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices).

Every row below is a **group total**: where a row names several companies, the
number is their sum, not any one company's count. Per-company figures are given
underneath.

| Company/group | Entries in saved snapshot | Decision-year range |
|---|---:|---|
| Gleamer | 4 | 2022–2025 |
| AZmed | 5 | 2022–2026 |
| Visiana | None listed | — |
| 16 Bit | 1 | 2024 |
| Ever Fortune.AI | 12 | 2022–2026 |
| BrightHeart | 5 | 2024–2025 |
| GE HealthCare | 109 | 2014–2026 |
| Siemens Healthineers | 96 | 2014–2026 |
| Philips | 48 | 2018–2026 |
| Canon Medical | 46 | 2019–2026 |
| Subtle Medical + AIRS Medical (two companies combined) | 15 | 2018–2026 |
| Qure.ai | 9 | 2020–2026 |
| Aidoc + Viz.ai (two companies combined) | 46 | 2018–2026 |

The four scanner makers were a single combined row until 2026-09-17; they are now one row each, so the
numbers above are per company and no longer a group total. The original 307 scanner-company count was inflated by a substring search for `GE`, which also matched unrelated names such as Imagen, Change, Merge and Visage. Word-boundary matching plus the General Electric alias gives 109 GE + 46 Canon + **96 Siemens** + 48 Philips = **299** in the 2026-09-17 snapshot (107 + 43 + 90 + 44 = 284 in the 2026-09-03 one), consistent with the snapshot's normalized company totals. Subtle/AIRS is 10 + 5; Aidoc/Viz is 35 + 11.

The snapshot is not a current census of every authorization. For example, [AZmed announced its sixth FDA clearance on September 15, 2026](https://www.azmed.co/news-post/azmed-receives-its-6th-fda-clearance-taking-rayvolve-to-eight-fda-cleared-findings-across-msk), whereas the saved list contains five AZmed entries (the most recent, K260378, decided 05/12/2026). Keep the snapshot date visible; replacing only AZmed's number with a vendor-reported total would mix counting methods. The new AZchest clearance is independently recorded as [K261378, August 28, 2026](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K261378).

## Product corrections

### 1. Gleamer — BoneView

The US product assists fracture detection. Broader international functions include dislocations, effusions and focal bone lesions; these should not all be described as FDA-cleared pediatric functions. The [manufacturer's product page](https://www.gleamer.ai/us/copilot/boneview) and [manufacturer-hosted study](https://www.gleamer.ai/us/clinical-studies/assessment-of-performances-of-a-deep-learning-algorithm-for-the-detection-of-limbs-and-pelvic-fractures-dislocations-focal-bone-lesions-and-elbow-effusions-on-trauma-x-rays) describe these capabilities.

The age restriction also needs anatomy: [K222176, BoneView 1.1-US](https://www.accessdata.fda.gov/cdrh_docs/pdf22/K222176.pdf), pages 5–7, permits ages 2–21 for specified extremity views, including clavicle. Pelvis, hip, femur, ribs, thoracic spine and lumbosacral spine are adult-only in that summary. “Age 2+” alone overstates the pediatric anatomical scope.

### 2. AZmed — Rayvolve suite

Rayvolve encompasses **AZtrauma**, **AZchest**, **AZmeasure** and **AZboneage**. Functions include musculoskeletal finding detection, chest finding detection/triage, orthopedic measurements and bone-age estimation. [AZtrauma](https://www.azmed.co/azproducts-pages/aztrauma) lists fractures, joint effusions, dislocations, tumoral and degenerative lesions, and osteoarthritis. [AZchest](https://www.azmed.co/azproducts-pages/azchest) describes broader chest findings; international and US feature sets differ. [AZmed's suite overview](https://www.azmed.co/) distinguishes FDA/CE modules from CE-only offerings.

[K240845](https://www.accessdata.fda.gov/cdrh_docs/pdf24/K240845.pdf) supports the 2024 pediatric fracture indication starting at age two. [AZboneage](https://www.azmed.co/azproducts-pages/azboneage) uses Greulich–Pyle assessment and is presented as CE-marked. The September 2026 announcement lists five US chest findings and describes the May 2026 expansion to effusion/dislocation detection; it does not make every Rayvolve function a pediatric FDA indication.

### 3. Visiana — BoneXpert

Expand beyond bone age: the software provides GP/TW3 assessment and a **Bone Health Index**; an associated tool predicts adult height. The [current manufacturer homepage](https://bonexpert.com/) explicitly labels US availability as research use only and other markets as CE-marked. The [clinical manual](https://www.bonexpert.com/docs/BoneXpertClinicalManual3_rev1.pdf) explains bone-age and cortical-bone measurements, and the [adult-height predictor manual](https://bonexpert.com/files/BoneXpert_AdultHeightPredictor_v3-005.pdf) documents prediction outputs. An absence from the FDA AI list alone would not establish US regulatory status; the vendor statement supplies that distinction.

### 4. 16 Bit — replace Rho with Physis

**Rho is not a bone-age product.** It screens existing radiographs for possible low bone mineral density in patients aged 50 or older, prompting assessment of bone health. See the [US Rho FAQ and intended use](https://www.16bit.ai/rho/faq/us).

**Physis** is the company's pediatric bone-age tool: AI estimation, GP atlas matching and report assistance. See [Physis](https://www.16bit.ai/physis). The [company homepage](https://www.16bit.ai/) calls it a research tool; its dedicated page also displays a Health Canada licensing statement. Neither statement establishes FDA authorization. No Physis FDA authorization was identified in this review. The company's one saved FDA entry is **Rho, DEN230023**, not Physis, and the slide now explicitly says so.

### 5. Ever Fortune.AI — EFAI Bonesuite XR Bone Age Pro

Specify the actual input and output: GP bone-age quantification from a **PA left-hand radiograph**, with the hand and wrist visible. [K234042](https://www.accessdata.fda.gov/cdrh_docs/pdf23/K234042.pdf), cleared June 7, 2024, specifies patients aged **2–16** and use as an adjunct for pediatric radiologists. See also the [vendor's radiology product directory](https://www.everfortuneai.com.tw/en/category/medical-ai-soultion/radiology/) and [bone-age product page](https://medical.everfortuneai.com.tw/products/efai-bap). The eleven-company-entry total does not mean eleven bone-age authorizations.

### 6. BrightHeart — Fetal EchoScan and View Classifier

The original row conflated two devices. **Fetal EchoScan** flags eight morphological findings suspicious for congenital heart defects. **BrightHeart View Classifier** identifies standard views, extracts representative frames and checks documentation against an acquisition protocol. The [vendor website](https://www.brightheart.ai/) uses B-Right Screen/B-Right Views branding; the slide uses the FDA device names for traceability.

[Fetal EchoScan v1.2, K252294](https://www.accessdata.fda.gov/cdrh_docs/pdf25/K252294.pdf) is for second-trimester exams in pregnant women aged 18+, with specified cardiac views; it excludes postnatal exams, multiple pregnancies and fetal heterotaxy. [View Classifier, K251456](https://www.accessdata.fda.gov/cdrh_docs/pdf25/K251456.pdf) covers second-/third-trimester transabdominal fetal ultrasound, with maternal age 18+ in the summary. These are prenatal applications, not general postnatal pediatric echocardiography.

### 7. GE HealthCare, Canon, Siemens and Philips — reconstruction

These four are one row each on the slide, with their own FDA counts, because the group total (299) said
nothing about any one vendor and the pediatric-label column differs sharply between them: Philips 28 (1
software), GE 19 (2), Siemens 10 (3), Canon 3 (0). The products also differ by modality rather than all
four doing both CT and MRI:

- **GE TrueFidelity:** CT deep-learning reconstruction for noise/image-quality optimization. The [GE product page](https://www.gehealthcare.com/static/truefidelity/) describes the reconstruction function; its [clinical evidence white paper](https://www.gehealthcare.com/-/jssmedia/gehc/us/files/products/computed-tomography/apex-platform/truefidelity-evidence-white-paper-v-released-jb22322xx.pdf?rev=-1) discusses applications across ages.
- **Canon AiCE:** CT **and** MRI reconstruction. See Canon's [CT technical paper](https://global.medical.canon/publications/ct/2019wp-aice-deep-learning/), [MRI product page](https://global.medical.canon/products/magnetic-resonance-imaging/aice/) and [pediatric CT examples](https://us.medical.canon/products/computed-tomography/aquilion-one-prism/clinical-gallery/pediatric/).
- **Siemens Deep Resolve:** MRI reconstruction, denoising and resolution enhancement supporting accelerated acquisition. Siemens publishes [pediatric protocols using Deep Resolve](https://www.magnetomworld.siemens-healthineers.com/clinical-corner/protocols/pediatric-mri-protocols/deep-resolve-pediatric).
- **GE AIR Recon DL:** MRI deep-learning reconstruction supporting shorter acquisitions at comparable image quality; see the [GE product page](https://www.gehealthcare.com/products/magnetic-resonance-imaging/air-recon-dl).
- **Philips SmartSpeed:** MRI acceleration with deep-learning reconstruction; see the [Philips product page](https://www.philips.com/healthcare/resources/landing/smartspeed).
- **Philips Precise Image:** CT reconstruction; potential dose reduction depends on clinical task, size and anatomy. See the [US technical white paper](https://www.philips.com/c-dam/b2bhc/master/resource-catalog/landing/precise-suite/usa-documents/ct-5100-incisive-precise-image-wp-nam.pdf) and [Philips pediatric imaging discussion](https://www.philips.com/a-w/about/news/archive/standard/news/articles/2024/enabling-first-time-right-imaging-for-every-child-q-and-a-with-atul-gupta-md).

Remove the blanket “adult-cleared” statement. Pediatric applications are documented, while permitted use still depends on each scanner/software configuration. MRI scan time and CT radiation dose are different benefits, and neither is a fixed reduction guaranteed by the software name.

### 8. Subtle Medical and AIRS Medical — SubtleMR / SwiftMR

Describe **image post-processing**, with denoising and sharpening supporting shorter acquisitions or improved image quality. [Subtle Medical's description](https://subtlemedical.com/subtle-medical-launches-subtlemr-2-0-to-expand-improved-mri-capabilities/) and [SubtleMR K223623](https://www.accessdata.fda.gov/cdrh_docs/pdf22/K223623.pdf) specify noise reduction across listed body regions and increased sharpness for head MRI. The reviewed indications do not state an adult-only restriction.

[SwiftMR's product page](https://airsmed.com/swiftmr/) describes processing after acquisition. [K253775](https://www.accessdata.fda.gov/cdrh_docs/pdf25/K253775.pdf) covers all-body MR image enhancement and processing, and also describes MIP/minIP/MPR tools. Its validation includes ages **0–21 (8.9%)**. Inclusion in validation is not a claim that every pediatric protocol has independently established performance. The old shared “adult-cleared” label was unsupported by these indications.

### 9. Qure.ai — qXR / qER families

Expand chest tasks to detection/triage, TB screening, breathing-tube assessment and cardiothoracic-ratio measurement. Expand head imaging to triage, quantification and CTA LVO alerts. The [qXR overview](https://www.qure.ai/us/product/qxr) describes international breadth; [Qure's regulatory page](https://www.qure.ai/us/regulatory-and-privacy) distinguishes US modules. qER-Quant measures intracranial hyperdensities, ventricles and midline shift. [qER-CTA K251610](https://www.accessdata.fda.gov/cdrh_docs/pdf25/K251610.pdf) specifies ICA/M1 LVO notification for adults aged 22+.

“Pediatric TB-screening evidence only” is outdated: [Qure's October 17, 2025 announcement](https://www.qure.ai/us/news-press-coverages/ai-tool-regulatory-cleared-for-early-detection-of-tb-in-children-aged-0-3-years-promising-faster-diagnosis) reports CE Class IIb coverage extending to ages 0–3, completing coverage across childhood to age 15. This is a vendor-reported CE status, not a US pediatric FDA indication.

### 10. Aidoc and Viz.ai — BriefCase / Viz LVO / Viz ICH

[Aidoc's solutions page](https://www.aidoc.com/solutions/) includes ICH, LVO, PE, pneumothorax, fractures and intra-abdominal free gas among its imaging applications. Individual BriefCase modules have distinct indications; a single company-level adult-only claim is too broad. The slide lists examples, not every Aidoc product or partner algorithm.

[Viz's indications for use](https://www.viz.ai/indications-for-use) identify **Viz LVO** as CTA-based LVO notification and **Viz ICH** as noncontrast-head-CT hemorrhage notification. These products support specialist communication and care coordination; they do not autonomously establish a diagnosis. The original grouped row could misleadingly suggest that Viz LVO/ICH themselves detect PE or pneumothorax. The revision attributes tasks to the appropriate company/product and removes the unsupported deployment superlative.

---

# 2026-09-17 addition: the pediatric-label column, the six new companies, and the product table

The commercial section of the deck grew from one slide to five: a line chart of
products held per company, a bar chart of clinical problems addressed, the
company table, and two product tables. This section records what supports the
new claims and what does not.

## The new column: "Of those, pediatric population stated (software)"

Source: `data/processed/fda_pediatric_inventory.json`, built by
`scripts/build_fda_pediatric_inventory.py` from the decision-summary PDFs of
every Radiology-panel record in the 2026-09-16 FDA AI-device CSV. A record is a
**label-positive candidate** when its extracted intended-use text contains a
direct pediatric or fetal patient-population statement; phantom studies,
validation-only mentions and explicit exclusions are held back as
`needs-label-review` and are **not** counted in this column. 230 of 1,230
records are label-positive candidates.

Three things this number is not:

1. **Not a pediatric indication.** The screen reads the summary, not the label
   as a regulator would. A statement that children are in the intended
   population is a candidate for review, which is why the source file calls it
   one.
2. **Not pediatric evidence.** Aidoc holds 23 of the 110 pediatric-labeled
   software entries; the performance data behind them is adult.
3. **Not comparable across device kinds.** 120 of the 230 are whole imaging
   systems (`config.COMMERCIAL_SYSTEM_CODES`: ultrasound, CT, MR and
   fluoroscopy system codes), where "Pediatric" is one row of the standard
   clinical-application table every scanner label carries. That is why the
   column reports standalone software separately in parentheses, and why the
   line chart's dashed series is software only. Philips is the clearest case:
   28 pediatric-labeled entries, one of them software.

## Clinical problems (`config.COMMERCIAL_PROBLEM_TERMS` / `_CODES`)

The FDA list has no clinical-problem field. Each device is assigned one from its
**name** first and its **FDA product code** second (`pedrad_ai/commercial.py`).
Names win because the codes are mostly generic — QIH, "Automated Radiological
Image Processing Software", covers 305 of 1,230 records, and the scanner
codes 411 between them. 542 devices name a problem this way; the remaining 688 are counted
and reported as unassigned rather than guessed at.

Product-code names were taken from the openFDA device classification endpoint
(`api.fda.gov/device/classification.json`), so the codes mapped to a problem —
QBS fracture, QAS/QFM triage and prioritization, QDQ/POK cancer lesions, OEB/QWO
lung, OTE/SEZ breast, SAO/KGI bone density, SHE delivery date, QHA coronary, PCS
liver iron, MUJ/QKB/QTZ radiation therapy — carry FDA's own wording, not ours.
The keyword rules are heuristic and are ordered so that a specific clinical
problem beats the cross-cutting categories (image quality, measurement, triage)
that almost any product could also be filed under. Multi-finding products are
filed under the first match, so a multi-triage CT submission that lists a
fracture among its findings lands in fracture / trauma.

## The six companies added to `config.COMMERCIAL_PEDIATRIC`

Each was added because its FDA entries carry pediatric or fetal population
statements, and each row's regulatory claim is supported by the submissions
named below in the saved snapshot. Functions are described from the device names
and decision summaries in the snapshot; they have not been re-checked against
vendor marketing pages the way rows 1–10 above were.

| Vendor | Entries | Pediatric-label entries | Submissions behind the pediatric claim |
|:--|---:|---:|:--|
| Hyperfine | 13 | 9 | Swoop Portable MR (K221393, K221923, K230208, K232760, K240944, K250236, K251276, K253489) and BrainInsight (K223268) |
| EOS imaging (Alphatec) | 4 | 4 | VEA Align (K231917), VEA Align; spineEOS (K240582, K251747), AutoDensity (K251078) |
| Sonio | 5 | 5 | Sonio Detect (K230365, K240406, K252433), Sonio Suspect (K243614, K261519) |
| Smart Soft Healthcare | 4 | 4 | CoLumbo (K220497, K241211), CoLumboX (K250367), CoLumbo C-Spine (K254015) |
| Milvue | 2 | 2 | SmartChest (K232410), TechCare Trauma (K242171) |
| Butterfly Network / Clarius | 16 | 12 | Butterfly iQ/iQ+ and Clarius scanner and tool entries; the pediatric statements are mostly scanner labeling (2 of 12 are software) |

Hyperfine's and Butterfly/Clarius's counts are dominated by scanner entries
(LNH and IYN codes), so their pediatric numbers should be read with the
scanner caveat above. EOS, Sonio, Smart Soft and Milvue are software-only.

## The product table (`config.COMMERCIAL_PRODUCTS`)

23 products, one row each. Three columns carry different evidentiary weight:

- **Pediatric scope with a bracketed submission** — the claim is checked against
  the saved FDA list: `tests/test_commercial.py` fails if a cited submission is
  not in `data/processed/fda_ai_devices.json`. The *content* of the claim comes
  from the decision summary text archived under
  `data/raw/fda_pediatric_inventory/2026-09-16/`.
- **Pediatric scope without a submission** — no US authorization was identified.
  BoneXpert (CE-marked, US research use only), Physis (Health Canada), qXR-TB
  (vendor-reported CE Class IIb, ages 0–15) and the four scanner-maker
  reconstruction products carry claims verified in sections 3, 4, 7, 8 and 9
  above; they are repeated here, not independently re-verified.
- **"Where it stands"** — an editorial judgment about deployment, not a measured
  adoption rate. Nothing in the repository measures installations, and the
  slide footnote says so. Read "widely deployed" as "you will meet it in
  practice", not as a market-share claim.

Two rows are deliberate outliers. **Arterys Cardio DL (K163253, 2017)** is in the
table because it is one of the earliest AI clearances whose intended use names
neonates, infants, children and adolescents outright, which makes it a useful
reference point for how rare that still is. **Second Opinion Pediatric
(K243893)** is dental, not diagnostic radiology, but it sits on the Radiology
panel and is one of the very few cleared devices whose name and indication are
pediatric from the start.
