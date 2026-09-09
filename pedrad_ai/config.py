"""Central configuration: search vocabularies, year ranges, and output paths.

Editing the query strings here changes what every collector pulls, so this is
the single place to tune scope. Queries are intentionally broad-then-narrow:
``RADIOLOGY_AI`` captures the field, ``PEDIATRIC_RADIOLOGY_AI`` is the subset we
care about, and the modality/topic breakdowns let the reports say *where* inside
radiology AI the activity sits.
"""

from __future__ import annotations

import datetime as _dt
import os
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FIGURE_DIR = REPO_ROOT / "figures"
REPORT_DIR = REPO_ROOT / "reports"

for _d in (RAW_DIR, PROCESSED_DIR, FIGURE_DIR, REPORT_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Time window
# --------------------------------------------------------------------------- #
# The "radiology AI" wave is usually dated to the 2012 ImageNet / deep-learning
# moment, with clinical hype peaking around Geoffrey Hinton's 2016 "stop
# training radiologists" remark. We start in 2008 to capture a pre-deep-learning
# baseline and run to the present.
START_YEAR = 2008
# Inclusive. Runs to the current calendar year so a re-run always reaches the
# present; the current year is *partial* (year-to-date) and the reports label it
# as such and use the last complete year for headline numbers and growth rates.
END_YEAR = _dt.date.today().year
PARTIAL_YEAR = END_YEAR  # the year that is still accumulating records

# --------------------------------------------------------------------------- #
# Contact / API etiquette
# --------------------------------------------------------------------------- #
# NCBI and Crossref ask for an identifying email in the User-Agent / tool param.
# Override with the PEDRAD_AI_EMAIL environment variable.
CONTACT_EMAIL = os.environ.get("PEDRAD_AI_EMAIL", "josephrich98@gmail.com")
USER_AGENT = f"pedrad_ai/0.1 (mailto:{CONTACT_EMAIL})"

# Optional API keys (all collectors work without them, just slower / rate-limited)
NCBI_API_KEY = os.environ.get("NCBI_API_KEY")  # raises PubMed rate limit 3->10 rps
SEMANTIC_SCHOLAR_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # falls back to `gh` CLI auth

# --------------------------------------------------------------------------- #
# Search vocabularies
# --------------------------------------------------------------------------- #
# Each value is a PubMed-style boolean query. The Crossref / Semantic Scholar
# collectors translate these into their own simpler keyword forms.

# Artificial-intelligence terms shared across queries.
_AI_TERMS = (
    '("artificial intelligence" OR "machine learning" OR "deep learning" OR '
    '"convolutional neural network" OR "neural network" OR "computer-aided '
    'diagnosis" OR radiomics OR "computer vision")'
)

# Radiology / imaging terms.
#
# Query v2 (2026-09): the ambiguous tokens are fielded. PubMed's automatic
# term mapping expanded bare ``ultrasound`` to the "diagnostic imaging" MeSH
# *subheading* (attached to almost any imaging-related paper, dental and
# retinal included) and bare ``tomography`` to the whole Tomography MeSH tree
# (which contains optical coherence tomography). The validation script showed
# that about a third of the v1 count came only through such expansions and
# that most of those records were not radiology. Each modality now needs a
# title/abstract mention or its specific MeSH heading, and the other imaging
# specialties (ophthalmology, dental, pathology, endoscopy, dermatology) are
# excluded explicitly.
_RADIOLOGY_TERMS = (
    '((radiology OR radiological OR radiograph* OR "medical imaging" OR "diagnostic imaging"[tiab] OR '
    '"tomography, x-ray computed"[MeSH Terms] OR "tomography, emission-computed"[MeSH Terms] OR '
    'tomograph*[tiab] OR "magnetic resonance" OR MRI OR "computed tomography" OR CT[tiab] OR '
    'ultrasound[tiab] OR ultrasonograph*[tiab] OR sonograph*[tiab] OR echocardiograph*[tiab] OR '
    '"ultrasonography"[MeSH Terms] OR mammograph* OR "chest x-ray") '
    'NOT ("optical coherence"[tiab] OR fundus[tiab] OR retina*[tiab] OR dental[tiab] OR '
    'histopatholog*[tiab] OR "whole slide"[tiab] OR dermoscop*[tiab] OR endoscop*[tiab] OR '
    'colonoscop*[tiab] OR microscop*[tiab]))'
)

# Pediatric terms.
_PEDIATRIC_TERMS = (
    '(pediatric* OR paediatric* OR child* OR infant* OR neonat* OR adolescen* '
    'OR "children\'s hospital")'
)

QUERIES: dict[str, str] = {
    # The whole field, as a denominator.
    "all_radiology": _RADIOLOGY_TERMS,
    # Radiology AI: the numerator for "how popular is radiology AI".
    "radiology_ai": f"{_RADIOLOGY_TERMS} AND {_AI_TERMS}",
    # Pediatric radiology overall (denominator for the pediatric fraction).
    "pediatric_radiology": f"{_RADIOLOGY_TERMS} AND {_PEDIATRIC_TERMS}",
    # The intersection we ultimately care about.
    "pediatric_radiology_ai": (
        f"{_RADIOLOGY_TERMS} AND {_AI_TERMS} AND {_PEDIATRIC_TERMS}"
    ),
    # All AI, to put medical imaging AI in context.
    "all_ai": _AI_TERMS,
}

# Modality breakdown inside radiology AI (used for "where is the activity").
#
# Every term is restricted to the title/abstract field ([tiab]). Bare words are
# a trap here: PubMed's automatic term mapping expands ``ultrasound`` to the
# "diagnostic imaging" MeSH *subheading*, which is attached to almost every
# imaging paper, so an unfielded ultrasound clause matched ~2/3 of the
# radiology-AI corpus. With [tiab] a paper counts for a modality only when its
# title or abstract actually names it.
MODALITY_TERMS: dict[str, str] = {
    "x-ray / radiography": (
        '(radiograph*[tiab] OR "x-ray"[tiab] OR "x-rays"[tiab] OR "chest x-ray"[tiab] '
        'OR "plain film"[tiab] OR CXR[tiab] OR DXA[tiab])'
    ),
    "CT": '("computed tomography"[tiab] OR CT[tiab] OR "CT scan"[tiab] OR "CT scans"[tiab] OR CTA[tiab])',
    "MRI": '("magnetic resonance"[tiab] OR MRI[tiab] OR "MR imaging"[tiab] OR fMRI[tiab])',
    "ultrasound": (
        "(ultrasound[tiab] OR ultrasonograph*[tiab] OR sonograph*[tiab] "
        "OR echocardiograph*[tiab] OR elastograph*[tiab])"
    ),
    "mammography": '(mammogra*[tiab] OR tomosynthesis[tiab] OR "breast imaging"[tiab])',
    "nuclear / PET": (
        '("positron emission"[tiab] OR PET[tiab] OR "PET/CT"[tiab] OR SPECT[tiab] '
        'OR scintigraph*[tiab] OR "nuclear medicine"[tiab])'
    ),
}

# Task breakdown inside radiology AI, organised by *what the model produces*.
# Version 3 (2026-09): the old "classification / detection" and
# "segmentation / quantification" pairs were ambiguous (outcome prediction is
# also a classification; a mask and a number are different products), so the
# categories are now one product each: a present-finding label or box, a mask,
# a number, a future risk, a better or missing image, text, a reusable
# pretrained backbone, an autonomous multi-step action, or a non-interpretive
# workflow decision. As with modalities, all terms are [tiab] and the labels
# overlap (a paper can be both segmentation and measurement).
TASK_TERMS: dict[str, str] = {
    "detection / diagnosis": (
        "(detect*[tiab] OR classif*[tiab] OR triage[tiab] OR screening[tiab] "
        'OR "computer-aided diagnosis"[tiab] OR "computer-aided detection"[tiab])'
    ),
    "segmentation": "(segment*[tiab] OR contour*[tiab] OR delineat*[tiab])",
    "measurement / quantification": (
        '("bone age"[tiab] OR "skeletal maturity"[tiab] OR volumetr*[tiab] OR quantif*[tiab] '
        'OR measurement*[tiab] OR biometry[tiab] OR "Cobb angle"[tiab] OR "brain age"[tiab])'
    ),
    "outcome prediction": (
        '(prognos*[tiab] OR "outcome prediction"[tiab] OR survival[tiab] '
        'OR "risk prediction"[tiab] OR "treatment response"[tiab] OR radiomic*[tiab])'
    ),
    "reconstruction / imputation": (
        '(reconstruct*[tiab] OR denois*[tiab] OR "dose reduction"[tiab] OR "low-dose"[tiab] '
        'OR "super-resolution"[tiab] OR "artifact reduction"[tiab] OR "image quality"[tiab] '
        'OR accelerat*[tiab] OR "image synthesis"[tiab] OR "synthetic CT"[tiab] OR "image-to-image"[tiab] '
        'OR imput*[tiab] OR "missing modality"[tiab])'
    ),
    "report generation / LLM": (
        '("report generation"[tiab] OR "large language model"[tiab] OR "large language models"[tiab] '
        'OR LLM[tiab] OR LLMs[tiab] OR ChatGPT[tiab] OR "GPT-4"[tiab] OR "radiology report"[tiab] '
        'OR "radiology reports"[tiab] OR "natural language processing"[tiab])'
    ),
    "foundation model / vision-language": (
        '("foundation model"[tiab] OR "foundation models"[tiab] OR "vision-language"[tiab] '
        'OR "self-supervised"[tiab] OR "segment anything"[tiab] OR pretrain*[tiab] '
        'OR "pre-trained"[tiab])'
    ),
    "agent / autonomous": (
        '("AI agent"[tiab] OR "AI agents"[tiab] OR agentic[tiab] OR "multi-agent"[tiab] '
        'OR "LLM agent"[tiab] OR "LLM agents"[tiab] OR autonomous[tiab])'
    ),
    "workflow / non-interpretive": (
        "(protocol*[tiab] OR scheduling[tiab] OR worklist[tiab] OR "
        '"turnaround time"[tiab] OR education[tiab] OR "decision support"[tiab] '
        'OR "order"[tiab] OR "appropriateness"[tiab])'
    ),
}
# One-line meaning of each task, shown next to the task figures.
TASK_GLOSS: dict[str, str] = {
    "detection / diagnosis": "is a finding present now, and which one (label or box): fracture, pneumonia, tumor; includes triage and screening",
    "segmentation": "outline a structure or lesion (a mask)",
    "measurement / quantification": "a number from the image: bone age, Cobb angle, organ volume, fetal biometry",
    "outcome prediction": "a future risk, response, or survival estimate from the image (prognosis, radiomics signatures)",
    "reconstruction / imputation": "a better or missing image: lower dose, faster scans, denoising, synthetic CT/MR",
    "report generation / LLM": "text: draft, summarize, or extract from radiology reports",
    "foundation model / vision-language": "a large pretrained model reused across tasks (segment-anything, self-supervised)",
    "agent / autonomous": "multi-step actions taken without a human in the loop",
    "workflow / non-interpretive": "protocoling, scheduling, ordering, decision support, education",
}

# Two eras for the most-cited and problem-breakdown views: citation counts
# favor old papers, so "what mattered before" and "what matters now" are
# ranked separately.
ERAS: list[tuple[str, int, int]] = [
    ("2008-2022", START_YEAR, 2022),
    ("2023-present", 2023, END_YEAR),
]

# Clinical problems addressed by pediatric radiology AI (all [tiab]; overlapping).
# Counted against the pediatric radiology-AI query per era.
PEDIATRIC_PROBLEM_TERMS: dict[str, str] = {
    "bone age / skeletal maturity": '("bone age"[tiab] OR "skeletal maturity"[tiab] OR "skeletal age"[tiab])',
    "fracture / trauma / abuse": (
        '(fracture*[tiab] OR "abusive head trauma"[tiab] OR "non-accidental"[tiab] OR "child abuse"[tiab] '
        'OR "traumatic brain injury"[tiab])'
    ),
    "pneumonia / bronchiolitis / RSV / TB": (
        '(pneumonia[tiab] OR bronchiolitis[tiab] OR "respiratory syncytial"[tiab] OR RSV[tiab] '
        'OR tuberculosis[tiab] OR "lower respiratory tract"[tiab])'
    ),
    "COVID-19 / MIS-C": '(COVID*[tiab] OR "SARS-CoV-2"[tiab] OR "MIS-C"[tiab] OR "multisystem inflammatory"[tiab])',
    "chronic lung disease of prematurity / neonatal lung": (
        '("bronchopulmonary dysplasia"[tiab] OR "chronic lung disease"[tiab] OR "respiratory distress syndrome"[tiab] '
        'OR "neonatal lung"[tiab] OR "lung ultrasound"[tiab])'
    ),
    "cystic fibrosis / asthma / airway": '("cystic fibrosis"[tiab] OR asthma[tiab] OR bronchiectasis[tiab] OR airway[tiab])',
    "appendicitis / intussusception / NEC": (
        '(appendicitis[tiab] OR intussusception[tiab] OR "pyloric stenosis"[tiab] OR "necrotizing enterocolitis"[tiab] '
        'OR malrotation[tiab])'
    ),
    "neonatal jaundice / biliary atresia / liver": (
        '("biliary atresia"[tiab] OR jaundice[tiab] OR cholestasis[tiab] OR "liver fibrosis"[tiab] OR steatosis[tiab] '
        'OR "fatty liver"[tiab])'
    ),
    "inflammatory bowel disease": '(Crohn*[tiab] OR "inflammatory bowel"[tiab] OR "ulcerative colitis"[tiab])',
    "hydronephrosis / VUR / kidney": (
        '(hydronephrosis[tiab] OR "vesicoureteral"[tiab] OR "urinary tract"[tiab] OR "posterior urethral"[tiab] '
        'OR "kidney"[tiab] OR renal[tiab])'
    ),
    "brain tumors": (
        '(glioma*[tiab] OR medulloblastoma[tiab] OR "brain tumor*"[tiab] OR "brain tumour*"[tiab] '
        'OR "posterior fossa"[tiab] OR DIPG[tiab] OR ependymoma[tiab] OR craniopharyngioma[tiab] OR "optic pathway"[tiab])'
    ),
    "other solid tumors / leukemia": (
        '(neuroblastoma[tiab] OR Wilms[tiab] OR nephroblastoma[tiab] OR osteosarcoma[tiab] OR "Ewing"[tiab] '
        'OR rhabdomyosarcoma[tiab] OR hepatoblastoma[tiab] OR lymphoma[tiab] OR leukemia[tiab] OR leukaemia[tiab])'
    ),
    "preterm / neonatal brain injury (HIE, IVH)": (
        '("hypoxic-ischemic"[tiab] OR "hypoxic ischemic"[tiab] OR "intraventricular hemorrhage"[tiab] OR "germinal matrix"[tiab] '
        'OR "white matter injury"[tiab] OR leukomalacia[tiab] OR "neonatal encephalopathy"[tiab] OR "preterm brain"[tiab] '
        'OR "cranial ultrasound"[tiab])'
    ),
    "fetal anomalies / prenatal": (
        '(fetal[tiab] OR fetus[tiab] OR prenatal[tiab] OR "congenital anomal*"[tiab] OR "gestational age"[tiab] '
        'OR placenta*[tiab])'
    ),
    "congenital heart disease / cardiac": (
        '("congenital heart"[tiab] OR tetralogy[tiab] OR "rheumatic heart"[tiab] OR cardiomyopathy[tiab] OR Kawasaki[tiab] '
        'OR "ventricular function"[tiab] OR "ejection fraction"[tiab])'
    ),
    "hydrocephalus / ventricles": '(hydrocephalus[tiab] OR "ventricular volume"[tiab] OR ventriculomegaly[tiab] OR shunt[tiab])',
    "epilepsy": '(epilep*[tiab] OR "focal cortical dysplasia"[tiab] OR seizure*[tiab])',
    "autism / ADHD / neurodevelopment": (
        '(autis*[tiab] OR ADHD[tiab] OR "attention deficit"[tiab] OR "neurodevelopment*"[tiab] OR "cerebral palsy"[tiab] '
        'OR "brain age"[tiab] OR "brain development"[tiab])'
    ),
    "scoliosis / hip dysplasia / MSK": (
        '(scoliosis[tiab] OR "Cobb angle"[tiab] OR "hip dysplasia"[tiab] OR DDH[tiab] OR Perthes[tiab] '
        'OR "leg length"[tiab] OR clubfoot[tiab] OR "slipped capital"[tiab] OR osteomyelitis[tiab] OR "juvenile idiopathic arthritis"[tiab])'
    ),
    "craniosynostosis / craniofacial": '(craniosynostosis[tiab] OR cleft[tiab] OR craniofacial[tiab] OR "skull shape"[tiab])',
    "stroke / sickle cell / vascular": '("sickle cell"[tiab] OR moyamoya[tiab] OR stroke[tiab] OR "arteriovenous"[tiab] OR "vein of Galen"[tiab])',
    "lines and tubes / NICU support devices": (
        '("endotracheal tube"[tiab] OR catheter*[tiab] OR "tube position"[tiab] OR "lines and tubes"[tiab] '
        'OR "umbilical"[tiab] OR "nasogastric"[tiab])'
    ),
    "testicular / ovarian torsion": '(torsion[tiab])',
}

# --------------------------------------------------------------------------- #
# Recall is checked against a hand-picked "gold" set of landmark radiology-AI
# papers that a sufficient query must retrieve. Each DOI is resolved to a PMID;
# papers not indexed in PubMed (arXiv/CVPR-only) are dropped from the
# denominator. Pediatric entries are additionally checked against the
# pediatric query. Kept deliberately mixed: methods papers, clinical
# validations, reconstruction, guidelines, commercial-landscape surveys.
GOLD_PAPERS: list[dict[str, str | bool]] = [
    {"doi": "10.1038/s41592-020-01008-z", "label": "nnU-Net (Nat Methods 2021)"},
    {"doi": "10.1148/ryai.230024", "label": "TotalSegmentator (Radiol AI 2023)"},
    {"doi": "10.1038/s41591-019-0447-x", "label": "Ardila lung-cancer screening CT (Nat Med 2019)"},
    {"doi": "10.1038/s41586-019-1799-6", "label": "McKinney mammography (Nature 2020)"},
    {"doi": "10.1371/journal.pmed.1002686", "label": "CheXNeXt chest radiograph (PLoS Med 2018)"},
    {"doi": "10.1016/S0140-6736(18)31645-3", "label": "Chilamkurthy head CT (Lancet 2018)"},
    {"doi": "10.1038/s41591-018-0147-y", "label": "Titano ICH triage (Nat Med 2018)"},
    {"doi": "10.1148/radiol.2017162326", "label": "Lakhani TB radiograph (Radiology 2017)"},
    {"doi": "10.1371/journal.pmed.1002683", "label": "Zech cross-site generalization (PLoS Med 2018)"},
    {"doi": "10.1038/s41568-018-0016-5", "label": "Hosny AI in radiology (Nat Rev Cancer 2018)"},
    {"doi": "10.1016/j.media.2017.07.005", "label": "Litjens DL survey (Med Image Anal 2017)"},
    {"doi": "10.1109/tmi.2017.2715284", "label": "RED-CNN low-dose CT (IEEE TMI 2017)"},
    {"doi": "10.1002/mrm.26977", "label": "Variational network MRI recon (MRM 2018)"},
    {"doi": "10.1148/ryai.2020200029", "label": "CLAIM checklist (Radiol AI 2020)"},
    {"doi": "10.1007/s00330-021-07892-z", "label": "van Leeuwen 100 commercial products (Eur Radiol 2021)"},
    {"doi": "10.1038/s41467-024-44824-z", "label": "MedSAM (Nat Commun 2024)"},
    {"doi": "10.1038/s41746-020-00376-2", "label": "Esteva medical computer vision (npj Digit Med 2021)"},
    {"doi": "10.1016/j.cell.2018.02.010", "label": "Kermany OCT / chest X-ray (Cell 2018)"},
    {"doi": "10.1148/rg.2017160130", "label": "Erickson ML for medical imaging (RadioGraphics 2017)"},
    {"doi": "10.1148/radiol.2017170236", "label": "Larson bone age (Radiology 2018)", "pediatric": True},
    {"doi": "10.1148/radiol.2018180736", "label": "RSNA bone age challenge (Radiology 2019)", "pediatric": True},
    {"doi": "10.1148/radiol.2020202317", "label": "Brady pediatric CT DL reconstruction (Radiology 2021)", "pediatric": True},
    {"doi": "10.1097/rli.0000000000000615", "label": "Supracondylar fracture CNN (Invest Radiol 2020)", "pediatric": True},
    {"doi": "10.3174/ajnr.a6704", "label": "Posterior fossa tumor DL (AJNR 2020)", "pediatric": True},
    {"doi": "10.1259/bjr.20201263", "label": "Pediatric pneumonia transfer learning (BJR 2021)", "pediatric": True},
    {"doi": "10.1016/j.media.2023.102833", "label": "Fetal brain tissue challenge (Med Image Anal 2023)", "pediatric": True},
    {"doi": "10.1007/s00247-022-05295-w", "label": "BoneXpert autonomous bone age (Pediatr Radiol 2022)", "pediatric": True},
    {"doi": "10.1016/j.jacr.2023.04.017", "label": "Commercial AI of interest to pediatric radiology (JACR 2023)", "pediatric": True},
    {"doi": "10.1016/j.jacr.2023.06.003", "label": "ACR pediatric AI white paper (JACR 2023)", "pediatric": True},
    {"doi": "10.1007/s00247-023-05746-y", "label": "Unintended consequences of AI in paediatric radiology (2024)", "pediatric": True},
]

# Precision proxy: a "strict" variant of the radiology-AI query that only
# accepts title/abstract hits (no MeSH expansion). The ratio strict/broad says
# how much of the headline count rests on PubMed's automatic term mapping; a
# sample of broad-only records is drawn so the report can show what they are.
_AI_TERMS_TIAB = (
    '("artificial intelligence"[tiab] OR "machine learning"[tiab] OR "deep learning"[tiab] OR '
    '"convolutional neural network"[tiab] OR "convolutional neural networks"[tiab] OR '
    '"neural network"[tiab] OR "neural networks"[tiab] OR "computer-aided diagnosis"[tiab] OR '
    'radiomics[tiab] OR "computer vision"[tiab])'
)
_RADIOLOGY_TERMS_TIAB = (
    "(radiology[tiab] OR radiological[tiab] OR radiograph*[tiab] OR "
    '"medical imaging"[tiab] OR tomography[tiab] OR "magnetic resonance"[tiab] OR MRI[tiab] OR '
    '"computed tomography"[tiab] OR CT[tiab] OR ultrasound[tiab] OR ultrasonograph*[tiab] OR '
    'sonograph*[tiab] OR mammograph*[tiab] OR "chest x-ray"[tiab])'
)
STRICT_QUERIES: dict[str, str] = {
    "radiology_ai": f"{_RADIOLOGY_TERMS_TIAB} AND {_AI_TERMS_TIAB}",
    "pediatric_radiology_ai": f"{_RADIOLOGY_TERMS_TIAB} AND {_AI_TERMS_TIAB} AND {_PEDIATRIC_TERMS}",
}

# --------------------------------------------------------------------------- #
# OpenAlex union queries for the "biggest players" tables
# --------------------------------------------------------------------------- #
# OpenAlex full-text search requires every word, so a single "radiology deep
# learning" query misses papers whose title/abstract never say "radiology"
# (e.g. TotalSegmentator, framed purely as CT segmentation). These modality- and
# task-specific queries are run separately and unioned, recovering those papers.
RADIOLOGY_AI_QUERIES = [
    "radiology deep learning",
    "medical imaging deep learning",
    "CT deep learning segmentation",
    "MRI deep learning",
    "chest radiograph deep learning",
    "chest x-ray deep learning",
    "mammography deep learning",
    "ultrasound deep learning diagnosis",
    "radiomics machine learning",
    "computer aided diagnosis convolutional",
    "lung nodule deep learning",
    "anatomical structures segmentation CT",
    # Preprint-first recent work rarely says "deep learning" in the title.
    "radiology foundation model",
    "medical imaging foundation model",
    "medical vision-language model",
    "radiology report generation",
    "chest x-ray vision-language",
    "radiology large language model",
    "medical image segmentation foundation model",
]
PEDIATRIC_RADIOLOGY_AI_QUERIES = [
    "pediatric radiology deep learning",
    "pediatric CT deep learning",
    "pediatric MRI deep learning",
    "bone age deep learning",
    "children chest radiograph deep learning",
    "pediatric pneumonia deep learning radiograph",
    "fetal MRI deep learning segmentation",
    "neonatal brain MRI deep learning",
    "pediatric fracture deep learning radiograph",
    "pediatric radiology foundation model",
    "pediatric chest x-ray vision-language",
    "fetal ultrasound deep learning",
    "pediatric appendicitis deep learning",
]

# --------------------------------------------------------------------------- #
# Conference venues (for the "fraction of conference papers" analyses)
# --------------------------------------------------------------------------- #
# Conferences are tracked over a fixed recent window.
CONF_START_YEAR = 2016
CONF_END_YEAR = 2026

# Machine-learning / computer-vision venues live in DBLP. For these the
# interesting quantity is what *fraction is radiology / medical imaging* (they
# are ~all "AI" by construction). ICCV is biennial (odd years); DBLP simply
# returns nothing for the off years, which the collector skips.
DBLP_VENUES: dict[str, str] = {
    "CVPR": "conf/cvpr",
    "ICCV": "conf/iccv",
    "NeurIPS": "conf/nips",
    "ICML": "conf/icml",
    "ICLR": "conf/iclr",
}

# Radiology society meetings (RSNA, ACR, ECR, SPR) do not publish
# machine-readable programs, so their engagement with AI is approximated by the
# AI fraction of their flagship journals in PubMed (matched by journal
# abbreviation [ta]). For these venues the interesting quantity is the *AI
# fraction* of an otherwise all-radiology body of work.
SOCIETY_JOURNALS: dict[str, list[str]] = {
    "RSNA": ["Radiology", "Radiographics", "Radiol Artif Intell"],
    "ACR": ["J Am Coll Radiol"],
    "ECR": ["Eur Radiol", "Insights Imaging", "Eur Radiol Exp"],
    "SPR": ["Pediatr Radiol"],
}

# Keyword sets used to label a conference paper as "radiology / medical imaging"
# or "AI" from its title.
# Matched as whole words / phrases (see conferences._matches). Kept
# high-precision so the NeurIPS "radiology share" is not inflated by substrings
# like "organization" or "production".
RADIOLOGY_TITLE_KEYWORDS = [
    "radiology", "radiological", "radiograph", "radiographs", "x-ray", "xray",
    "chest x-ray", "mri", "magnetic resonance", "ct scan", "ultrasound",
    "mammography", "mammographic", "tomography", "radiomics", "lesion",
    "tumor", "tumour", "nodule", "medical image", "medical imaging",
    "clinical imaging", "pathology image", "histopathology",
]
AI_TITLE_KEYWORDS = [
    "deep learning", "neural network", "convolutional", "machine learning",
    "transformer", "self-supervised", "segmentation", "classification",
    "diffusion model", "foundation model", "representation learning",
    "generative", "attention",
]
PEDIATRIC_TITLE_KEYWORDS = [
    "pediatric", "paediatric", "child", "infant", "neonat", "adolescent",
    "fetal", "foetal", "newborn", "bone age",
]

# --------------------------------------------------------------------------- #
# Venue tables: which radiology-AI works made it into the big venues
# --------------------------------------------------------------------------- #
# One slide per venue over the recent window, all from Semantic Scholar's bulk
# search (``venue=`` filter; DBLP has no citation counts and OpenAlex has a
# daily budget). Radiology societies are represented by their journals
# (meeting abstracts are not indexed anywhere machine-readable).
VENUE_WORKS_START = 2023
CONFERENCE_WORKS: dict[str, dict] = {
    "NeurIPS": {"kind": "s2", "venue": "NeurIPS", "full": "Conference on Neural Information Processing Systems"},
    "ICLR": {"kind": "s2", "venue": "ICLR", "full": "International Conference on Learning Representations"},
    "ICML": {"kind": "s2", "venue": "ICML", "full": "International Conference on Machine Learning"},
    "CVPR": {"kind": "s2", "venue": "CVPR", "full": "IEEE/CVF Conference on Computer Vision and Pattern Recognition"},
    "MICCAI": {"kind": "s2", "venue": "MICCAI", "full": "Medical Image Computing and Computer-Assisted Intervention"},
    "MIDL": {"kind": "s2", "venue": "MIDL", "full": "Medical Imaging with Deep Learning"},
    "RSNA": {
        "kind": "s2", "query": "ai",
        "venue": "Radiology,Radiology: Artificial Intelligence,RadioGraphics",
        "full": "Radiological Society of North America: Radiology, Radiology: AI, RadioGraphics",
        "note": "RSNA annual-meeting abstracts are not indexed; the society's journals stand in.",
    },
    "SPR": {
        "kind": "s2", "query": "ai",
        "venue": "Pediatric Radiology",
        "full": "Society for Pediatric Radiology: Pediatric Radiology (journal)",
        "note": "SPR meeting abstracts are not indexed; the society's journal stands in.",
    },
}
S2_AI_QUERY = (
    '("artificial intelligence" | "machine learning" | "deep learning" | "neural network" | radiomics | '
    'convolutional | "foundation model" | "language model" | "computer-aided")'
)
# Semantic Scholar bulk-search syntax: | = OR, * = prefix, quotes = phrase.
S2_RADIOLOGY_QUERY = (
    '(radiolog* | mri | "magnetic resonance" | "x-ray" | "chest radiograph" | radiograph* | '
    'ultrasound | ultrasonograph* | echocardiograph* | "computed tomography" | "ct scan" | '
    '"ct images" | "medical imag*" | mammogra* | "bone age" | fetal | "pet/ct" | tomography)'
)

# Title-level relevance filters for the most-cited and venue tables. A paper
# is kept only if its title carries a radiology / medical-imaging signal and
# is not from an adjacent imaging domain (retina, pathology, EEG, ...). This
# keeps recall high (TotalSegmentator, nnU-Net) while dropping generic CS
# papers and non-radiology imaging.
PAPER_MEDICAL_SIGNAL = RADIOLOGY_TITLE_KEYWORDS + [
    "ct", "mri", "imaging", "radiograph", "tumor", "tumour", "lesion",
    "nodule", "cancer", "disease", "diagnosis", "diagnostic", "medical",
    "clinical", "biomedical", "segment", "radiomics", "pneumonia",
    "fracture", "bone age", "covid", "chest", "u-net", "unet", "nnu-net",
    "brain", "cardiac", "abdominal", "anatomic", "anatomical", "pulmonary",
    "fetal", "fmri", "echocardiography", "ultrasound", "x-ray", "pet",
]
PAPER_EXCLUDE_DOMAIN = [
    "retinopathy", "fundus", "ophthalmolog", "retinal", "dermatolog",
    "skin lesion", "skin cancer", "histopath", "whole slide", "whole-slide",
    "microscop", "cytolog", "genomic", "electrocardiogram", "endoscop",
    "eeg", "electroencephalogra", "practice guideline", "encephalopathy",
    "wearable", "ecg", "gaussian splatting", "prohibited item", "baggage",
    "security screening", "dental", "tooth", "teeth", "cbct", "maxillofacial",
    "blood cell", "omics", "big data analytics", "wearable sensor", "speech", "protein",
    "brain decoding", "fmri-to-image", "connectom", "brain activit", "brain signals",
    "pathology image", "pathology images", "clinical text", "text summarization",
]
# The title must also say something about AI / modelling, otherwise a
# highly-cited clinical paper that merely mentions CT and "machine learning"
# in its abstract (a COVID follow-up cohort, say) floats into the AI tables.
PAPER_AI_SIGNAL = AI_TITLE_KEYWORDS + [
    "learning", "artificial intelligence", "ai", "ai-based", "ai-assisted", "model", "models", "network",
    "networks", "automated", "automatic", "algorithm", "algorithms", "segment", "detection", "prediction",
    "predicting", "radiomics", "radiomic", "reconstruction", "u-net", "unet", "nnu-net", "gpt", "chatgpt",
    "language model", "language models", "computer-aided", "computer aided", "vision-language",
    "vision language", "foundation model", "diffusion", "mamba", "large-scale", "benchmark", "dataset",
    "challenge", "synthesis", "denoising", "super-resolution", "registration", "classification",
    "quantification", "estimation", "software", "computational", "computer vision",
]
PAPER_PEDIATRIC_SIGNAL = PEDIATRIC_TITLE_KEYWORDS + [
    "bone age", "pediatrics", "paediatrics", "kawasaki", "scoliosis",
    "preterm", "premature", "congenital", "young adult",
]

# --------------------------------------------------------------------------- #
# Newsletter / trade-press archives (for "what is the field talking about")
# --------------------------------------------------------------------------- #
# The peer-reviewed literature lags practice by a year or more; trade
# newsletters and society news do not. Each source below is an archive that can
# be enumerated without a login. Every issue/article is split into stories and
# a story counts as pediatric-radiology-AI news only when pediatric AND AI (AND,
# for general-tech sources, radiology) terms co-occur inside the same story.
#
# kind:
#   wordpress  - WordPress REST API (``/wp-json/wp/v2/<type>``); full archive.
#   rsna_news  - RSNA News archive page (rsna.org/news/archive) + article bodies.
#   tldr       - TLDR daily pages (``tldr.tech/<newsletter>/YYYY-MM-DD``).
#   rss        - plain RSS/Atom feed; only the recent window the feed exposes.
# radiology_domain: True means every story is about imaging, so the radiology
# vocabulary is not required for a hit.
NEWSLETTER_SOURCES: dict[str, dict] = {
    "The Imaging Wire": {
        "kind": "wordpress",
        "base": "https://theimagingwire.com",
        "types": ["newsletter", "legacy-newsletter"],
        "radiology_domain": True,
        "url": "https://theimagingwire.com/newsletters/",
    },
    "RSNA News": {
        "kind": "rsna_news",
        "archive": "https://www.rsna.org/news/archive",
        "radiology_domain": True,
        "url": "https://www.rsna.org/news",
    },
    "TLDR AI": {
        "kind": "tldr",
        "base": "https://tldr.tech",
        "newsletter": "ai",
        "radiology_domain": False,
        "url": "https://tldr.tech/ai/archives",
    },
    "TLDR Tech": {
        "kind": "tldr",
        "base": "https://tldr.tech",
        "newsletter": "tech",
        "radiology_domain": False,
        "url": "https://tldr.tech/tech/archives",
    },
    "Signify Research": {
        "kind": "wordpress",
        "base": "https://www.signifyresearch.net",
        "types": ["posts"],
        "radiology_domain": False,
        "url": "https://www.signifyresearch.net/insights/",
    },
    # European Society of Radiology: the society news feed (which carries the
    # ECR congress coverage, category "ecr") and the ESR AI Blog, both served
    # by the same WordPress REST API. There is no scannable ECR Today archive;
    # ECR stories live in the news posts.
    "ESR / ECR": {
        "kind": "wordpress",
        "base": "https://www.myesr.org",
        "types": ["posts", "ai-blog"],
        "radiology_domain": True,
        "url": "https://www.myesr.org/news/",
    },
    "Radiology Business": {
        "kind": "rss",
        "feed": "https://radiologybusiness.com/rss.xml",
        "radiology_domain": True,
        "url": "https://radiologybusiness.com",
    },
}

# Sources that were tried and cannot be scanned; listed so the report can say
# so rather than silently omit them.
NEWSLETTER_BLOCKED: dict[str, dict[str, str]] = {
    "AuntMinnie": {"url": "https://www.auntminnie.com", "reason": "blocks automated clients (HTTP 403)"},
    "Diagnostic Imaging": {"url": "https://www.diagnosticimaging.com", "reason": "blocks automated clients (HTTP 403)"},
    "Health Imaging": {"url": "https://healthimaging.com", "reason": "RSS feed exposes no items; no public archive listing"},
    "RSNA AI newsletter / journal e-alerts": {"url": "https://www.rsna.org", "reason": "email-only, no public archive; RSNA News is used instead"},
}

# TLDR has no archive listing beyond the last ~20 issues, so its daily pages are
# enumerated by date from this point forward (weekdays only).
NEWSLETTER_START_DATE = "2024-01-01"

# Vocabularies for labelling a story. Each entry is a regular expression
# fragment matched case-insensitively at a word boundary; a trailing ``\\b`` is
# added only when the pattern ends with a word character and no explicit
# boundary is wanted (stems like ``child`` deliberately match ``children``).
NEWS_PEDIATRIC_PATTERNS = [
    # "child" excludes the Child-Pugh liver score and the idiom "poster child",
    # both of which occur in adult-imaging stories.
    r"p(a)?ediatric", r"(?<!poster )child(?!-pugh)", r"infant", r"neonat", r"newborn", r"adolescen",
    r"f(o)?etal", r"fetus", r"bone age", r"preterm", r"\bnicu\b", r"toddler",
    r"kids\b", r"in utero", r"prenatal",
]
NEWS_AI_PATTERNS = [
    r"artificial intelligence", r"\bai\b", r"\bai-", r"machine learning",
    r"deep learning", r"neural net", r"algorithm", r"large language model",
    r"\bllms?\b", r"chatgpt", r"\bgpt-", r"foundation model", r"computer-aided",
    r"radiomics", r"generative", r"convolutional", r"\bcad\b",
]
NEWS_RADIOLOGY_PATTERNS = [
    r"radiolog", r"imaging", r"x-ray", r"xray", r"\bmri\b", r"\bct\b",
    r"ultrasound", r"sonograph", r"mammogra", r"tomograph", r"radiograph",
    r"\bpet\b", r"\bpacs\b", r"scanner",
]

# Topic tags applied to each pediatric-radiology-AI story so the report can say
# what the news is *about* (overlapping; a story may carry several).
NEWS_TOPIC_PATTERNS: dict[str, list[str]] = {
    "bone age / skeletal maturity": [r"bone age", r"skeletal maturity"],
    "fracture / trauma / abuse": [r"fractur", r"trauma", r"abuse", r"non-accidental"],
    "chest / pneumonia": [r"pneumonia", r"chest x-ray", r"chest radiograph", r"chest ct", r"lung"],
    "CT dose / reconstruction": [r"dose", r"reconstruct", r"denois"],
    "fetal / neonatal brain MRI": [r"f(o)?etal", r"neonat", r"brain mri", r"preterm"],
    "cancer / oncology": [r"tumou?r", r"cancer", r"oncolog", r"glioma", r"neuroblastoma"],
    "cardiac / echo": [r"cardiac", r"echocardiogra", r"congenital heart"],
    "appendicitis / abdomen / ultrasound": [r"appendic", r"abdom", r"ultrasound", r"hydroneph"],
    "regulatory / FDA clearance": [r"\bfda\b", r"clearance", r"cleared", r"510\(k\)", r"ce mark"],
    "LLMs / report generation": [r"large language model", r"\bllm", r"chatgpt", r"\bgpt", r"report generation"],
    "funding / business": [r"funding", r"raises", r"acqui", r"venture", r"\bm&a\b", r"startup", r"commercial"],
    "scoliosis / MSK": [r"scoliosis", r"cobb", r"hip dysplasia", r"musculoskeletal"],
}

# --------------------------------------------------------------------------- #
# Commercial players: FDA AI-enabled device list + curated pediatric products
# --------------------------------------------------------------------------- #
# FDA publishes the list of AI-enabled medical devices it has authorized
# (510(k), De Novo, PMA) as a spreadsheet: decision date, device, company,
# lead panel. Filtering on the Radiology panel gives the commercial radiology-AI
# landscape by year and by company. The list carries no pediatric flag, so
# pediatric relevance comes from device names plus the curated list below.
FDA_AI_DEVICES_URL = "https://www.fda.gov/media/178540/download?attachment"
FDA_AI_DEVICES_PAGE = (
    "https://www.fda.gov/medical-devices/software-medical-device-samd/"
    "artificial-intelligence-enabled-medical-devices"
)
FDA_PEDIATRIC_NAME_PATTERNS = [
    r"p(a)?ediatric", r"bone age", r"child", r"infant", r"neonat", r"f(o)?etal",
    r"skeletal maturity", r"boneview", r"rayvolve", r"bonexpert", r"\brho\b",
]

# Commercial products with a documented pediatric angle, for the commercial
# slide. "status" is what is publicly stated by the vendor / regulator; the
# FDA-list cross-check adds the company's authorization count and years.
COMMERCIAL_PEDIATRIC: list[dict[str, str]] = [
    {"vendor": "Gleamer", "product": "BoneView", "task": "fracture detection on radiographs",
     "pediatric": "pediatric indication (age 2+) cleared 2023", "modality": "x-ray",
     "fda_company": "Gleamer", "url": "https://www.gleamer.ai"},
    {"vendor": "AZmed", "product": "Rayvolve", "task": "fracture (and chest) findings on radiographs",
     "pediatric": "pediatric fracture indication cleared 2024", "modality": "x-ray",
     "fda_company": "AZmed", "url": "https://azmed.co"},
    {"vendor": "Visiana", "product": "BoneXpert", "task": "automated bone age (GP / TW)",
     "pediatric": "pediatric by design; CE-marked since 2009 (not on the FDA AI list)", "modality": "x-ray",
     "fda_company": "Visiana", "url": "https://bonexpert.com"},
    {"vendor": "16 Bit", "product": "Rho", "task": "automated bone age",
     "pediatric": "pediatric by design", "modality": "x-ray",
     "fda_company": "16 Bit", "url": "https://www.16bit.ai"},
    {"vendor": "Ever Fortune.AI", "product": "EFAI Bonesuite Bone Age Pro", "task": "automated bone age",
     "pediatric": "pediatric by design", "modality": "x-ray",
     "fda_company": "Ever Fortune", "url": ""},
    {"vendor": "BrightHeart", "product": "Fetal EchoScan", "task": "fetal echocardiography view / anomaly assist",
     "pediatric": "prenatal (fetal) by design", "modality": "ultrasound",
     "fda_company": "BrightHeart", "url": ""},
    {"vendor": "GE HealthCare / Canon / Siemens / Philips", "product": "TrueFidelity, AiCE, Deep Resolve, Precise Image",
     "task": "deep-learning CT / MR reconstruction (lower dose, faster scans)",
     "pediatric": "adult-cleared scanner software, widely used for pediatric dose reduction", "modality": "CT / MRI",
     "fda_company": "GE|Canon|Siemens|Philips", "url": ""},
    {"vendor": "Subtle Medical / AIRS Medical", "product": "SubtleMR, SwiftMR",
     "task": "accelerated MRI via deep-learning denoising", "pediatric": "adult-cleared; pediatric scan-time studies",
     "modality": "MRI", "fda_company": "Subtle Medical|AIRS Medical", "url": ""},
    {"vendor": "Qure.ai", "product": "qXR / qER", "task": "chest radiograph and head CT triage / quantification",
     "pediatric": "adult indications; pediatric TB-screening evidence only", "modality": "x-ray / CT",
     "fda_company": "Qure.ai", "url": "https://www.qure.ai"},
    {"vendor": "Aidoc / Viz.ai", "product": "BriefCase, Viz LVO / ICH",
     "task": "worklist triage (hemorrhage, LVO, PE, pneumothorax)",
     "pediatric": "adult-only indications; the largest deployed category", "modality": "CT / x-ray",
     "fda_company": "Aidoc|Viz.ai", "url": ""},
]

# Company / tool names counted in newsletter stories ("who is being talked
# about"). Mixed on purpose: vendors, scanner makers, big tech, and the
# open-source tools, so the same chart puts commercial and academic players on
# one scale. Patterns are case-insensitive regex fragments.
NEWS_PLAYER_PATTERNS: dict[str, list[str]] = {
    "Aidoc": [r"\baidoc"], "Viz.ai": [r"\bviz\.ai", r"\bviz ai\b"], "Gleamer": [r"\bgleamer"],
    "AZmed": [r"\bazmed"], "Qure.ai": [r"\bqure\.?ai"], "Lunit": [r"\blunit"],
    "Annalise.ai": [r"\bannalise"], "Rad AI": [r"\brad ai\b", r"\bradai\b"],
    "RapidAI": [r"\brapidai", r"\brapid ai\b"], "Brainomix": [r"\bbrainomix"],
    "HeartFlow": [r"\bheartflow"], "Subtle Medical": [r"\bsubtle medical", r"\bsubtlemr"],
    "AIRS Medical": [r"\bairs medical", r"\bswiftmr"], "Siemens Healthineers": [r"\bsiemens"],
    "GE HealthCare": [r"\bge healthcare", r"\bge health"], "Philips": [r"\bphilips"],
    "Canon Medical": [r"\bcanon medical", r"\bcanon\b"], "Fujifilm": [r"\bfujifilm"],
    "Nuance / Microsoft": [r"\bnuance", r"\bmicrosoft"], "Google": [r"\bgoogle", r"\bdeepmind"],
    "OpenAI / ChatGPT": [r"\bopenai", r"\bchatgpt", r"\bgpt-4"], "Nvidia": [r"\bnvidia"],
    "Bayer (Calantic)": [r"\bcalantic", r"\bbayer\b"], "Arterys": [r"\barterys"],
    "Zebra / Nanox": [r"\bzebra medical", r"\bnanox"], "Kheiron": [r"\bkheiron"],
    "iCAD": [r"\bicad\b"], "Volpara": [r"\bvolpara"], "Hologic": [r"\bhologic"],
    "DeepHealth / RadNet": [r"\bdeephealth", r"\bradnet"], "Imagen": [r"\bimagen technolog", r"\bosteodetect"],
    "Radiobotics": [r"\bradiobotics"], "Koios": [r"\bkoios"], "Butterfly": [r"\bbutterfly network", r"\bbutterfly iq"],
    "Caption Health": [r"\bcaption health"], "Visiana (BoneXpert)": [r"\bbonexpert", r"\bvisiana"],
    "16 Bit": [r"\b16 ?bit\b"], "Harrison.ai": [r"\bharrison\.?ai"], "Enlitic": [r"\benlitic"],
    "Infervision": [r"\binfervision"], "United Imaging": [r"\bunited imaging"],
    "Sirona Medical": [r"\bsirona"], "Sectra": [r"\bsectra"], "Blackford": [r"\bblackford"],
    "Quibim": [r"\bquibim"], "icometrix": [r"\bicometrix"], "Perspectum": [r"\bperspectum"],
    "Riverain": [r"\briverain"], "Coreline": [r"\bcoreline"], "VUNO": [r"\bvuno"],
    "Mediaire / others": [r"\bmediaire"], "Medtronic": [r"\bmedtronic"],
    "MONAI (open source)": [r"\bmonai"], "nnU-Net (open source)": [r"\bnnu-?net"],
    "TotalSegmentator (open source)": [r"\btotalsegmentator"], "Segment Anything / MedSAM": [r"\bsegment anything", r"\bmedsam"],
}

# Open-source tools every radiologist should know, fetched directly by name so
# the leaderboard does not depend on GitHub search recall (search misses MONAI
# and nnU-Net because their descriptions do not say "radiology").
KNOWN_REPOS: list[str] = [
    "Project-MONAI/MONAI", "MIC-DKFZ/nnUNet", "wasserth/TotalSegmentator",
    "bowang-lab/MedSAM", "facebookresearch/fastMRI", "Slicer/Slicer",
    "fepegar/torchio", "SimpleITK/SimpleITK", "InsightSoftwareConsortium/ITK",
    "MedMNIST/MedMNIST", "mlmed/torchxrayvision", "Tencent/MedicalNet",
    "Project-MONAI/MONAILabel", "microsoft/InnerEye-DeepLearning",
    "pydicom/pydicom", "nipy/nibabel", "OHIF/Viewers", "cornerstonejs/cornerstone3D",
    "microsoft/LLaVA-Med", "chaoyi-wu/RadFM", "bowang-lab/MedRAX",
    "rajpurkarlab/CheXzero", "ANTsX/ANTs", "Beckschen/TransUNet",
    "HuCaoFighting/Swin-Unet", "MrGiovanni/ModelsGenesis", "JJGO/UniverSeg",
    "uni-medical/SAM-Med3D", "black0017/MedicalZooPytorch", "ellisdg/3DUnetCNN",
]

# Example images for the "what it looks like" slides. Each entry names where a
# representative picture can be fetched without a login:
#   github_readme  - first image linked from the repository README
#   og_image       - the page's Open Graph preview image (vendor sites)
#   europepmc_fig  - first figure of an open-access article, by DOI
# --------------------------------------------------------------------------- #
# Public pediatric imaging datasets (curated; numbers verified against the
# primary papers / hosting pages on 2026-09-07). Sorted by size for the slide.
# --------------------------------------------------------------------------- #
PEDIATRIC_DATASETS: list[dict[str, str]] = [
    {"name": "CBTN clinical MRI (Children's Brain Tumor Network)", "year": "2023", "modality": "brain / spine tumor MRI",
     "size": "23,101 exams (1,526 patients); tumor masks for 370", "ages": "pediatric", "access": "application (NCI CCDI)", "ref": "arXiv:2310.01413"},
    {"name": "GRAZPEDWRI-DX", "year": "2022", "modality": "wrist radiographs (trauma)",
     "size": "20,327 images (6,091 patients)", "ages": "0.2--19 y", "access": "open", "ref": "Nagy, Sci Data 2022"},
    {"name": "RSNA Pediatric Bone Age Challenge", "year": "2017", "modality": "hand radiographs",
     "size": "14,236 images (bone age + sex)", "ages": "mean 10.6 y", "access": "open (RSNA terms)", "ref": "Halabi, Radiology 2019"},
    {"name": "FETAL\_PLANES\_DB", "year": "2020", "modality": "fetal ultrasound (standard planes)",
     "size": "12,400 images (1,792 pregnancies)", "ages": "fetal", "access": "open", "ref": "Burgos-Artizzu, Sci Rep 2020"},
    {"name": "ABCD Study", "year": "2018--", "modality": "brain MRI, longitudinal",
     "size": "11,878 participants, up to 7 follow-ups", "ages": "9--10 y at baseline", "access": "application (NBDC)", "ref": "Casey, Dev Cogn Neurosci 2018"},
    {"name": "PediCXR / VinDr-PCXR", "year": "2023", "modality": "chest radiographs",
     "size": "9,125 studies; 36 findings, 15 diagnoses", "ages": "< 10 y", "access": "credentialed (PhysioNet)", "ref": "Pham, Sci Data 2023"},
    {"name": "Guangzhou pediatric chest X-ray (Kermany)", "year": "2018", "modality": "chest radiographs",
     "size": "5,856 images (normal / bacterial / viral pneumonia)", "ages": "1--5 y", "access": "open", "ref": "Kermany, Cell 2018"},
    {"name": "ABIDE I + II (autism)", "year": "2012 / 2016", "modality": "brain MRI (structural, resting fMRI)",
     "size": "2,156 subjects", "ages": "5--64 y (mostly children)", "access": "open", "ref": "Di Martino, Mol Psychiatry 2014"},
    {"name": "Regensburg Pediatric Appendicitis", "year": "2023", "modality": "abdominal ultrasound + labs",
     "size": "1,709 images (579 patients)", "ages": "0--18 y", "access": "open", "ref": "Marcinkevičs, Med Image Anal 2024"},
    {"name": "dHCP (Developing Human Connectome Project)", "year": "2022--24", "modality": "neonatal + fetal brain MRI",
     "size": "886 neonatal + 297 fetal datasets, with segmentations", "ages": "20--45 weeks", "access": "open (NDA)", "ref": "Edwards, Front Neurosci 2022"},
    {"name": "Pediatric-CT-SEG (TCIA)", "year": "2022", "modality": "chest / abdomen / pelvis CT",
     "size": "718 series (359 patients); 29 organ contours", "ages": "5 days -- 16 y", "access": "open", "ref": "Jordan, Med Phys 2022"},
    {"name": "BraTS-PEDs (pediatric brain tumor challenge)", "year": "2023--25", "modality": "brain tumor MRI",
     "size": "464 patients (2024 challenge); 1,649 series on TCIA", "ages": "pediatric", "access": "registration / TCIA", "ref": "Kazerooni, MELBA 2025"},
    {"name": "FeTA (fetal brain tissue annotation)", "year": "2021--24", "modality": "fetal brain MRI",
     "size": "280 volumes (120 train + 160 test); 7 tissue labels", "ages": "18--35 weeks", "access": "registration", "ref": "Payette, Sci Data 2021"},
]

EXAMPLE_IMAGES: list[dict[str, str]] = [
    {"slug": "totalsegmentator", "kind": "github_readme", "ref": "wasserth/TotalSegmentator",
     "caption": "TotalSegmentator: 100+ anatomic structures segmented on any CT (repository README)", "group": "open source"},
    {"slug": "nnunet", "kind": "github_readme", "ref": "MIC-DKFZ/nnUNet",
     "caption": "nnU-Net: self-configuring segmentation pipeline (repository README)", "group": "open source"},
    {"slug": "medsam_paper", "kind": "url",
     "ref": "https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41467-024-44824-z/MediaObjects/41467_2024_44824_Fig1_HTML.png",
     "caption": "MedSAM (Nat Commun 2024, CC BY): prompt-based segmentation across modalities", "group": "open source"},
    {"slug": "zech_generalization", "kind": "url",
     "ref": "https://journals.plos.org/plosmedicine/article/figure/image?size=large&id=10.1371/journal.pmed.1002683.g002",
     "caption": "Zech et al. (PLoS Med 2018, CC BY): the model learns which hospital took the film", "group": "paper"},
    {"slug": "pediatric_pneumonia", "kind": "europepmc_fig", "ref": "10.1259/bjr.20201263",
     "caption": "Pediatric chest X-ray pneumonia detection (BJR 2021), figure 1", "group": "paper"},
    {"slug": "posterior_fossa", "kind": "europepmc_fig", "ref": "10.3174/ajnr.a6704",
     "caption": "Pediatric posterior fossa tumor detection on MRI (AJNR 2020)", "group": "paper"},
    {"slug": "fetal_cortical_plate", "kind": "europepmc_fig", "ref": "10.1109/tmi.2020.3046579",
     "caption": "Fetal cortical plate segmentation on MRI (IEEE TMI 2021)", "group": "paper"},
    {"slug": "gleamer", "kind": "page_image", "ref": "https://www.gleamer.ai/solutions/boneview",
     "caption": "Gleamer BoneView: fracture detection with a pediatric indication (vendor site)", "group": "commercial"},
    {"slug": "azmed", "kind": "url", "ref": "https://cdn.prod.website-files.com/66ab8ecb1ed279875233cfc6/66fdc5061c42a4692cd79b7a_full%20chest%20final%20(1).webp",
     "caption": "AZmed Rayvolve: fracture detection on radiographs (vendor site)", "group": "commercial"},
    {"slug": "bonexpert", "kind": "og_image", "ref": "https://bonexpert.com",
     "caption": "Visiana BoneXpert: automated bone age (vendor site)", "group": "commercial"},
    {"slug": "qure", "kind": "page_image", "ref": "https://www.qure.ai/product/qxr",
     "caption": "Qure.ai qXR: chest radiograph findings (vendor site)", "group": "commercial"},
    # Paper spotlights (one slide per paper; text lives in curated.PAPER_SPOTLIGHTS).
    # ``fig`` = 1-based index into the article's PMC figure list.
    {"slug": "spot_fracture_ed", "kind": "europepmc_fig", "ref": "10.1007/s00330-025-11554-9", "fig": 5,
     "caption": "Ziegner et al., Eur Radiol 2025, figure 4: pediatric fractures the software found, with its per-region sensitivity and specificity", "group": "spotlight"},
    {"slug": "spot_ped_tb", "kind": "europepmc_fig", "ref": "10.1038/s41467-025-64391-1", "fig": 1,
     "caption": "Capellan-Martin et al., Nat Commun 2025, figure 1: the multi-view pTBLightNet pipeline", "group": "spotlight"},
    {"slug": "spot_dl_recon_mri", "kind": "europepmc_fig", "ref": "10.3348/kjr.2024.0701", "fig": 2,
     "caption": "Yoo et al., Korean J Radiol 2025, figure 2: conventional (A, D) vs accelerated 3D T1 pediatric brain MRI without (B, E) and with (C, F) deep-learning reconstruction", "group": "spotlight"},
    {"slug": "spot_deeplasia_rare", "kind": "europepmc_fig", "ref": "10.3389/fendo.2026.1741927", "fig": 1,
     "caption": "Skaf et al., Front Endocrinol 2026, figure 1: Deeplasia bone age vs the expert mean in the endocrine cohort (scatter and Bland-Altman)", "group": "spotlight"},
    {"slug": "spot_pet_dose", "kind": "europepmc_fig", "ref": "10.1186/s40658-026-00876-2", "fig": 5,
     "caption": "Han et al., EJNMMI Phys 2026, figure 5: pediatric whole-body FDG PET, standard 90 s vs 20 s per bed, with and without patch-based deep-learning denoising", "group": "spotlight"},
    {"slug": "spot_not_small_adults", "kind": "europepmc_fig", "ref": "10.1007/s10278-024-01273-w", "fig": 7,
     "caption": "Chatterjee et al., J Imaging Inform Med 2025, figure 7: pediatric CT organ labels, ground truth vs adult-trained TotalSegmentator vs pediatric-trained models", "group": "spotlight"},
]

# --------------------------------------------------------------------------- #
# Paper database (structured, per-paper extraction)
# --------------------------------------------------------------------------- #
# The counting collectors answer "how much"; the paper database answers "what",
# one row per pediatric radiology-AI paper: which model, on which modality, in
# which children, for which clinical problem, and whether anyone outside the
# authors' institution can actually use it. Rows are produced by reading each
# abstract with Claude under a fixed schema (see :mod:`pedrad_ai.paper_db` and
# :mod:`pedrad_ai.extract`) and are appended incrementally, so a refresh only
# pays for papers that are new since the last run.

PAPER_DB_JSON = PROCESSED_DIR / "pedrad_paper_db.json"
PAPER_DB_CSV = PROCESSED_DIR / "pedrad_paper_db.csv"
PAPER_DB_SUMMARY = PROCESSED_DIR / "pedrad_paper_db_summary.json"
# Papers waiting to be read, written by --worklist and read back by --ingest.
# This is the no-API-key path: the abstracts are dumped for a person (or a
# Claude Code session) to read, and the rows come back through the same schema
# validation the API path uses.
PAPER_DB_WORKLIST = PROCESSED_DIR / "pedrad_paper_db_worklist.json"
# Hand corrections, keyed by PMID: {"12345678": {"model_name": "BoneXpert", ...}}.
# Applied after extraction and never overwritten by a re-run, so a human
# reviewing the table can fix a row permanently. Committed to the repo.
PAPER_DB_OVERRIDES = DATA_DIR / "paper_db_overrides.json"

# Bump when the extraction schema or prompt changes in a way that makes old
# rows non-comparable; rows stamped with an older version are re-extracted.
PAPER_DB_SCHEMA_VERSION = 1

# Candidate papers come from the pediatric radiology-AI PubMed query. 2015 is
# the practical floor: before it the corpus is mostly hand-crafted-feature work
# with no named, reusable model, which is what these columns are for.
PAPER_DB_START_YEAR = 2015

# Candidate query for the database. Deliberately stricter than
# QUERIES["pediatric_radiology_ai"], which is the right net for *counting* (it
# accepts MeSH-indexed papers whose abstract never says "child") but the wrong
# one for a table of what has been built for children: ranked by citations, that
# query's top results are Global Burden of Disease reports and adult
# neuroimaging that match only through MeSH expansion. Here every clause has to
# appear in the title or abstract, which is the same rule the modality and task
# term groups already follow. Counting queries are untouched, so the headline
# numbers in the reports stay comparable.
_PEDIATRIC_TERMS_TIAB = (
    "(pediatric*[tiab] OR paediatric*[tiab] OR child*[tiab] OR infant*[tiab] OR "
    "neonat*[tiab] OR adolescen*[tiab] OR fetal[tiab] OR foetal[tiab] OR "
    "newborn*[tiab] OR preterm[tiab] OR \"children's hospital\"[tiab])"
)
PAPER_DB_QUERY = f"{STRICT_QUERIES['radiology_ai']} AND {_PEDIATRIC_TERMS_TIAB}"

# Citation floor. The query returns ~10,000 records from 2015 on, most of which
# nobody has read: a threshold on NIH iCite's citedByPmidCount (PubMed-indexed
# citing papers, so a conservative count) is the cheapest way to keep the
# database to work the field actually engages with. 20 keeps roughly a fifth of
# the corpus. Note that it is also an implicit recency filter — a 2026 paper has
# had no time to accrue citations — so the last two years are always
# under-represented; --min-citations 0 turns the filter off.
PAPER_DB_MIN_CITATIONS = 20

# Year-normalized floors, combined with the raw count by OR. A raw count is the
# wrong filter for the current year, where nothing has had time to be cited:
# of the 763 papers this query returns for 2026, eight have five citations. So a
# rate (citations per year) and iCite's relative citation ratio (RCR, where 1.0
# is the median NIH-funded paper of the same field and year) let recent work in
# on its own terms. Note RCR is only computed once a paper is about two years
# old — present for 94% of 2024 papers here but 17% of 2025 and 1% of 2026 —
# so the rate is what actually carries the newest years. 0 disables a clause.
PAPER_DB_MIN_CITATIONS_PER_YEAR = 10.0
PAPER_DB_MIN_RCR = 5.0

# Preprints. PubMed does not index arXiv and indexes medRxiv and bioRxiv only
# through the NIH preprint pilot, so a PubMed-only view of the current year
# misses much of the methods work. Candidates are topped up from OpenAlex
# ``type:preprint`` and deduplicated against the PubMed set by PMID, DOI and
# normalized title, so a preprint drops out once its journal version appears.
PAPER_DB_INCLUDE_PREPRINTS = True
PAPER_DB_PREPRINT_CAP = 600  # per year, a guard against a runaway OpenAlex page loop

# Conference proceedings. Much of the methods work in this field is published at
# MICCAI, ISBI, IPMI, MIDL, NeurIPS and CVPR rather than in journals. Coverage
# comes from three directions and none of them alone is enough:
#   * PubMed indexes some proceedings outright (IPMI, IEEE EMBC, SPIE Medical
#     Imaging), so those already arrive through PAPER_DB_QUERY;
#   * the arXiv preprint stream carries the author versions of most NeurIPS,
#     CVPR and MICCAI papers, so PAPER_DB_INCLUDE_PREPRINTS catches many;
#   * this source adds works OpenAlex types as ``conference-paper``, plus a
#     second pass over Lecture Notes in Computer Science, where the MICCAI, IPMI
#     and MIDL proceedings are filed.
# The work type is the filter and the venue is not: OpenAlex files MICCAI under
# a book series, NeurIPS and CVPR under their own sources, and
# ``primary_location.source.type:conference`` catches almost none of them while
# sweeping in a long tail of unrelated local proceedings. A record that comes
# back with no abstract — which is most of them — cannot be read under the
# extraction schema and is reported, not guessed at.
PAPER_DB_INCLUDE_CONFERENCE = True
PAPER_DB_CONFERENCE_CAP = 1200  # a guard against a runaway OpenAlex page loop
# The second clause is an imaging clause, not a machine-learning one. An earlier
# version paired the pediatric terms with "segmentation OR detection OR
# classification ..."; across all conference proceedings that matches papers on
# cyberbullying detection, crowd counting and blockchain, because "child" and
# "detection" co-occur everywhere. Requiring a modality or an imaging phrase is
# what makes this a radiology search.
PAPER_DB_CONFERENCE_QUERY = (
    "(pediatric OR paediatric OR pediatrics OR paediatrics OR fetal OR foetal OR neonatal OR "
    "neonate OR infant OR infants OR children OR child OR newborn OR preterm OR adolescent OR "
    "adolescents OR prenatal) AND "
    "(radiograph OR radiographs OR radiography OR radiology OR radiological OR \"x-ray\" OR "
    "\"chest x-ray\" OR ultrasound OR ultrasonography OR sonography OR sonographic OR "
    "echocardiography OR MRI OR \"magnetic resonance\" OR \"computed tomography\" OR tomography OR "
    "PET OR SPECT OR mammography OR fluoroscopy OR angiography OR tractography OR neurosonography OR "
    "\"bone age\" OR \"medical image\" OR \"medical imaging\" OR neuroimaging OR "
    "\"image segmentation\" OR \"image registration\" OR \"image reconstruction\" OR "
    "\"image analysis\" OR \"image classification\")"
)
# OpenAlex source id for Lecture Notes in Computer Science, where the MICCAI,
# IPMI and MIDL proceedings are filed.
PAPER_DB_LNCS_SOURCE = "S106296714"

# Extraction is a per-abstract structured-output call, so cost scales with the
# number of new papers. Defaults are deliberately modest; scripts/build_paper_db.py
# takes --limit / --all / --model / --effort to override.
PAPER_DB_MODEL = os.environ.get("PEDRAD_AI_EXTRACT_MODEL", "claude-sonnet-5")
PAPER_DB_EFFORT = os.environ.get("PEDRAD_AI_EXTRACT_EFFORT", "low")
PAPER_DB_RUN_LIMIT = int(os.environ.get("PEDRAD_AI_EXTRACT_LIMIT", "250"))
PAPER_DB_WORKERS = int(os.environ.get("PEDRAD_AI_EXTRACT_WORKERS", "4"))

# Controlled vocabularies. The extractor is only allowed to emit these values,
# so the database groups cleanly and stays comparable with the count-based
# modality / task breakdowns above. "other" and "not stated" are always legal.
PAPER_DB_MODALITIES = [
    "x-ray / radiography",
    "CT",
    "MRI",
    "ultrasound",
    "nuclear / PET",
    "fluoroscopy",
    "mammography",
    "multiple",
    "other",
]

PAPER_DB_AGE_GROUPS = [
    "fetal",
    "neonate",
    "infant",
    "child",
    "adolescent",
    "pediatric (unspecified)",
    "mixed pediatric and adult",
]

# Mirrors TASK_TERMS: categories named for what the model produces.
PAPER_DB_TASKS = list(TASK_TERMS.keys()) + ["other"]

# The release axis: can anyone outside the authors' group run this model?
PAPER_DB_RELEASE_STATUS = [
    "open-source",   # weights and/or code publicly available (repo, model hub)
    "commercial",    # sold or licensed as a product / cleared device
    "unreleased",    # described in the paper only, no code, no product
    "unclear",       # abstract does not say either way
]

PAPER_DB_VALIDATION = [
    "internal only",
    "external / multi-center",
    "prospective",
    "reader study",
    "none / not stated",
]

PAPER_DB_DATA_SOURCE = [
    "single center",
    "multi center",
    "public dataset",
    "not stated",
]

# Code-hosting hosts scanned in the abstract text; a hit is strong evidence of
# an open-source release and overrides an "unclear" verdict from the model.
PAPER_DB_CODE_HOSTS = [
    "github.com",
    "gitlab.com",
    "bitbucket.org",
    "huggingface.co",
    "zenodo.org",
    "codeocean.com",
    "sourceforge.net",
]
