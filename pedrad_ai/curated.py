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
    # --- 2023-present, per-year lists (foundation models, VLMs, agents) -------
    "10.1038/s41586-023-05881-4": ("foundation model", "What would a single generalist medical AI model that handles images, text and records look like? (perspective)"),
    "10.1038/s41467-024-44824-z": ("segmentation", "Can Segment Anything be adapted to segment any medical image with a click or box? (MedSAM)"),
    "10.1016/j.media.2023.102918": ("segmentation", "How well does the unmodified Segment Anything Model work on medical images? (it needs prompts and adaptation)"),
    "10.48550/arxiv.2303.00915": ("foundation model", "Can a vision-language model pretrained on 15 million figure-caption pairs serve as a biomedical backbone? (BiomedCLIP)"),
    "10.48550/arXiv.2307.14334": ("foundation model", "Can one model answer questions across radiology, pathology, genomics and text? (Med-PaLM M)"),
    "10.3390/diagnostics13172760": ("survey / review", "Where does AI fit in radiology workflow, from acquisition to reporting? (review)"),
    "10.1145/3767748": ("segmentation", "Does a state-space (Mamba) backbone beat convolutions and transformers for medical segmentation?"),
    "10.48550/arXiv.2401.03495": ("segmentation", "How has Segment Anything been used in medical imaging so far? (review)"),
    "10.1148/radiol.232756": ("report generation / LLM", "How should radiologists use chatbots and LLMs safely in clinical and research work? (primer)"),
    "10.3389/frai.2024.1430984": ("report generation / LLM", "What can vision-language models do for report generation and visual question answering? (review)"),
    "10.1186/s13244-023-01572-w": ("radiomics", "How should the quality of a radiomics study be scored? (METRICS checklist)"),
    "10.1109/CVPR52733.2024.02093": ("foundation model", "How good are large vision-language models at medical visual questions across modalities? (benchmark)"),
    "10.1109/ISBI60581.2025.10981134": ("segmentation", "Does encoding anatomy into Segment Anything improve medical segmentation? (ASAM)"),
    "10.1038/s41467-025-62385-7": ("foundation model", "Can a radiology foundation model trained on web-scale 2D and 3D scans generalize across modalities and tasks? (RadFM)"),
    "10.48550/arXiv.2506.07044": ("foundation model", "Can one open multimodal model handle medical understanding and reasoning across image types? (Lingshu)"),
    "10.48550/arXiv.2502.19634": ("foundation model", "Does reinforcement learning make a medical vision-language model reason more reliably? (MedVLM-R1)"),
    "10.1038/s43018-025-00991-6": ("agent / autonomous", "Can an autonomous LLM agent that calls imaging and other tools support oncology decisions? (validation study)"),
    "10.1148/ryai.250651": ("agent / autonomous", "What are agentic AI systems in radiology and what stands between them and clinical use? (review)"),
    "10.48550/arXiv.2601.10880": ("segmentation", "Can a Segment Anything 3 foundation model segment any medical image from a text or visual prompt?"),
    "10.1016/j.dcn.2026.101706": ("segmentation", "Can one network segment infant brain MRI across the first years of life? (BIBSNet)"),
    "10.1038/s41591-025-04184-7": ("foundation model", "How can medical AI be scaled across hospitals, populations and tasks without breaking? (perspective)"),
    "10.1016/j.landig.2025.100960": ("report generation / LLM", "Can LLMs make radiology reports understandable to patients? (meta-analysis)"),
    "10.1186/s12880-025-02118-w": ("survey / review", "Which explainability methods are used in medical imaging AI and do they help? (review)"),
    # --- pediatric, 2023-present -------------------------------------------
    "10.1016/j.eswa.2023.122153": ("fetal ultrasound", "Can an ensemble of networks classify the standard fetal ultrasound planes?"),
    "10.1101/2023.04.18.537347": ("fetal MRI", "Can fetal brain volumes and parcellation be automated on 3D reconstructed fetal MRI? (BOUNTI)"),
    "10.1093/noajnl/vdad027": ("oncology", "Can pediatric brain tumors be segmented automatically on multiparametric MRI across institutions?"),
    "10.1002/uog.27503": ("fetal ultrasound", "Does a prenatal congenital heart disease screening model work on retrospective real-world scans?"),
    "10.1016/j.dib.2023.109708": ("fetal ultrasound", "Is there a large annotated dataset for fetal head biometry on ultrasound? (dataset)"),
    "10.1186/s13244-024-01635-6": ("epilepsy", "Can focal cortical dysplasia lesions be found automatically on preoperative pediatric MRI?"),
    "10.1148/ryai.230240": ("bone age", "How robust is the RSNA-winning bone age model to rotations, contrast and marker changes? (stress test)"),
    "10.1016/j.ejrad.2024.111637": ("fracture", "How accurate is a commercial fracture AI on pediatric appendicular radiographs?"),
    "10.3389/fcvm.2024.1323443": ("reconstruction", "Does deep-learning denoising improve fetal cardiac cine MRI?"),
    "10.1007/s00330-025-11554-9": ("fracture", "Does AI fracture detection help residents in a real pediatric emergency department?"),
    "10.1007/s00247-025-06386-0": ("policy", "What do the pediatric radiology societies require for safe AI implementation? (multi-society statement)"),
    "10.1038/s41598-025-86536-4": ("fetal ultrasound", "Does explainable AI for fetal growth scans hold up across institutions and operator levels?"),
    "10.1136/bmjopen-2025-101263": ("fetal ultrasound", "Can deep learning on prenatal ultrasound video detect congenital heart defects?"),
    "10.1038/s41746-025-01704-0": ("fetal ultrasound", "Can deep learning predict abnormal fetal growth from routine scans?"),
    "10.1007/s00234-026-03976-z": ("oncology", "Can AI and radiomics classify pediatric brain tumors and their molecular subtypes? (review)"),
    "10.1002/uog.70168": ("fetal ultrasound", "Can deep learning grade fetal brain maturation on 3D ultrasound in growth restriction?"),
    "10.1007/s00247-026-06544-y": ("foundation model", "What should a pediatric radiologist know about foundation models? (primer)"),
    "10.1007/s00247-025-06504-y": ("policy", "How can AI serve pediatric radiology where radiologists and scanners are scarce?"),
    "10.3389/fendo.2026.1741927": ("bone age", "Does an open bone-age model hold up in rare growth disorders against several experts? (Deeplasia)"),
    "10.1186/s40658-026-00876-2": ("reconstruction", "Can pediatric PET use one fifth of the counts with patch-based deep-learning denoising?"),
    "10.1016/j.ejrad.2026.112703": ("reconstruction", "Does low-dose thin-slice deep-learning reconstruction match standard-dose pediatric CT?"),
    "10.1016/j.ejrad.2026.112799": ("reconstruction", "Can deep-learning reconstruction lower pediatric chest CT dose while improving image quality?"),
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
    ("\"Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs\" (Zech et al., PLoS Med 2018)", "paper", "the cleanest demonstration that a model can learn the hospital instead of the disease; the reason to demand local validation"),
    ("CLAIM checklist (Radiology: AI 2020)", "guideline", "how to tell a well-reported AI study from a weak one"),
    ("\"Improving Image Quality and Reducing Radiation Dose for Pediatric CT by Using Deep Learning Reconstruction\" (Brady et al., Radiology 2021)", "paper", "the most-cited non-bone-age pediatric paper: deep-learning reconstruction lowers pediatric CT dose with better image quality; the most immediately usable pediatric benefit"),
    ("FDA AI-enabled device list", "registry", "the authoritative list of what is cleared; check the indication's age range before buying"),
    ("Gleamer BoneView / AZmed Rayvolve", "products", "the first fracture-detection tools with pediatric indications; realistic first pediatric AI purchases"),
    ("MedSAM / segment-anything models", "foundation models", "where annotation and segmentation tooling is heading: click, don't draw"),
]


