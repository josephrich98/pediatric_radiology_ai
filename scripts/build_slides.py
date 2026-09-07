#!/usr/bin/env python3
"""Generate a Beamer slide deck (slides/pedrad_ai_slides.tex) from the data.

Headline numbers are pulled from data/processed/ so the slides stay consistent
with the reports. Figures are included from ../figures/. Compile with:

    cd slides && latexmk -pdf pedrad_ai_slides.tex

Run `python scripts/make_figures.py` first so the figures exist. The template
uses ``@@KEY@@`` placeholders (not str.format) because the LaTeX body is full of
literal braces. Slides whose data file is missing degrade to a one-line note
rather than breaking the build.

Deck outline:
  objectives; methods (sources, pediatric filter, commercial players);
  query-sufficiency check; growth graph; modality x task (all, pediatric);
  task x modality (all, pediatric); most-cited papers + what they answer
  (all, pediatric); most-starred tools + what they do; newsletters (pediatric,
  all-ages, who is talked about); commercial (FDA list, pediatric products);
  example images; worth knowing; does well / bleeding edge / unresolved /
  implications; summary.
"""

from __future__ import annotations

import json
import textwrap

from pedrad_ai import analysis, config, curated, fda_devices, utils

SLIDES_DIR = config.REPO_ROOT / "slides"
SLIDES_DIR.mkdir(exist_ok=True)

# Thresholds for the "what do the top papers / tools answer" follow-up slides.
CITE_THRESHOLD_RADIOLOGY = 1500
CITE_THRESHOLD_PEDIATRIC = 100
STAR_THRESHOLD = 2000
MAX_TABLE_ROWS = 10


def _load(name, default=None):
    p = config.PROCESSED_DIR / name
    return utils.load_json(p) if p.exists() else default


def _pct(x, nd=1):
    return f"{x*100:.{nd}f}\\%" if isinstance(x, (int, float)) else "n/a"


def _fig(name, height=0.72):
    if not (config.FIGURE_DIR / name).exists():
        return "\\begin{center}\\footnotesize(figure %s not generated in this run)\\end{center}" % _tex(name)
    return (
        "\\begin{center}\\includegraphics[height=%.2f\\textheight,"
        "width=\\textwidth,keepaspectratio]{%s}\\end{center}" % (height, name)
    )


def _tex(s) -> str:
    s = str(s) if s is not None else ""
    for a, b in (("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"), ("_", "\\_"), ("#", "\\#"),
                 ("$", "\\$"), ("{", "\\{"), ("}", "\\}"), ("~", "\\textasciitilde{}"), ("^", "\\^{}"),
                 ("…", "\\ldots{}"), ("–", "--"), ("—", "---"), ("’", "'"), ("“", "``"), ("”", "''"),
                 ("→", "$\\rightarrow$"), ("×", "$\\times$"), ("≥", "$\\geq$"), ("≤", "$\\leq$")):
        s = s.replace(a, b)
    return s


def _short(s: str, n: int) -> str:
    s = s or ""
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


# --------------------------------------------------------------------------- #
# Slide fragments
# --------------------------------------------------------------------------- #
def paper_question_table(papers, threshold, max_rows=MAX_TABLE_ROWS):
    rows = [p for p in papers if p.get("citation_count", 0) >= threshold][:max_rows]
    if not rows:
        return "\\footnotesize No papers above the threshold in this run."
    out = ["\\begin{tabular}{@{}r p{0.30\\textwidth} p{0.58\\textwidth}@{}}",
           "\\textbf{Cites} & \\textbf{Paper} & \\textbf{Clinical question it answers} \\\\ \\hline"]
    for p in rows:
        topic, q = curated.question_for(p)
        title = _short(p.get("title") or "", 70)
        out.append(f"{p.get('citation_count', 0):,} & {_tex(title)} ({p.get('year')}) & "
                   f"\\textit{{{_tex(topic)}}}: {_tex(_short(q, 120))} \\\\")
    out.append("\\end{tabular}")
    return "\n".join(out)


