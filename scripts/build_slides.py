#!/usr/bin/env python3
"""Generate a Beamer slide deck (slides/pedrad_ai_slides.tex) from the data.

Headline numbers are pulled from data/processed/ so the slides stay consistent
with the reports. Figures are included from ../figures/. Compile with:

    cd slides && latexmk -pdf pedrad_ai_slides.tex

Run `python scripts/make_figures.py` first so the figures exist. The template
uses ``@@KEY@@`` placeholders (not str.format) because the LaTeX body is full of
literal braces. Slides whose data file is missing degrade to a one-line note
rather than breaking the build.

Deck outline (2026-09 revision):
  title; objectives; methods; growth graph; modality x task with task
  definitions (all, pediatric); cross-check against the 2025 scoping review;
  biggest pediatric datasets; most-cited papers per era (all: 2008-2022,
  2023-present; pediatric: same); clinical problems addressed (pediatric, per
  era); one spotlight slide per landmark pediatric paper; newsletters (all
  ages, pediatric, then one slide per year listing the pediatric stories);
  commercial products with a pediatric angle; worth knowing; does well /
  bleeding edge / open problems / implications.
"""

from __future__ import annotations

import json
import re

from pedrad_ai import analysis, config, curated, fda_devices, utils

SLIDES_DIR = config.REPO_ROOT / "slides"
SLIDES_DIR.mkdir(exist_ok=True)

MAX_TABLE_ROWS = 10
NEWS_YEARS_FROM = 2023  # one slide per year from here to the present


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
                 ("→", "$\\rightarrow$"), ("×", "$\\times$"), ("≥", "$\\geq$"), ("≤", "$\\leq$"),
                 ("·", "$\\cdot$"), ("€", "EUR ")):
        s = s.replace(a, b)
    return s


def _short(s: str, n: int) -> str:
    s = s or ""
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _share(tab, label):
    """Share of a crosstab corpus whose title/abstract carries a task term."""
    if not tab or not tab.get("col_totals"):
        return None
    return tab["col_totals"].get(label, 0) / (tab["total"] or 1)


# --------------------------------------------------------------------------- #
# Slide fragments
# --------------------------------------------------------------------------- #
def paper_table(papers, max_rows=MAX_TABLE_ROWS):
    """Most-cited papers of one era: citations, title (venue, year), what it answers."""
    rows = papers[:max_rows]
    if not rows:
        return "\\footnotesize No papers collected for this era."
    out = ["\\begin{tabular}{@{}r p{0.40\\textwidth} p{0.47\\textwidth}@{}}",
           "\\textbf{Cites} & \\textbf{Paper} & \\textbf{What it answers} \\\\ \\hline"]
    for p in rows:
        topic, q = curated.question_for(p)
        title = _short(p.get("title") or "", 105)
        venue = _short(p.get("venue") or "", 34)
        meta = f" ({_tex(venue)}, {p.get('year')})" if venue else f" ({p.get('year')})"
        q = "" if q == (p.get("title") or "") else _short(q, 125)
        cell = f"\\textit{{{_tex(topic)}}}" + (f": {_tex(q)}" if q else "")
        out.append(f"{p.get('citation_count', 0):,} & {_tex(title)}{meta} & {cell} \\\\")
    out.append("\\end{tabular}")
    return "\n".join(out)


def dataset_table():
    out = ["\\renewcommand{\\arraystretch}{1.0}", "\\begin{tabular}{@{}p{0.24\\textwidth} p{0.05\\textwidth} p{0.17\\textwidth} p{0.23\\textwidth} p{0.08\\textwidth} p{0.11\\textwidth}@{}}",
           "\\textbf{Dataset} & \\textbf{Year} & \\textbf{Modality} & \\textbf{Size} & \\textbf{Ages} & \\textbf{Access} \\\\ \\hline"]
    for d in config.PEDIATRIC_DATASETS:
        out.append(f"{d['name']} & {d['year']} & {_tex(d['modality'])} & {_tex(d['size'])} & {_tex(d['ages'])} & {_tex(d['access'])} \\\\")
    out.append("\\end{tabular}")
    return "\n".join(out)


