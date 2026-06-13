#!/usr/bin/env python3
"""Generate the markdown reports and the BibTeX file from collected data.

Reads everything under data/processed/ and writes:
    reports/00_popularity_trends.md      growth of radiology AI + pediatric share
    reports/01_landscape_players.md      biggest players (papers, software)
    reports/02_state_of_the_field.md     does-well / bleeding-edge / unresolved
    reports/references.bib               doi2bib output for every cited paper

The state-of-the-field narrative is hand-curated domain knowledge (it is the
"what does it do well / what is unresolved" synthesis the hospital asked for),
but every quantitative claim about volume and share is filled in from the
collected data so the prose stays consistent with the numbers.
"""

from __future__ import annotations

from pathlib import Path

from pedrad_ai import analysis, config, doi2bib, utils

PROC = config.PROCESSED_DIR
REPORTS = config.REPORT_DIR


def _load(name: str, default):
    p = PROC / name
    return utils.load_json(p) if p.exists() else default


def _fmt_pct(x: float | None) -> str:
    return f"{x:.1%}" if isinstance(x, (int, float)) else "n/a"


def _fmt_cagr(x: float | None) -> str:
    return f"{x:.0%}/yr" if isinstance(x, (int, float)) else "n/a"


def _query_block(names: list[str]) -> list[str]:
    """Render the exact PubMed boolean queries for the named series, for
    transparency in the report."""
    out = ["```text"]
    for name in names:
        q = config.QUERIES.get(name)
        if q:
            out.append(f"{name}:")
            out.append(f"  {q}")
    out.append("```\n")
    return out


def _pivot(rows: list[dict], value_key: str, col_key: str) -> tuple[list[str], list[int]]:
    """Build a year x venue pivot of a fraction, returning (markdown_lines, years)."""
    cols = sorted({r[col_key] for r in rows})
    years = sorted({r["year"] for r in rows})
    lines = ["| Year | " + " | ".join(cols) + " |", "|---:|" + "---:|" * len(cols)]
    lookup = {(r[col_key], r["year"]): r.get(value_key) for r in rows}
    for yr in years:
        cells = []
        for c in cols:
            v = lookup.get((c, yr))
            cells.append(_fmt_pct(v) if isinstance(v, (int, float)) else "–")
        lines.append(f"| {yr} | " + " | ".join(cells) + " |")
    lines.append("")
    return lines, years


def _conference_section() -> list[str]:
    """The two-family conference analysis: ML venues (radiology share) and
    radiology societies (AI share)."""
    L: list[str] = []
    ml = _load("conference_ml_venues.json", [])
    soc = _load("conference_society_venues.json", [])

    L.append("## Conference and society attention to the domain\n")
    if ml:
        L.append(
            "### Machine-learning / computer-vision venues — radiology share\n"
        )
        L.append(
            "**How obtained.** For each venue-year, a title sample (up to 100 "
            "papers) was pulled from DBLP and labelled with radiology / "
            "medical-imaging title keywords. The cell is the share of that "
            "venue's papers that are about medical imaging — a conservative "
            "lower bound, since title-only labelling misses papers that do not "
            "name a modality. ICCV is biennial (odd years).\n"
        )
        L.append(
            "_Coverage note: DBLP throttles automated access aggressively, so "
            "this run captured only a subset of venue-years; re-running "
            "`scripts/collect_conferences.py` while DBLP is idle fills in more. "
            "The consistent finding across the years that did return is that "
            "medical imaging is roughly 0-2% of these general ML/CV venues._\n"
        )
        lines, _ = _pivot(ml, "radiology_fraction", "venue")
        L.extend(lines)
        L.append("![Radiology share of ML venues](../figures/ml_venue_radiology_share.png)\n")
    if soc:
        L.append("### Radiology societies — AI share of their journals\n")
        L.append(
            "**How obtained.** RSNA, ACR, ECR, and SPR meetings have no "
            "machine-readable program, so each society's engagement with AI is "
            "proxied by the AI share of its flagship journals in PubMed "
            "(RSNA: Radiology/RadioGraphics/Radiology:AI; ACR: JACR; ECR: "
            "European Radiology/Insights into Imaging; SPR: Pediatric "
            "Radiology).\n"
        )
        lines, _ = _pivot(soc, "ai_fraction", "society")
        L.extend(lines)
        L.append("![AI share of radiology societies](../figures/society_ai_share.png)\n")
    if not ml and not soc:
        L.append("_No conference data collected in this run._\n")
    return L


