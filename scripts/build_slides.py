#!/usr/bin/env python3
"""Generate a Beamer slide deck (slides/pedrad_ai_slides.tex) from the data.

Headline numbers are pulled from data/processed/ so the slides stay consistent
with the reports. Figures are included from ../figures/. Compile with:

    cd slides && latexmk -pdf pedrad_ai_slides.tex

Run `python scripts/make_figures.py` first so the figures exist. The template
uses ``@@KEY@@`` placeholders (not str.format) because the LaTeX body is full of
literal braces.
"""

from __future__ import annotations

from pedrad_ai import analysis, config, utils

SLIDES_DIR = config.REPO_ROOT / "slides"
SLIDES_DIR.mkdir(exist_ok=True)


def _load(name, default=None):
    p = config.PROCESSED_DIR / name
    return utils.load_json(p) if p.exists() else default


def _pct(x):
    return f"{x*100:.1f}\\%" if isinstance(x, (int, float)) else "n/a"


def _fig(name):
    return (
        "\\begin{center}\\includegraphics[height=0.72\\textheight,"
        "width=\\textwidth,keepaspectratio]{%s}\\end{center}" % name
    )


def _tex_escape(s: str) -> str:
    for a, b in (("&", "\\&"), ("%", "\\%"), ("_", "\\_"), ("#", "\\#")):
        s = s.replace(a, b)
    return s


def main() -> None:
    summary = _load("pubmed_summary.json", {})
    counts = _load("pubmed_yearly_counts.json", {})
    rsna = _load("rsna_ai_fraction.json", [])
    rad = _load("top_papers_radiology_ai.json", [])
    ped = _load("top_papers_pediatric_radiology_ai.json", [])

    yr0, yr1 = summary.get("year_range", [2008, 2025])
    cagr = summary.get("radiology_ai_cagr")
    cagr_s = f"{cagr*100:.0f}\\%/yr" if isinstance(cagr, (int, float)) else "n/a"

    mod = analysis.breakdown_table(counts, "modality", denom_series="radiology_ai") if counts else []
    task = analysis.breakdown_table(counts, "task", denom_series="radiology_ai") if counts else []

    def bullets(rows, n=4):
        return "\n".join(f"\\item {r['label']} --- {_pct(r.get('fraction'))}" for r in rows[:n])

    repl = {
        "@@yr0@@": str(yr0),
        "@@yr1@@": str(yr1),
        "@@rad_ai_latest@@": f"{summary.get('radiology_ai_latest', 0):,}",
        "@@cagr@@": cagr_s,
        "@@ai_share_first@@": _pct(summary.get("ai_share_of_radiology_first")),
        "@@ai_share_last@@": _pct(summary.get("ai_share_of_radiology_latest")),
        "@@ped_share@@": _pct(summary.get("pediatric_share_of_radiology_ai_latest")),
        "@@ped_latest@@": f"{summary.get('pediatric_radiology_ai_latest', 0):,}",
        "@@rsna_first@@": _pct(rsna[0]["rsna_ai_fraction"]) if rsna else "n/a",
        "@@rsna_last@@": _pct(rsna[-1]["rsna_ai_fraction"]) if rsna else "n/a",
        "@@fig_trend@@": _fig("radiology_ai_trend.png"),
        "@@fig_pedshare@@": _fig("pediatric_share.png"),
        "@@fig_modality@@": _fig("modality_breakdown.png"),
        "@@fig_task@@": _fig("task_breakdown.png"),
        "@@fig_rsna@@": _fig("rsna_ai_share.png"),
        "@@fig_society@@": _fig("society_ai_share.png"),
        "@@fig_mlvenue@@": _fig("ml_venue_radiology_share.png"),
        "@@fig_toppapers@@": _fig("top_papers_radiology.png"),
        "@@fig_pedpapers@@": _fig("top_papers_pediatric.png"),
        "@@fig_github@@": _fig("github_stars.png"),
        "@@modality_bullets@@": bullets(mod),
        "@@task_bullets@@": bullets(task),
    }

    tex = TEMPLATE
    for k, v in repl.items():
        tex = tex.replace(k, v)

    out = SLIDES_DIR / "pedrad_ai_slides.tex"
    out.write_text(tex, encoding="utf-8")
    print(f"Wrote {out} ({tex.count(chr(10))} lines)")