def repo_table(repos, threshold=STAR_THRESHOLD, max_rows=MAX_TABLE_ROWS):
    from make_figures import github_board  # noqa: E402  (same scripts dir)

    board = [r for r in github_board(repos, n=40) if r["stars"] >= threshold][:max_rows]
    if not board:
        return "\\footnotesize No repositories above the threshold in this run."
    out = ["\\begin{tabular}{@{}r p{0.26\\textwidth} p{0.22\\textwidth} p{0.40\\textwidth}@{}}",
           "\\textbf{Stars} & \\textbf{Repository} & \\textbf{What it is} & \\textbf{Why it matters} \\\\ \\hline"]
    for r in board:
        what, why = curated.repo_note(r["full_name"], r.get("description", ""))
        out.append(f"{r['stars']:,} & {_tex(r['full_name'])} & {_tex(_short(what, 40))} & {_tex(_short(why, 95))} \\\\")
    out.append("\\end{tabular}")
    return "\n".join(out)


def validation_block(v):
    if not v:
        return "\\item Query validation not run (\\texttt{scripts/validate\\_queries.py})."
    r, p = v["recall"], v["precision"]
    s = p["series"]["radiology_ai"]
    sp = p["series"]["pediatric_radiology_ai"]
    missed = ", ".join(_tex(m.split(" (")[0]) for m in r["missed"]) or "none"
    lines = [
        f"\\item \\textbf{{Recall}} on {r['n_indexed']} hand-picked landmark papers (methods, clinical validations, "
        f"reconstruction, guidelines): \\textbf{{{r['n_retrieved']}/{r['n_indexed']}}} retrieved "
        f"({_pct(r['recall'], 0)}); pediatric subset {r['n_pediatric_retrieved']}/{r['n_pediatric_indexed']}. "
        f"Missed: {missed} --- methods papers that name no modality (``biomedical image segmentation'') or "
        "cross-domain papers removed by the non-radiology-imaging exclusion (OCT, microscopy); "
        "the most-cited tables use OpenAlex union queries, which recover them.",
        f"\\item \\textbf{{Precision proxy}} ({p['year']}): a strict title/abstract-only variant of the query returns "
        f"{s['strict']:,} records vs {s['broad']:,} for the headline query; {_pct(s['strict_share_of_broad'], 0)} of the "
        f"headline count is confirmed by explicit wording (pediatric: {_pct(sp['strict_share_of_broad'], 0)}). "
        "The remainder enters via MeSH indexing; a sample of those records is in the validation report.",
        "\\item \\textbf{Term audit}: PubMed auto-maps bare \\emph{ultrasound} to the ``diagnostic imaging'' MeSH "
        "subheading and bare \\emph{tomography} to a tree that includes optical coherence tomography. Version 1 of the "
        "query counted 63\\% of radiology-AI papers as ``ultrasound''; version 2 fields every modality term "
        "([tiab] or its specific MeSH heading) and excludes ophthalmic, dental, pathology and endoscopic imaging.",
    ]
    return "\n".join(lines)


def commercial_table(fda):
    out = ["\\begin{tabular}{@{}p{0.15\\textwidth} p{0.12\\textwidth} p{0.26\\textwidth} p{0.24\\textwidth} p{0.12\\textwidth}@{}}",
           "\\textbf{Vendor} & \\textbf{Product} & \\textbf{Task} & \\textbf{Pediatric status} & \\textbf{FDA list} \\\\ \\hline"]
    for c in config.COMMERCIAL_PEDIATRIC:
        look = fda_devices.company_lookup(fda, c["fda_company"]) if fda else {"devices": 0, "years": []}
        if look["devices"]:
            yrs = look["years"]
            fda_s = f"{look['devices']} ({yrs[0]}--{yrs[-1]})" if len(yrs) > 1 else f"{look['devices']} ({yrs[0]})"
        else:
            fda_s = "not listed"
        out.append(f"{_tex(c['vendor'])} & {_tex(c['product'])} & {_tex(c['task'])} & {_tex(c['pediatric'])} & {fda_s} \\\\")
    out.append("\\end{tabular}")
    return "\n".join(out)