# One slide per paper: image slug (config.EXAMPLE_IMAGES, group "spotlight"),
# short title, reference line, and the bullets (problem, data, method, result,
# why it matters). Numbers are taken from the papers' abstracts.
PAPER_SPOTLIGHTS: list[dict[str, object]] = [
    # One slide each; 2025-2026 papers, chosen from the per-year most-cited
    # pediatric lists for open-access figures and clinical relevance.
    {
        "slug": "spot_fracture_ed",
        "title": "AI fracture detection in a real pediatric emergency department",
        "ref": "Ziegner et al., European Radiology 2025 (second most-cited pediatric paper of 2025)",
        "doi": "10.1007/s00330-025-11554-9",
        "bullets": [
            ("Problem", "fractures in children are missed most often by the least experienced readers, at night, in the emergency department."),
            ("Data", "1,672 consecutive radiographs of children under 18 from one tertiary pediatric emergency department, plus a selected medicolegal set (proximal tibia, radial condyle); three pediatric residents read each before and after seeing the AI."),
            ("Method", "a commercially available, CE-marked deep-learning fracture detector (adult-derived, pediatric extension) run stand-alone and as a second reader."),
            ("Result", "stand-alone sensitivity 92%, specificity 83%; 100% for proximal tibia but 68% for radial condyle fractures; residents' accuracy rose from 88% to 90%, and in 2% of cases they dropped a correct diagnosis after seeing the AI."),
            ("Why it matters", "the first real-life pediatric ED evaluation: the gain from a cleared adult tool is real but modest, and the elbow remains the weak spot."),
        ],
    },
    {
        "slug": "spot_ped_tb",
        "title": "pTBLightNet: pediatric tuberculosis on frontal and lateral chest radiographs",
        "ref": "Capellán-Martín et al., Nature Communications 2025 (open access)",
        "doi": "10.1038/s41467-025-64391-1",
        "bullets": [
            ("Problem", "pediatric pulmonary TB has vaguer symptoms and subtler radiographs than adult TB; most affected children in high-burden settings are never diagnosed."),
            ("Data", "pre-trained on 114,173 adult chest radiographs, then fine-tuned and tested on 918 radiographs from three pediatric TB cohorts, with lateral views."),
            ("Method", "a multi-view network that scores frontal and lateral films for TB-compatible findings; separate models for under-5 and 5-18 years."),
            ("Result", "AUC 0.90 on internal and 0.68 on external testing; lateral views helped most in the youngest children; age-specific models matched larger undifferentiated ones."),
            ("Why it matters", "shows both the value of adult pre-training for a rare pediatric target and the internal-to-external drop that every pediatric deployment should expect."),
        ],
    },
    {
        "slug": "spot_dl_recon_mri",
        "title": "Deep-learning reconstruction shortens pediatric brain MRI",
        "ref": "Yoo et al., Korean Journal of Radiology 2025 (open access)",
        "doi": "10.3348/kjr.2024.0701",
        "bullets": [
            ("Problem", "long 3D T1 sequences are where children move, sedation is prescribed, and scanner time is lost."),
            ("Data", "46 children scanned with both the conventional and an accelerated 3D T1 protocol (pre- and post-contrast) on one 3T scanner."),
            ("Method", "vendor deep-learning reconstruction applied to the accelerated acquisition; noise, contrast, signal-to-noise and radiologist ratings compared with the conventional scan."),
            ("Result", "acquisition time cut by 29% (pre-contrast) and 41% (post-contrast); the deep-learning images had lower noise, higher SNR and CNR, better overall quality and fewer artifacts than the conventional scan."),
            ("Why it matters", "reconstruction AI is on the scanner today and gives children a shorter, better exam without any diagnostic model in the loop."),
        ],
    },
    {
        "slug": "spot_deeplasia_rare",
        "title": "Deeplasia bone age in rare growth disorders, against multiple experts",
        "ref": "Skaf et al., Frontiers in Endocrinology 2026 (open access); external validation of Rassmann et al., Pediatr Radiol 2023",
        "doi": "10.3389/fendo.2026.1741927",
        "bullets": [
            ("Problem", "bone-age models are trained on ordinary hands; the children who need bone age most have syndromes, endocrine disease or lysosomal storage disorders that distort the skeleton."),
            ("Data", "1,138 hand radiographs from several centers: SHOX deficiency, Noonan, Silver-Russell, Turner, CAH, precocious puberty (cohort 1) and mucopolysaccharidoses and other storage disorders (cohort 2); two to five expert Greulich-Pyle readings each."),
            ("Method", "the open-source Deeplasia system run unchanged; each human rater and the model scored against the remaining experts."),
            ("Result", "mean absolute error 6.0 months (cohort 1) and 7.1 months (storage disorders), 1-year accuracy 90% and 81%; the model beat every individual human rater."),
            ("Why it matters", "an open pediatric model validated on the hardest cases, by an outside group, on external data: the template for how a children's hospital should test any tool."),
        ],
    },
    {
        "slug": "spot_pet_dose",
        "title": "Pediatric PET at one fifth of the counts with patch-based deep learning",
        "ref": "Han et al., EJNMMI Physics 2026 (open access; Cincinnati Children's)",
        "doi": "10.1186/s40658-026-00876-2",
        "bullets": [
            ("Problem", "PET dose and scan time in children are set by noise; conventional denoising networks need large training sets that pediatric PET does not have."),
            ("Data", "one high-quality pediatric exam for training; a NEMA phantom and 88 clinical whole-body FDG exams (under 12 years) with list-mode data truncated from 90 s to 20 s per bed."),
            ("Method", "a patch-based network that learns local structure from a single exam and denoises the reduced-count images; blinded observer study and SUV analysis."),
            ("Result", "20-second images rated equal or better than the standard 90-second images in more than 85% of cases, with resolution, contrast and SUV preserved."),
            ("Why it matters", "either a 4.5x shorter scan or about 22% of today's injected activity, from a method trainable on a single local exam."),
        ],
    },
    {
        "slug": "spot_not_small_adults",
        "title": "Children are not small adults: an adult CT segmentation model in children",
        "ref": "Chatterjee et al., Journal of Imaging Informatics in Medicine 2025",
        "doi": "10.1007/s10278-024-01273-w",
        "bullets": [
            ("Problem", "the most-used open CT organ segmentation model (TotalSegmentator) was trained on adults; nobody had measured how it behaves in children."),
            ("Data", "external adult (n = 300) and pediatric (n = 359) abdominal CT sets with expert organ labels."),
            ("Method", "TotalSegmentator scored on both sets; then a pediatric-only nnU-Net and an adult model fine-tuned on pediatric cases."),
            ("Result", "mean Dice fell from 0.81 in adults to 0.73 in children, worst for the adrenals (0.69 to 0.41 and 0.35), duodenum and pancreas; pediatric training or fine-tuning recovered the loss."),
            ("Why it matters", "the clearest quantitative case for local pediatric validation and fine-tuning of adult-derived tools before clinical use."),
        ],
    },
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