def task_gloss_columns():
    items = list(config.TASK_GLOSS.items())
    third = (len(items) + 2) // 3
    cols = []
    for chunk in (items[:third], items[third:2 * third], items[2 * third:]):
        body = "\n".join(f"\\item \\textbf{{{_tex(t)}}}: {_tex(g)}" for t, g in chunk)
        cols.append("\\begin{column}{0.33\\textwidth}\n\\begin{itemize}\n%s\n\\end{itemize}\n\\end{column}" % body)
    return "\\begin{columns}[T]\n" + "\n".join(cols) + "\n\\end{columns}"


def spotlight_frames(manifest):
    files = {e["slug"]: e for e in manifest if e.get("file")}
    frames = []
    for sp in curated.PAPER_SPOTLIGHTS:
        e = files.get(sp["slug"])
        bullets = "\n".join(f"\\item \\textbf{{{_tex(k)}}}: {_tex(v)}" for k, v in sp["bullets"])
        if e:
            src = e.get("source_url") or ""
            host = src.split("/")[2] if src.startswith("http") else ""
            left = ("\\includegraphics[height=0.55\\textheight,width=\\textwidth,keepaspectratio]{examples/%s}\\\\[2pt]\n"
                    "{\\tiny %s}\\\\{\\tiny source: %s}" % (e["file"], _tex(e["caption"]), _tex(host)))
        else:
            left = "{\\footnotesize (figure not fetched; run scripts/collect\\_examples.py)}"
        frames.append(
            "\\begin{frame}{%s}\n"
            "{\\scriptsize %s\\par}\\vspace{2pt}\n"
            "\\begin{columns}[T]\n"
            "\\begin{column}{0.42\\textwidth}\\centering\n%s\n\\end{column}\n"
            "\\begin{column}{0.56\\textwidth}\n\\scriptsize\n\\begin{itemize}\n%s\n\\end{itemize}\n\\end{column}\n"
            "\\end{columns}\n\\end{frame}"
            % (_tex(sp["title"]), _tex(sp["ref"]), left, bullets)
        )
    return "\n\n".join(frames)


_NEWS_PREFIX = re.compile(r"^(The (Resource |Industry )?Wire)\s*[·•]\s*", re.I)


def _clean_story(s: str) -> str:
    s = _NEWS_PREFIX.sub("", s or "").strip()
    return s.rstrip(":").strip()


def news_year_frames(items):
    if not items:
        return ""
    frames = []
    for year in range(NEWS_YEARS_FROM, config.PARTIAL_YEAR + 1):
        rows = sorted((i for i in items if (i.get("date") or "").startswith(str(year))), key=lambda i: i["date"])
        ytd = " (year to date)" if year == config.PARTIAL_YEAR else ""
        if not rows:
            body = "\\footnotesize No pediatric radiology-AI stories found for this year."
        else:
            size = "\\tiny" if len(rows) > 14 else "\\scriptsize"
            out = [size, "\\begin{tabular}{@{}l l p{0.72\\textwidth}@{}}",
                   "\\textbf{Date} & \\textbf{Newsletter} & \\textbf{Story} \\\\ \\hline"]
            for i in rows:
                out.append(f"{i['date']} & {_tex(i['source'])} & {_tex(_short(_clean_story(i.get('story')), 105))} \\\\")
            out.append("\\end{tabular}")
            body = "\n".join(out)
        frames.append("\\begin{frame}{Pediatric radiology AI in the trade press, %d%s (%d stories)}\n%s\n\\end{frame}"
                      % (year, ytd, len(rows), body))
    return "\n\n".join(frames)


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


def worth_knowing_items():
    return "\n".join(f"\\item \\textbf{{{_tex(n)}}} ({_tex(k)}): {_tex(w)}" for n, k, w in curated.WORTH_KNOWING)


def modality_bullets(counts, prefix, denom, n=4, skip=("mammography",)):
    rows = analysis.breakdown_table(counts, prefix, denom_series=denom) if counts else []
    rows = [r for r in rows if r["label"] not in skip]
    return ", ".join(f"{_tex(r['label'])} {_pct(r.get('fraction'), 0)}" for r in rows[:n])


