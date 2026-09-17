# Commercial software slide: verification and sources

Checked 2026-09-16 against manufacturer pages and FDA summaries. This review covers all 16 companies in the slide's ten rows. The slide describes selected products, rather than each company's entire portfolio. Product functions outside the US are distinguished from FDA indications.

## What the FDA column means

**Company-wide FDA AI entries (n; years)** counts radiology-panel entries associated with the named companies in `data/processed/fda_ai_devices.json`, saved 2026-09-03. Parentheses give the earliest and latest decision years. Grouped companies are summed. Entries include different versions, submissions and unrelated products; they are not counts of unique algorithms, the selected products, pediatric indications, installations or clinical adoption. The [FDA describes its AI-enabled device list as noncomprehensive](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices).

| Company/group | Entries in saved snapshot | Decision-year range |
|---|---:|---|
| Gleamer | 4 | 2022–2025 |
| AZmed | 4 | 2022–2025 |
| Visiana | None listed | — |
| 16 Bit | 1 | 2024 |
| Ever Fortune.AI | 11 | 2022–2026 |
| BrightHeart | 5 | 2024–2025 |
| GE / Canon / Siemens / Philips | **284** | 2014–2026 |
| Subtle Medical / AIRS Medical | 13 | 2018–2026 |
| Qure.ai | 9 | 2020–2026 |
| Aidoc / Viz.ai | 43 | 2018–2026 |

The original 307 scanner-company count was inflated by a substring search for `GE`, which also matched unrelated names such as Imagen, Change, Merge and Visage. Word-boundary matching plus the General Electric alias gives 107 GE + 43 Canon + 90 Siemens + 44 Philips = **284**, consistent with the snapshot's normalized company totals. Subtle/AIRS is 8 + 5; Aidoc/Viz is 34 + 9.

The snapshot is not a current census of every authorization. For example, [AZmed announced its sixth FDA clearance on September 15, 2026](https://www.azmed.co/news-post/azmed-receives-its-6th-fda-clearance-taking-rayvolve-to-eight-fda-cleared-findings-across-msk), whereas the saved list contains four AZmed entries. Keep the snapshot date visible; replacing only AZmed's number with a vendor-reported total would mix counting methods. The new AZchest clearance is independently recorded as [K261378, August 28, 2026](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K261378).

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

Map the products to modalities rather than imply that all four do both CT and MRI:

- **GE TrueFidelity:** CT deep-learning reconstruction for noise/image-quality optimization. The [GE product page](https://www.gehealthcare.com/static/truefidelity/) describes the reconstruction function; its [clinical evidence white paper](https://www.gehealthcare.com/-/jssmedia/gehc/us/files/products/computed-tomography/apex-platform/truefidelity-evidence-white-paper-v-released-jb22322xx.pdf?rev=-1) discusses applications across ages.
- **Canon AiCE:** CT **and** MRI reconstruction. See Canon's [CT technical paper](https://global.medical.canon/publications/ct/2019wp-aice-deep-learning/), [MRI product page](https://global.medical.canon/products/magnetic-resonance-imaging/aice/) and [pediatric CT examples](https://us.medical.canon/products/computed-tomography/aquilion-one-prism/clinical-gallery/pediatric/).
- **Siemens Deep Resolve:** MRI reconstruction, denoising and resolution enhancement supporting accelerated acquisition. Siemens publishes [pediatric protocols using Deep Resolve](https://www.magnetomworld.siemens-healthineers.com/clinical-corner/protocols/pediatric-mri-protocols/deep-resolve-pediatric).
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