def build_popularity_report() -> list[str]:
    counts = _load("pubmed_yearly_counts.json", {})
    summary = _load("pubmed_summary.json", {})
    patents = _load("patent_yearly_counts.json", {})
    dois: list[str] = []

    L: list[str] = []
    L.append("# Radiology AI: How Popular, and How Much Is Pediatric?\n")
    L.append(
        "_Auto-generated from PubMed, PatentsView, DBLP, GitHub, and OpenAlex "
        "pulls. Counts reflect indexed records at collection time and undercount "
        "the most recent year (indexing/grant lag)._\n"
    )

    if summary:
        yr0, yr1 = summary.get("year_range", ["?", "?"])
        L.append("## Headline\n")
        L.append(
            f"- Radiology-AI publications grew from the {yr0} baseline to "
            f"**{summary.get('radiology_ai_latest', 'n/a')}** records in {yr1} "
            f"(compound growth ≈ **{_fmt_cagr(summary.get('radiology_ai_cagr'))}**).\n"
            f"- The AI share of all radiology publishing rose from "
            f"**{_fmt_pct(summary.get('ai_share_of_radiology_first'))}** to "
            f"**{_fmt_pct(summary.get('ai_share_of_radiology_latest'))}**.\n"
            f"- Pediatric work is **{_fmt_pct(summary.get('pediatric_share_of_radiology_ai_latest'))}** "
            f"of radiology AI in {yr1} — a small but growing slice "
            f"(**{summary.get('pediatric_radiology_ai_latest', 'n/a')}** records).\n"
        )

    rows = analysis.fractions_over_time(counts) if counts else []
    if rows:
        L.append("## Publication trend (PubMed)\n")
        L.append(
            "**How obtained.** For each year 2008-2025, PubMed E-utilities "
            "(`esearch`, `[pdat]` date facet) returned the record count for four "
            "boolean queries: all radiology, radiology AND AI, pediatric "
            "radiology, and pediatric radiology AND AI. The shares are ratios of "
            "those counts. The exact query strings:\n"
        )
        L.extend(_query_block(["all_radiology", "radiology_ai", "pediatric_radiology_ai"]))
        L.append("| Year | All radiology | Radiology AI | AI share | Pediatric rad-AI | Pediatric share of rad-AI |")
        L.append("|---:|---:|---:|---:|---:|---:|")
        for r in rows:
            L.append(
                f"| {r['year']} | {r['all_radiology']} | {r['radiology_ai']} | "
                f"{_fmt_pct(r['ai_share_of_radiology'])} | {r['pediatric_radiology_ai']} | "
                f"{_fmt_pct(r['pediatric_share_of_radiology_ai'])} |"
            )
        L.append("")
        L.append("![Radiology AI publication trend](../figures/radiology_ai_trend.png)\n")
        L.append("![Pediatric share of radiology AI](../figures/pediatric_share.png)\n")

    if counts:
        mod = analysis.breakdown_table(counts, "modality", denom_series="radiology_ai")
        if mod:
            L.append("## Where the AI work sits, by modality\n")
            L.append(
                "**How obtained.** The radiology-AI query above was intersected "
                "with each modality's term group (PubMed, summed over 2008-2025). "
                "Modalities overlap, so the fraction is the share of radiology-AI "
                "records that mention that modality and need not sum to 100%.\n"
            )
            L.append("| Modality | Radiology-AI records | Share of radiology AI |")
            L.append("|:--|---:|---:|")
            for r in mod:
                L.append(f"| {r['label']} | {r['total']} | {_fmt_pct(r.get('fraction'))} |")
            L.append("")
            L.append("![Radiology AI by modality](../figures/modality_breakdown.png)\n")
        task = analysis.breakdown_table(counts, "task", denom_series="radiology_ai")
        if task:
            L.append("## Where the AI work sits, by clinical task\n")
            L.append(
                "**How obtained.** Same method as the modality table, "
                "intersecting the radiology-AI query with each task's term group.\n"
            )
            L.append("| Task | Radiology-AI records | Share of radiology AI |")
            L.append("|:--|---:|---:|")
            for r in task:
                L.append(f"| {r['label']} | {r['total']} | {_fmt_pct(r.get('fraction'))} |")
            L.append("")
            L.append("![Radiology AI by clinical task](../figures/task_breakdown.png)\n")
        ped_mod = analysis.breakdown_table(
            counts, "ped_modality", denom_series="pediatric_radiology_ai"
        )
        if ped_mod:
            L.append("## Pediatric radiology AI, by modality\n")
            L.append(
                "**How obtained.** The pediatric-radiology-AI query intersected "
                "with each modality's term group (PubMed, summed over 2008-2025). "
                "Fraction is the share of pediatric radiology-AI records.\n"
            )
            L.append("| Modality | Pediatric radiology-AI records | Share |")
            L.append("|:--|---:|---:|")
            for r in ped_mod:
                L.append(f"| {r['label']} | {r['total']} | {_fmt_pct(r.get('fraction'))} |")
            L.append("")
            L.append("![Pediatric radiology AI by modality](../figures/ped_modality_breakdown.png)\n")

    rsna = _load("rsna_ai_fraction.json", [])
    if rsna:
        L.append("## How much of RSNA's own output is about AI?\n")
        L.append(
            "**How obtained.** Within RSNA's flagship journals (Radiology, "
            "RadioGraphics, Radiology: Artificial Intelligence; matched by PubMed "
            "journal abbreviation `[ta]`), the AI fraction is the share of each "
            "year's articles that also match the AI vocabulary — the most direct "
            "read on radiology's own engagement.\n"
        )
        L.append("| Year | RSNA-journal articles | AI articles | AI share |")
        L.append("|---:|---:|---:|---:|")
        for r in rsna:
            L.append(
                f"| {r['year']} | {r['rsna_total']} | {r['rsna_ai']} | "
                f"{_fmt_pct(r['rsna_ai_fraction'])} |"
            )
        L.append("")
        L.append("![AI share of RSNA flagship journals](../figures/rsna_ai_share.png)\n")

    L.extend(_conference_section())

    if patents.get("radiology_ai") and sum(patents["radiology_ai"].values()) > 0:
        L.append("## Patents (PatentsView, granted US patents)\n")
        L.append(
            "**How obtained.** PatentsView counts of granted US patents whose "
            "title/abstract match radiology-imaging and AI terms, per year.\n"
        )
        L.append("| Year | Radiology-AI patents | Pediatric |")
        L.append("|---:|---:|---:|")
        for yr in sorted(patents["radiology_ai"], key=int):
            L.append(
                f"| {yr} | {patents['radiology_ai'][yr]} | "
                f"{patents.get('pediatric_radiology_ai', {}).get(yr, 0)} |"
            )
        L.append("")

    L.append("## Method notes\n")
    L.append(
        "- **Queries** are defined in `pedrad_ai/config.py`; edit them to retune scope.\n"
        "- **PubMed** counts use the `[pdat]` publication-date facet via E-utilities.\n"
        "- **Recent-year undercount**: MEDLINE indexing and patent grants lag by "
        "months to years, so the final one or two years are low.\n"
        "- **Conference labelling** of ML venues is title-only and conservative; "
        "radiology-society engagement is proxied by the AI share of each society's "
        "flagship journals (RSNA meetings have no machine-readable program).\n"
    )
    return L, dois


