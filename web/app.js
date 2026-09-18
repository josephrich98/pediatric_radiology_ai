/*
 * Pediatric Radiology AI Database: tabs, tables, search, columns, CSV.
 *
 * Every table is a static JSON snapshot written by scripts/build_site.py
 * ({columns, rows} with rows as arrays). A tab loads its files on first open;
 * search, sort, column choice and CSV export then run in memory, so the site
 * needs no backend. Layout and interaction follow conference-agent's table.
 */
(function () {
  const S = window.PedradSearch;
  const $ = (id) => document.getElementById(id);
  const PAGE = 200;

  // ------------------------------------------------------------------ helpers

  const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const DASH = '<span class="muted">—</span>';
  const fmtInt = (n) => (typeof n === "number" ? n.toLocaleString() : DASH);
  const fmtNum = (n, d = 2) => (typeof n === "number" ? n.toFixed(d).replace(/\.?0+$/, "") : DASH);
  const safeUrl = (u) => (/^https?:\/\//i.test(u || "") ? u : "");
  const link = (url, text) => {
    const u = safeUrl(url);
    return u ? `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(text)}</a>` : esc(text);
  };
  const quoteVal = (v) => (/[\s()"]/.test(v) ? `"${String(v).replace(/"/g, "")}"` : v);

  // A clickable tag: clicking it adds `field:="value"` to the search.
  function tag(field, value, cls = "") {
    return `<span class="tag ${cls}" data-q="${esc(`${field}:=${quoteVal(value)}`)}" title="Filter to ${esc(value)}">${esc(value)}</span>`;
  }
  function tags(field, value, classFor) {
    const vals = Array.isArray(value) ? value : String(value ?? "").split(/;\s*/);
    const clean = vals.map((v) => String(v).trim()).filter(Boolean);
    return clean.length ? clean.map((v) => tag(field, v, classFor ? classFor(v) : "")).join("") : DASH;
  }
  const text = (v, cls = "") => (S.isEmpty(v) ? DASH : `<div class="${cls}">${esc(v)}</div>`);
  const clamp = (v) => text(v, "clamp");

  // A yes / no cell. Clicking it filters to the rows with the same answer;
  // `why` becomes the tooltip on "yes", so it always says what it rests on.
  function yesNo(field, on, why) {
    return on
      ? `<span class="tag green" data-q="${esc(`${field}:yes`)}" title="${esc(why || "yes")}">yes</span>`
      : `<span class="tag gray" data-q="${esc(`NOT ${field}:yes`)}" title="no">no</span>`;
  }

  const RELEASE_CLASS = { "open-source": "green", commercial: "blue", unreleased: "orange", unclear: "gray" };

  // ------------------------------------------------------------------ columns
  // key, label, type (text | tags | list | num | date), show (default visible),
  // render(row) -> html, cls (cell class), facet (a value-filter dropdown in
  // the header; default on for tags and list columns). Search can scope to
  // any key.

  const ARTICLE_COLS = [
    { key: "title", label: "Title", show: true, cls: "title-cell", render: (r) => link(r.url, r.title) || DASH },
    { key: "first_author", label: "First author", show: true, cls: "nobreak" },
    { key: "year", label: "Year", type: "num", show: true, facet: true, render: (r) => r.year ?? DASH },
    { key: "venue", label: "Journal / venue", show: true, cls: "wide", aliases: ["journal"], facet: true },
    { key: "publication_form", label: "Form", type: "tags", show: true, render: (r) => tags("publication_form", r.publication_form) },
    { key: "modality", label: "Modality", type: "tags", show: true, render: (r) => tags("modality", r.modality) },
    { key: "task", label: "Task", type: "tags", show: true, render: (r) => tags("task", r.task) },
    { key: "age_groups", label: "Ages", type: "tags", show: true, render: (r) => tags("age_groups", r.age_groups) },
    { key: "clinical_problem", label: "Clinical problem", show: true, cls: "wide", render: (r) => clamp(r.clinical_problem) },
    { key: "release_status", label: "Release", type: "tags", show: true, render: (r) => tags("release_status", r.release_status, (v) => RELEASE_CLASS[v] || "") },
    { key: "citations", label: "Citations", type: "num", show: true, cls: "num", render: (r) => fmtInt(r.citations) },
    { key: "model_name", label: "Model name" },
    { key: "model_family", label: "Model family", cls: "wide", render: (r) => clamp(r.model_family) },
    { key: "model_description", label: "Model description", cls: "wide", render: (r) => clamp(r.model_description) },
    { key: "body_region", label: "Body region", cls: "wide", render: (r) => clamp(r.body_region) },
    { key: "patient_population", label: "Patient population", cls: "wide", render: (r) => clamp(r.patient_population) },
    { key: "study_design", label: "Study design", cls: "wide", render: (r) => clamp(r.study_design) },
    { key: "dataset_size", label: "Dataset size", cls: "wide", render: (r) => clamp(r.dataset_size) },
    { key: "data_source", label: "Data source", type: "tags", render: (r) => tags("data_source", r.data_source) },
    { key: "validation", label: "Validation", type: "tags", render: (r) => tags("validation", r.validation) },
    { key: "headline_result", label: "Headline result", cls: "wide", render: (r) => clamp(r.headline_result) },
    { key: "code_url", label: "Code", render: (r) => (r.code_url ? link(r.code_url, r.code_url.replace(/^https?:\/\/(www\.)?/, "")) : DASH) },
  ];

  const SOFTWARE_COLS = [
    { key: "name", label: "Repository", show: true, cls: "repo-cell", render: (r) => `<b>${link(r.url, r.name)}</b>` },
    { key: "stars", label: "Stars", type: "num", show: true, cls: "num", render: (r) => fmtInt(r.stars) },
    { key: "description", label: "Description", show: true, cls: "wide", render: (r) => clamp(r.description) },
    { key: "updated", label: "Last updated", type: "date", show: true, cls: "nobreak" },
    { key: "created", label: "Created", type: "date", cls: "nobreak" },
    // Last, so the yes / no answer sits at the right edge of the table.
    { key: "pediatric", label: "Pediatric use", show: true, cls: "check-cell", facet: true,
      render: (r) => yesNo("pediatric", r.pediatric === "yes", r.pediatric_evidence) },
  ];

  const NEWS_COLS = [
    { key: "story", label: "Story", show: true, cls: "title-cell", render: (r) => link(r.url, r.story) },
    { key: "date", label: "Date", type: "date", show: true, cls: "nobreak" },
    { key: "source", label: "Source", type: "tags", show: true, render: (r) => tags("source", r.source) },
    { key: "snippet", label: "Snippet", show: true, cls: "wide", render: (r) => clamp(r.snippet) },
    { key: "topics", label: "Topics", type: "list", show: true, render: (r) => tags("topics", r.topics) },
    { key: "players", label: "Companies / tools", type: "list", show: true, render: (r) => tags("players", r.players) },
    { key: "paper", label: "Paper", show: true, cls: "wide", render: (r) => (r.paper ? `<span title="${esc(r.paper_title)}">${link(r.paper_url, r.paper)}</span>` : DASH) },
    { key: "paper_title", label: "Paper title", cls: "wide", render: (r) => clamp(r.paper_title) },
    { key: "issue_title", label: "Issue", cls: "wide", render: (r) => clamp(r.issue_title) },
    { key: "pediatric_terms", label: "Pediatric terms", type: "list", render: (r) => tags("pediatric_terms", r.pediatric_terms) },
    { key: "url", label: "URL", render: (r) => link(r.url, "link") },
  ];

  const FDA_COLS = [
    { key: "device", label: "Device", show: true, cls: "title-cell" },
    { key: "company", label: "Company", show: true, facet: true, render: (r) => tag("company", r.company) },
    { key: "date", label: "Decision date", type: "date", show: true, cls: "nobreak" },
    { key: "submission", label: "Submission", show: true, cls: "nobreak",
      render: (r) => (r.submission ? link(r.submission_url, r.submission) : r.submission_url ? link(r.submission_url, "vendor site") : DASH) },
    { key: "us_status", label: "US status", type: "tags", show: true,
      render: (r) => tags("us_status", r.us_status, (v) => (v === "FDA-authorized" ? "" : "orange")) },
    { key: "earlier_submissions", label: "Earlier authorizations", type: "list", show: true, cls: "nobreak", facet: false,
      render: (r) => (r.earlier_submissions.length ? r.earlier_submissions.map(esc).join("<br>") : DASH) },
    { key: "product_code", label: "Product code", type: "tags", show: true, render: (r) => tags("product_code", r.product_code) },
    { key: "pediatric_status", label: "Pediatric-use screen", facet: true, render: (r) => (r.pediatric_status ? '<span class="tag green" data-q="pediatric_status:=label-positive-candidate">label-positive candidate</span>' : DASH) },
    { key: "pediatric_evidence_pages", label: "Evidence pages", render: (r) => text(r.pediatric_evidence_pages) },
    { key: "curated_product", label: "Curated pediatric product", type: "list", show: true, cls: "wide",
      render: (r) => tags("curated_product", r.curated_product) },
    // Last, so the yes / no answer sits at the right edge of the table.
    { key: "pediatric", label: "Pediatric use", show: true, cls: "check-cell", facet: true,
      render: (r) => yesNo("pediatric", r.pediatric === "yes", r.pediatric_evidence) },
  ];

  const DATASET_COLS = [
    { key: "name", label: "Dataset", show: true, cls: "title-cell" },
    { key: "year", label: "Year", show: true, cls: "nobreak", facet: true },
    { key: "modality", label: "Modality", show: true, cls: "wide" },
    { key: "size", label: "Size", show: true, cls: "wide" },
    { key: "ages", label: "Ages", show: true },
    { key: "access", label: "Access", show: true, facet: true },
    { key: "ref", label: "Reference", show: true },
  ];

  const FILES = {
    articles: { cols: ARTICLE_COLS, sort: { key: "year", order: "desc" } },
    software: { cols: SOFTWARE_COLS, sort: { key: "stars", order: "desc" } },
    news: { cols: NEWS_COLS, sort: { key: "date", order: "desc" } },
    fda: { cols: FDA_COLS, sort: { key: "date", order: "desc" } },
    datasets: { cols: DATASET_COLS, sort: null },
  };

  // --------------------------------------------------------------------- tabs

  const TABS = [
    {
      id: "articles", label: "Articles",
      presets: [
        // The file already holds only the corpus; the filter keeps the tab
        // honest if a future build ships more.
        { id: "included", label: "Included studies", file: "articles", filter: (r) => r.record_type === "included study" },
      ],
      examples: ['bone age', 'modality:MRI AND task:segmentation', 'year>=2024 AND release_status:open-source', 'age_groups:neonate', 'citations>=50 AND validation:external', '(fracture OR trauma) AND NOT modality:CT'],
      intro: (m) => `The ${Number(m.counts.articles).toLocaleString()} primary studies included in the systematic review, with model, modality, population, task and release status read from each abstract. <b>Release “unclear”</b> means the abstract does not say, not that the model is unavailable. <b>Impact</b> is field-normalized (FWCI, else iCite RCR; 1.0 = average paper of that field and year). Recent years undercount because of indexing lag. Snapshot ${m.snapshots.articles}.`,
    },
    {
      id: "software", label: "Open source software",
      presets: [
        { id: "all", label: "All", file: "software" },
      ],
      examples: ['segmentation', 'pediatric:yes', 'stars>=1000', 'updated>=2025', 'pediatric:yes AND stars>=100'],
      intro: (m) => `Repositories from the GitHub leaderboards (searched by topic, plus well-known tools fetched by name; stars as of ${m.snapshots.software}) and every code link stated in a pediatric radiology-AI paper. Code links that are not on a leaderboard have no star count. <b>Pediatric use</b> is yes when the repository came from the pediatric-imaging or bone-age searches, or names a pediatric population itself; hover the yes for which. A general tool that a pediatric study merely used is a no.`,
    },
    {
      id: "news", label: "Newsletters",
      presets: [
        { id: "all", label: "All stories", file: "news" },
      ],
      examples: ['bone age', 'source:"RSNA News"', 'date>=2026-01', 'players:*', 'topics:fracture'],
      intro: (m) => `Newsletter and trade-press stories in which pediatric and AI terms co-occur, with topic tags, the companies or tools named, and the paper a story links to. Not scanned: ${m.news_blocked.map((b) => `${esc(b.name)} (${esc(b.reason)})`).join("; ")}. Snapshot ${m.snapshots.news}.`,
    },
    {
      id: "commercial", label: "Commercial",
      presets: [
        { id: "fda", label: "Commercial radiology AI devices", file: "fda" },
      ],
      examples: ['pediatric:yes', 'company:="GE HealthCare"', 'date>=2025', 'fetal OR pediatric', 'us_status:="not FDA-authorized"'],
      intro: (m) => `The FDA's list of AI-enabled medical devices, Radiology panel only (snapshot ${m.snapshots.fda}; <a href="${esc(m.fda_source)}" target="_blank" rel="noopener">source</a>), one row per device: a device the FDA authorized more than once (a new version or indication) is shown at its most recent authorization, with the earlier ones listed, so the ${Number(m.counts.fda_authorizations).toLocaleString()} authorizations make ${Number(m.counts.fda - m.counts.fda_not_authorized).toLocaleString()} rows. The FDA describes the list as noncomprehensive. The ${Number(m.counts.fda_not_authorized).toLocaleString()} rows marked <b>not FDA-authorized</b> are pediatric products on our curated list that have no US authorization (for example BoneXpert, CE-marked and US research use only). <b>Pediatric use</b> is yes for the ${Number(m.counts.fda_pediatric).toLocaleString()} authorized devices with at least one authorization whose linked label states a pediatric or fetal patient population or intended use (${m.snapshots.fda_pediatric} screen); hover the yes for which. About half are whole scanners whose labels list pediatric imaging as one clinical application, so confirm the current authorization before purchase. <b>Curated pediatric product</b> marks the ${Number(m.counts.products).toLocaleString()} products with a documented pediatric indication reviewed by hand on ${m.snapshots.products}; on an FDA row it is a company-level flag, not a claim about that row's authorization.`,
    },
    {
      id: "datasets", label: "Datasets",
      presets: [{ id: "all", label: "Public pediatric imaging datasets", file: "datasets" }],
      examples: ['MRI', 'access:open', 'fetal'],
      intro: (m) => `Public pediatric imaging datasets, with sizes verified against the primary papers and hosting pages on ${m.snapshots.datasets}.`,
    },
  ];

  // -------------------------------------------------------------------- state

  let META = null;
  const DATA = {}; // file -> rows (objects with _hay)
  const LOADING = {};
  const state = { tab: TABS[0].id, preset: {}, query: {}, sort: {}, rows: [], shown: PAGE, open: new Set() };

  const tabById = (id) => TABS.find((t) => t.id === id) || TABS[0];
  const currentTab = () => tabById(state.tab);
  const currentPreset = () => {
    const t = currentTab();
    return t.presets.find((p) => p.id === state.preset[t.id]) || t.presets[0];
  };
  const currentFile = () => FILES[currentPreset().file];
  const viewKey = () => `${state.tab}/${currentPreset().id}`;

  // Column visibility per file, persisted as {file: [hidden keys]}.
  const COLS_KEY = "pedrad-ai-db.hidden-columns";
  let hidden = {};
  try { hidden = JSON.parse(localStorage.getItem(COLS_KEY) || "{}") || {}; } catch (e) { hidden = {}; }
  function hiddenSet(file) {
    if (!hidden[file]) hidden[file] = FILES[file].cols.filter((c) => !c.show).map((c) => c.key);
    return new Set(hidden[file]);
  }
  function saveHidden(file, set) {
    hidden[file] = [...set];
    try { localStorage.setItem(COLS_KEY, JSON.stringify(hidden)); } catch (e) { /* storage unavailable */ }
    applyColumnVisibility();
  }
  function visibleCols() {
    const file = currentPreset().file;
    const h = hiddenSet(file);
    return FILES[file].cols.filter((c) => !h.has(c.key));
  }
  function applyColumnVisibility() {
    const h = hiddenSet(currentPreset().file);
    $("col-style").textContent = [...h].map((k) => `[data-col="${k}"] { display: none; }`).join("\n");
  }

  // --------------------------------------------------------------------- data

  async function fetchJson(path) {
    const resp = await fetch(path);
    if (!resp.ok) throw new Error(`${path}: ${resp.status} ${resp.statusText}`);
    return resp.json();
  }

  function loadFile(file) {
    if (DATA[file]) return Promise.resolve(DATA[file]);
    if (!LOADING[file]) {
      LOADING[file] = fetchJson(`data/${file}.json`).then((payload) => {
        const cols = FILES[file].cols;
        DATA[file] = payload.rows.map((arr) => {
          const row = {};
          payload.columns.forEach((c, i) => { row[c] = arr[i]; });
          row._hay = S.haystack(row, cols);
          return row;
        });
        return DATA[file];
      });
    }
    return LOADING[file];
  }

  // ------------------------------------------------------------------- render

  function renderTabs() {
    $("tabs").innerHTML = TABS.map((t) => {
      const count = !META ? "" : t.presets.map((p) => p.file)
        .filter((f, i, a) => a.indexOf(f) === i)
        .reduce((n, f) => n + (META.counts[f] || 0), 0);
      return `<button role="tab" data-tab="${t.id}" class="${t.id === state.tab ? "active" : ""}">${esc(t.label)}<span class="count">${count ? Number(count).toLocaleString() : ""}</span></button>`;
    }).join("");
    const active = $("tabs").querySelector("button.active");
    if (active && $("tabs").scrollWidth > $("tabs").clientWidth) active.scrollIntoView({ block: "nearest", inline: "nearest" });
  }

  function renderPresets() {
    const t = currentTab();
    const p = currentPreset();
    if (t.presets.length < 2) { $("presets").innerHTML = ""; return; }
    $("presets").innerHTML = t.presets.map((x) => {
      const rows = DATA[x.file];
      const n = rows ? (x.filter ? rows.filter(x.filter).length : rows.length) : null;
      return `<button data-preset="${x.id}" class="${x.id === p.id ? "active" : ""}">${esc(x.label)}${n !== null ? `<span class="count">${n.toLocaleString()}</span>` : ""}</button>`;
    }).join("");
  }

  function renderIntro() {
    const t = currentTab();
    $("intro").innerHTML = META ? t.intro(META, currentPreset().id) : "";
    const ex = t.examples || [];
    $("examples").innerHTML = ex.map((q) => `<code data-example="${esc(q)}">${esc(q)}</code>`).join(" ");
    $("query").placeholder = ex.length ? `e.g.  ${ex[1] || ex[0]}` : "Search";
    renderFieldsHelp();
  }

  function renderFieldsHelp() {
    const cols = currentFile().cols;
    const typeLabel = { num: "number: = > >= < <=", date: "date: 2025, 2025-06, >=2025-06-01", list: "list: substring, := exact item", tags: "text: substring, := exact value" };
    $("fields-help").innerHTML =
      `<p class="muted" style="margin:0 0 6px">Bare words search every column. Combine with AND / OR / NOT and parentheses. <code>field:*</code> means the field is filled. Click any tag in the table to filter by it, or use a column's ▾ to pick values from a list; either way the filter is written into the search.</p>` +
      `<table>${cols.map((c) => `<tr><td class="fname">${c.key}</td><td>${esc(c.label)}</td><td class="muted">${typeLabel[c.type] || "text: substring, := exact value"}</td></tr>`).join("")}</table>`;
  }

  function renderColumnsMenu() {
    const file = currentPreset().file;
    const h = hiddenSet(file);
    $("columns-list").innerHTML = "";
    for (const col of FILES[file].cols) {
      const label = document.createElement("label");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = !h.has(col.key);
      cb.addEventListener("change", () => {
        const s = hiddenSet(file);
        if (cb.checked) s.delete(col.key); else s.add(col.key);
        saveHidden(file, s);
      });
      label.appendChild(cb);
      label.appendChild(document.createTextNode(col.label));
      $("columns-list").appendChild(label);
    }
  }

  function currentSort() {
    return state.sort[viewKey()] || currentFile().sort;
  }

  function renderHeader() {
    const sort = currentSort();
    const active = new Set(queryClauses().filter((c) => c.filter).map((c) => c.filter.key));
    $("header-row").innerHTML = `<th class="expand-cell"></th>` + currentFile().cols.map((c) => {
      const arrow = sort && sort.key === c.key ? ` <span class="arrow">${sort.order === "asc" ? "▲" : "▼"}</span>` : "";
      const on = active.has(c.key);
      const filt = facetable(c)
        ? `<button class="filt${on ? " on" : ""}" data-filter="${c.key}" title="${on ? "Filtered: change" : "Filter by value"}" aria-label="Filter ${esc(c.label)} by value">▾</button>`
        : "";
      return `<th data-col="${c.key}" data-sort="${c.key}" class="sortable${c.cls === "check-cell" ? " check-cell" : ""}">${esc(c.label)}${arrow}${filt}</th>`;
    }).join("");
  }

  // ----------------------------------------------------------- column filters
  // Excel-style value lists behind each header's ▾. The search box stays the
  // one source of truth: OK writes the choice into it as a single clause for
  // that column (see search.js), so a filtered view is still a plain query
  // that the link, the row count and the CSV export all follow, and editing
  // the query by hand moves the checkboxes.

  const facetable = (c) => c.facet ?? (c.type === "tags" || c.type === "list");
  const FP_MAX = 1000; // values listed at once; the search box narrows the rest
  let fp = null; // the open popup: {col, items: [{v, label, n, on}], single}

  // Top-level clauses of the current query ([] when it does not parse).
  function queryClauses() {
    try { return S.topClauses($("query").value, currentFile().cols); } catch (e) { return []; }
  }

  function blankLabel(col) { return col.cls === "check-cell" ? "no" : "(blank)"; }

  function openFilter(key, btn) {
    const preset = currentPreset();
    const cols = currentFile().cols;
    const col = cols.find((c) => c.key === key);
    const all = DATA[preset.file];
    if (!col || !all) return;
    let clauses;
    try { clauses = S.topClauses($("query").value, cols); } catch (e) {
      setStatus(`Fix the search before filtering by column: ${e.message}`, true);
      return;
    }
    const mine = clauses.filter((c) => c.filter && c.filter.key === key).map((c) => c.filter);
    const allowed = (v) => mine.every((f) => (f.include ? f.include.has(v) : !f.exclude.has(v)));

    // Count values over the rows every *other* filter lets through, as Excel does.
    const pred = S.buildPredicate(S.joinClauses(clauses.filter((c) => !(c.filter && c.filter.key === key))), cols);
    let rows = preset.filter ? all.filter(preset.filter) : all;
    if (pred) rows = rows.filter(pred);
    const counts = new Map();
    const bump = (v, label) => {
      const x = counts.get(v);
      if (x) x.n += 1; else counts.set(v, { v, label, n: 1 });
    };
    for (const r of rows) {
      const vals = S.cellValues(col, r);
      if (!vals.length) bump(S.BLANK, blankLabel(col));
      for (const raw of new Set(vals)) bump(raw.toLowerCase(), raw);
    }
    // A value the filter keeps stays listed (at 0) even if other filters hide it.
    for (const f of mine) for (const v of f.include || []) {
      if (!counts.has(v)) counts.set(v, { v, label: v === S.BLANK ? blankLabel(col) : v, n: 0 });
    }
    const byLabel = (a, b) => a.label.localeCompare(b.label, undefined, { sensitivity: "base", numeric: true });
    const items = [...counts.values()].sort((a, b) =>
      (a.v === S.BLANK) - (b.v === S.BLANK)
      || (col.type === "num" ? Number(b.label) - Number(a.label) : b.n - a.n || byLabel(a, b)));
    items.forEach((it, i) => { it.i = i; it.on = allowed(it.v); });

    fp = { col, btn, items, single: all.every((r) => S.cellValues(col, r).length <= 1) };
    const pop = $("filter-pop");
    $("fp-title").textContent = col.label;
    $("fp-search").value = "";
    $("fp-clear").hidden = !mine.length;
    renderFilterList();
    pop.hidden = false;
    placeFilter();
    $("fp-search").focus({ preventScroll: true });
  }

  // Under the header's ▾; re-run when the table scrolls sideways.
  function placeFilter() {
    const pop = $("filter-pop");
    const b = fp.btn.getBoundingClientRect();
    const maxLeft = window.scrollX + document.documentElement.clientWidth - pop.offsetWidth - 8;
    pop.style.left = `${Math.max(window.scrollX + 8, Math.min(window.scrollX + b.left, maxLeft))}px`;
    pop.style.top = `${window.scrollY + b.bottom + 4}px`;
  }

  function visibleItems() {
    const q = $("fp-search").value.trim().toLowerCase();
    return q ? fp.items.filter((it) => it.label.toLowerCase().includes(q)) : fp.items;
  }

  function renderFilterList() {
    const vis = visibleItems();
    const shown = vis.slice(0, FP_MAX);
    $("fp-list").innerHTML = shown.length
      ? shown.map((it) => `<label${it.v === S.BLANK ? ' class="blank"' : ""}><input type="checkbox" data-i="${it.i}"${it.on ? " checked" : ""}><span class="fp-label">${esc(it.label)}</span><span class="fp-n">${it.n.toLocaleString()}</span></label>`).join("")
        + (vis.length > FP_MAX ? `<div class="fp-note">${(vis.length - FP_MAX).toLocaleString()} more; type to narrow</div>` : "")
      : '<div class="fp-note">No values match.</div>';
    updateFilterControls(vis);
  }

  function updateFilterControls(vis = visibleItems()) {
    const on = vis.filter((it) => it.on).length;
    const all = $("fp-all");
    all.checked = vis.length > 0 && on === vis.length;
    all.indeterminate = on > 0 && on < vis.length;
    $("fp-all-label").textContent = $("fp-search").value.trim() ? "Select all search results" : "Select all";
    $("fp-ok").disabled = !vis.some((it) => it.on);
  }

  function closeFilter() {
    fp = null;
    $("filter-pop").hidden = true;
  }

  // The clause for the checked values: a list of values to keep, or, for a
  // one-value-per-row column where that is shorter, the values to drop. (A
  // row with several values is kept if any is checked, so dropping a value
  // is only the same thing when no row has two.) With a search typed, only
  // the checked values among the results count, as in Excel.
  function filterClause() {
    const vis = new Set(visibleItems());
    const on = fp.items.filter((it) => it.on && vis.has(it));
    const off = fp.items.filter((it) => !(it.on && vis.has(it)));
    if (!off.length) return "";
    const f = fp.col.key;
    const lit = (it) => `${f}:="${it.label.replace(/"/g, "")}"`;
    if (fp.single && off.length < on.length) {
      const ts = off.map((it) => (it.v === S.BLANK ? `${f}:*` : `NOT ${lit(it)}`));
      return ts.length > 1 ? `(${ts.join(" AND ")})` : ts[0];
    }
    const ts = on.map((it) => (it.v === S.BLANK ? `NOT ${f}:*` : lit(it)));
    return ts.length > 1 ? `(${ts.join(" OR ")})` : ts[0];
  }

  function applyFilter(clause) {
    const key = fp.col.key;
    closeFilter();
    let clauses;
    try { clauses = S.topClauses($("query").value, currentFile().cols); } catch (e) { return; }
    const kept = clauses.filter((c) => !(c.filter && c.filter.key === key));
    if (clause) kept.push({ text: clause });
    $("query").value = S.joinClauses(kept);
    run();
  }

  function cellHtml(c, r) {
    if (c.render) return c.render(r);
    return S.isEmpty(r[c.key]) ? DASH : esc(S.asText(r[c.key]));
  }

  function detailHtml(r) {
    const cols = currentFile().cols.filter((c) => !S.isEmpty(r[c.key]));
    return `<div class="detail-grid">${cols.map((c) => {
      const v = r[c.key];
      let html;
      if (c.key === "papers") html = c.render(r);
      else if (/url$/.test(c.key) || c.key === "doi" || c.key === "pmid" || c.key === "arxiv_id" || c.key === "submission") html = c.render(r);
      else if (c.type === "list" || c.type === "tags") html = c.render ? c.render(r) : esc(S.asText(v));
      else if (c.type === "num") html = esc(String(v));
      else html = esc(S.asText(v));
      return `<div class="k">${esc(c.label)}</div><div class="v">${html}</div>`;
    }).join("")}</div>`;
  }

  function renderRows() {
    const cols = currentFile().cols;
    const body = $("results-body");
    const rows = state.rows.slice(0, state.shown);
    if (!rows.length) {
      body.innerHTML = `<tr><td colspan="${cols.length + 1}" class="muted">No rows match.</td></tr>`;
    } else {
      const html = [];
      rows.forEach((r, i) => {
        const open = state.open.has(r);
        html.push(`<tr class="row${open ? " open" : ""}" data-i="${i}"><td class="expand-cell"><button class="expand" data-i="${i}" title="Show every field" aria-label="Show every field">▶</button></td>` +
          cols.map((c) => `<td data-col="${c.key}"${c.cls ? ` class="${c.cls}"` : ""}>${cellHtml(c, r)}</td>`).join("") + "</tr>");
        if (open) html.push(`<tr class="detail"><td colspan="${cols.length + 1}">${detailHtml(r)}</td></tr>`);
      });
      body.innerHTML = html.join("");
    }
    const left = state.rows.length - rows.length;
    $("more").innerHTML = left > 0
      ? `<button class="btn" id="more-btn">Show ${Math.min(PAGE, left).toLocaleString()} more</button><button class="btn" id="all-btn">Show all ${state.rows.length.toLocaleString()}</button><span>${left.toLocaleString()} not shown</span>`
      : "";
  }

  // ------------------------------------------------------------------- search

  function setStatus(msg, err) {
    $("status").textContent = msg;
    $("status").className = err ? "err" : "";
  }

  async function run({ resetPage = true } = {}) {
    const preset = currentPreset();
    const t = currentTab();
    renderTabs();
    renderIntro();
    applyColumnVisibility();
    renderColumnsMenu();
    renderHeader();
    let rows = DATA[preset.file];
    if (!rows) {
      setStatus("Loading…");
      $("results-body").innerHTML = "";
      $("more").innerHTML = "";
      try { rows = await loadFile(preset.file); } catch (e) { setStatus(`Failed to load data: ${e.message || e}`, true); return; }
      if (currentPreset() !== preset || currentTab() !== t) return; // user moved on
    }
    renderPresets();
    const q = $("query").value;
    state.query[viewKey()] = q;
    let pred = null;
    try { pred = S.buildPredicate(q, currentFile().cols); } catch (e) {
      setStatus(`Query error: ${e.message}`, true);
      state.rows = [];
      renderRows();
      return;
    }
    let out = preset.filter ? rows.filter(preset.filter) : rows;
    const base = out.length;
    if (pred) out = out.filter(pred);
    const sort = currentSort();
    if (sort) {
      const col = currentFile().cols.find((c) => c.key === sort.key);
      if (col) out = S.sortRows(out, col, sort.order);
    }
    state.rows = out;
    if (resetPage) { state.shown = PAGE; state.open = new Set(); }
    setStatus(pred ? `${out.length.toLocaleString()} of ${base.toLocaleString()} rows match.` : `${out.length.toLocaleString()} rows.`);
    renderRows();
    writeHash();
  }

  // ---------------------------------------------------------------- URL hash
  // #tab=articles&view=included&q=bone%20age  (shareable links)

  function writeHash() {
    const p = new URLSearchParams();
    p.set("tab", state.tab);
    p.set("view", currentPreset().id);
    const q = $("query").value.trim();
    if (q) p.set("q", q);
    const h = `#${p.toString()}`;
    if (location.hash !== h) history.replaceState(null, "", h);
  }

  function readHash() {
    const p = new URLSearchParams(location.hash.slice(1));
    const t = tabById(p.get("tab"));
    state.tab = t.id;
    if (p.get("view")) state.preset[t.id] = p.get("view");
    $("query").value = p.get("q") || "";
  }

  function switchTo(tabId, presetId, query) {
    state.query[viewKey()] = $("query").value;
    state.tab = tabId;
    if (presetId) state.preset[tabId] = presetId;
    $("query").value = query !== undefined ? query : (state.query[viewKey()] || "");
    $("columns-panel").hidden = true;
    closeFilter();
    run();
  }

  function addToQuery(term) {
    const q = $("query").value.trim();
    if (q.split(/\s+AND\s+/).includes(term) || q.split(/\s+/).includes(term)) return;
    $("query").value = q ? `${q} AND ${term}` : term;
    run();
  }

  // ------------------------------------------------------------------- export

  function csvField(v) {
    if (v === null || v === undefined) return "";
    const s = Array.isArray(v) ? v.join("; ") : String(v);
    return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  }

  function exportCsv() {
    const cols = currentFile().cols.map((c) => c.key);
    const lines = [cols.join(",")].concat(state.rows.map((r) => cols.map((c) => csvField(r[c])).join(",")));
    const blob = new Blob(["﻿" + lines.join("\r\n")], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `pedrad_ai_${state.tab}_${currentPreset().id}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  }

  // ------------------------------------------------------------------- events

  $("tabs").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-tab]");
    if (b && b.dataset.tab !== state.tab) switchTo(b.dataset.tab);
  });
  $("presets").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-preset]");
    if (b) switchTo(state.tab, b.dataset.preset);
  });
  $("search-btn").addEventListener("click", () => run());
  $("clear-btn").addEventListener("click", () => { $("query").value = ""; run(); });
  $("query").addEventListener("keydown", (e) => { if (e.key === "Enter") run(); });
  $("csv-btn").addEventListener("click", exportCsv);
  $("examples").addEventListener("click", (e) => {
    const c = e.target.closest("[data-example]");
    if (c) { $("query").value = c.dataset.example; run(); }
  });
  $("header-row").addEventListener("click", (e) => {
    const fb = e.target.closest("button[data-filter]");
    if (fb) {
      e.stopPropagation();
      if (fp && fp.col.key === fb.dataset.filter) closeFilter(); else openFilter(fb.dataset.filter, fb);
      return;
    }
    const th = e.target.closest("th[data-sort]");
    if (!th) return;
    const cur = currentSort();
    const col = currentFile().cols.find((c) => c.key === th.dataset.sort);
    const firstOrder = col.type === "num" || col.type === "date" ? "desc" : "asc";
    state.sort[viewKey()] = cur && cur.key === col.key
      ? { key: col.key, order: cur.order === "asc" ? "desc" : "asc" }
      : { key: col.key, order: firstOrder };
    run({ resetPage: false });
  });
  $("results-body").addEventListener("click", (e) => {
    const go = e.target.closest("[data-goto]");
    if (go) { e.preventDefault(); switchTo(go.dataset.goto, go.dataset.preset, go.dataset.q); return; }
    const t = e.target.closest("[data-q]");
    if (t) { addToQuery(t.dataset.q); return; }
    const x = e.target.closest(".expand");
    if (x) {
      const r = state.rows[Number(x.dataset.i)];
      if (state.open.has(r)) state.open.delete(r); else state.open.add(r);
      renderRows();
    }
  });
  $("more").addEventListener("click", (e) => {
    if (e.target.id === "more-btn") state.shown += PAGE;
    else if (e.target.id === "all-btn") state.shown = state.rows.length;
    else return;
    renderRows();
  });
  $("columns-btn").addEventListener("click", (e) => { e.stopPropagation(); $("columns-panel").hidden = !$("columns-panel").hidden; });
  const setCols = (fn) => { const file = currentPreset().file; saveHidden(file, fn(file)); renderColumnsMenu(); };
  $("columns-all").addEventListener("click", () => setCols(() => new Set()));
  $("columns-none").addEventListener("click", () => setCols((f) => new Set(FILES[f].cols.map((c) => c.key))));
  $("columns-default").addEventListener("click", () => setCols((f) => new Set(FILES[f].cols.filter((c) => !c.show).map((c) => c.key))));
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".columns-menu")) $("columns-panel").hidden = true;
    if (fp && !e.target.closest("#filter-pop")) closeFilter();
  });
  $("fp-search").addEventListener("input", renderFilterList);
  $("fp-search").addEventListener("keydown", (e) => { if (e.key === "Enter" && !$("fp-ok").disabled) applyFilter(filterClause()); });
  $("fp-list").addEventListener("change", (e) => {
    const it = fp.items[Number(e.target.dataset.i)];
    if (it) it.on = e.target.checked;
    updateFilterControls();
  });
  $("fp-all").addEventListener("change", (e) => {
    visibleItems().forEach((it) => { it.on = e.target.checked; });
    renderFilterList();
  });
  $("fp-ok").addEventListener("click", () => applyFilter(filterClause()));
  $("fp-cancel").addEventListener("click", closeFilter);
  $("fp-clear").addEventListener("click", () => applyFilter(""));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && fp) closeFilter(); });
  window.addEventListener("resize", () => { if (fp) placeFilter(); });
  document.querySelector(".table-wrap").addEventListener("scroll", () => { if (fp) placeFilter(); });
  $("help-toggle").addEventListener("click", () => {
    const h = $("fields-help");
    const showing = h.style.display === "block";
    h.style.display = showing ? "none" : "block";
    $("help-toggle").textContent = showing ? "show fields" : "hide fields";
  });
  window.addEventListener("hashchange", () => { readHash(); run(); });

  // --------------------------------------------------------------------- boot

  readHash();
  run();
  fetchJson("data/meta.json").then((m) => {
    META = m;
    $("footer").innerHTML = `Built ${esc(m.built_on)} from the processed data of the <a href="https://github.com/josephrich98/pediatric_radiology_ai" target="_blank" rel="noopener">pediatric_radiology_ai</a> pipeline (<code>python scripts/build_site.py</code>). Counts reflect what public indexes held on each snapshot date; the current year is partial.`;
    renderTabs();
    renderIntro();
  }).catch(() => { /* tables still work without meta */ });
})();
