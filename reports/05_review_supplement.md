# Supplementary material

## From evidence to deployment: a systematic, continuously updated review of artificial intelligence in pediatric radiology

**Authors:** Joseph Rich, Amit Sura

## Supplementary Table S1. Information sources and complete search strategies

Searches covered January 1, 2005, through September 9, 2026. All concept terms were limited to titles and abstracts. No topic exclusions, publication-type filters, or language restrictions were applied at the search stage.

### PubMed/MEDLINE

**Date searched:** September 9, 2026  
**Records retrieved:** 6,000

The following three blocks were combined with `AND`, followed by `AND 2005:2026[pdat]`.

**Imaging block**

```text
(radiology[tiab] OR radiological[tiab] OR radiograph*[tiab] OR "medical imaging"[tiab]
 OR "diagnostic imaging"[tiab] OR tomography[tiab] OR "magnetic resonance"[tiab]
 OR MRI[tiab] OR "MR imaging"[tiab] OR "MR images"[tiab] OR MRIs[tiab]
 OR "MR image"[tiab] OR "MR scan"[tiab] OR "MR scans"[tiab]
 OR "computed tomography"[tiab] OR CT[tiab] OR ultrasound[tiab]
 OR ultrasonograph*[tiab] OR sonograph*[tiab] OR echocardiograph*[tiab]
 OR mammograph*[tiab] OR "chest x-ray"[tiab] OR "x-ray"[tiab]
 OR fluoroscop*[tiab] OR scintigraph*[tiab] OR "positron emission"[tiab]
 OR PET[tiab] OR SPECT[tiab] OR angiograph*[tiab] OR neuroimaging[tiab]
 OR tractograph*[tiab] OR elastograph*[tiab] OR "fMRI"[tiab]
 OR "functional MRI"[tiab] OR "functional magnetic resonance"[tiab]
 OR connectome*[tiab] OR "diffusion tensor"[tiab] OR DTI[tiab]
 OR "bone age"[tiab] OR "skeletal age"[tiab] OR "skeletal maturity"[tiab]
 OR "barium enema"[tiab])
```

**Artificial-intelligence block**

```text
("artificial intelligence"[tiab] OR "machine learning"[tiab] OR "deep learning"[tiab]
 OR "convolutional neural network"[tiab] OR "convolutional neural networks"[tiab]
 OR "neural network"[tiab] OR "neural networks"[tiab]
 OR "computer-aided diagnosis"[tiab] OR "computer aided diagnosis"[tiab]
 OR "computer-aided detection"[tiab] OR radiomic*[tiab] OR "computer vision"[tiab]
 OR "large language model"[tiab] OR "large language models"[tiab]
 OR "foundation model"[tiab] OR "foundation models"[tiab]
 OR "transfer learning"[tiab] OR "vision transformer"[tiab]
 OR "self-supervised"[tiab] OR "random forest"[tiab]
 OR "support vector machine"[tiab] OR "gradient boosting"[tiab]
 OR "natural language processing"[tiab])
```

**Pediatric-population block**

```text
(pediatric*[tiab] OR paediatric*[tiab] OR child*[tiab] OR infant*[tiab]
 OR neonat*[tiab] OR adolescen*[tiab] OR fetal[tiab] OR foetal[tiab]
 OR fetus*[tiab] OR foetus*[tiab] OR newborn*[tiab] OR preterm[tiab]
 OR "premature infant"[tiab] OR "premature infants"[tiab]
 OR "premature birth"[tiab] OR "premature neonate"[tiab]
 OR "premature neonates"[tiab] OR prenatal[tiab] OR antenatal[tiab]
 OR perinatal[tiab] OR youth[tiab] OR juvenile[tiab]
 OR "children's hospital"[tiab] OR schoolchild*[tiab] OR toddler*[tiab])
```

### Embase (Embase.com)

**Date searched:** September 9, 2026  
**Records retrieved:** 7,288

The PubMed concepts were translated term for term to Embase title/abstract syntax. The following lines were entered in Advanced Search.

