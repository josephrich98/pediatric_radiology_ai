"""Hand-curated context for the landscape slides.

The collectors say *which* papers, tools and products are big; this module
says, in one clinical sentence each, *what question they answer* and why a
radiologist should know them. Keyed by DOI / repository name so the text
follows the data when rankings change; anything unmapped falls back to a
heuristic built from the title (see :func:`question_for`).
"""

from __future__ import annotations

import re

# DOI -> (topic tag, clinical question answered). Topic tags are short so they
# can be plotted; questions are written for clinical leadership.
PAPER_QUESTIONS: dict[str, tuple[str, str]] = {
    # --- radiology AI overall -------------------------------------------------
    "10.1016/j.media.2017.07.005": ("survey", "What can deep learning do across medical imaging? (the field's reference survey)"),
    "10.1038/s41592-020-01008-z": ("segmentation", "Can one self-configuring method segment any organ or lesion without hand tuning? (nnU-Net)"),
    "10.1158/0008-5472.can-17-0339": ("radiomics", "Can standardized image features (radiomics) be extracted reproducibly? (PyRadiomics)"),
    "10.1146/annurev-bioeng-071516-044442": ("survey", "How does deep learning apply to medical image analysis? (review)"),
    "10.1016/j.cell.2018.02.010": ("classification", "Can transfer learning diagnose pediatric pneumonia on chest X-ray and retinal disease on OCT?"),
    "10.1007/s13244-018-0639-9": ("tutorial", "What is a convolutional neural network, explained for radiologists?"),
    "10.1038/s41568-018-0016-5": ("review", "How will AI change radiology practice? (Hosny et al.)"),
    "10.1038/s41598-020-76550-z": ("classification", "Can a CNN detect COVID-19 on chest X-ray? (COVID-Net)"),
    "10.1609/aaai.v33i01.3301590": ("dataset", "A 224k chest-radiograph dataset with uncertainty labels for training and benchmarking (CheXpert)"),
    "10.1007/s13246-020-00865-4": ("classification", "Can transfer learning detect COVID-19 on X-ray with small data?"),
    "10.1109/tnnls.2020.3027314": ("explainability", "How can AI decisions in medicine be made explainable?"),
    "10.1109/tmi.2018.2837502": ("segmentation", "Is automatic cardiac MRI segmentation solved? (ACDC challenge)"),
    "10.1016/j.neunet.2019.08.025": ("segmentation", "Architecture variant of U-Net for multimodal segmentation"),
    "10.1109/tmi.2019.2903562": ("segmentation", "Architecture variant for 2D medical image segmentation (CE-Net)"),
    "10.1038/s41591-019-0447-x": ("screening", "Can AI read low-dose CT for lung-cancer screening as well as radiologists? (Google)"),
    "10.1016/j.zemedi.2018.11.002": ("review", "Deep learning in MRI: acquisition to interpretation (overview)"),
    "10.1016/j.neucom.2018.09.013": ("synthesis", "Can GAN-generated synthetic lesions improve training with scarce data?"),
    "10.1109/access.2020.3010287": ("classification", "Can AI screen viral vs COVID-19 pneumonia on X-ray?"),
    "10.1109/access.2021.3086020": ("survey", "U-Net and its variants: a review"),
    "10.1109/tmi.2017.2715284": ("reconstruction", "Can a CNN denoise low-dose CT to standard-dose quality? (RED-CNN)"),
    "10.1002/mrm.26977": ("reconstruction", "Can a learned reconstruction accelerate MRI 4x without losing diagnostic quality?"),
    "10.1148/rg.2017160130": ("tutorial", "Machine learning for medical imaging: a primer for radiologists"),
    "10.1109/tmi.2018.2827462": ("reconstruction", "Can a GAN denoise low-dose CT while keeping texture natural?"),
    "10.1007/s10278-019-00227-x": ("survey", "Segmentation methods: achievements and challenges (review)"),
    "10.1371/journal.pmed.1002683": ("generalization", "Does a pneumonia model trained at one hospital work at another? (often not)"),
    "10.1109/access.2017.2788044": ("survey", "Deep learning applications in medical image analysis (review)"),
    "10.1371/journal.pmed.1002686": ("classification", "Can an algorithm match radiologists on 14 chest-radiograph findings? (CheXNeXt)"),
    "10.1148/ryai.230024": ("segmentation", "Can one open tool segment 100+ anatomic structures on any CT? (TotalSegmentator)"),
    "10.1038/s41746-020-00376-2": ("review", "Where does medical computer vision stand? (review)"),
    "10.1016/j.cmpb.2020.105581": ("classification", "Can a CNN diagnose COVID-19 on chest X-ray? (CoroNet)"),
    "10.1038/s41586-019-1799-6": ("screening", "Can AI reduce false positives and negatives in mammography screening? (Google/DeepMind)"),
    "10.1016/S0140-6736(18)31645-3": ("triage", "Can AI flag critical findings on non-contrast head CT? (Qure.ai)"),
    "10.1038/s41591-018-0147-y": ("triage", "Does AI triage of head CT shorten time to diagnosis of hemorrhage?"),
    "10.1148/ryai.2020200029": ("reporting", "How should an AI imaging study be reported? (CLAIM checklist)"),
    "10.1038/s41467-024-44824-z": ("foundation", "Can a prompt-based 'segment anything' model work on medical images? (MedSAM)"),
    # --- pediatric ----------------------------------------------------------
    "10.1148/radiol.2018180736": ("bone age", "How well can crowdsourced AI estimate bone age? (RSNA challenge, 260 teams)"),
    "10.1148/radiol.2017170236": ("bone age", "Can a CNN assess skeletal maturity as accurately as radiologists?"),
    "10.1007/s10278-017-9955-8": ("bone age", "Fully automated bone age from hand radiographs"),
    "10.1016/j.media.2016.10.010": ("bone age", "Deep learning for automated bone age (BoNet)"),
    "10.1148/radiol.2020202317": ("reconstruction", "Can deep-learning reconstruction cut pediatric CT dose while improving image quality?"),
    "10.2214/ajr.17.18224": ("bone age", "Is a commercial deep-learning bone-age program accurate and faster in practice?"),
    "10.1109/jbhi.2018.2876916": ("bone age", "Regression CNN for pediatric bone age"),
    "10.1007/s00256-018-3033-2": ("bone age", "Does AI assistance make radiologists' bone-age reads more accurate and consistent?"),
    "10.3389/fnins.2018.01005": ("reconstruction", "Can deep learning replace CT for PET/MRI attenuation correction in children?"),
    "10.1097/rli.0000000000000615": ("fracture", "Can a CNN detect supracondylar fractures on pediatric elbow radiographs?"),
    "10.1148/rg.2021210105": ("reconstruction", "Deep-learning reconstruction for lower-dose pediatric CT: how it works and what to expect"),
    "10.1007/s10278-018-0053-3": ("bone age", "Machine-assisted bone age labeling (MABAL)"),
    "10.1016/j.artmed.2019.04.005": ("bone age", "Region detection plus classification for bone age"),
    "10.3390/diagnostics10100781": ("bone age", "Bone age assessment with deep learning: survey and open challenges"),
    "10.1016/j.future.2019.10.032": ("bone age", "Feature extraction for bone age determination"),
    "10.1109/access.2019.2903131": ("bone age", "TW3-based fully automated bone age system"),
    "10.1259/bjr.20201263": ("pneumonia", "Can transfer learning detect pneumonia on pediatric chest X-rays?"),
    "10.3174/ajnr.a6704": ("brain tumor", "Can deep learning detect and classify posterior fossa tumors on pediatric MRI across institutions?"),
    "10.1093/neuonc/noab151": ("brain tumor", "Can AI measure tumor burden automatically in pediatric high-grade glioma and medulloblastoma?"),
    "10.1109/tmi.2020.3046579": ("fetal MRI", "Can a CNN segment the fetal cortical plate on MRI?"),
    "10.3348/kjr.2020.0941": ("bone age", "Automated bone age: the future of bone age assessment (review)"),
    "10.1016/j.media.2023.102833": ("fetal MRI", "How well do algorithms segment fetal brain tissue? (FeTA challenge)"),
    "10.3171/2020.6.peds20251": ("hydrocephalus", "Can AI segment and measure cerebral ventricles automatically in children?"),
    "10.1007/s40747-021-00376-z": ("bone age", "Computer-aided bone age assessment"),
    "10.1016/j.radonc.2020.09.056": ("radiotherapy", "Can MRI-only (synthetic CT) planning work for pediatric abdominal tumors?"),
    "10.21037/cdt.2019.06.09": ("cardiac MRI", "AI in pediatric and congenital cardiac MRI: an unmet need (review)"),
    "10.2214/ajr.21.27255": ("reconstruction", "Can 80-kVp pediatric CT with DL reconstruction cut dose further?"),
    "10.1155/2020/8460493": ("bone age", "Bone age on a large-scale hand X-ray dataset"),
    "10.1007/s10278-019-00201-7": ("lines / tubes", "Can AI find catheters and tubes on pediatric X-rays?"),
    "10.3348/kjr.2021.0466": ("reconstruction", "DL reconstruction vs FBP and iterative reconstruction in pediatric CT"),
    "10.1007/s00259-020-05108-y": ("epilepsy PET", "Can deep learning read FDG-PET in pediatric temporal lobe epilepsy?"),
    "10.1007/s00330-020-07349-9": ("reconstruction", "Noise reduction in pediatric abdominal CT combining DL and dual energy"),
}

