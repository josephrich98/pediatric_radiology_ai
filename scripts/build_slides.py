#!/usr/bin/env python3
"""Generate a Beamer slide deck (slides/pedrad_ai_slides.tex) from the data.

Headline numbers are pulled from data/processed/ so the slides stay consistent
with the reports. Figures are included from ../figures/. Compile with:

    cd slides && latexmk -xelatex pedrad_ai_slides.tex

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


# Beamer 16:9 frame geometry (Madrid theme), in pt, for the table-fit estimate.
_TEXTWIDTH, _TEXTHEIGHT, _TABCOLSEP = 433.3, 243.4, 6.0
# (baselineskip, average glyph width) per font size used in tables.
_FONT_METRICS = {"tiny": (7.0, 3.1), "scriptsize": (9.5, 4.2)}


def _cell_plain(cell):
    """Visible text of a LaTeX table cell, for length estimates only."""
    cell = re.sub(r"\$[^$]*\$", "x", cell)
    cell = re.sub(r"\\[A-Za-z]+\*?", "", cell)
    return re.sub(r"\s+", " ", cell.replace("{", "").replace("}", "")).strip()


def _wrapped_lines(text, width_chars):
    """Line count of ``text`` word-wrapped at ``width_chars``."""
    lines, cur = 1, 0
    for word in text.split():
        n = len(word)
        if cur and cur + 1 + n > width_chars:
            lines += 1 + (n - 1) // width_chars
            cur = n % width_chars or width_chars
        elif not cur and n > width_chars:
            lines += (n - 1) // width_chars
            cur = n % width_chars or width_chars
        else:
            cur += n + (1 if cur else 0)
    return lines


def _fit(lines, height, size="tiny"):
    """Wrap a tabular (list of lines) so every cell's full text fits the frame.

    Cells are never truncated. The paragraph (``p``) columns are rescaled
    together so the table's shape matches a box of ``\textwidth`` by ``height``
    of ``\textheight`` -- wider when the text would otherwise wrap into a tall,
    narrow table -- and adjustbox then shrinks (never grows) the result to fit
    that box exactly, so a long table gets smaller type rather than cut cells.
    Rows keep enough padding that no glyph touches a rule.
    """
    head, rows, tail = lines[0], lines[1:-1], lines[-1]
    m = re.match(r"\\begin\{tabular\}\{(.*)\}$", head)
    spec = m.group(1)
    cols = re.findall(r"p\{([0-9.]+)\\textwidth\}|(?<![a-z{])([lcr])(?![a-z])", spec)
    widths = [float(w) if w else None for w, _ in cols]
    cells = [[_cell_plain(c) for c in re.split(r"(?<!\\)&", re.sub(r"\\\\\s*\\hline\s*$", "", r.replace("\\hline", "", 1) if r.startswith("\\hline") else r))]
             for r in rows]
    base, char_w = _FONT_METRICS.get(size, _FONT_METRICS["tiny"])
    auto_w = [max((len(r[j]) for r in cells if j < len(r)), default=1) * char_w if w is None else 0.0
              for j, w in enumerate(widths)]
    avail_h = height * _TEXTHEIGHT

    def shrink(k):
        nat_w = sum(auto_w) + sum(w * k * _TEXTWIDTH for w in widths if w) + 2 * _TABCOLSEP * len(widths)
        nat_h = 0.0
        for r in cells:
            n = max((_wrapped_lines(c, max(1, int(widths[j] * k * _TEXTWIDTH / char_w)))
                     for j, c in enumerate(r) if j < len(widths) and widths[j]), default=1)
            nat_h += n * base + 0.3 * base
        return min(1.0, _TEXTWIDTH / nat_w, avail_h / nat_h)

    best_k, best = 1.0, shrink(1.0)
    for step in range(12, 61):
        k = step / 20
        sc = shrink(k)
        if sc > best + 1e-3:
            best_k, best = k, sc
    it = iter(w * best_k for w in widths if w)
    spec = re.sub(r"p\{[0-9.]+\\textwidth\}", lambda _: "p{%.3f\\textwidth}" % next(it), spec)
    return "\n".join(["\\begin{adjustbox}{max totalsize={\\textwidth}{%.2f\\textheight}}" % height,
                      "\\renewcommand{\\arraystretch}{1.2}", "\\begin{tabular}{%s}" % spec,
                      *rows, tail, "\\end{adjustbox}"])


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


def paper_table(papers, max_rows=MAX_TABLE_ROWS, show_year=True, height=0.64):
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
    out = ["\\begin{tabular}{|r|r%s%s%s|}" % (_p(0.34), _p(0.15), _p(0.25)),
           "\\hline \\textbf{Cites} & \\textbf{FWCI} & \\textbf{Paper} & \\textbf{Venue} & \\textbf{What it answers} \\\\ \\hline"]
    for p in rows:
        topic, q = curated.question_for(p)
        title = p.get("title") or ""
        venue = _venue(p)
        meta = f" ({p.get('year')})" if show_year else ""
        q = "" if q == (p.get("title") or "") else q
        cell = f"\\textit{{{_tex(topic)}}}" + (f": {_tex(q)}" if q else "")
        out.append(f"{p.get('citation_count', 0):,} & {_fwci(p)} & {_tex(title)}{meta} & {_tex(venue)} & {cell} \\\\ \\hline")
    out.append("\\end{tabular}")
    return _fit(out, height)


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
            "\\begin{frame}[category=Journals/Preprints]{Most-cited %s papers, %d%s}\n\\tiny\n%s\n\\\\[1pt]\n{\\tiny %s%s}\n\\end{frame}"
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
        # Pediatric papers on the acceptance list that the citation ranking left
        # out go in as extra rows at the bottom, so a venue's few are never hidden.
        key = lambda t: re.sub(r"[^a-z0-9]", "", (t or "").lower())
        shown = {key(w.get("title")) for w in rows}
        indexed = {key(w.get("title")): w for w in v.get("works", [])}
        for pw in v.get("pediatric_works") or []:
            if key(pw["title"]) not in shown:
                title = pw["title"].title() if pw["title"].isupper() else pw["title"]
                rows.append({**indexed.get(key(pw["title"]), {"citation_count": None}),
                             "title": title, "year": pw["year"], "pediatric": True})
        yrs = v.get("years", [config.VENUE_WORKS_START, config.END_YEAR])
        by_year = ", ".join(f"{y}: {n}" for y, n in sorted(v.get("by_year", {}).items()))
        found = "accepted (from the meeting's paper list)" if v.get("count_source") else "found"
        head = (f"\\textbf{{{_tex(v.get('full', name))}}}. Radiology-AI works {found}, {yrs[0]}--{yrs[1]}: "
                f"{v.get('n_works', 0)} ({by_year}); {v.get('n_pediatric', 0)} pediatric (marked $\\star$).")
        if v.get("note"):
            head += " " + _tex(v["note"])
        if not rows:
            body = "\\footnotesize No works found for this venue."
        else:
            out = ["\\begin{tabular}{|l|r|r%s|}" % _p(0.68),
                   "\\hline \\textbf{Year} & \\textbf{Cites} & \\textbf{FWCI} & \\textbf{Paper} \\\\ \\hline"]
            for w in rows:
                star = " $\\star$" if w.get("pediatric") else ""
                cites = "--" if w.get("citation_count") is None else f"{w['citation_count']:,}"
                out.append(f"{w.get('year')} & {cites} & {_fwci(w)} & {_tex(w.get('title') or '')}{star} \\\\ \\hline")
            out.append("\\end{tabular}")
            body = _fit(out, 0.60)
        src = "Semantic Scholar venue search, citations and FWCI from OpenAlex" if v.get("kind") == "s2" else "OpenAlex, restricted to the society's journals"
        frames.append("\\begin{frame}[category=Conferences]{%s: radiology AI works, %d--%d}\n{\\scriptsize %s\\par}\\vspace{2pt}\n\\tiny\n%s\n\\\\[2pt]\n{\\tiny Source: %s; title-level relevance filter; the %d most-cited of the %d works indexed there, newest year first.}\n\\end{frame}"
                      % (_tex(name), yrs[0], yrs[1], head, body, src, len(rows), v.get("n_indexed", v.get("n_works", 0))))
    return "\n\n".join(frames)


def _population(title):
    t = (title or "").lower()
    if re.search(r"fetal|foetal|fetus|gestational|intrapartum|prenatal", t):
        return "Fetal"
    if re.search(r"infant|neonat|newborn|preterm|premature", t):
        return "Infant / neonatal"
    return "Pediatric"


def venue_pediatric_frames(works):
    """Every pediatric radiology-AI title on each listed conference's acceptance
    lists, newest year first, split across slides when long."""
    frames = []
    for name in config.VENUE_PEDIATRIC_SLIDES:
        v = (works or {}).get(name) or {}
        rows = sorted(v.get("pediatric_works") or [], key=lambda w: (-w["year"], w["title"].lower()))
        if not rows:
            continue
        yrs = v.get("years", [config.VENUE_WORKS_START, config.END_YEAR])
        held = sorted(int(y) for y in v.get("accepted_by_year") or {})
        n = config.VENUE_PEDIATRIC_ROWS
        chunks = [rows[i:i + n] for i in range(0, len(rows), n)]
        pops = [_population(w["title"]) for w in rows]
        mix = ", ".join(f"{pops.count(p)} {p.lower()}" for p in ("Fetal", "Infant / neonatal", "Pediatric") if pops.count(p))
        for k, chunk in enumerate(chunks):
            out = ["\\begin{tabular}{|l|l%s|}" % _p(0.72),
                   "\\hline \\textbf{Year} & \\textbf{Population} & \\textbf{Paper} \\\\ \\hline"]
            for w in chunk:
                out.append(f"{w['year']} & {_population(w['title'])} & {_tex(w['title'])} \\\\ \\hline")
            out.append("\\end{tabular}")
            cont = f" ({k + 1}/{len(chunks)})" if len(chunks) > 1 else ""
            head = (f"{len(rows)} pediatric radiology-AI papers accepted {yrs[0]}--{yrs[1]} ({mix}). "
                    f"Meetings with a published paper list: {', '.join(map(str, held))}.")
            frames.append(
                "\\begin{frame}[category=Conferences]{%s: pediatric radiology AI works%s}\n\\relax{\\scriptsize %s\\par}\\vspace{2pt}\n\\tiny\n%s\n\\\\[2pt]\n"
                "{\\tiny Source: the meeting's accepted-paper list; a title counts when it names an imaging modality, an AI method and a pediatric term (fetal included). Titles only, so pediatric work that does not say so in its title is missed.}\n\\end{frame}"
                % (_tex(name), cont, head, _fit(out, 0.66)))
    return "\n\n".join(frames)


def dataset_table():
    out = ["\\begin{tabular}{%s|l%s%s%s%s|}" % (_p(0.21), _p(0.14), _p(0.21), _p(0.07), _p(0.10)),
           "\\hline \\textbf{Dataset} & \\textbf{Year} & \\textbf{Modality} & \\textbf{Size} & \\textbf{Ages} & \\textbf{Access} \\\\ \\hline"]
    for d in config.PEDIATRIC_DATASETS:
        out.append(f"{d['name']} & {d['year']} & {_tex(d['modality'])} & {_tex(d['size'])} & {_tex(d['ages'])} & {_tex(d['access'])} \\\\ \\hline")
    out.append("\\end{tabular}")
    return _fit(out, 0.70)



def _methods_query_line(label: str, terms: str) -> str:
    return f"\\textbf{{{label}}}: {_tex(terms)}"


def methods_query_block() -> str:
    """The search strategy, one line per concept block, straight from config."""
    blocks = [("radiology", config._REVIEW_MODALITY_TIAB), ("AI", config._REVIEW_AI_TIAB),
              ("pediatric", config._REVIEW_PEDIATRIC_TIAB)]
    out = ["{\\small\\textbf{Search strategy}: radiology AND AI [AND pediatric]\\par}",
           "\\vspace{2pt}",
           "{\\tiny\\fontsize{6}{7.3}\\selectfont\\raggedright"]
    out.append("\\\\[2pt]\n".join(_methods_query_line(k, v) for k, v in blocks))
    out.append("\\par}")
    return "\n".join(out)


def methods_table(review_n: str = "") -> str:
    """One line per data source."""
    rows = [
        ("Journals, Preprints", "PubMed, Embase, arXiv, medRxiv"),
        ("Conferences", "NeurIPS, ICLR, ICML, CVPR, MICCAI, MIDL"),
        ("Datasets", "Hand-curated list"),
        ("Newsletters", ", ".join(config.NEWSLETTER_SOURCES)),
        ("Commercial", "FDA list of AI-enabled devices"),
    ]
    lines = "\\\\\n".join(f"\\textbf{{{_tex(k)}}}: {_tex(v)}" for k, v in rows)
    return "{\\small\n" + lines + "\\par}"


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
            "\\begin{frame}[category=Journals/Preprints]{%s}\n"
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
            size = "tiny" if len(rows) > 14 else "scriptsize"
            out = ["\\begin{tabular}{|l|l%s%s|}" % (_p(0.43), _p(0.20)),
                   "\\hline \\textbf{Date} & \\textbf{Newsletter} & \\textbf{Story} & \\textbf{Paper} \\\\ \\hline"]
            for i in rows:
                paper = (i.get("paper") or {}).get("citation") or ""
                out.append(f"{i['date']} & {_tex(i['source'])} & {_tex(_clean_story(i.get('story')))} & {_tex(paper)} \\\\ \\hline")
            out.append("\\end{tabular}")
            body = "\\" + size + "\n" + _fit(out, 0.84, size)
        frames.append("\\begin{frame}[category=Newsletters]{Pediatric radiology AI in the trade press, %d%s (%d stories)}\n%s\n\\end{frame}"
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


def review_paper_table(rows, max_rows=REVIEW_TABLE_ROWS, show_year=True, height=0.70):
    """Impact-ranked studies from the review corpus."""
    rows = corpus.by_impact(rows, max_rows)
    if not rows:
        return "\\footnotesize No studies in this window."
    year_col = "|r" if show_year else ""
    out = ["\\begin{tabular}{|r|r%s%s%s%s|}" % (year_col, _p(0.33), _p(0.14), _p(0.22)),
           "\\hline \\textbf{Impact} & \\textbf{Cites} & "
           + ("\\textbf{Year} & " if show_year else "")
           + "\\textbf{Study} & \\textbf{Venue} & \\textbf{What it does} \\\\ \\hline"]
    for r in rows:
        name = r.get("model_name") or r.get("title") or ""
        # PubMed appends a subtitle ("... : the official journal of ..."): not part of the name
        venue = re.split(r"\s+:\s+", r.get("journal") or "", maxsplit=1)[0]
        what = r.get("clinical_problem") or r.get("task") or ""
        mark = " $\\dagger$" if (r.get("source") or "") == "embase" else ""
        mark += " $\\ast$" if str(r.get("is_preprint")).lower() in ("true", "1") else ""
        year = f"{r.get('year')} & " if show_year else ""
        out.append(f"{_impact_cell(r)} & {_n(r.get('citations'), '0')} & {year}"
                   f"{_tex(name)}{mark} & {_tex(venue)} & {_tex(what)} \\\\ \\hline")
    out.append("\\end{tabular}")
    return _fit(out, height)


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
            "\\begin{frame}[category=Journals/Preprints]{Highest-impact pediatric radiology AI studies, %d%s}\n\\tiny\n%s\n"
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
           "\\hline \\textbf{Vendor} & \\textbf{Selected products} & \\textbf{Functions} & \\textbf{Pediatric / regulatory scope} & \\textbf{Company-wide FDA AI entries (n; years)} \\\\ \\hline"]
    for c in config.COMMERCIAL_PEDIATRIC:
        look = fda_devices.company_lookup(fda, c["fda_company"]) if fda else {"devices": 0, "years": []}
        if look["devices"]:
            yrs = look["years"]
            fda_s = f"{look['devices']} ({yrs[0]}--{yrs[-1]})" if len(yrs) > 1 else f"{look['devices']} ({yrs[0]})"
        else:
            fda_s = "not listed"
        out.append(f"{_tex(c['vendor'])} & {_tex(c['product'])} & {_tex(c['task'])} & {_tex(c['pediatric'])} & {fda_s} \\\\ \\hline")
    out.append("\\end{tabular}")
    return _fit(out, 0.66)


def commercial_footnote(fda):
    date = _tex((fda or {}).get("collected_on", "date unavailable"))
    return (
        r"{\scriptsize Counts = company-wide radiology entries in the FDA AI-enabled device list "
        f"(saved {date}); grouped vendors are summed. "
        r"Includes versions and unrelated products, not pediatric-clearance counts; parentheses = decision-year range. "
        r"The list is not exhaustive and may lag new authorizations.\\[2pt]"
        r"Functions / labeling checked 2026-09-16; features vary by market and version. "
        r"GP = Greulich--Pyle; TW3 = Tanner--Whitehouse 3; CHD = congenital heart disease.}"
    )


def fda_pediatric_inventory_frames(inv):
    """Appendix frames for every candidate from the dated FDA screen."""
    if not inv:
        return ""
    rows = inv.get("records", [])
    groups = [("label-positive candidates", [r for r in rows if r.get("status") == "label-positive-candidate"]),
              ("needs label review", [r for r in rows if r.get("status") != "label-positive-candidate"])]
    frames = [r"\begin{frame}[category=FDA appendix]{FDA pediatric-use inventory: scope}", r"\scriptsize\begin{itemize}",
              f"\\item Screened all {inv.get('records_screened', 0):,} Radiology-panel records in the FDA AI-device CSV downloaded 2026-09-16.",
              f"\\item {len(rows)} records had pediatric/fetal keywords; {sum(r.get('status') == 'label-positive-candidate' for r in rows)} are label-positive candidates.",
              "\\item This is exhaustive for the dated FDA-list snapshot, not for the commercial market: FDA says its AI list is not comprehensive. Repeated submissions are retained so the result is auditable.",
              "\\item Candidate status is a keyword screen of linked decision-summary PDFs. Confirm the current authorization and full labeling before purchase.",
              r"\end{itemize}", r"\vspace{5pt}\tiny Source: \texttt{data/processed/fda\_pediatric\_inventory.json}; evidence pages are retained per submission.", r"\end{frame}"]
    for label, group in groups:
        for start in range(0, len(group), 20):
            chunk = group[start:start+20]
            lines = [r"\begin{tabular}{|p{0.12\textwidth}|p{0.10\textwidth}|p{0.20\textwidth}|p{0.46\textwidth}|p{0.08\textwidth}|}",
                     r"\hline \textbf{Submission} & \textbf{Date} & \textbf{Company} & \textbf{Device} & \textbf{Code} \\\\ \hline"]
            for r in chunk:
                lines.append(f"{_tex(r['submission'])} & {_tex(r['decision_date'])} & {_tex(r['company'])} & {_tex(r['device'])} & {_tex(r['product_code'])} \\\\ \\hline")
            lines.append(r"\end{tabular}")
            frames.extend([f"\\begin{{frame}}[category=FDA appendix]{{FDA pediatric-use inventory: {label} ({start+1}--{start+len(chunk)} of {len(group)})}}", _fit(lines, 0.78), r"\end{frame}"])
    return "\n".join(frames)


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
    fda_pediatric = _load("fda_pediatric_inventory.json", {})
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
        "@@fig_news_lines@@": _fig("newsletter_by_source.png", 0.82),
        "@@fig_venue_lines@@": _fig("venue_works_by_year.png", 0.82),
        "@@task_gloss@@": task_gloss_columns(),
        "@@paper_table_rad_a@@": paper_table(_load(f"top_papers_radiology_ai_{era_a}.json", [])),
        "@@paper_table_ped_a@@": paper_table(_load(f"top_papers_pediatric_radiology_ai_{era_a}.json", [])),
        "@@year_frames_rad@@": year_frames("radiology_ai", "radiology AI"),
        "@@year_frames_ped@@": year_frames("pediatric_radiology_ai", "pediatric radiology AI"),
        "@@venue_frames@@": venue_frames(venue_works),
        "@@venue_pediatric_frames@@": venue_pediatric_frames(venue_works),
        "@@fwci_note@@": FWCI_NOTE,
        "@@pre_rad_latest@@": f"{int((preprints.get('yearly') or {}).get('radiology_ai', {}).get(str(yr1), 0)):,}",
        "@@pre_ped_latest@@": f"{int((preprints.get('yearly') or {}).get('pediatric_radiology_ai', {}).get(str(yr1), 0)):,}",
        "@@rad_pub_total@@": f"{(rad_tab or {}).get('pubmed_total', (rad_tab or {}).get('total', 0)):,}",
        "@@rad_pre_total@@": f"{(rad_tab or {}).get('preprint_total', 0):,}",
        "@@ped_pre_total@@": f"{(ped_tab or {}).get('preprint_total', 0):,}",
        "@@dataset_table@@": dataset_table(),
        "@@methods_table@@": methods_table(f"{(rstats.get('flow') or {}).get('included', len(rrows)):,}"),
        "@@methods_query@@": methods_query_block(),
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
        "@@commercial_footnote@@": commercial_footnote(fda),
        "@@fda_pediatric_inventory_frames@@": fda_pediatric_inventory_frames(fda_pediatric),
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
\usepackage{iftex}
% Helvetica Neue under XeLaTeX/LuaLaTeX when installed; TeX Gyre Heros (a
% Helvetica clone shipped with TeX Live) otherwise, and helvet under pdfLaTeX.
\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
  \usepackage[scaled]{helvet}
\else
  \usepackage{fontspec}
  \IfFontExistsTF{Helvetica Neue}{\setsansfont{Helvetica Neue}}{%
    \setsansfont{texgyreheros}[Extension=.otf, UprightFont=*-regular, BoldFont=*-bold,
      ItalicFont=*-italic, BoldItalicFont=*-bolditalic]}
\fi
\usepackage{array}
\usepackage{adjustbox}
\graphicspath{{../figures/}}
\setbeamertemplate{navigation symbols}{}
% No bottom bar: just "n / N" in the bottom-right corner.
\setbeamertemplate{footline}{%
  \hfill{\usebeamercolor[fg]{page number in head/foot}\usebeamerfont{page number in head/foot}%
  \insertframenumber\,/\,\inserttotalframenumber}\hspace*{2ex}\vskip4pt}
\setbeamerfont{frametitle}{size=\large}
% Deck section, bold caps, top-right of the title bar: \begin{frame}[category=Conferences]{...}.
% Reset before every frame so a category never carries over to the next slide.
\makeatletter
\def\slidecategory{}
\define@key{beamerframe}{category}{\def\slidecategory{#1}}
\AddToHook{env/frame/before}{\def\slidecategory{}}
\setbeamerfont{slide category}{size=\scriptsize,series=\bfseries}
\setbeamertemplate{frametitle}{%
  \nointerlineskip
  \begin{beamercolorbox}[wd=\paperwidth,leftskip=.3cm,rightskip=.3cm]{frametitle}%
    \vskip1pt
    \hbox to \dimexpr\paperwidth-.6cm\relax{\hfill\usebeamerfont{slide category}\strut\MakeUppercase{\slidecategory}}%
    \vskip-5pt
    \usebeamerfont{frametitle}\strut\insertframetitle\par
    \vskip1pt
  \end{beamercolorbox}}
\makeatother
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
\vspace{-4pt}
@@methods_table@@
\vspace{2pt}
@@methods_query@@
\end{frame}

\begin{frame}[category=Journals/Preprints]{Radiology AI publication counts}
@@fig_trend@@
\end{frame}

\begin{frame}[category=Journals/Preprints]{Pediatric radiology AI publications, stratified by modality and task}
@@fig_ped_mod_task@@
\vspace{-6pt}
{\tiny Same construction, restricted to the pediatric subset (@@ped_total@@ papers incl. @@ped_pre_total@@ preprints). Top pediatric modalities:
@@ped_mod_bullets@@. @@mam_note@@}
\vspace{-2pt}
\tiny
@@task_gloss@@
\end{frame}

\begin{frame}[category=Journals/Preprints]{Which journals publish pediatric radiology AI}
@@fig_journal_impact@@
\vspace{-8pt}
{\tiny @@journal_note@@}
\end{frame}

\begin{frame}[category=Journals/Preprints]{Which journals publish pediatric radiology AI, 2023--present}
@@fig_journal_impact_recent@@
\vspace{-8pt}
{\tiny @@journal_note_recent@@}
\end{frame}

\begin{frame}[category=Journals/Preprints]{Cross-check: an independent 2025 scoping review of pediatric radiology AI}
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

\begin{frame}[category=Journals]{ACR white paper: the pediatric AI gap}
\relax
{\scriptsize Sammer et al., \textit{J Am Coll Radiol} 2023;20:730--737
(\href{https://doi.org/10.1016/j.jacr.2023.06.003}{doi 10.1016/j.jacr.2023.06.003})\par}
\medskip
\small
\begin{itemize}
  \item \textbf{Scope}: ACR Pediatric AI Workgroup white paper framing limited access to pediatric AI as a health equity issue.
  \item \textbf{Availability}: at the time of the review, only 6 of more than 200 FDA-cleared tools in the ACR catalog indicated pediatric use (about 3\%).
  \item \textbf{Why adult AI may fail}: growth, disease patterns, and imaging protocols differ; published studies show uneven performance across pediatric subgroups.
  \item \textbf{Barriers}: scarce labeled pediatric data, consent and privacy concerns, and weak financial incentives for smaller pediatric markets.
  \item \textbf{Recommendations}: validate in children, disclose age-specific evidence, fund pediatric development, involve families, and protect pediatric workflows. The authors introduce \textit{Image IntelliGently} to advance this work.
\end{itemize}
\end{frame}

\begin{frame}[category=Journals]{Multisociety statement: safe pediatric AI implementation}
\relax
{\scriptsize Shelmerdine et al., \textit{J Am Coll Radiol} 2026;23:89--101
(\href{https://doi.org/10.1016/j.jacr.2025.08.019}{doi 10.1016/j.jacr.2025.08.019})\par}
\medskip
{\small ACR, ESPR, SPR, SLARP, AOSPR, and SPIN propose four pillars for safe adoption:\par}
\small
\begin{itemize}
  \item \textbf{Regulation and purchasing}: pediatric labeling and proposed safety ratings; diverse datasets, subgroup performance, transparency, and cybersecurity.
  \item \textbf{Implementation and integration}: define a local clinical need, select tools validated in children, pilot before scaling, and involve pediatric specialists and families.
  \item \textbf{Interpretation and postmarket surveillance}: retain human oversight; audit performance and patient outcomes; manage discrepancies, report adverse events, and address automation bias.
  \item \textbf{Education}: foundational AI literacy for all staff, pediatric-specific training, continuing education, and patient/public engagement.
\end{itemize}
\end{frame}

\begin{frame}[category=Journals/Preprints]{Reading the whole pediatric literature, not a sample of it}
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

\begin{frame}[category=Journals/Preprints]{Study selection}
@@fig_review_prisma@@
\end{frame}

\begin{frame}[category=Journals/Preprints]{Included studies per publication year}
@@fig_review_year@@
\vspace{-4pt}
{\tiny Blue = the @@review_n@@ included primary studies; gray = records read and then excluded as off-topic or
non-primary. @@yr1@@+ is year to date and still being indexed.}
\end{frame}

\begin{frame}[category=Journals/Preprints]{What the pediatric literature is made of}
@@fig_review_modality@@
\vspace{-4pt}
{\tiny @@review_composition@@ Categories are multilabel, so an axis can exceed 100\%. MRI leads on the strength of
the fetal and developmental-neuroscience literature: remove the MRI studies that use cognitive-neuroscience methods
or report cognitive and behavioral outcomes and MRI falls level with ultrasound (30\% each), which is why reviews
built on narrower vocabulary rank radiography or ultrasound first.}
\end{frame}

\begin{frame}[category=Journals/Preprints]{What the models produce}
@@fig_review_task@@
\end{frame}

\begin{frame}[category=Journals/Preprints]{How well is it tested?}
@@fig_review_validation@@
\vspace{-4pt}
{\tiny Of @@review_n@@ included studies, external or multi-center validation was reported by @@review_external@@,
a reader study by @@review_reader@@, prospective evaluation by @@review_prospective@@, and a working code or model
URL by @@review_code@@ studies. External validation rose across eras; reader studies did not.}
\end{frame}

\begin{frame}[category=Journals/Preprints]{From published study to a tool a child benefits from}
@@fig_review_funnel@@
\end{frame}

\begin{frame}[category=Journals/Preprints]{Which of these studies is the field actually reading?}
@@fig_review_impact_dist@@
\vspace{-6pt}
\begin{itemize}\scriptsize
@@review_impact_bullets@@
\end{itemize}
\end{frame}

\begin{frame}[category=Journals/Preprints]{Does citation impact pick out the better-validated work?}
@@fig_review_impact_subset@@
\vspace{-4pt}
{\tiny The most-cited decile is somewhat more likely to report external validation and a reader study, but
the difference is small: citations track topic and audience more than evidence.}
\end{frame}

\begin{frame}[category=Journals/Preprints]{Highest-impact pediatric radiology AI studies, @@review_start@@--@@review_end@@}
\tiny
@@review_table_all@@
\\[2pt]
{\tiny @@review_impact_note@@}
\end{frame}

@@review_year_frames@@

\begin{frame}[category=Datasets]{The biggest public pediatric radiology AI datasets}
\tiny
@@dataset_table@@
\\[3pt]
{\tiny Sizes verified against the primary paper or hosting page (2026-09). Only two pediatric radiograph sets exceed
10,000 images; the largest public pediatric-only CT set has 359 patients; no RSNA pediatric challenge has run since
bone age in 2017. Adult benchmarks (CheXpert 224k, MIMIC-CXR 377k) exclude children.}
\end{frame}

\begin{frame}[category=Journals/Preprints]{Most-cited radiology AI papers, @@era_a@@}
\tiny
@@paper_table_rad_a@@
\\[1pt]
{\tiny @@fwci_note@@}
\end{frame}

@@year_frames_rad@@

\begin{frame}[category=Journals/Preprints]{Most-cited pediatric radiology AI papers, @@era_a@@}
\tiny
@@paper_table_ped_a@@
\\[2pt]
{\tiny A different corpus from the systematic-review tables earlier in the deck: this is a citation search of
Semantic Scholar over radiology AI with a pediatric title filter, so it includes conference papers and is not
screened for eligibility. The review tables rank the screened corpus. Both are shown because neither contains
the other.}
\end{frame}

@@year_frames_ped@@

\begin{frame}[category=Conferences]{Radiology AI works per year, by conference}
@@fig_venue_lines@@
\end{frame}

@@venue_frames@@

@@venue_pediatric_frames@@

\begin{frame}[category=Journals/Preprints]{Which medical problems pediatric radiology AI addresses}
@@fig_problems@@
\end{frame}

@@spotlights@@

\begin{frame}[category=Newsletters]{Newsletters --- radiology AI stories per year, by source}
@@fig_news_lines@@
\end{frame}

@@news_year_frames@@

\begin{frame}[category=Commercial Software]{Commercial software with a pediatric angle}
\tiny
@@commercial_table@@
\\[4pt]
@@commercial_footnote@@
\end{frame}

@@fda_pediatric_inventory_frames@@

\begin{frame}{Worth knowing as a radiologist --- and why}
\scriptsize
\begin{itemize}
@@worth_knowing@@
\end{itemize}
\end{frame}

\begin{frame}{Recommendations for pediatric radiologists}
\begin{itemize}
  \setlength{\itemsep}{12pt}
  \item Choose one task worth improving in your practice: bone-age measurements,
        fracture detection, or reducing CT dose / MRI scan time.
  \item Before adopting a tool, ask which children it was tested on. Check the
        intended age range and test it on your own cases, including younger children
        and unusual anatomy.
  \item In a local pilot, measure what changes with AI: reading time, missed findings,
        false alarms, dose, or scan time. Review errors and keep checking after rollout.
  \item Help build the evidence we need: choose a pediatric problem you see often,
        label cases carefully, and work with other hospitals to test whether a model
        works beyond the site that built it.
\end{itemize}
\end{frame}

\end{document}
"""


if __name__ == "__main__":
    main()