def problem_facts(prob):
    """Numbers for the problems slide and the open-problems slide."""
    if not prob or not prob.get("counts"):
        return {"top": "n/a", "low": "n/a", "era": "", "n_recent": "n/a", "mam": ""}
    eras = [e["label"] for e in prob["eras"]]
    recent = eras[-1]
    ranked = sorted(prob["counts"].items(), key=lambda kv: -kv[1].get(recent, 0))
    top = "; ".join(f"{_tex(k)} ({v[recent]:,})" for k, v in ranked[:4])
    low = "; ".join(f"{_tex(k)} ({v[recent]:,})" for k, v in ranked[-6:][::-1])
    return {"top": top, "low": low, "era": recent, "n_recent": f"{prob['totals'][recent]:,}"}


# --------------------------------------------------------------------------- #
def main() -> None:
    summary = _load("pubmed_summary.json", {})
    counts = _load("pubmed_yearly_counts.json", {})
    xt = _load("pubmed_crosstab.json", {})
    prob = _load("pubmed_pediatric_problems.json", {})
    news = _load("newsletter_summary.json", {})
    news_items = _load("newsletter_items.json", [])
    fda = _load("fda_ai_devices.json", {})
    manifest_p = config.FIGURE_DIR / "examples" / "manifest.json"
    manifest = json.loads(manifest_p.read_text()) if manifest_p.exists() else []

    yr0, yr1 = summary.get("year_range", [2008, config.PARTIAL_YEAR - 1])
    cagr = summary.get("radiology_ai_cagr")
    cagr_s = f"{cagr*100:.0f}\\%/yr" if isinstance(cagr, (int, float)) else "n/a"
    fda_rad = fda.get("radiology_devices", 0) if fda else 0
    rad_tab = xt.get("radiology_ai") if xt else None
    ped_tab = xt.get("pediatric_radiology_ai") if xt else None
    mam = (ped_tab or {}).get("row_totals", {}).get("mammography", 0)
    ped_total = (ped_tab or {}).get("total", 0)
    pf = problem_facts(prob)
    era_a, era_b = config.ERAS[0][0], config.ERAS[1][0]
    n_ped_news = sum(1 for i in news_items if (i.get("date") or "") >= str(NEWS_YEARS_FROM))

    repl = {
        "@@yr0@@": str(yr0),
        "@@yr1@@": str(yr1),
        "@@era_a@@": era_a,
        "@@era_b@@": era_b.replace("present", "present"),
        "@@rad_ai_latest@@": f"{summary.get('radiology_ai_latest', 0):,}",
        "@@cagr@@": cagr_s,
        "@@ai_share_first@@": _pct(summary.get("ai_share_of_radiology_first")),
        "@@ai_share_last@@": _pct(summary.get("ai_share_of_radiology_latest")),
        "@@ped_share@@": _pct(summary.get("pediatric_share_of_radiology_ai_latest")),
        "@@ped_latest@@": f"{summary.get('pediatric_radiology_ai_latest', 0):,}",
        "@@fig_trend@@": _fig("radiology_ai_trend.png", 0.8),
        "@@fig_mod_task@@": _fig("modality_by_task.png", 0.47),
        "@@fig_ped_mod_task@@": _fig("ped_modality_by_task.png", 0.47),
        "@@fig_problems@@": _fig("ped_problems.png", 0.82),
        "@@fig_news_ped@@": _fig("newsletter_watch.png", 0.82),
        "@@fig_news_all@@": _fig("newsletter_radiology_ai.png", 0.82),
        "@@task_gloss@@": task_gloss_columns(),
        "@@paper_table_rad_a@@": paper_table(_load(f"top_papers_radiology_ai_{era_a}.json", [])),
        "@@paper_table_rad_b@@": paper_table(_load(f"top_papers_radiology_ai_{era_b}.json", [])),
        "@@paper_table_ped_a@@": paper_table(_load(f"top_papers_pediatric_radiology_ai_{era_a}.json", [])),
        "@@paper_table_ped_b@@": paper_table(_load(f"top_papers_pediatric_radiology_ai_{era_b}.json", [])),
        "@@dataset_table@@": dataset_table(),
        "@@spotlights@@": spotlight_frames(manifest),
        "@@news_year_frames@@": news_year_frames(news_items),
        "@@n_ped_news@@": str(n_ped_news),
        "@@commercial_table@@": commercial_table(fda),
        "@@worth_knowing@@": worth_knowing_items(),
        "@@fda_rad@@": f"{fda_rad:,}",
        "@@ped_mod_bullets@@": modality_bullets(counts, "ped_modality", "pediatric_radiology_ai"),
        "@@mam_note@@": (f"Mammography is omitted: its {mam} pediatric-query hits (of {ped_total:,}) are adult breast-imaging "
                         "papers whose abstracts mention children." if mam else ""),
        "@@ped_total@@": f"{ped_total:,}",
        "@@rad_total@@": f"{(rad_tab or {}).get('total', 0):,}",
        "@@det_rad@@": _pct(_share(rad_tab, "detection / diagnosis"), 0),
        "@@det_ped@@": _pct(_share(ped_tab, "detection / diagnosis"), 0),
        "@@seg_rad@@": _pct(_share(rad_tab, "segmentation"), 0),
        "@@meas_ped@@": _pct(_share(ped_tab, "measurement / quantification"), 0),
        "@@recon_rad@@": _pct(_share(rad_tab, "reconstruction / imputation"), 0),
        "@@recon_ped@@": _pct(_share(ped_tab, "reconstruction / imputation"), 0),
        "@@fm_rad@@": _pct(_share(rad_tab, "foundation model / vision-language"), 1),
        "@@fm_ped@@": _pct(_share(ped_tab, "foundation model / vision-language"), 1),
        "@@llm_rad@@": _pct(_share(rad_tab, "report generation / LLM"), 1),
        "@@agent_rad@@": _pct(_share(rad_tab, "agent / autonomous"), 1),
        "@@agent_ped_n@@": f"{(ped_tab or {}).get('col_totals', {}).get('agent / autonomous', 0):,}",
        "@@wf_rad@@": _pct(_share(rad_tab, "workflow / non-interpretive"), 0),
        "@@prob_top@@": pf["top"],
        "@@prob_low@@": pf["low"],
        "@@prob_era@@": pf["era"],
        "@@prob_n_recent@@": pf["n_recent"],
        "@@news_ped_total@@": f"{news.get('total_pediatric_radiology_ai_stories', 0):,}" if news else "n/a",
    }

    tex = TEMPLATE
    for k, v in repl.items():
        tex = tex.replace(k, v)

    out = SLIDES_DIR / "pedrad_ai_slides.tex"
    out.write_text(tex, encoding="utf-8")
    print(f"Wrote {out} ({tex.count(chr(10))} lines, {tex.count(chr(92) + 'begin{frame}') + 1} frames)")