# Repository -> (what it is, why a radiologist should know it)
REPO_NOTES: dict[str, tuple[str, str]] = {
    "MIC-DKFZ/nnUNet": ("self-configuring segmentation", "the default strong baseline; wins most segmentation challenges out of the box"),
    "Project-MONAI/MONAI": ("PyTorch framework for medical imaging", "the common platform most academic and vendor research models are built on (NVIDIA-backed)"),
    "bowang-lab/MedSAM": ("'segment anything' for medical images", "click-to-segment foundation model; what interactive annotation tools are moving to"),
    "OHIF/Viewers": ("web DICOM viewer", "the open viewer behind many AI-result overlays and research PACS"),
    "wasserth/TotalSegmentator": ("whole-body CT / MR segmentation", "free organ and bone segmentation on any CT; enables opportunistic measurements"),
    "Slicer/Slicer": ("3D Slicer", "the free workstation for segmentation, registration, and trying AI models"),
    "TorchIO-project/torchio": ("3D image loading and augmentation", "plumbing library"),
    "Beckschen/TransUNet": ("transformer U-Net", "architecture paper code"),
    "HuCaoFighting/Swin-Unet": ("transformer U-Net", "architecture paper code"),
    "Tencent/MedicalNet": ("pretrained 3D backbones", "transfer learning for 3D scans"),
    "facebookresearch/fastMRI": ("accelerated MRI benchmark", "the public dataset behind learned MRI reconstruction (shorter scans, less sedation)"),
    "ellisdg/3DUnetCNN": ("3D U-Net", "early reference implementation"),
    "SimpleITK/SimpleITK": ("image IO / registration toolkit", "plumbing library"),
    "InsightSoftwareConsortium/ITK": ("image analysis toolkit", "plumbing library"),
    "mlmed/torchxrayvision": ("pretrained chest X-ray models", "ready-made CXR classifiers and datasets"),
    "MedMNIST/MedMNIST": ("benchmark datasets", "small standardized benchmarks"),
    "pydicom/pydicom": ("DICOM reading in Python", "plumbing library"),
    "microsoft/LLaVA-Med": ("vision-language model", "the biomedical multimodal chat model line"),
    "chaoyi-wu/RadFM": ("radiology foundation model", "generalist radiology model trained on 16M scans"),
    "bowang-lab/MedRAX": ("chest X-ray reasoning agent", "an LLM agent that calls imaging tools; what 'agent' means in radiology"),
    "rajpurkarlab/CheXzero": ("zero-shot CXR classification", "labels findings without labelled training data"),
    "cornerstonejs/cornerstone3D": ("web imaging rendering", "plumbing for browser viewers"),
    "Project-MONAI/MONAILabel": ("interactive labeling server", "AI-assisted annotation inside 3D Slicer / OHIF"),
    "black0017/MedicalZooPytorch": ("3D segmentation zoo", "reference implementations"),
    "MrGiovanni/ModelsGenesis": ("self-supervised pretraining", "learn from unlabeled scans"),
    "microsoft/InnerEye-DeepLearning": ("Azure segmentation toolkit", "cloud training (archived)"),
    "JJGO/UniverSeg": ("universal segmentation", "in-context segmentation model"),
    "uni-medical/SAM-Med3D": ("3D segment-anything", "volumetric prompt segmentation"),
    "ANTsX/ANTs": ("registration toolkit", "brain MRI registration standard"),
}

