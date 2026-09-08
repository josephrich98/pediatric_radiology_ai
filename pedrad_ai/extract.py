"""Structured, schema-constrained reading of one abstract by Claude.

Every other collector in this package counts records. This one *reads* them:
given a PubMed record it returns one row of the paper database (which model, on
which modality, in which children, for which clinical problem, released or
not). The schema below is a Pydantic model, and the request uses the Claude
structured-output API (``client.messages.parse`` with ``output_format=``), so
the response is either a validated :class:`PaperExtraction` or an error — never
free text that has to be scraped.

Reproducibility. An LLM is not deterministic, so the database does not re-read
a paper it has already read: :mod:`pedrad_ai.paper_db` stores every extracted
row together with the hash of the exact input the model saw
(:func:`input_fingerprint`) and the prompt/schema version, and re-extracts only
when one of those changes. A clone of the repository therefore rebuilds the
same database from the committed rows with no API calls at all, and a refresh
pays only for papers that are new.

Requires ``anthropic`` (``pip install -e ".[db]"``) and Anthropic credentials.
Without either, :func:`available` is False and the caller keeps the database it
already has instead of failing — the same degrade-gracefully rule the network
collectors follow.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal

from pydantic import BaseModel, Field

from . import config

# Bump when the field set or the instructions below change in a way that makes
# previously extracted rows non-comparable. Rows carry the version they were
# made with, and paper_db re-extracts anything older.
PROMPT_VERSION = 1

# --------------------------------------------------------------------------- #
# Schema
# --------------------------------------------------------------------------- #
# Controlled vocabularies come from config so the database groups on the same
# axes as the count-based modality / task breakdowns.
Modality = Literal[tuple(config.PAPER_DB_MODALITIES)]  # type: ignore[valid-type]
AgeGroup = Literal[tuple(config.PAPER_DB_AGE_GROUPS)]  # type: ignore[valid-type]
Task = Literal[tuple(config.PAPER_DB_TASKS)]  # type: ignore[valid-type]
ReleaseStatus = Literal[tuple(config.PAPER_DB_RELEASE_STATUS)]  # type: ignore[valid-type]
Validation = Literal[tuple(config.PAPER_DB_VALIDATION)]  # type: ignore[valid-type]
DataSource = Literal[tuple(config.PAPER_DB_DATA_SOURCE)]  # type: ignore[valid-type]


class PaperExtraction(BaseModel):
    """One row of the pediatric radiology-AI paper database.

    Every field is required. "Not stated in the abstract" is expressed as an
    empty string or an empty list, never as a guess.
    """

    is_pediatric_radiology_ai: bool = Field(
        description=(
            "True only if the paper develops, evaluates, or reviews an AI/ML model "
            "applied to diagnostic imaging (radiography, CT, MRI, ultrasound, nuclear "
            "medicine, fluoroscopy) in a population that is at least partly pediatric "
            "(fetal through adolescent). False for adult-only work, for non-imaging "
            "AI, for imaging that is not radiology (retinal photography, endoscopy, "
            "histopathology, dermoscopy, dental), and for papers where 'child' appears "
            "only incidentally."
        )
    )
    exclusion_reason: str = Field(
        description="If is_pediatric_radiology_ai is false, one short clause saying why. Otherwise an empty string."
    )
    model_name: str = Field(
        description=(
            "The name the authors give their model, system, or product (e.g. 'BoneXpert', "
            "'nnU-Net', 'PedsNet'). Empty string if the model is unnamed. Do not invent a "
            "name and do not put the architecture here."
        )
    )
    model_family: str = Field(
        description=(
            "The method in a few words as the authors describe it: e.g. '3D U-Net', "
            "'ResNet-50 transfer learning', 'random forest on radiomic features', "
            "'GPT-4', 'vision transformer'. Empty string if the abstract does not say."
        )
    )
    modality: list[Modality] = Field(
        description="Imaging modalities the model operates on. Empty list if none is named."
    )
    body_region: str = Field(
        description="Anatomy or organ system imaged, in a few words (e.g. 'hand and wrist', 'brain', 'chest')."
    )
    clinical_problem: str = Field(
        description=(
            "The clinical question in one short phrase, as a clinician would say it: "
            "'skeletal maturity assessment', 'appendicitis on ultrasound', "
            "'hydrocephalus shunt failure'. Not the ML task."
        )
    )
    patient_population: str = Field(
        description=(
            "Who the children were, in one clause: age range, disease state, and setting "
            "if stated (e.g. 'neonates under 32 weeks with suspected NEC', "
            "'children 0-18 undergoing hand radiography for endocrine referral')."
        )
    )
    age_groups: list[AgeGroup] = Field(
        description="Age bands actually covered by the study population."
    )
    task: list[Task] = Field(
        description=(
            "What the model produces, using the fixed categories. Most papers have one; "
            "list a second only when the paper genuinely does both."
        )
    )
    model_description: str = Field(
        description=(
            "Two or three plain sentences for a radiologist who has not read the paper: "
            "what goes in, what comes out, how it was trained, and what it is for. "
            "Written from the abstract only — no outside knowledge, no praise, no hedging "
            "language copied from the authors' conclusions."
        )
    )
    release_status: ReleaseStatus = Field(
        description=(
            "'open-source' if code or weights are stated to be publicly available (a "
            "repository URL, a model hub, 'code is available at ...'); 'commercial' if "
            "the model is a named vendor product, a CE-marked or FDA-cleared device, or "
            "is described as commercially available software; 'unreleased' if the "
            "abstract makes clear it is a research prototype with no release; 'unclear' "
            "if the abstract simply does not say. Most academic papers are 'unclear' — "
            "prefer it over guessing 'unreleased'."
        )
    )
    release_evidence: str = Field(
        description="The words in the abstract that justify release_status, quoted or closely paraphrased. Empty if none."
    )
    code_url: str = Field(
        description="Repository or model-hub URL if the abstract gives one, else an empty string."
    )
    dataset_size: str = Field(
        description="Study size as stated, keeping the authors' units (e.g. '1,286 radiographs from 743 children')."
    )
    data_source: DataSource = Field(description="Where the data came from.")
    validation: Validation = Field(
        description=(
            "The strongest validation the abstract claims: 'external / multi-center' for "
            "a held-out site or cohort, 'prospective' for prospectively collected "
            "evaluation, 'reader study' for comparison against radiologists, "
            "'internal only' for a split of one institution's data."
        )
    )
    headline_result: str = Field(
        description="The main quantitative result as stated, with its metric (e.g. 'AUC 0.94 vs 0.88 for residents'). Empty if none."
    )
    study_design: str = Field(
        description="A few words: 'retrospective single-center diagnostic accuracy', 'systematic review', 'technical development', 'survey'."
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="How well the abstract supported these fields. 'low' when most fields had to be left empty."
    )


# --------------------------------------------------------------------------- #
# Prompt
# --------------------------------------------------------------------------- #
# Kept as one stable string so it caches cleanly across the run: only the
# per-paper user message varies.
SYSTEM_PROMPT = """\
You are building a structured database of pediatric radiology artificial-intelligence \
papers for the clinical and research leadership of a children's hospital. You are given \
one PubMed record — title, journal, year, publication types, MeSH headings, and abstract \
— and you fill in one row of that database.