def image_slides(manifest):
    """Two images per slide, grouped: open source / papers / commercial."""
    if not manifest:
        return "\\begin{frame}{What it looks like}\\footnotesize No example images fetched (run scripts/collect\\_examples.py).\\end{frame}"
    groups = {}
    for e in manifest:
        if e.get("file"):
            groups.setdefault(e.get("group", "other"), []).append(e)
    titles = {"open source": "What it looks like --- open-source tools",
              "paper": "What it looks like --- landmark papers",
              "commercial": "What it looks like --- commercial products"}
    frames = []
    for g in ("open source", "paper", "commercial"):
        items = groups.get(g, [])
        for i in range(0, len(items), 2):
            pair = items[i:i + 2]
            cols = []
            for e in pair:
                src = e.get("source_url") or ""
                host = src.split("/")[2] if src.startswith("http") else ""
                cols.append(
                    "\\begin{column}{%.2f\\textwidth}\\centering\n"
                    "\\includegraphics[height=0.62\\textheight,width=\\textwidth,keepaspectratio]{examples/%s}\\\\[2pt]\n"
                    "{\\scriptsize %s}\\\\{\\tiny source: %s}\n\\end{column}"
                    % (0.48 if len(pair) == 2 else 0.8, e["file"], _tex(e["caption"]), _tex(host))
                )
            frames.append("\\begin{frame}{%s}\n\\begin{columns}[T]\n%s\n\\end{columns}\n\\end{frame}"
                          % (titles[g], "\n".join(cols)))
    return "\n\n".join(frames)


def worth_knowing_items():
    return "\n".join(f"\\item \\textbf{{{_tex(n)}}} ({_tex(k)}): {_tex(w)}" for n, k, w in curated.WORTH_KNOWING)


def task_gloss():
    return "\n".join(f"\\item \\textbf{{{_tex(t)}}}: {_tex(g)}" for t, g in config.TASK_GLOSS.items())


def modality_bullets(counts, prefix, denom, n=4):
    rows = analysis.breakdown_table(counts, prefix, denom_series=denom) if counts else []
    return ", ".join(f"{_tex(r['label'])} {_pct(r.get('fraction'), 0)}" for r in rows[:n])


def news_bullets(news):
    if not news:
        return "No newsletter data collected."
    srcs = news.get("sources", {})
    by_year = news.get("by_year", {})
    last_y = str(config.PARTIAL_YEAR - 1)
    tot = lambda y, k: sum(by_year.get(n, {}).get(y, {}).get(k, 0) for n in by_year)
    out = (
        f"{news.get('total_pediatric_radiology_ai_stories', 0)} pediatric radiology-AI stories across "
        f"{len(srcs)} archives; in {last_y}, {tot(last_y, 'pediatric_radiology_ai')} of "
        f"{tot(last_y, 'radiology_ai'):,} radiology-AI stories were pediatric."
    )
    topics = [t for t, c in news.get("topics", {}).items() if c][:3]
    if topics:
        out += " Leading pediatric topics: " + _tex("; ".join(t.split(" / ")[0] for t in topics)) + "."
    return out


