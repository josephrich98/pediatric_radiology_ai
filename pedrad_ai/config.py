"""Central configuration: search vocabularies, year ranges, and output paths.

Editing the query strings here changes what every collector pulls, so this is
the single place to tune scope. Queries are intentionally broad-then-narrow:
``RADIOLOGY_AI`` captures the field, ``PEDIATRIC_RADIOLOGY_AI`` is the subset we
care about, and the modality/topic breakdowns let the reports say *where* inside
radiology AI the activity sits.
"""

from __future__ import annotations

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
END_YEAR = 2025  # inclusive; collectors clamp to the current year if earlier

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
_RADIOLOGY_TERMS = (
    '(radiology OR radiological OR radiograph* OR "medical imaging" OR '
    'tomography OR "magnetic resonance" OR MRI OR "computed tomography" OR CT OR '
    'ultrasound OR mammograph* OR "chest x-ray" OR radiograph)'
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
MODALITY_TERMS: dict[str, str] = {
    "x-ray / radiography": '(radiograph* OR "x-ray" OR "chest x-ray")',
    "CT": '("computed tomography" OR "CT scan")',
    "MRI": '("magnetic resonance" OR MRI)',
    "ultrasound": "(ultrasound OR sonograph* OR echocardiograph*)",
    "mammography": "(mammograph* OR breast imaging)",
    "nuclear / PET": '("positron emission" OR PET OR scintigraph* OR "nuclear medicine")',
}

# Clinical-task breakdown inside radiology AI.
TASK_TERMS: dict[str, str] = {
    "detection / screening": "(detection OR screening OR "
    'triage OR "computer-aided detection")',
    "segmentation": "(segmentation OR contouring OR delineation)",
    "classification / diagnosis": "(classification OR diagnosis OR "
    "diagnostic OR characterization)",
    "image reconstruction / denoising": '("image reconstruction" OR '
    "denoising OR \"dose reduction\" OR super-resolution)",
    "report generation": '("report generation" OR "natural language '
    'generation" OR "large language model" OR "structured reporting")',
    "prognosis / outcome": "(prognosis OR prognostic OR "
    'outcome OR "risk prediction" OR survival)',
}

# --------------------------------------------------------------------------- #
# Conference venues (for the "fraction of conference papers" analyses)
# --------------------------------------------------------------------------- #
# DBLP venue stream keys and OpenReview venue ids are looked up by the
# conference collector. RSNA does not publish a clean machine-readable program,
# so we approximate its AI fraction through PubMed-indexed Radiology/RadioGraphics
# articles plus the RSNA abstract archive where available.
NEURIPS_OPENREVIEW_PREFIX = "NeurIPS.cc"  # e.g. NeurIPS.cc/2023/Conference
DBLP_VENUES: dict[str, str] = {
    "NeurIPS": "conf/nips",
    "MICCAI": "conf/miccai",
    "CVPR": "conf/cvpr",
    "ICCV": "conf/iccv",
    "ISBI": "conf/isbi",  # IEEE Int. Symp. Biomedical Imaging
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