# The short list for the "worth knowing" slide: (name, kind, why)
WORTH_KNOWING: list[tuple[str, str, str]] = [
    ("TotalSegmentator", "open tool", "free, one-command segmentation of 100+ structures on any CT (and MR); the basis for opportunistic measurements (bone density, muscle, organ volumes)"),
    ("nnU-Net", "open tool", "if a vendor claims a segmentation result, this is the baseline they had to beat"),
    ("MONAI", "open framework", "what your data scientists will build with; knowing the name lets you read a methods section"),
    ("RSNA Pediatric Bone Age Challenge (2017)", "paper / dataset", "the one pediatric task with a public benchmark, many models, and cleared products (BoneXpert, Rho)"),
    ("Zech et al. 2018 (PLoS Med)", "paper", "the cleanest demonstration that a model can learn the hospital instead of the disease; the reason to demand local validation"),
    ("CLAIM checklist (Radiology: AI 2020)", "guideline", "how to tell a well-reported AI study from a weak one"),
    ("Brady et al. 2021 (Radiology)", "paper", "deep-learning CT reconstruction lowers pediatric dose with better image quality; the most immediately usable pediatric benefit"),
    ("FDA AI-enabled device list", "registry", "the authoritative list of what is cleared; check the indication's age range before buying"),
    ("Gleamer BoneView / AZmed Rayvolve", "products", "the first fracture-detection tools with pediatric indications; realistic first pediatric AI purchases"),
    ("MedSAM / segment-anything models", "foundation models", "where annotation and segmentation tooling is heading: click, don't draw"),
]