# --------------------------------------------------------------------------- #
def main() -> None:
    summary = _load("pubmed_summary.json", {})
    counts = _load("pubmed_yearly_counts.json", {})
    rsna = _load("rsna_ai_fraction.json", [])
    rad = _load("top_papers_radiology_ai.json", [])
    ped = _load("top_papers_pediatric_radiology_ai.json", [])
    repos = _load("github_repos.json", {})
    news = _load("newsletter_summary.json", {})
    fda = _load("fda_ai_devices.json", {})
    val = _load("query_validation.json", {})
    manifest_p = config.FIGURE_DIR / "examples" / "manifest.json"
    manifest = json.loads(manifest_p.read_text()) if manifest_p.exists() else []

    yr0, yr1 = summary.get("year_range", [2008, config.PARTIAL_YEAR - 1])
    cagr = summary.get("radiology_ai_cagr")
    cagr_s = f"{cagr*100:.0f}\\%/yr" if isinstance(cagr, (int, float)) else "n/a"
    fda_rad = fda.get("radiology_devices", 0) if fda else 0
    fda_all = fda.get("total_devices_all_panels", 0) if fda else 0
    fda_last = (fda.get("by_year", {}) or {}).get(str(yr1), 0) if fda else 0

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
        "@@fig_trend@@": _fig("radiology_ai_trend.png", 0.8),
        "@@fig_mod_task@@": _fig("modality_by_task.png", 0.74),
        "@@fig_ped_mod_task@@": _fig("ped_modality_by_task.png", 0.74),
        "@@fig_task_mod@@": _fig("task_by_modality.png", 0.72),
        "@@fig_ped_task_mod@@": _fig("ped_task_by_modality.png", 0.74),
        "@@fig_toppapers@@": _fig("top_papers_radiology.png", 0.8),
        "@@fig_pedpapers@@": _fig("top_papers_pediatric.png", 0.8),
        "@@fig_github@@": _fig("github_stars.png", 0.8),
        "@@fig_news_ped@@": _fig("newsletter_watch.png", 0.82),
        "@@fig_news_all@@": _fig("newsletter_radiology_ai.png", 0.82),
        "@@fig_news_players@@": _fig("newsletter_players.png", 0.66),
        "@@fig_fda_year@@": _fig("fda_devices_per_year.png", 0.72),
        "@@fig_fda_companies@@": _fig("fda_companies.png", 0.72),
        "@@paper_table_rad@@": paper_question_table(rad, CITE_THRESHOLD_RADIOLOGY),
        "@@paper_table_ped@@": paper_question_table(ped, CITE_THRESHOLD_PEDIATRIC),
        "@@repo_table@@": repo_table(repos),
        "@@validation@@": validation_block(val),
        "@@commercial_table@@": commercial_table(fda),
        "@@image_slides@@": image_slides(manifest),
        "@@worth_knowing@@": worth_knowing_items(),
        "@@task_gloss@@": task_gloss(),
        "@@news_bullets@@": news_bullets(news),
        "@@cite_thr_rad@@": f"{CITE_THRESHOLD_RADIOLOGY:,}",
        "@@cite_thr_ped@@": f"{CITE_THRESHOLD_PEDIATRIC:,}",
        "@@star_thr@@": f"{STAR_THRESHOLD:,}",
        "@@fda_rad@@": f"{fda_rad:,}",
        "@@fda_all@@": f"{fda_all:,}",
        "@@fda_share@@": _pct(fda.get("radiology_share")) if fda else "n/a",
        "@@fda_last@@": f"{fda_last:,}",
        "@@fda_date@@": _tex(fda.get("collected_on", "")) if fda else "",
        "@@mod_bullets@@": modality_bullets(counts, "modality", "radiology_ai"),
        "@@ped_mod_bullets@@": modality_bullets(counts, "ped_modality", "pediatric_radiology_ai"),
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
\usepackage[T1]{fontenc}
\usepackage{array}
\graphicspath{{../figures/}}
\setbeamertemplate{navigation symbols}{}
\setbeamerfont{frametitle}{size=\large}
\renewcommand{\arraystretch}{1.08}

\title[Radiology AI]{Artificial Intelligence in Radiology}
\subtitle{How fast it is growing, where it sits, who the players are, and how much is pediatric}
\author{Pediatric Radiology AI project}
\date{\today}

\begin{document}

\frame{\titlepage}

\begin{frame}{Objectives}
\begin{itemize}
  \item Quantify how much \textbf{radiology AI} has grown, from a pre-deep-learning
        @@yr0@@ baseline to today, using reproducible queries against public databases.
  \item Measure \textbf{where} inside radiology the AI work sits --- by imaging
        modality and by the question each model answers.
  \item Measure how much of radiology AI is \textbf{pediatric}, and in which modalities and tasks.
  \item Identify the \textbf{biggest players}: most-cited papers, most-used
        open-source software, most-cleared commercial products, and who the trade press talks about.
  \item Summarize what the field \textbf{does well}, what is \textbf{bleeding edge},
        and what remains \textbf{unresolved} --- for a children's hospital.
\end{itemize}
\end{frame}