```text
#1 (radiology:ti,ab OR radiological:ti,ab OR radiograph*:ti,ab
    OR 'medical imaging':ti,ab OR 'diagnostic imaging':ti,ab OR tomography:ti,ab
    OR 'magnetic resonance':ti,ab OR MRI:ti,ab OR 'mr imaging':ti,ab
    OR 'mr images':ti,ab OR 'computed tomography':ti,ab OR CT:ti,ab
    OR ultrasound:ti,ab OR ultrasonograph*:ti,ab OR sonograph*:ti,ab
    OR echocardiograph*:ti,ab OR mammograph*:ti,ab OR 'chest x ray':ti,ab
    OR 'x ray':ti,ab OR fluoroscop*:ti,ab OR scintigraph*:ti,ab
    OR 'positron emission':ti,ab OR PET:ti,ab OR SPECT:ti,ab
    OR angiograph*:ti,ab OR neuroimaging:ti,ab OR tractograph*:ti,ab
    OR elastograph*:ti,ab OR fMRI:ti,ab OR 'functional MRI':ti,ab
    OR 'functional magnetic resonance':ti,ab OR connectome*:ti,ab
    OR 'diffusion tensor':ti,ab OR DTI:ti,ab OR 'bone age':ti,ab
    OR 'skeletal age':ti,ab OR 'skeletal maturity':ti,ab OR 'barium enema':ti,ab)

#2 ('artificial intelligence':ti,ab OR 'machine learning':ti,ab
    OR 'deep learning':ti,ab OR 'convolutional neural network*':ti,ab
    OR 'neural network*':ti,ab OR 'computer aided diagnosis':ti,ab
    OR 'computer aided detection':ti,ab OR radiomic*:ti,ab
    OR 'computer vision':ti,ab OR 'large language model*':ti,ab
    OR 'foundation model*':ti,ab OR 'transfer learning':ti,ab
    OR 'vision transformer':ti,ab OR 'self supervised':ti,ab
    OR 'random forest':ti,ab OR 'support vector machine':ti,ab
    OR 'gradient boosting':ti,ab OR 'natural language processing':ti,ab)

#3 (pediatric*:ti,ab OR paediatric*:ti,ab OR child*:ti,ab OR infant*:ti,ab
    OR neonat*:ti,ab OR adolescen*:ti,ab OR fetal:ti,ab OR foetal:ti,ab
    OR fetus*:ti,ab OR foetus*:ti,ab OR newborn*:ti,ab OR preterm:ti,ab
    OR 'premature infant*':ti,ab OR 'premature birth':ti,ab
    OR 'premature neonate*':ti,ab OR prenatal:ti,ab OR antenatal:ti,ab
    OR perinatal:ti,ab OR youth:ti,ab OR juvenile:ti,ab
    OR 'children s hospital':ti,ab OR schoolchild*:ti,ab OR toddler*:ti,ab)

#4 #1 AND #2 AND #3 AND [2005-2026]/py
#5 #4 NOT [medline]/lim
#6 #4 AND [medline]/lim
```

Line 5 was exported to identify records outside the MEDLINE-indexed Embase subset, then deduplicated against the complete PubMed corpus by DOI, PMID, and normalized title. The `[medline]/lim` flag was not treated as equivalent to presence in PubMed because PubMed also contains PubMed Central-only records.

### Other information sources

OpenAlex records typed as preprints and the arXiv API were used to supplement the most recent literature. Reference lists of included reviews and the supplementary article list from Kamran et al. [1] were checked. Web of Science, Scopus, IEEE Xplore, and the Cochrane Library were not searched.

### Search-validation results

| Validation set | Retrieved | Denominator | Recall |
|:--|--:|--:|--:|
| Prespecified pediatric landmark papers | 26 | 26 | 100% |
| Articles from Kamran et al. resolved to PubMed | 639 | 663 | 96.4% |
| MEDLINE-indexed records returned by the Embase translation | 3,715 | 3,728 | 99.7% |

## Supplementary Table S2. Eligibility criteria