_TOPIC_RULES = [
    (r"bone age|skeletal matur", "bone age"), (r"fractur", "fracture"), (r"pneumonia|covid", "pneumonia / COVID"),
    (r"segment", "segmentation"), (r"reconstruct|denois|low-dose|dose|noise", "reconstruction"),
    (r"radiomic", "radiomics"), (r"survey|review|overview", "survey / review"), (r"tumou?r|glioma|cancer", "oncology"),
    (r"fetal|foetal", "fetal MRI"), (r"screening", "screening"), (r"triage", "triage"), (r"detect", "detection"),
    (r"classif|diagnos", "classification"), (r"language model|gpt|report", "LLM / reports"),
]


def question_for(paper: dict) -> tuple[str, str]:
    """Curated (topic, question) for a paper, else a heuristic from its title."""
    doi = (paper.get("doi") or "").lower()
    for k, v in PAPER_QUESTIONS.items():
        if k.lower() == doi:
            return v
    title = paper.get("title") or ""
    topic = "other"
    for rx, lab in _TOPIC_RULES:
        if re.search(rx, title, re.I):
            topic = lab
            break
    return topic, title


def repo_note(full_name: str, description: str) -> tuple[str, str]:
    if full_name in REPO_NOTES:
        return REPO_NOTES[full_name]
    return ("", (description or "").strip())
