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

# Task breakdown inside radiology AI, organised by *what the model produces*
# so the categories are mutually intelligible (the old "detection" vs
# "classification" split was not): a label or box, a mask/measurement, a risk,
# a better image, text, a reusable pretrained backbone, a synthetic image, an
# autonomous multi-step action, or a non-interpretive workflow decision. As
# with modalities, all terms are [tiab] and the labels overlap.
TASK_TERMS: dict[str, str] = {
    "classification / detection": (
        "(classif*[tiab] OR detect*[tiab] OR triage[tiab] OR screening[tiab] "
        'OR "computer-aided diagnosis"[tiab] OR "computer-aided detection"[tiab])'
    ),
    "segmentation / quantification": (
        "(segment*[tiab] OR contour*[tiab] OR delineat*[tiab] OR volumetr*[tiab] "
        "OR quantif*[tiab] OR measurement*[tiab])"
    ),
    "prognosis / outcome prediction": (
        '(prognos*[tiab] OR "outcome prediction"[tiab] OR survival[tiab] '
        'OR "risk prediction"[tiab] OR "treatment response"[tiab] OR radiomic*[tiab])'
    ),
    "reconstruction / image enhancement": (
        '(reconstruct*[tiab] OR denois*[tiab] OR "dose reduction"[tiab] OR "low-dose"[tiab] '
        'OR "super-resolution"[tiab] OR "artifact reduction"[tiab] OR "image quality"[tiab] '
        "OR accelerat*[tiab])"
    ),
    "report generation / LLM": (
        '("report generation"[tiab] OR "large language model"[tiab] OR "large language models"[tiab] '
        'OR LLM[tiab] OR LLMs[tiab] OR ChatGPT[tiab] OR "GPT-4"[tiab] OR "radiology report"[tiab] '
        'OR "radiology reports"[tiab] OR "natural language processing"[tiab])'
    ),
    "foundation model / vision-language": (
        '("foundation model"[tiab] OR "foundation models"[tiab] OR "vision-language"[tiab] '
        'OR "self-supervised"[tiab] OR "segment anything"[tiab] OR pretrain*[tiab] '
        'OR "pre-trained"[tiab] OR multimodal[tiab])'
    ),
    "generative / synthesis / registration": (
        '("generative adversarial"[tiab] OR GAN[tiab] OR GANs[tiab] OR "diffusion model"[tiab] '
        'OR "diffusion models"[tiab] OR "image synthesis"[tiab] OR "image-to-image"[tiab] '
        "OR registration[tiab])"
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

# Short one-line meaning of each task label, shown next to the task figures.
TASK_GLOSS: dict[str, str] = {
    "classification / detection": "is a finding present, and where (label or box)",
    "segmentation / quantification": "outline / measure a structure or lesion",
    "prognosis / outcome prediction": "predict risk, response, or survival from images",
    "reconstruction / image enhancement": "better images from less dose or shorter scans",
    "report generation / LLM": "draft, summarize, or extract from report text",
    "foundation model / vision-language": "large pretrained models reused across tasks",
    "generative / synthesis / registration": "make or align images (GAN, diffusion)",
    "agent / autonomous": "multi-step actions taken without a human in the loop",
    "workflow / non-interpretive": "protocoling, scheduling, ordering, education",
}

# --------------------------------------------------------------------------- #
# Query validation (is the radiology-AI query sufficient?)
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
    r"p(a)?ediatric", r"child", r"infant", r"neonat", r"newborn", r"adolescen",
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
]