Rules, in order of importance:

1. Use only what the record says. If a field is not supported by the abstract, leave it \
empty (empty string or empty list) or choose the "not stated" / "unclear" option. Never \
infer a value from your own knowledge of the model, the vendor, or the authors, and never \
carry a value over from a paper that sounds similar.
2. Screen first. Many records match the search only incidentally — adult studies that \
mention children in a limitation, non-radiologic imaging (retina, endoscopy, pathology \
slides, dental, dermoscopy), non-imaging clinical prediction, or bibliometric pieces about \
AI rather than uses of it. Set is_pediatric_radiology_ai to false for those and give a \
short exclusion_reason; the remaining fields may then be left empty.
3. Reviews, guidelines, editorials and challenge reports stay in the database when they \
are about pediatric radiology AI. They have no model_name; describe the scope of the \
review in model_description and set study_design accordingly.
4. Write for a radiologist, not for an ML audience. clinical_problem is the clinical \
question, not the loss function. model_description says what goes in and what comes out.
5. Do not repeat the authors' promotional language. "Promising", "revolutionary" and \
"outperformed radiologists" are claims; report the number instead.
6. release_status is the column the audience cares about most, so be strict with it. A \
stated repository URL or "code is available" means open-source. A named vendor product, a \
cleared device, or software described as commercially available means commercial. Say \
unclear when the abstract is silent, which it usually is.
"""


def prompt_fingerprint() -> str:
    """Hash of the prompt + schema, so a change to either forces re-extraction."""
    blob = SYSTEM_PROMPT + json.dumps(PaperExtraction.model_json_schema(), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def input_fingerprint(article: dict[str, Any]) -> str:
    """Hash of exactly what the model is shown for ``article``.

    Used as the cache key: if PubMed later attaches an abstract or corrects a
    title, the fingerprint changes and the row is re-read; otherwise it is not.
    """
    return hashlib.sha256(_user_message(article).encode("utf-8")).hexdigest()[:16]


def _user_message(article: dict[str, Any]) -> str:
    def _join(key: str) -> str:
        vals = article.get(key) or []
        return "; ".join(str(v) for v in vals)

    return "\n".join(
        [
            f"Title: {article.get('title', '')}",
            f"Journal: {article.get('journal', '')}",
            f"Year: {article.get('year', '')}",
            f"DOI: {article.get('doi') or ''}",
            f"Authors: {_join('authors')}",
            f"Publication types: {_join('publication_types')}",
            f"MeSH headings: {_join('mesh_terms')}",
            "",
            "Abstract:",
            article.get("abstract") or "(no abstract available)",
        ]
    )


# --------------------------------------------------------------------------- #
# Client
# --------------------------------------------------------------------------- #
def available() -> tuple[bool, str]:
    """Whether extraction can run. Returns (ok, reason-if-not)."""
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False, 'anthropic not installed (pip install -e ".[db]")'
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        # The SDK also reads an `ant auth login` profile from ~/.config/anthropic,
        # so an unset key is not proof there are no credentials; let the client
        # constructor decide.
        try:
            import anthropic

            anthropic.Anthropic()
        except Exception as exc:  # pragma: no cover - depends on local auth
            return False, f"no Anthropic credentials ({exc.__class__.__name__})"
    return True, ""


def _client():
    import anthropic

    return anthropic.Anthropic(max_retries=4, timeout=180.0)


# Models that accept the server-side `fallbacks` parameter.
_SUPPORTS_FALLBACKS = re.compile(r"^claude-(opus-5|fable-5)")


def extract_one(
    article: dict[str, Any],
    *,
    client=None,
    model: str | None = None,
    effort: str | None = None,
) -> dict[str, Any]:
    """Read one article. Returns the extracted fields plus provenance.

    On failure the returned dict carries ``error`` and no fields, so one bad
    record never aborts a run.
    """
    model = model or config.PAPER_DB_MODEL
    effort = effort or config.PAPER_DB_EFFORT
    client = client or _client()

    provenance = {
        "extractor_model": model,
        "extractor_effort": effort,
        "prompt_version": PROMPT_VERSION,
        "prompt_fingerprint": prompt_fingerprint(),
        "input_fingerprint": input_fingerprint(article),
    }
    kwargs: dict[str, Any] = dict(
        model=model,
        max_tokens=4000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                # The system prompt is identical for every paper in the run;
                # caching it makes the per-paper cost the abstract only.
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": _user_message(article)}],
        output_config={"effort": effort},
        output_format=PaperExtraction,
    )
    # Server-side refusal fallback: a clinical abstract occasionally trips a
    # safety classifier (self-harm imaging, abuse radiology), and without a
    # fallback that paper would simply have no row. Only the models that accept
    # the parameter get it.
    endpoint = client.messages.parse
    if _SUPPORTS_FALLBACKS.match(model):
        endpoint = client.beta.messages.parse
        kwargs["betas"] = ["server-side-fallback-2026-07-01"]
        kwargs["fallbacks"] = "default"
    try:
        response = endpoint(**kwargs)
    except Exception as exc:
        return {**provenance, "error": f"{exc.__class__.__name__}: {exc}"}

    if response.stop_reason == "refusal":
        detail = getattr(response.stop_details, "category", None)
        return {**provenance, "error": f"refusal ({detail})"}
    parsed = response.parsed_output
    if parsed is None:
        return {**provenance, "error": "no parsed output"}

    usage = response.usage
    return {
        **parsed.model_dump(),
        **provenance,
        "usage": {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", 0) or 0,
        },
    }


def extract_many(
    articles: list[dict[str, Any]],
    *,
    model: str | None = None,
    effort: str | None = None,
    workers: int | None = None,
    on_result=None,
) -> list[dict[str, Any]]:
    """Read a batch of articles concurrently, preserving input order.

    ``on_result(index, article, extraction)`` is called as each one lands, so a
    long run can checkpoint the store instead of losing everything on an
    interrupt.
    """
    if not articles:
        return []
    workers = workers or config.PAPER_DB_WORKERS
    client = _client()
    results: list[dict[str, Any] | None] = [None] * len(articles)

    def _work(item: tuple[int, dict[str, Any]]) -> tuple[int, dict[str, Any]]:
        idx, art = item
        return idx, extract_one(art, client=client, model=model, effort=effort)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for idx, extraction in pool.map(_work, list(enumerate(articles))):
            results[idx] = extraction
            if on_result is not None:
                on_result(idx, articles[idx], extraction)
    return [r for r in results if r is not None]