TEMPLATE = r"""\documentclass[aspectratio=169]{beamer}
\usetheme{Madrid}
\usecolortheme{whale}
\usepackage{graphicx}
\usepackage[utf8]{inputenc}
\graphicspath{{../figures/}}
\setbeamertemplate{navigation symbols}{}

\title[Radiology AI]{Artificial Intelligence in Radiology}
\subtitle{How fast it is growing, where it sits, and how much is pediatric}
\author{Pediatric Radiology AI project}
\date{\today}

\begin{document}

\frame{\titlepage}

\begin{frame}{Objectives}
\begin{itemize}
  \item Quantify how much \textbf{radiology AI} has grown, from a pre-deep-learning
        2008 baseline to today, using reproducible queries against public databases.
  \item Measure \textbf{where} inside radiology the AI work sits --- by imaging
        modality and by clinical task.
  \item Measure how much of radiology AI is \textbf{pediatric}, and in which modalities.
  \item Identify the \textbf{biggest players}: most-cited papers and most-used
        open-source software.
  \item Summarize what the field \textbf{does well}, what is \textbf{bleeding edge},
        and what remains \textbf{unresolved} --- for a children's hospital.
\end{itemize}
\end{frame}

\begin{frame}{Methods --- databases and queries}
\textbf{Databases queried:}
\begin{itemize}
  \item \textbf{PubMed} (NCBI E-utilities) --- publication counts by year, by query.
  \item \textbf{OpenAlex} --- citation counts and most-cited papers (union of
        modality/task searches, deduped by work id).
  \item \textbf{GitHub} --- open-source tools ranked by stars.
  \item \textbf{DBLP} --- ML/CV venue programs (CVPR, ICCV, NeurIPS, ICML, ICLR).
  \item \textbf{PatentsView} --- granted US patents (requires an API key).
\end{itemize}
\textbf{Representative PubMed query (radiology $\cap$ AI):}
\begin{block}{}
\scriptsize
(radiology OR radiograph* OR ``medical imaging'' OR MRI OR CT OR ultrasound \dots)
\textbf{AND} (``artificial intelligence'' OR ``deep learning'' OR
``convolutional neural network'' OR radiomics \dots)
\end{block}
\footnotesize Counts use the \texttt{[pdat]} date facet; shares are ratios of counts.
The exact strings live in \texttt{pedrad\_ai/config.py}.
\end{frame}

\begin{frame}{How much has AI grown in the radiology literature?}
\begin{columns}
\begin{column}{0.42\textwidth}
\footnotesize
\begin{itemize}
  \item @@rad_ai_latest@@ radiology-AI papers in @@yr1@@.
  \item Compound growth $\approx$ \textbf{@@cagr@@}.
  \item AI share of all radiology rose from \textbf{@@ai_share_first@@} (@@yr0@@) to
        \textbf{@@ai_share_last@@} (@@yr1@@).
\end{itemize}
\end{column}
\begin{column}{0.58\textwidth}
@@fig_trend@@
\end{column}
\end{columns}
\end{frame}

\begin{frame}{Where the AI work sits --- by modality}
\begin{columns}
\begin{column}{0.40\textwidth}
\footnotesize Share of radiology-AI papers mentioning each modality (overlapping):
\begin{itemize}
@@modality_bullets@@
\end{itemize}
\end{column}
\begin{column}{0.60\textwidth}
@@fig_modality@@
\end{column}
\end{columns}
\end{frame}

\begin{frame}{Where the AI work sits --- by clinical task}
\begin{columns}
\begin{column}{0.40\textwidth}
\footnotesize Share of radiology-AI papers by task (overlapping):
\begin{itemize}
@@task_bullets@@
\end{itemize}
\end{column}
\begin{column}{0.60\textwidth}
@@fig_task@@
\end{column}
\end{columns}
\end{frame}

\begin{frame}{How much is pediatric?}
\begin{columns}
\begin{column}{0.42\textwidth}
\footnotesize
\begin{itemize}
  \item Pediatric work is \textbf{@@ped_share@@} of radiology AI in @@yr1@@
        (@@ped_latest@@ papers).
  \item Small but growing; strongest in ultrasound and MRI.
\end{itemize}
\end{column}
\begin{column}{0.58\textwidth}
@@fig_pedshare@@
\end{column}
\end{columns}
\end{frame}

\begin{frame}{Radiology's own engagement: AI share of RSNA journals}
\begin{columns}
\begin{column}{0.40\textwidth}
\footnotesize
The AI share of RSNA's flagship journals rose from \textbf{@@rsna_first@@} to
\textbf{@@rsna_last@@} --- about one in four articles now touches AI.
\end{column}
\begin{column}{0.60\textwidth}
@@fig_rsna@@
\end{column}
\end{columns}
\end{frame}

\begin{frame}{Conferences and societies}
\begin{columns}
\begin{column}{0.5\textwidth}
\centering \footnotesize Radiology share of ML venues\\
@@fig_mlvenue@@
\end{column}
\begin{column}{0.5\textwidth}
\centering \footnotesize AI share of radiology-society journals\\
@@fig_society@@
\end{column}
\end{columns}
\end{frame}

\begin{frame}{Biggest players --- most-cited radiology AI papers}
@@fig_toppapers@@
\end{frame}

\begin{frame}{Biggest players --- most-cited pediatric radiology AI papers}
@@fig_pedpapers@@
\end{frame}

\begin{frame}{Biggest players --- most-starred open-source tools}
@@fig_github@@
\end{frame}

\begin{frame}{What radiology AI does well}
\begin{itemize}
  \item \textbf{Worklist triage}: hemorrhage, large-vessel occlusion, pulmonary
        embolism, pneumothorax --- the most validated, most deployed category.
  \item \textbf{Detection / measurement aids} on high-volume adult exams
        (lung nodules, mammography, volumetry).
  \item \textbf{Image quality / acquisition}: deep-learning reconstruction and
        denoising --- lower dose, shorter scans (most valuable in pediatrics).
  \item \textbf{Quantification / standardization}: segmentation, longitudinal
        tumor measurement.
\end{itemize}
\end{frame}

\begin{frame}{Bleeding edge}
\begin{itemize}
  \item Foundation models and vision-language / report-generation systems.
  \item Opportunistic screening (bone density, coronary calcium, body composition).
  \item Multimodal and longitudinal models (imaging $+$ EHR $+$ priors).
  \item Self-supervised / label-efficient learning (key where labels are scarce).
  \item \textbf{Pediatric frontiers}: bone age (mature), fetal/neonatal brain MRI,
        congenital anomaly detection, scoliosis / Cobb-angle, growth-aware models.
\end{itemize}
\end{frame}

\begin{frame}{What remains unresolved}
\begin{itemize}
  \item \textbf{Generalization}: models degrade across scanners, sites, populations.
  \item \textbf{Pediatric data scarcity \& age dependence}: children are not small
        adults; adult models transfer poorly.
  \item \textbf{Prospective benefit}: most evidence is retrospective accuracy, not
        improved outcomes.
  \item \textbf{Report-generation trust}: LLM reports can be fluent and wrong.
  \item \textbf{Regulation/liability}: most cleared devices are validated on adults.
  \item \textbf{Workflow integration, monitoring, drift, and equity.}
\end{itemize}
\end{frame}

\begin{frame}{Implications for a children's hospital}
\begin{enumerate}
  \item \textbf{Buy maturity, build for the gaps}: adopt cleared adult-derived tools
        that transfer (triage, reconstruction); treat pediatric tasks as local
        validation / research.
  \item \textbf{Demand local pediatric validation} before clinical use.
  \item \textbf{Prioritize dose and throughput}: deep-learning reconstruction gives
        the clearest pediatric benefit today.
  \item \textbf{Plan for monitoring}: pediatric drift (growth, protocol change) is
        faster than in adults.
\end{enumerate}
\end{frame}

\begin{frame}{Summary}
\begin{itemize}
  \item Radiology AI grew from \textbf{@@ai_share_first@@} to \textbf{@@ai_share_last@@}
        of the radiology literature (@@yr0@@--@@yr1@@), $\approx$@@cagr@@.
  \item Pediatric work is \textbf{@@ped_share@@} of radiology AI --- small but growing.
  \item RSNA journals: AI share \textbf{@@rsna_first@@} $\rightarrow$ \textbf{@@rsna_last@@}.
  \item Mature where data are large and adult (triage, reconstruction); pediatric
        bone age is the one mature pediatric task.
  \item Generalization, pediatric data, and prospective benefit remain the gaps.
\end{itemize}
\end{frame}

\end{document}
"""


if __name__ == "__main__":
    main()
