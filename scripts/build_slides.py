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
  biggest pediatric datasets; most-cited papers (all: 2008-2022, then one
  slide per year 2023-present with citations and FWCI; pediatric: same); one
  slide per big venue (NeurIPS, ICLR, ICML, CVPR, MICCAI, MIDL, RSNA, SPR)
  with the radiology-AI works that appeared there; clinical problems addressed
  (pediatric, per era); one spotlight slide per landmark pediatric paper
  (2025-2026 focus); newsletters (all ages, pediatric, then one slide per year
  listing the pediatric stories and the paper each story reports on);
  commercial products with a pediatric angle; worth knowing; does well /
  bleeding edge / open problems / implications.
"""

from __future__ import annotations

import json
import re

from pedrad_ai import analysis, config, corpus, curated, fda_devices, utils

SLIDES_DIR = config.REPO_ROOT / "slides"
SLIDES_DIR.mkdir(exist_ok=True)

MAX_TABLE_ROWS = 10
# One fewer for the review tables: their rows carry a wrapped venue and a
# wrapped description, so ten of them plus the footnote overflow the frame.
REVIEW_TABLE_ROWS = 9
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


_UNICODE_MAP = {"\u2009": " ", "\u202f": " ", "\u00a0": " ", "\u2010": "-", "\u2011": "-", "\u2012": "-",
                "\u2212": "-", "\u2019": "'", "\u2018": "`", "\u201c": "``", "\u201d": "''", "\u2026": "...",
                "\u03b1": "alpha", "\u03b2": "beta", "\u00d7": "x", "\u2264": "<=", "\u2265": ">=", "\u2032": "'",
                "\u2013": "--", "\u2014": "---", "\u2192": "->", "\u20ac": "EUR ", "\u2022": "-"}


def _tex(s) -> str:
    """Escape for LaTeX; fold characters pdflatex's utf8 tables do not cover
    (thin spaces, Unicode hyphens, Greek) to ASCII so a title from an API
    never breaks the build."""
    import unicodedata

    s = str(s) if s is not None else ""
    for a, b in _UNICODE_MAP.items():
        s = s.replace(a, b)
    s = "".join(ch if ord(ch) < 0x250 else (unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode() or "") for ch in s)
    for a, b in (("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"), ("_", "\\_"), ("#", "\\#"),
                 ("$", "\\$"), ("{", "\\{"), ("}", "\\}"), ("~", "\\textasciitilde{}"), ("^", "\\^{}"),
                 ("<", "\\textless{}"), (">", "\\textgreater{}")):
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
def _p(w):
    """Left-aligned (not justified) paragraph column of width ``w`` textwidth."""
    return "|>{\\raggedright\\arraybackslash}p{%.2f\\textwidth}" % w


def _venue(p):
    """Venue for tables: preprint servers by name ("arXiv"), else the journal / conference."""
    v = p.get("venue_label") or p.get("venue") or ""
    return v.replace(" (preprint)", "")


def _impact(p):
    f = p.get("fwci")
    return f if isinstance(f, (int, float)) else -1.0


def by_impact(papers, n):
    """Top ``n`` rows by FWCI (papers without one last, by citations)."""
    return sorted(papers, key=lambda p: (_impact(p), p.get("citation_count", 0)), reverse=True)[:n]


def _fwci(p):
    f = p.get("fwci")
    return f"{f:.1f}" if isinstance(f, (int, float)) else "--"


def paper_table(papers, max_rows=MAX_TABLE_ROWS, show_year=True):
    """Most-cited papers of a period, ordered by FWCI: citations, FWCI, title
    (year), venue, what it answers.

    The candidate pool is the 15 most-cited papers (the rows enrich_fwci.py
    fills in); they are re-ranked by FWCI = OpenAlex field-weighted citation
    impact (1.0 = the world average for papers of the same field and year), so
    a 2025 paper can be read next to a 2023 one.
    """
    rows = by_impact(papers[:15], max_rows)
    if not rows:
        return "\\footnotesize No papers collected for this period."
    out = ["\\renewcommand{\\arraystretch}{0.92}",
           "\\begin{tabular}{|r|r%s%s%s|}" % (_p(0.34), _p(0.15), _p(0.25)),
           "\\hline \\textbf{Cites} & \\textbf{FWCI} & \\textbf{Paper} & \\textbf{Venue} & \\textbf{What it answers} \\\\ \\hline"]
    for p in rows:
        topic, q = curated.question_for(p)
        title = _short(p.get("title") or "", 78)
        venue = _short(_venue(p), 28)
        meta = f" ({p.get('year')})" if show_year else ""
        q = "" if q == (p.get("title") or "") else _short(q, 78)
        cell = f"\\textit{{{_tex(topic)}}}" + (f": {_tex(q)}" if q else "")
        out.append(f"{p.get('citation_count', 0):,} & {_fwci(p)} & {_tex(title)}{meta} & {_tex(venue)} & {cell} \\\\ \\hline")
    out.append("\\end{tabular}")
    return "\n".join(out)


FWCI_NOTE = ("Rows are the most-cited papers of the period, ordered by FWCI = field-weighted citation impact (OpenAlex): "
             "citations relative to the world average for papers of the same field and year (1 = average), so a recent paper "
             "can be compared with an older one. Preprints (arXiv, medRxiv) are included; the venue column names the server.")


def year_frames(name, label):
    """One slide per year of the recent era: top papers with citations and FWCI."""
    frames = []
    for year in range(config.ERAS[-1][1], config.END_YEAR + 1):
        papers = _load(f"top_papers_{name}_{year}.json", [])
        ytd = " (year to date)" if year == config.PARTIAL_YEAR else ""
        n_pre = sum(1 for p in papers[:MAX_TABLE_ROWS] if p.get("is_preprint"))
        note = FWCI_NOTE if year == config.ERAS[-1][1] else ""
        if year == config.PARTIAL_YEAR:
            note = "Citations for the current year are still accumulating; the FWCI column is the more stable signal here."
        frames.append(
            "\\begin{frame}{Most-cited %s papers, %d%s}\n\\tiny\n%s\n\\\\[1pt]\n{\\tiny %s%s}\n\\end{frame}"
            % (label, year, ytd, paper_table(papers, show_year=False), _tex(note),
               f" {n_pre} of the {min(len(papers), MAX_TABLE_ROWS)} rows are preprints." if n_pre else ""))
    return "\n\n".join(frames)


def venue_frames(works):
    """One slide per big venue: the radiology-AI works that made it there."""
    if not works:
        return ""
    frames = []
    for name, v in works.items():
        rows = sorted(v.get("works", [])[:12], key=lambda w: (w.get("year") or 0, w.get("citation_count", 0)), reverse=True)
        yrs = v.get("years", [config.VENUE_WORKS_START, config.END_YEAR])
        by_year = ", ".join(f"{y}: {n}" for y, n in sorted(v.get("by_year", {}).items()))
        head = (f"\\textbf{{{_tex(v.get('full', name))}}}. Radiology-AI works found, {yrs[0]}--{yrs[1]}: "
                f"{v.get('n_works', 0)} ({by_year}); {v.get('n_pediatric', 0)} pediatric (marked $\\star$).")
        if v.get("note"):
            head += " " + _tex(v["note"])
        if not rows:
            body = "\\footnotesize No works found for this venue."
        else:
            out = ["\\renewcommand{\\arraystretch}{1.0}",
                   "\\begin{tabular}{|l|r|r%s|}" % _p(0.68),
                   "\\hline \\textbf{Year} & \\textbf{Cites} & \\textbf{FWCI} & \\textbf{Paper} \\\\ \\hline"]
            for w in rows:
                star = " $\\star$" if w.get("pediatric") else ""
                out.append(f"{w.get('year')} & {w.get('citation_count', 0):,} & {_fwci(w)} & {_tex(_short(w.get('title') or '', 120))}{star} \\\\ \\hline")
            out.append("\\end{tabular}")
            body = "\n".join(out)
        src = "Semantic Scholar venue search, citations and FWCI from OpenAlex" if v.get("kind") == "s2" else "OpenAlex, restricted to the society's journals"
        frames.append("\\begin{frame}{%s: radiology AI works, %d--%d}\n{\\scriptsize %s\\par}\\vspace{2pt}\n\\tiny\n%s\n\\\\[2pt]\n{\\tiny Source: %s; title-level relevance filter; the %d most-cited of %d works, newest year first.}\n\\end{frame}"
                      % (_tex(name), yrs[0], yrs[1], head, body, src, len(rows), v.get("n_works", 0)))
    return "\n\n".join(frames)


def dataset_table():
    out = ["\\renewcommand{\\arraystretch}{0.92}",
           "\\begin{tabular}{%s|l%s%s%s%s|}" % (_p(0.21), _p(0.14), _p(0.21), _p(0.07), _p(0.10)),
           "\\hline \\textbf{Dataset} & \\textbf{Year} & \\textbf{Modality} & \\textbf{Size} & \\textbf{Ages} & \\textbf{Access} \\\\ \\hline"]
    for d in config.PEDIATRIC_DATASETS:
        out.append(f"{d['name']} & {d['year']} & {_tex(d['modality'])} & {_tex(d['size'])} & {_tex(d['ages'])} & {_tex(d['access'])} \\\\ \\hline")
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
            left = ("\\includegraphics[height=0.50\\textheight,width=\\textwidth,keepaspectratio]{examples/%s}\\\\[2pt]\n"
                    "{\\tiny %s}\\\\{\\tiny source: %s}" % (e["file"], _tex(e["caption"]), _tex(host)))
        else:
            left = "{\\footnotesize (figure not fetched; run scripts/collect\\_examples.py)}"
        frames.append(
            "\\begin{frame}{%s}\n"
            "{\\scriptsize %s\\par}\\vspace{2pt}\n"
            "\\begin{columns}[T]\n"
            "\\begin{column}{0.42\\textwidth}\\centering\n%s\n\\end{column}\n"
            "\\begin{column}{0.56\\textwidth}\n\\scriptsize\\setlength{\\itemsep}{1pt}\n\\begin{itemize}\n%s\n\\end{itemize}\n\\end{column}\n"
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
            stretch = "\\renewcommand{\\arraystretch}{0.85}" if len(rows) > 18 else "\\renewcommand{\\arraystretch}{0.90}"
            out = [size, stretch, "\\begin{tabular}{|l|l%s%s|}" % (_p(0.43), _p(0.20)),
                   "\\hline \\textbf{Date} & \\textbf{Newsletter} & \\textbf{Story} & \\textbf{Paper} \\\\ \\hline"]
            for i in rows:
                paper = (i.get("paper") or {}).get("citation") or ""
                out.append(f"{i['date']} & {_tex(i['source'])} & {_tex(_short(_clean_story(i.get('story')), 72))} & {_tex(_short(paper, 44))} \\\\ \\hline")
            out.append("\\end{tabular}")
            body = "\n".join(out)
        frames.append("\\begin{frame}{Pediatric radiology AI in the trade press, %d%s (%d stories)}\n%s\n\\end{frame}"
                      % (year, ytd, len(rows), body))
    return "\n\n".join(frames)


# --------------------------------------------------------------------------- #
# The systematic-review corpus
# --------------------------------------------------------------------------- #
# The corpus is thousands of studies. Every aggregate slide draws on all of it;
# the slides that name individual papers rank them by field- and
# year-normalized citation impact (pedrad_ai.corpus), which is the only measure
# the Embase-only records — no PMID, therefore no RCR — can be ranked on.
def review_rows():
    """The review corpus, from the exported table, with the id guard applied."""
    import csv

    path = config.PROCESSED_DIR / "pedrad_paper_db.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    keep = corpus.included_ids()
    return [r for r in rows if not keep or (r.get("record_id") or r.get("pmid")) in keep]


def _n(x, default="--"):
    try:
        return f"{float(x):,.0f}" if float(x) == int(float(x)) else f"{float(x):,.1f}"
    except (TypeError, ValueError):
        return default


def _impact_cell(row):
    value, measure = corpus.impact(row)
    return f"{value:.0f}x" if value is not None else "--"


def review_paper_table(rows, max_rows=REVIEW_TABLE_ROWS, show_year=True):
    """Impact-ranked studies from the review corpus."""
    rows = corpus.by_impact(rows, max_rows)
    if not rows:
        return "\\footnotesize No studies in this window."
    year_col = "|r" if show_year else ""
    out = ["\\renewcommand{\\arraystretch}{0.92}",
           "\\begin{tabular}{|r|r%s%s%s%s|}" % (year_col, _p(0.33), _p(0.14), _p(0.22)),
           "\\hline \\textbf{Impact} & \\textbf{Cites} & "
           + ("\\textbf{Year} & " if show_year else "")
           + "\\textbf{Study} & \\textbf{Venue} & \\textbf{What it does} \\\\ \\hline"]
    for r in rows:
        name = r.get("model_name") or r.get("title") or ""
        venue = _short(r.get("journal") or "", 26)
        what = _short(r.get("clinical_problem") or r.get("task") or "", 62)
        mark = " $\\dagger$" if (r.get("source") or "") == "embase" else ""
        mark += " $\\ast$" if str(r.get("is_preprint")).lower() in ("true", "1") else ""
        year = f"{r.get('year')} & " if show_year else ""
        out.append(f"{_impact_cell(r)} & {_n(r.get('citations'), '0')} & {year}"
                   f"{_tex(_short(name, 72))}{mark} & {_tex(venue)} & {_tex(what)} \\\\ \\hline")
    out.append("\\end{tabular}")
    return "\n".join(out)


REVIEW_IMPACT_NOTE = (
    "Impact = citations relative to the average paper of the same field and year (OpenAlex FWCI; iCite "
    f"RCR where OpenAlex has none), shown once a study has {config.IMPACT_MIN_CITATIONS} citations. "
    "$\\dagger$ Embase-only; $\\ast$ preprint.")


def review_year_frames(rows):
    """One slide per recent year: the highest-impact studies published that year."""
    frames = []
    for year in range(config.SLIDE_REVIEW_YEARS_FROM, config.END_YEAR + 1):
        sub = [r for r in rows if str(r.get("year") or "") == str(year)]
        if not sub:
            continue
        ytd = " (year to date)" if year == config.PARTIAL_YEAR else ""
        note = REVIEW_IMPACT_NOTE if year == config.SLIDE_REVIEW_YEARS_FROM else ""
        if year == config.PARTIAL_YEAR:
            note = ("Few studies from this year have enough citations for a normalized value yet, so "
                    "this table is thin by construction rather than because the year was quiet.")
        scored = sum(1 for r in sub if corpus.impact_value(r) is not None)
        frames.append(
            "\\begin{frame}{Highest-impact pediatric radiology AI studies, %d%s}\n\\tiny\n%s\n"
            "\\\\[2pt]\n{\\tiny %d studies included from %d; %d have enough citations to be ranked. %s}\n"
            "\\end{frame}"
            % (year, ytd, review_paper_table(sub, show_year=False), len(sub), year, scored, note))
    return "\n\n".join(frames)


def review_flow_line(stats):
    """The PRISMA arithmetic as one sentence of slide text."""
    f = (stats or {}).get("flow") or {}
    if not f:
        return ""
    src = ", ".join(f"{k} {v:,}" for k, v in (stats.get("by_search_source") or {}).items())
    return (f"{f.get('screened_all_sources', 0):,} records retrieved, "
            f"{f.get('conference_excluded', 0):,} conference proceedings set aside, "
            f"{f.get('screened', 0):,} screened, {f.get('excluded_screening', 0):,} off-topic and "
            f"{f.get('non_primary', 0):,} non-primary removed, "
            f"{f.get('included', 0):,} primary studies included ({src}).")


def review_composition_line(stats):
    """Modality / task / age headline shares as one line of caption text."""
    def top(block, n=4):
        items = list((stats.get(block) or {}).items())[:n]
        return ", ".join(f"{_tex(k)} {v['pct']:.0f}\\%" for k, v in items if v.get("pct") is not None)

    parts = []
    for label, block in (("Modality", "modality"), ("Task", "task"), ("Age group", "age_groups")):
        line = top(block)
        if line:
            parts.append(f"\\textbf{{{label}}}: {line}")
    return ". ".join(parts) + "." if parts else ""


def review_impact_bullets(stats):
    """What selecting the corpus on citation impact does to it."""
    imp = (stats or {}).get("impact") or {}
    if not imp:
        return ""
    val = (stats.get("validation") or {}).get("external / multi-center", {}).get("pct")
    src = ", ".join(f"{k} {v:,}" for k, v in (imp.get("above_floor_by_source") or {}).items())
    items = [
        f"\\item The median included study is cited {imp.get('median', 0):g} times the world average "
        f"for its field and year: this is a well-cited literature, not a neglected one.",
        f"\\item {imp.get('n_scored', 0):,} of {(stats.get('flow') or {}).get('included', 0):,} studies "
        f"({imp.get('pct_scored', 0)}\\%) have enough citations to be ranked; the rest are too recent.",
        f"\\item The top decile is the {imp.get('n_above_floor', 0):,} studies at "
        f"{imp.get('floor', 0):.0f}x average and up ({src}).",
    ]
    if val is not None and imp.get("above_floor_external_pct") is not None:
        items.append(
            f"\\item Selecting on citations does not select for rigor: external or multi-center "
            f"validation is {imp['above_floor_external_pct']}\\% in that decile against {val}\\% "
            f"across the corpus, and two thirds of it is still internal validation only.")
    return "\n".join(items)


def commercial_table(fda):
    out = ["\\begin{tabular}{%s%s%s%s%s|}" % (_p(0.14), _p(0.11), _p(0.25), _p(0.23), _p(0.11)),
           "\\hline \\textbf{Vendor} & \\textbf{Product} & \\textbf{Task} & \\textbf{Pediatric status} & \\textbf{FDA list} \\\\ \\hline"]
    for c in config.COMMERCIAL_PEDIATRIC:
        look = fda_devices.company_lookup(fda, c["fda_company"]) if fda else {"devices": 0, "years": []}
        if look["devices"]:
            yrs = look["years"]
            fda_s = f"{look['devices']} ({yrs[0]}--{yrs[-1]})" if len(yrs) > 1 else f"{look['devices']} ({yrs[0]})"
        else:
            fda_s = "not listed"
        out.append(f"{_tex(c['vendor'])} & {_tex(c['product'])} & {_tex(c['task'])} & {_tex(c['pediatric'])} & {fda_s} \\\\ \\hline")
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
def _journal_short(name, limit=40):
    """Trim a PubMed journal title down to something a caption can carry."""
    short = re.split(r"\s+:\s+", name, maxsplit=1)[0]
    return short if len(short) <= limit else short[: limit - 1].rstrip() + "\u2026"


def journal_note(data, *, since, min_papers):
    """Caption for a journal-impact slide: what is plotted and what it shows."""
    if not data:
        return "(journal counts not collected in this run)"
    end = data["end_year"]
    rows = [r for r in data["journals"] if r.get("impact_factor") is not None]
    plotted = sorted(
        (r for r in rows if sum(n for y, n in r["counts"].items() if since <= int(y) <= end) >= min_papers),
        key=lambda r: -sum(n for y, n in r["counts"].items() if since <= int(y) <= end),
    )
    if not plotted:
        return "(no journal cleared the plotting threshold)"

    def n_of(r):
        return sum(n for y, n in r["counts"].items() if since <= int(y) <= end)

    total = sum(n_of(r) for r in data["journals"])
    shown = sum(n_of(r) for r in plotted)
    top = plotted[0]
    hi = [r for r in plotted if r["impact_factor"] >= 10]
    mid = sorted(r["impact_factor"] for r in plotted)[len(plotted) // 2]
    axis = ("Journal Impact Factor (JCR)" if data.get("n_overrides")
            else "OpenAlex 2-year mean citedness (a free JIF analogue; runs below the published JIF)")
    # The reading of the chart follows the numbers rather than being asserted:
    # where the mass sits is exactly what the slide is for.
    verdict = (
        "this work reaches journals well above the median of the field"
        if len(hi) > len(plotted) / 2 else
        "this work lands mostly in mid-impact specialty and technical journals"
    )
    # medRxiv and the MICCAI proceedings publish plenty of this work and have no
    # impact number of any kind; saying so is better than dropping them quietly.
    no_impact = sorted(
        (r for r in data["journals"]
         if r.get("impact_factor") is None
         and sum(n for y, n in r["counts"].items() if since <= int(y) <= end) >= min_papers),
        key=lambda r: -sum(n for y, n in r["counts"].items() if since <= int(y) <= end),
    )
    missing = ""
    if no_impact:
        n_missing = sum(n_of(r) for r in no_impact)
        # Naming them is not worth it: PubMed calls the two biggest
        # "Proceedings of the Annual International Conference of the IEEE ..."
        # and "Proceedings". What matters is what kind of source they are.
        kinds = ("proceedings", "conference", "preprint", "arxiv", "medrxiv", "biorxiv")
        what = ("conference proceedings and preprint servers"
                if all(any(k in r["journal"].lower() for k in kinds) for r in no_impact)
                else "sources")
        if len(no_impact) == 1:
            missing = (f" {_journal_short(no_impact[0]['journal'], 30)} clears the threshold "
                       f"({n_missing:,} papers) but has no impact number of any kind, so it is not plotted.")
        else:
            missing = (f" A further {len(no_impact)} {what} clear the threshold ({n_missing:,} papers) "
                       f"but have no impact number of any kind and are not plotted.")
    gif = ""
    if since == data["start_year"] and (config.FIGURE_DIR / "journal_impact.gif").exists():
        gif = " The same chart animated year by year: \\texttt{figures/journal\\_impact.gif}."
    return _tex(
        f"x = {axis}. y = cumulative pediatric radiology-AI papers {since}-{end} (PubMed, strict "
        f"title/abstract query). The {len(plotted)} journals with at least {min_papers} of them are shown, "
        f"carrying {shown:,} of {total:,}; the rest is a long tail. Largest: {top['journal']} "
        f"({n_of(top):,}); median impact {mid:.1f}, {len(hi)} at 10 or above -- {verdict}.{missing}"
    ) + gif



def main() -> None:
    preprints = _load("preprint_counts.json", {})
    counts = analysis.add_preprints(_load("pubmed_yearly_counts.json", {}), preprints)
    summary = analysis.summarize(counts) if counts else _load("pubmed_summary.json", {})
    xt = {k: analysis.merge_crosstab(v, (preprints.get("crosstab") or {}).get(k))
          for k, v in _load("pubmed_crosstab.json", {}).items()}
    prob = analysis.merge_problems(_load("pubmed_pediatric_problems.json", {}), preprints.get("problems")) or {}
    venue_works = _load("conference_works.json", {})
    news = _load("newsletter_summary.json", {})
    news_items = _load("newsletter_items.json", [])
    fda = _load("fda_ai_devices.json", {})
    journals = _load("journal_impact.json", {})
    rstats = _load("review_stats.json", {})
    rrows = review_rows()
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
        "@@fig_journal_impact@@": _fig("journal_impact.png", 0.66),
        "@@fig_journal_impact_recent@@": _fig(f"journal_impact_2023_{config.JOURNAL_END_YEAR}.png", 0.70),
        "@@journal_note@@": journal_note(journals, since=config.JOURNAL_START_YEAR,
                                         min_papers=config.JOURNAL_MIN_PAPERS),
        "@@journal_note_recent@@": journal_note(journals, since=2023,
                                                min_papers=config.JOURNAL_MIN_PAPERS_RECENT),
        "@@fig_news_ped@@": _fig("newsletter_watch.png", 0.82),
        "@@fig_news_all@@": _fig("newsletter_radiology_ai.png", 0.82),
        "@@task_gloss@@": task_gloss_columns(),
        "@@paper_table_rad_a@@": paper_table(_load(f"top_papers_radiology_ai_{era_a}.json", [])),
        "@@paper_table_ped_a@@": paper_table(_load(f"top_papers_pediatric_radiology_ai_{era_a}.json", [])),
        "@@year_frames_rad@@": year_frames("radiology_ai", "radiology AI"),
        "@@year_frames_ped@@": year_frames("pediatric_radiology_ai", "pediatric radiology AI"),
        "@@venue_frames@@": venue_frames(venue_works),
        "@@fwci_note@@": FWCI_NOTE,
        "@@pre_rad_latest@@": f"{int((preprints.get('yearly') or {}).get('radiology_ai', {}).get(str(yr1), 0)):,}",
        "@@pre_ped_latest@@": f"{int((preprints.get('yearly') or {}).get('pediatric_radiology_ai', {}).get(str(yr1), 0)):,}",
        "@@rad_pub_total@@": f"{(rad_tab or {}).get('pubmed_total', (rad_tab or {}).get('total', 0)):,}",
        "@@rad_pre_total@@": f"{(rad_tab or {}).get('preprint_total', 0):,}",
        "@@ped_pre_total@@": f"{(ped_tab or {}).get('preprint_total', 0):,}",
        "@@dataset_table@@": dataset_table(),
        "@@review_flow@@": _tex(review_flow_line(rstats)),
        "@@review_n@@": f"{(rstats.get('flow') or {}).get('included', len(rrows)):,}",
        "@@review_screened@@": f"{(rstats.get('flow') or {}).get('screened', 0):,}",
        "@@review_embase@@": f"{(rstats.get('by_search_source') or {}).get('Embase', 0):,}",
        "@@review_start@@": str(config.REVIEW_START_YEAR),
        "@@review_end@@": str(config.END_YEAR),
        "@@review_composition@@": review_composition_line(rstats),
        "@@review_impact_bullets@@": review_impact_bullets(rstats),
        "@@review_impact_note@@": REVIEW_IMPACT_NOTE,
        "@@review_table_all@@": review_paper_table(rrows),
        "@@review_year_frames@@": review_year_frames(rrows),
        "@@review_external@@": _pct(((rstats.get("validation") or {}).get("external / multi-center", {}).get("pct") or 0) / 100, 1),
        "@@review_reader@@": _pct(((rstats.get("validation") or {}).get("reader study", {}).get("pct") or 0) / 100, 1),
        "@@review_prospective@@": _pct(((rstats.get("validation") or {}).get("prospective", {}).get("pct") or 0) / 100, 1),
        "@@review_code@@": f"{((rstats.get('funnel') or {}).get('code_available') or {}).get('n', 0):,}",
        "@@fig_review_prisma@@": _fig("review_prisma.png", 0.76),
        "@@fig_review_year@@": _fig("review_by_year.png", 0.72),
        "@@fig_review_modality@@": _fig("review_modality_year.png", 0.56),
        "@@fig_review_task@@": _fig("review_task_year.png", 0.76),
        "@@fig_review_validation@@": _fig("review_validation_era.png", 0.74),
        "@@fig_review_funnel@@": _fig("review_funnel.png", 0.76),
        "@@fig_review_impact_dist@@": _fig("review_impact_distribution.png", 0.46),
        "@@fig_review_impact_subset@@": _fig("review_impact_subset.png", 0.70),
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
\tiny
\textbf{Academic output.} \textbf{PubMed} (E-utilities) yearly counts per query and per modality/task term group,
plus \textbf{preprints} (OpenAlex \texttt{type:preprint}: arXiv, medRxiv, bioRxiv, \dots) counted with the same
queries, because PubMed does not index arXiv (@@pre_rad_latest@@ radiology-AI preprints in @@yr1@@).
\textbf{Most-cited papers} from OpenAlex (union of modality/task searches, deduped, articles and preprints):
one list for @@era_a@@, then one per year from 2023, each showing raw citations and the field-weighted citation
impact (FWCI, 1 = world average for that field and year), so recent papers are not buried under 2023 ones.
\textbf{Venues}: Semantic Scholar venue search (NeurIPS, ICLR, ICML, CVPR, MICCAI, MIDL) and OpenAlex journal filters
(RSNA, SPR), 2023--present; \textbf{PatentsView} for granted patents.\\[3pt]
\textbf{Systematic review.} Separately from the counts, every pediatric radiology-AI record from
@@review_start@@ onward was retrieved from \textbf{PubMed/MEDLINE and Embase}, screened against prespecified
criteria, and read into a structured row under a fixed schema (@@review_n@@ included primary studies). This is
the corpus behind the review section, the paper database, and the manuscript; slides that name individual
studies rank them by citation impact normalized to the field and year.\\[3pt]
\textbf{Clinical problems.} The pediatric radiology-AI query AND a term group per problem (bone age, fracture, pneumonia,
appendicitis, brain tumor, \dots), counted per era; a paper can name several problems.\\[3pt]
\textbf{Datasets.} Public pediatric imaging datasets, sizes verified against the primary papers or hosting pages.\\[3pt]
\textbf{Commercial players.} The \textbf{FDA AI-enabled device list} (public spreadsheet: decision date, device,
company, lead panel), filtered to the Radiology panel; cross-checked against a curated list of products with pediatric indications.\\[3pt]
\textbf{Trade press.} Newsletter archives (The Imaging Wire, RSNA News, ESR/ECR, TLDR, Signify Research, Radiology Business)
split into stories; a story is radiology-AI when AI terms co-occur with imaging terms, pediatric when pediatric terms
also co-occur; a story's outbound publisher link is resolved to a DOI and cited (OpenAlex).\\[3pt]
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
{\tiny Bar = percentage of radiology-AI papers (@@rad_total@@ = @@rad_pub_total@@ PubMed + @@rad_pre_total@@ preprints, @@yr0@@--present) whose title/abstract names the modality;
segments = which task terms those papers use (overlapping). What each task means, by what the model produces:}
\vspace{-2pt}
\tiny
@@task_gloss@@
\end{frame}

\begin{frame}{Pediatric radiology AI publications, stratified by modality and task}
@@fig_ped_mod_task@@
\vspace{-6pt}
{\tiny Same construction, restricted to the pediatric subset (@@ped_total@@ papers incl. @@ped_pre_total@@ preprints). Top pediatric modalities:
@@ped_mod_bullets@@. @@mam_note@@}
\vspace{-2pt}
\tiny
@@task_gloss@@
\end{frame}

\begin{frame}{Which journals publish pediatric radiology AI}
@@fig_journal_impact@@
\vspace{-8pt}
{\tiny @@journal_note@@}
\end{frame}

\begin{frame}{Which journals publish pediatric radiology AI, 2023--present}
@@fig_journal_impact_recent@@
\vspace{-8pt}
{\tiny @@journal_note_recent@@}
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

\begin{frame}{Reading the whole pediatric literature, not a sample of it}
\scriptsize
Counting publications says how much is being published; it does not say what was built, for which
children, or how well it was tested. So every pediatric radiology-AI record from @@review_start@@ onward was
retrieved from \textbf{PubMed/MEDLINE and Embase}, screened against prespecified criteria, and read
into a structured row --- model, modality, body region, age group, task, dataset size, data source,
validation, availability --- under one fixed schema.
\begin{itemize}\scriptsize
  \item @@review_flow@@
  \item \textbf{Embase earns its place}: @@review_embase@@ of the included studies are not in PubMed at all. They have
        no PMID, so no NIH relative citation ratio; ranking them at all is why the impact column below is
        OpenAlex's field-weighted score.
  \item Conference proceedings are retrieved and reported but not screened: an abstract cannot support a
        judgement about study design, and it carries no DOI linking it to the later full paper.
  \item Screening and extraction were done by a constrained model under a fixed schema, with a blinded
        second-model re-screen of 150 records (94.7\% agreement, $\kappa$ = 0.885). Dual-human validation is
        outstanding.
  \item The same corpus is the paper database (\texttt{reports/04\_paper\_database.md}) and the systematic
        review manuscript, so the three never disagree.
\end{itemize}
\end{frame}

\begin{frame}{Study selection}
@@fig_review_prisma@@
\end{frame}

\begin{frame}{Included studies per publication year}
@@fig_review_year@@
\vspace{-4pt}
{\tiny Blue = the @@review_n@@ included primary studies; gray = records read and then excluded as off-topic or
non-primary. @@yr1@@+ is year to date and still being indexed.}
\end{frame}

\begin{frame}{What the pediatric literature is made of}
@@fig_review_modality@@
\vspace{-4pt}
{\tiny @@review_composition@@ Categories are multilabel, so an axis can exceed 100\%. MRI leads on the strength of
the fetal and developmental-neuroscience literature: remove the MRI studies that use cognitive-neuroscience methods
or report cognitive and behavioral outcomes and MRI falls level with ultrasound (30\% each), which is why reviews
built on narrower vocabulary rank radiography or ultrasound first.}
\end{frame}

\begin{frame}{What the models produce}
@@fig_review_task@@
\end{frame}

\begin{frame}{How well is it tested?}
@@fig_review_validation@@
\vspace{-4pt}
{\tiny Of @@review_n@@ included studies, external or multi-center validation was reported by @@review_external@@,
a reader study by @@review_reader@@, prospective evaluation by @@review_prospective@@, and a working code or model
URL by @@review_code@@ studies. External validation rose across eras; reader studies did not.}
\end{frame}

\begin{frame}{From published study to a tool a child benefits from}
@@fig_review_funnel@@
\end{frame}

\begin{frame}{Which of these studies is the field actually reading?}
@@fig_review_impact_dist@@
\vspace{-6pt}
\begin{itemize}\scriptsize
@@review_impact_bullets@@
\end{itemize}
\end{frame}

\begin{frame}{Does citation impact pick out the better-validated work?}
@@fig_review_impact_subset@@
\vspace{-4pt}
{\tiny The most-cited decile is somewhat more likely to report external validation and a reader study, but
the difference is small: citations track topic and audience more than evidence.}
\end{frame}

\begin{frame}{Highest-impact pediatric radiology AI studies, @@review_start@@--@@review_end@@}
\tiny
@@review_table_all@@
\\[2pt]
{\tiny @@review_impact_note@@}
\end{frame}

@@review_year_frames@@

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
\\[1pt]
{\tiny @@fwci_note@@}
\end{frame}

@@year_frames_rad@@

\begin{frame}{Most-cited pediatric radiology AI papers, @@era_a@@}
\tiny
@@paper_table_ped_a@@
\\[2pt]
{\tiny A different corpus from the systematic-review tables earlier in the deck: this is a citation search of
Semantic Scholar over radiology AI with a pediatric title filter, so it includes conference papers and is not
screened for eligibility. The review tables rank the screened corpus. Both are shown because neither contains
the other.}
\end{frame}

@@year_frames_ped@@

@@venue_frames@@

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
\footnotesize
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