TEMPLATE = r"""\documentclass[aspectratio=169]{beamer}
\usetheme{Madrid}
\usecolortheme{whale}
\usepackage{graphicx}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{array}
\graphicspath{{../figures/}}
\setbeamertemplate{navigation symbols}{}
% No bottom bar: just "n / N" in the bottom-right corner.
\setbeamertemplate{footline}{%
  \hfill{\usebeamercolor[fg]{page number in head/foot}\usebeamerfont{page number in head/foot}%
  \insertframenumber\,/\,\inserttotalframenumber}\hspace*{2ex}\vskip4pt}
\setbeamerfont{frametitle}{size=\large}
\renewcommand{\arraystretch}{1.08}

\title[Radiology AI]{Artificial Intelligence in Pediatric Radiology}
\author{Joseph Rich, Dr.~Amit Sura}
\date{September 23, 2026}

\begin{document}

\frame{\titlepage}

\begin{frame}{Objectives}
\begin{itemize}
  \item Describe the big players in radiology AI, both general and pediatric, since 2023
  \item Summarize what radiology AI does well and what remains unresolved
\end{itemize}
\end{frame}

\begin{frame}{Methods}
\scriptsize
\textbf{Academic output.} \textbf{PubMed} (E-utilities) yearly counts per query and per modality/task term group;
\textbf{OpenAlex} citation counts (union of modality/task searches, deduped), ranked separately for
@@era_a@@ and @@era_b@@ because citations favor older papers; \textbf{DBLP} for ML venues;
\textbf{PatentsView} for granted patents.\\[3pt]
\textbf{Clinical problems.} The pediatric radiology-AI query AND a term group per problem (bone age, fracture, pneumonia,
appendicitis, brain tumor, \dots), counted per era; a paper can name several problems.\\[3pt]
\textbf{Datasets.} Public pediatric imaging datasets, sizes verified against the primary papers or hosting pages.\\[3pt]
\textbf{Commercial players.} The \textbf{FDA AI-enabled device list} (public spreadsheet: decision date, device,
company, lead panel), filtered to the Radiology panel; cross-checked against a curated list of products with pediatric indications.\\[3pt]
\textbf{Trade press.} Newsletter archives (The Imaging Wire, RSNA News, TLDR, Signify Research, Radiology Business)
split into stories; a story is radiology-AI when AI terms co-occur with imaging terms, pediatric when pediatric terms
also co-occur.\\[3pt]
\textbf{Pediatric filter.} PubMed: the radiology-AI query AND
(pediatric* OR paediatric* OR child* OR infant* OR neonat* OR adolescen* OR ``children's hospital'').
Most-cited lists: the title must also carry a pediatric term (bone age, fetal, newborn, \dots), otherwise
highly cited adult papers float in. Newsletters: pediatric term inside the same story.\\[3pt]
\textbf{Representative PubMed query (radiology $\cap$ AI):}
\begin{block}{}
\tiny
(radiology OR radiograph* OR ``medical imaging'' OR MRI OR ``computed tomography'' OR CT[tiab] OR ultrasound[tiab] \dots
NOT (``optical coherence'' OR fundus OR dental OR histopatholog* \dots))
\textbf{AND} (``artificial intelligence'' OR ``deep learning'' OR ``convolutional neural network'' OR radiomics \dots)
\end{block}
\end{frame}

\begin{frame}{Radiology AI publication counts}
@@fig_trend@@
\end{frame}

\begin{frame}{Radiology AI publications, stratified by modality and task}
@@fig_mod_task@@
\vspace{-6pt}
{\tiny Bar = percentage of radiology-AI papers (@@rad_total@@, @@yr0@@--present) whose title/abstract names the modality;
segments = which task terms those papers use (overlapping). What each task means, by what the model produces:}
\vspace{-2pt}
\tiny
@@task_gloss@@
\end{frame}

\begin{frame}{Pediatric radiology AI publications, stratified by modality and task}
@@fig_ped_mod_task@@
\vspace{-6pt}
{\tiny Same construction, restricted to the pediatric subset (@@ped_total@@ papers). Top pediatric modalities:
@@ped_mod_bullets@@. @@mam_note@@}
\vspace{-2pt}
\tiny
@@task_gloss@@
\end{frame}

\begin{frame}{Cross-check: an independent 2025 scoping review of pediatric radiology AI}
\scriptsize
Kamran et al., \textit{Pediatric Radiology} 2025 (doi 10.1007/s00247-025-06462-5): 789 original pediatric-focused
articles hand-screened from four databases, 2005 to August 2024. Our PubMed counts are larger because they include any
paper that mentions a pediatric term.
\begin{columns}[T]
\begin{column}{0.5\textwidth}
\begin{itemize}
  \item \textbf{Modality}: radiography 38\%, MRI 33\%, ultrasound 14\%, CT 11\%, nuclear 2\%. Our pediatric query
        ranks MRI first (@@ped_mod_bullets@@) because MRI-heavy neurodevelopment papers mention children.
  \item \textbf{Subspecialty}: musculoskeletal 33\%, neuro 29\%, chest 17\%, body 14\%, cardiac 6\%.
  \item \textbf{Top applications}: bone age (88 articles), pneumonia (65), brain tumors (54), scoliosis (45),
        hip dysplasia (28), congenital heart disease (25), autism (18), epilepsy (14), ADHD (9), hydrocephalus (9).
  \item \textbf{Use of AI}: 91\% image interpretation / diagnosis; 5.6\% image quality; under 2\% for
        acquisition, communication, protocoling, education, and policy combined.
\end{itemize}
\end{column}
\begin{column}{0.5\textwidth}
\begin{itemize}
  \item \textbf{Data}: 65\% used a single local hospital dataset; 7\% did not report the dataset;
        China 28\%, USA 25\%, Canada 7\% of articles.
  \item \textbf{Growth}: 23 articles in 2018, 158 in 2022, 171 in 2023, consistent with our PubMed curve.
  \item \textbf{Recommendations}: multi-institutional, age-diverse pediatric datasets; CLAIM-style reporting with
        subgroup results and calibration; funding for the neglected non-interpretive areas (policy, education,
        implementation); children and families as stakeholders across the AI lifecycle.
  \item \textbf{What it adds to this deck}: the same three leading tasks (bone age, pneumonia, brain tumor) and the
        same gap (small local datasets, adult tools applied to children) reached by a manual review.
\end{itemize}
\end{column}
\end{columns}
\end{frame}

\begin{frame}{The biggest public pediatric radiology AI datasets}
\tiny
@@dataset_table@@
\\[3pt]
{\tiny Sizes verified against the primary paper or hosting page (2026-09). Only two pediatric radiograph sets exceed
10,000 images; the largest public pediatric-only CT set has 359 patients; no RSNA pediatric challenge has run since
bone age in 2017. Adult benchmarks (CheXpert 224k, MIMIC-CXR 377k) exclude children.}
\end{frame}

\begin{frame}{Most-cited radiology AI papers, @@era_a@@}
\tiny
@@paper_table_rad_a@@
\end{frame}

\begin{frame}{Most-cited radiology AI papers, @@era_b@@}
\tiny
@@paper_table_rad_b@@
\\[3pt]
{\tiny Recent citations accrue to surveys first; the clinical landmarks of this era (TotalSegmentator, pancreatic
cancer detection on non-contrast CT, Sybil lung-cancer risk) sit among many review articles.}
\end{frame}

\begin{frame}{Most-cited pediatric radiology AI papers, @@era_a@@}
\tiny
@@paper_table_ped_a@@
\end{frame}

\begin{frame}{Most-cited pediatric radiology AI papers, @@era_b@@}
\tiny
@@paper_table_ped_b@@
\\[3pt]
{\tiny Fetal brain MRI segmentation, pediatric brain tumor segmentation, and bone age lead the recent era; citation
counts are two orders of magnitude below the adult list.}
\end{frame}

\begin{frame}{Which medical problems pediatric radiology AI addresses}
@@fig_problems@@
\end{frame}

@@spotlights@@

\begin{frame}{Newsletters --- radiology AI stories, all ages}
@@fig_news_all@@
\end{frame}

\begin{frame}{Newsletters --- pediatric radiology AI stories}
@@fig_news_ped@@
\end{frame}

@@news_year_frames@@

\begin{frame}{Commercial software with a pediatric angle}
\tiny
@@commercial_table@@
\\[4pt]
{\scriptsize ``FDA list'' = number of radiology AI-enabled devices the company has on the FDA list (years). Pediatric
status is the publicly stated indication; confirm the age range in the 510(k) summary before purchase.}
\end{frame}

\begin{frame}{Worth knowing as a radiologist --- and why}
\scriptsize
\begin{itemize}
@@worth_knowing@@
\end{itemize}
\end{frame}

\begin{frame}{What the field does well}
\small
\begin{itemize}
  \item \textbf{Finding what is there.} Detection / diagnosis is the bulk of the literature (@@det_rad@@ of
        radiology-AI papers, @@det_ped@@ of pediatric); in adults it has become deployed worklist triage, the largest
        block of the @@fda_rad@@ FDA-listed radiology AI devices.
  \item \textbf{Outlining and measuring.} Segmentation (@@seg_rad@@ of papers) has open, strong defaults (nnU-Net,
        TotalSegmentator); in children the mature measurement task is bone age (RSNA challenge: 4.2-month error,
        several cleared products), and measurement / quantification is @@meas_ped@@ of pediatric papers.
  \item \textbf{Better images from less dose.} Reconstruction / imputation is @@recon_rad@@ of radiology AI and
        @@recon_ped@@ of pediatric work; deep-learning reconstruction is on today's scanners and cut pediatric CT dose
        by about half at equal or better image quality.
  \item \textbf{Shared benchmarks where they exist.} Fetal and neonatal brain MRI (FeTA, dHCP) and pediatric brain
        tumors (BraTS-PEDs) now have challenge datasets, and multi-site pediatric neuro-oncology models match
        radiologists retrospectively.
\end{itemize}
\end{frame}

\begin{frame}{Bleeding edge}
\small
\begin{itemize}
  \item \textbf{Foundation and vision-language models}: @@fm_rad@@ of radiology-AI papers (@@fm_ped@@ pediatric);
        segment-anything style tools (MedSAM) and generalist radiology models are replacing task-specific training.
  \item \textbf{Report generation and LLMs}: @@llm_rad@@ of papers; drafting and extracting from reports, with
        fluency ahead of reliability.
  \item \textbf{Agents}: @@agent_rad@@ of radiology-AI papers (@@agent_ped_n@@ pediatric papers in total); LLMs that
        call imaging tools and take multi-step actions.
  \item \textbf{Pediatric-specific}: bone age robust to skeletal dysplasias (Deeplasia); fetal ultrasound AI is the
        most active commercial pediatric area in the trade press (BrightHeart, Sonio, DeepEcho clearances,
        2023--2026); adult fracture tools extended to children (Gleamer 2023, AZmed 2024) and now tested in a
        real pediatric emergency department.
  \item \textbf{Generalization studies}: adult-trained CT organ segmentation degrades in small children, and the
        first pediatric prospective-style reader studies show smaller gains than stand-alone accuracy implies.
\end{itemize}
\end{frame}

\begin{frame}{Open problems --- where a children's hospital could contribute}
\small
\begin{itemize}
  \item \textbf{Which diseases?} Since 2023 the pediatric corpus (@@prob_n_recent@@ papers) leans to
        @@prob_top@@. Barely studied: @@prob_low@@. Which of these deserve a model first is an open question for
        this group.
  \item \textbf{Dataset curation.} What would a multi-center pediatric dataset look like: age-stratified, consented,
        protocol-diverse, with rare phenotypes? Which of our own archives (CT, ultrasound, NICU radiographs) could
        become the pediatric benchmark that does not yet exist?
  \item \textbf{Validation.} Local, age-stratified testing of adult-cleared tools; prospective reader studies rather
        than retrospective accuracy; monitoring for drift as children grow and protocols change.
  \item \textbf{Beyond interpretation.} Workflow / non-interpretive work is @@wf_rad@@ of papers, but communication
        with families, education, protocoling and policy are almost absent; these are cheaper to build and evaluate
        than diagnostic models.
  \item \textbf{Regulation and liability.} Few of the @@fda_rad@@ radiology clearances carry a pediatric indication;
        which adult clearances are acceptable to use off-label in children, and under what local validation?
\end{itemize}
\end{frame}

\begin{frame}{Implications for a children's hospital}
\small
\begin{enumerate}
  \item \textbf{Buy maturity, build for the gaps}: adopt cleared adult-derived tools that transfer (reconstruction,
        bone age, fracture with a pediatric indication); treat the under-studied pediatric problems as local
        validation and research.
  \item \textbf{Demand local pediatric validation} before clinical use, by age group, and check the age range in
        the clearance.
  \item \textbf{Prioritize dose and throughput}: deep-learning reconstruction gives the clearest pediatric benefit
        today.
  \item \textbf{Invest in data}: a curated, shareable pediatric dataset is the scarcest resource in the field and the
        contribution a children's hospital is uniquely placed to make.
\end{enumerate}
\end{frame}

\end{document}
"""


if __name__ == "__main__":
    main()