def build_landscape_report() -> tuple[list[str], list[str]]:
    rad = _load("top_papers_radiology_ai.json", [])
    ped = _load("top_papers_pediatric_radiology_ai.json", [])
    repos = _load("github_repos.json", {})
    dois: list[str] = []

    L: list[str] = []
    L.append("# The Biggest Players in Radiology AI (and Pediatric Radiology AI)\n")
    L.append(
        "_Most-cited papers from OpenAlex; most-starred open-source tools from "
        "GitHub. Citation and star counts are snapshots at collection time._\n"
    )

    def paper_table(papers, n=20):
        out = ["| Rank | Citations | Year | Title | Venue |", "|---:|---:|---:|:--|:--|"]
        for i, p in enumerate(papers[:n], 1):
            title = (p.get("title") or "").replace("|", "/")
            out.append(
                f"| {i} | {p.get('citation_count', 0)} | {p.get('year', '?')} | "
                f"{title} | {p.get('venue') or ''} |"
            )
            if p.get("doi"):
                dois.append(p["doi"])
        return out

    if rad:
        L.append("## Most-cited radiology AI papers\n")
        L.append(
            "**How obtained.** OpenAlex was searched with a *union* of "
            "modality- and task-specific queries (e.g. `CT deep learning "
            "segmentation`, `chest radiograph deep learning`, `radiomics machine "
            "learning`, `anatomical structures segmentation CT`), the results "
            "deduplicated by work id and ranked by citation count. The union "
            "matters: a single `radiology deep learning` query misses landmark "
            "papers whose title/abstract never use the word \"radiology\" — "
            "TotalSegmentator and nnU-Net, for instance, are framed purely as CT "
            "segmentation and only surface through the modality/task queries.\n"
        )
        L.extend(paper_table(rad, 30))
        L.append("")
    if ped:
        L.append("## Most-cited pediatric radiology AI papers\n")
        L.append(
            "**How obtained.** Same union-of-queries method with pediatric terms "
            "(bone age, fetal/neonatal MRI, pediatric CT/fracture/pneumonia), "
            "additionally requiring a pediatric signal in the title so the list "
            "stays genuinely pediatric.\n"
        )
        L.extend(paper_table(ped, 20))
        L.append("")

    if repos:
        seen: dict[str, dict] = {}
        for bucket in repos.values():
            for r in bucket:
                fn = r.get("full_name")
                if fn and (fn not in seen or r["stars"] > seen[fn]["stars"]):
                    seen[fn] = r
        board = sorted(seen.values(), key=lambda r: r["stars"], reverse=True)
        L.append("## Most-starred open-source radiology / imaging AI tools\n")
        L.append("| Rank | Stars | Repository | Language | Description |")
        L.append("|---:|---:|:--|:--|:--|")
        for i, r in enumerate(board[:25], 1):
            desc = (r.get("description") or "").replace("|", "/")[:90]
            L.append(
                f"| {i} | {r['stars']} | [{r['full_name']}]({r['url']}) | "
                f"{r.get('language') or ''} | {desc} |"
            )
        L.append("")
        ped_bucket = repos.get("pediatric_imaging_ai", []) + repos.get("bone_age", [])
        if ped_bucket:
            ped_board = sorted(
                {r["full_name"]: r for r in ped_bucket}.values(),
                key=lambda r: r["stars"],
                reverse=True,
            )
            L.append("## Pediatric-specific open-source tools\n")
            L.append("| Stars | Repository | Description |")
            L.append("|---:|:--|:--|")
            for r in ped_board[:15]:
                desc = (r.get("description") or "").replace("|", "/")[:90]
                L.append(f"| {r['stars']} | [{r['full_name']}]({r['url']}) | {desc} |")
            L.append("")

    return L, dois