| Domain | Include | Exclude |
|:--|:--|:--|
| Population | Humans younger than 18 years at imaging; fetal or prenatal imaging; mixed-age cohorts if a pediatric subgroup was analyzed separately or the model was pediatric-specific | Adult-only cohorts; animal- or phantom-only studies without human pediatric data; mixed cohorts without pediatric subgroup analysis |
| Intervention/index test | AI or machine-learning methods developed, trained, fine-tuned, applied, validated, or clinically evaluated, including deep learning, classical machine learning, radiomics with a machine-learning classifier, foundation models, and large language models | Incidental mention of AI; conventional statistical modeling without a machine-learning component; rule-based software |
| Imaging | Diagnostic radiology: radiography, fluoroscopy, CT, MRI, ultrasound, echocardiography, nuclear medicine/PET/SPECT, angiography, and radiology reports or worklists derived from these modalities | Ophthalmic, dental, endoscopic, dermoscopic, histopathologic, whole-slide, or microscopic imaging; EEG, ECG, and other non-imaging signals |
| Study type | Primary model development or validation; reader, prospective, clinical, or implementation studies; dataset descriptors; challenge reports; primary regulatory-database analyses | Narrative or systematic reviews; editorials; letters; comments; case reports; errata; retractions; protocol-only papers |
| Publication form | Journal articles and preprints, with preprints removed when a journal version was identified | Conference abstracts and proceedings |
| Outcome | Any model performance, clinical, workflow, implementation, dataset, education, policy, or stakeholder outcome | No relevant outcome |
| Language | No restriction; non-English records were eligible | None based on language |
| Date | January 1, 2005, to September 9, 2026 | Outside the date range |

## Supplementary Table S3. Operational definitions for principal methodological outcomes

| Outcome | Operational definition |
|:--|:--|
| Internal validation only | Evaluation used data from the same source population or institution as model development, including internal holdout or cross-validation |
| External/multicenter validation | Evaluation used an independent institution, geography, acquisition environment, or multicenter cohort |
| Reader study | Human readers interpreted cases with and/or without the model and reader performance or behavior was measured |
| Prospective evaluation | Data collection, model use, or outcome assessment occurred prospectively after protocol initiation |
| Working code or model URL | The source record supplied a resolvable code-hosting or downloadable-model location |
| Open-source classification | The abstract or cross-check identified publicly available code or model weights; this broader classification can exceed the count of URLs documented directly in abstracts |
| Commercial product | A named commercial tool was evaluated or cross-linked to regulatory or vendor evidence |
| Release status unclear | The abstract did not establish public or commercial availability; this does not mean that the model was unavailable |
| Citations and citations per year | NIH iCite citation count for records with a PubMed identifier, and OpenAlex citation count matched by DOI for records without one; citations per year is the count divided by years since publication, counting the current year as a whole year |
| Normalized citation impact | OpenAlex field-weighted citation impact where available, otherwise the NIH iCite relative citation ratio; both place the average article of the same field and year at 1.0. Reported only for studies with at least five citations, because the ratio otherwise divides by a fraction of an expected citation. Used descriptively and for selecting studies to present individually, never for eligibility |
| Most-cited decile | The highest tenth, by normalized citation impact, of the included studies that have a normalized value |
| Developmental-neuroscience MRI sensitivity analyses (post hoc) | Two keyword rules over the extracted clinical problem, body region, population, description, and title, applied only to studies labelled MRI. **Narrow (diagnosis):** autism, ADHD/attention deficit, psychiatric, depressive, anxiety, schizophrenia, bipolar, internalizing, externalizing, substance use, addiction, gaming disorder, neurodevelopmental disorder. **Wide (diagnosis or neuroscience):** the narrow terms plus neurodevelopment, depression, cognitive, behavioral, intelligence, language development, brain age, brain development, connectome, functional connectivity, fMRI/functional magnetic resonance, resting-state, executive function, emotion, temperament, reward, ABCD study, brain-behavior, neurocognitive, developmental outcome, psychopathology, puberty, graph theory, social. Both rules were written after the corpus was assembled. These studies remain in the corpus; the analyses report composition with them removed |