\begin{frame}{Methods --- sources, filters, and players}
\scriptsize
\textbf{Academic output.} \textbf{PubMed} (E-utilities) yearly counts per query and per modality/task term group;
\textbf{OpenAlex} citation counts (union of modality/task searches, deduped); \textbf{DBLP} for ML venues;
\textbf{PatentsView} for granted patents.\\[3pt]
\textbf{Open-source software.} \textbf{GitHub} search leaderboards plus a fixed list of known tools fetched by name
(search alone misses MONAI and nnU-Net because their descriptions never say ``radiology'').\\[3pt]
\textbf{Commercial players.} The \textbf{FDA AI-enabled device list} (public spreadsheet: decision date, device,
company, lead panel), filtered to the Radiology panel: products per year, clearances per company, device names
matching pediatric terms; cross-checked against a curated list of products with pediatric indications.\\[3pt]
\textbf{Trade press.} Newsletter archives (The Imaging Wire, RSNA News, TLDR, Signify Research, Radiology Business)
split into stories; a story is radiology-AI when AI terms co-occur with imaging terms, pediatric when pediatric terms
also co-occur; company/tool mentions counted per story (sponsor blocks excluded).\\[3pt]
\textbf{Pediatric filter.} PubMed: the radiology-AI query AND
(pediatric* OR paediatric* OR child* OR infant* OR neonat* OR adolescen* OR ``children's hospital'').
Most-cited lists: the title must also carry a pediatric term (bone age, fetal, newborn, \dots), otherwise
highly cited adult papers float in. Newsletters: pediatric term inside the same story.\\[3pt]
\textbf{Representative PubMed query (radiology $\cap$ AI, version 2):}
\begin{block}{}
\tiny
(radiology OR radiograph* OR ``medical imaging'' OR MRI OR ``computed tomography'' OR CT[tiab] OR ultrasound[tiab] \dots
NOT (``optical coherence'' OR fundus OR dental OR histopatholog* \dots))
\textbf{AND} (``artificial intelligence'' OR ``deep learning'' OR ``convolutional neural network'' OR radiomics \dots)
\end{block}
\end{frame}

\begin{frame}{Methods --- is the radiology-AI query sufficient?}
\scriptsize
\begin{itemize}
@@validation@@
\item \textbf{Verdict}: recall is high; precision was the problem and is now controlled. Recent-year counts
      still undercount (indexing lag) and the current year is partial.
\end{itemize}
\end{frame}

\begin{frame}{How much has AI grown in the radiology literature?}
@@fig_trend@@
\end{frame}

\begin{frame}{Where the AI work sits --- by modality, and which questions are asked}
@@fig_mod_task@@
\vspace{-4pt}
{\scriptsize Bar = share of radiology-AI papers whose title/abstract names the modality (@@yr0@@--present, overlapping).
Segments = the mix of task terms inside that modality's papers.}
\end{frame}

\begin{frame}{Pediatric radiology AI --- by modality, and which questions are asked}
@@fig_ped_mod_task@@
\vspace{-4pt}
{\scriptsize Same construction, restricted to the pediatric subset. Top pediatric modalities:
@@ped_mod_bullets@@ (share of pediatric radiology-AI papers).}
\end{frame}

\begin{frame}{Where the AI work sits --- by task (what the model produces)}
\begin{columns}[T]
\begin{column}{0.70\textwidth}
@@fig_task_mod@@
\end{column}
\begin{column}{0.30\textwidth}
\tiny
\begin{itemize}
@@task_gloss@@
\end{itemize}
\end{column}
\end{columns}
\end{frame}

\begin{frame}{Pediatric radiology AI --- by task}
@@fig_ped_task_mod@@
\vspace{-4pt}
{\scriptsize Same task categories, restricted to the pediatric subset. Labels overlap; a paper can be both
segmentation and prognosis.}
\end{frame}

\begin{frame}{Biggest players --- most-cited radiology AI papers}
@@fig_toppapers@@
\end{frame}

\begin{frame}{What the most-cited radiology AI papers answer ($\geq$ @@cite_thr_rad@@ citations)}
\tiny
@@paper_table_rad@@
\end{frame}

\begin{frame}{Biggest players --- most-cited pediatric radiology AI papers}
@@fig_pedpapers@@
\end{frame}

\begin{frame}{What the most-cited pediatric papers answer ($\geq$ @@cite_thr_ped@@ citations)}
\tiny
@@paper_table_ped@@
\end{frame}

\begin{frame}{Biggest players --- most-starred open-source tools}
@@fig_github@@
\end{frame}

\begin{frame}{What the most-starred tools do ($\geq$ @@star_thr@@ stars)}
\tiny
@@repo_table@@
\end{frame}

\begin{frame}{Newsletters --- pediatric radiology AI stories}
@@fig_news_ped@@
\end{frame}

\begin{frame}{Newsletters --- radiology AI stories, all ages}
@@fig_news_all@@
\end{frame}

\begin{frame}{Newsletters --- who the trade press talks about}
@@fig_news_players@@
\vspace{-4pt}
{\scriptsize A third importance signal next to citations and stars: stories mentioning each company or tool
(sponsor blocks excluded). @@news_bullets@@}
\end{frame}

\begin{frame}{Commercial players --- the FDA AI-enabled device list}
\begin{columns}[T]
\begin{column}{0.5\textwidth}
@@fig_fda_year@@
\end{column}
\begin{column}{0.5\textwidth}
@@fig_fda_companies@@
\end{column}
\end{columns}
{\scriptsize @@fda_rad@@ of @@fda_all@@ AI-enabled devices (@@fda_share@@) sit in the Radiology panel; @@fda_last@@ radiology
devices were authorized in @@yr1@@. The list has no pediatric flag: age indications live in each 510(k) summary.
Snapshot @@fda_date@@.}
\end{frame}

\begin{frame}{Commercial software with a pediatric angle}
\tiny
@@commercial_table@@
\\[4pt]
{\scriptsize ``FDA list'' = number of radiology AI-enabled devices the company has on the FDA list (years). Pediatric
status is the publicly stated indication; confirm the age range in the 510(k) summary before purchase.}
\end{frame}

@@image_slides@@

\begin{frame}{Worth knowing as a radiologist --- and why}
\scriptsize
\begin{itemize}
@@worth_knowing@@
\end{itemize}
\end{frame}

\begin{frame}{What radiology AI does well}
\begin{itemize}
  \item \textbf{Worklist triage}: hemorrhage, large-vessel occlusion, pulmonary
        embolism, pneumothorax --- the most validated, most deployed category (and the largest
        block of FDA clearances).
  \item \textbf{Detection / measurement aids} on high-volume adult exams
        (lung nodules, mammography, fractures, volumetry).
  \item \textbf{Image quality / acquisition}: deep-learning reconstruction and
        denoising --- lower dose, shorter scans (most valuable in pediatrics).
  \item \textbf{Quantification / standardization}: segmentation, longitudinal
        tumor measurement, opportunistic screening from existing CTs.
\end{itemize}
\end{frame}

\begin{frame}{Bleeding edge}
\begin{itemize}
  \item Foundation models and vision-language / report-generation systems.
  \item Agents: LLMs that call imaging tools and take multi-step actions (still $<$1\% of papers).
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
  \item \textbf{Regulation/liability}: most cleared devices are validated on adults; only a
        handful of radiology clearances carry a pediatric indication.
  \item \textbf{Workflow integration, monitoring, drift, and equity.}
\end{itemize}
\end{frame}

\begin{frame}{Implications for a children's hospital}
\begin{enumerate}
  \item \textbf{Buy maturity, build for the gaps}: adopt cleared adult-derived tools
        that transfer (triage, reconstruction); treat pediatric tasks as local
        validation / research.
  \item \textbf{Demand local pediatric validation} before clinical use, and check the
        age range in the clearance.
  \item \textbf{Prioritize dose and throughput}: deep-learning reconstruction gives
        the clearest pediatric benefit today.
  \item \textbf{Plan for monitoring}: pediatric drift (growth, protocol change) is
        faster than in adults.
\end{enumerate}
\end{frame}

\begin{frame}{Summary}
\begin{itemize}
  \item Radiology AI grew from \textbf{@@ai_share_first@@} to \textbf{@@ai_share_last@@}
        of the radiology literature (@@yr0@@--@@yr1@@), $\approx$@@cagr@@; @@rad_ai_latest@@ papers in @@yr1@@.
  \item Pediatric work is \textbf{@@ped_share@@} of radiology AI --- small but growing;
        MRI-heavy, bone age and neuro lead.
  \item RSNA journals: AI share \textbf{@@rsna_first@@} $\rightarrow$ \textbf{@@rsna_last@@}.
  \item Commercial: @@fda_rad@@ FDA-authorized radiology AI devices; scanner makers and triage vendors dominate;
        pediatric indications are rare (fracture, bone age, fetal echo).
  \item Mature where data are large and adult (triage, reconstruction); pediatric
        bone age is the one mature pediatric task.
  \item Generalization, pediatric data, and prospective benefit remain the gaps.
\end{itemize}
\end{frame}

\end{document}
"""


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(config.REPO_ROOT / "scripts"))
    main()