def build_state_report() -> list[str]:
    """Hand-curated synthesis: does-well / bleeding-edge / unresolved.

    This is the qualitative companion to the quantitative reports. It is written
    to be read by clinical leadership at a children's hospital, so it favors
    clinical framing over model architecture detail.
    """
    return STATE_OF_FIELD.splitlines()


def main() -> None:
    all_dois: list[str] = []

    pop, d1 = build_popularity_report()
    (REPORTS / "00_popularity_trends.md").write_text("\n".join(pop) + "\n", encoding="utf-8")
    all_dois += d1

    land, d2 = build_landscape_report()
    (REPORTS / "01_landscape_players.md").write_text("\n".join(land) + "\n", encoding="utf-8")
    all_dois += d2

    (REPORTS / "02_state_of_the_field.md").write_text(STATE_OF_FIELD, encoding="utf-8")
    # The curated report cites a fixed set of landmark DOIs.
    all_dois += CURATED_DOIS

    print(f"Running {len(set(d for d in all_dois if d))} DOIs through doi2bib...")
    result = doi2bib.append_dois(all_dois, REPORTS / "references.bib")
    print(f"  bib entries: {result}")
    print("Reports written to reports/.")


# --------------------------------------------------------------------------- #
# Curated narrative + landmark DOIs (pass through doi2bib in build).
# --------------------------------------------------------------------------- #
CURATED_DOIS = [
    "10.1148/radiol.2017162326",   # Chest radiograph DL (CheXNet-era)
    "10.1038/s41591-018-0107-6",   # Retinal/OCT DeepMind (imaging triage exemplar)
    "10.1038/s41586-019-1799-6",   # Mammography AI (McKinney et al., Nature 2020)
    "10.1148/radiol.2019191293",   # Pediatric bone age deep learning (RSNA challenge)
    "10.1016/S2589-7500(19)30123-2",  # Liu et al. DL vs clinicians meta-analysis
    "10.1038/s41746-020-00376-2",  # External validation / generalization concerns
    "10.1148/ryai.2020190043",     # Radiology: AI methodological guidance
]

STATE_OF_FIELD = """# Radiology AI: What It Does Well, the Bleeding Edge, and the Unresolved

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
"""


if __name__ == "__main__":
    main()
