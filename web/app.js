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

  const RECORD_CLASS = {
    "included study": "green", "review / editorial": "blue", "screened out": "gray",
    "Embase, not retrieved": "gray",
  };
  const RELEASE_CLASS = { "open-source": "green", commercial: "blue", unreleased: "orange", unclear: "gray" };

  // ------------------------------------------------------------------ columns
  // key, label, type (text | tags | list | num | date), show (default visible),
  // render(row) -> html, cls (cell class). Search can scope to any key.

  const ARTICLE_COLS = [
    { key: "title", label: "Title", show: true, cls: "title-cell", render: (r) => link(r.url, r.title) || DASH },
    { key: "first_author", label: "First author", show: true, cls: "nobreak" },
    { key: "year", label: "Year", type: "num", show: true, render: (r) => r.year ?? DASH },
    { key: "venue", label: "Journal / venue", show: true, cls: "wide", aliases: ["journal"] },
    { key: "publication_form", label: "Form", type: "tags", show: true, render: (r) => tags("publication_form", r.publication_form) },
    { key: "record_type", label: "Record", type: "tags", show: true, render: (r) => tags("record_type", r.record_type, (v) => RECORD_CLASS[v] || "") },
    { key: "modality", label: "Modality", type: "tags", show: true, render: (r) => tags("modality", r.modality) },
    { key: "task", label: "Task", type: "tags", show: true, render: (r) => tags("task", r.task) },
    { key: "age_groups", label: "Ages", type: "tags", show: true, render: (r) => tags("age_groups", r.age_groups) },
    { key: "clinical_problem", label: "Clinical problem", show: true, cls: "wide", render: (r) => clamp(r.clinical_problem) },
    { key: "release_status", label: "Release", type: "tags", show: true, render: (r) => tags("release_status", r.release_status, (v) => RELEASE_CLASS[v] || "") },
    { key: "impact", label: "Impact", type: "num", show: true, cls: "num", render: (r) => (typeof r.impact === "number" ? `${fmtNum(r.impact)} <span class="muted">${esc((r.impact_measure || "").toUpperCase())}</span>` : DASH) },
    { key: "citations", label: "Citations", type: "num", show: true, cls: "num", render: (r) => fmtInt(r.citations) },
    { key: "citations_per_year", label: "Citations / yr", type: "num", cls: "num", render: (r) => fmtNum(r.citations_per_year, 1) },
    { key: "rcr", label: "RCR", type: "num", cls: "num", render: (r) => fmtNum(r.rcr) },
    { key: "fwci", label: "FWCI", type: "num", cls: "num", render: (r) => fmtNum(r.fwci) },
    { key: "nih_percentile", label: "NIH percentile", type: "num", cls: "num", render: (r) => fmtNum(r.nih_percentile, 1) },
    { key: "impact_measure", label: "Impact measure" },
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
    { key: "release_evidence", label: "Release evidence", cls: "wide", render: (r) => clamp(r.release_evidence) },
    { key: "exclusion_reason", label: "Exclusion reason", cls: "wide", render: (r) => clamp(r.exclusion_reason) },
    { key: "scope", label: "Scope", type: "tags", render: (r) => tags("scope", r.scope) },
    { key: "conference_venue", label: "Venue table", type: "tags", render: (r) => tags("conference_venue", r.conference_venue) },
    { key: "top_lists", label: "Most-cited lists", type: "tags", render: (r) => tags("top_lists", r.top_lists) },
    { key: "doi", label: "DOI", render: (r) => (r.doi ? link(`https://doi.org/${r.doi}`, r.doi) : DASH) },
    { key: "pmid", label: "PMID", render: (r) => (r.pmid ? link(`https://pubmed.ncbi.nlm.nih.gov/${r.pmid}/`, r.pmid) : DASH) },
    { key: "arxiv_id", label: "arXiv", render: (r) => (r.arxiv_id ? link(`https://arxiv.org/abs/${r.arxiv_id}`, r.arxiv_id) : DASH) },
    { key: "publication_types", label: "Publication types", cls: "wide", render: (r) => clamp(r.publication_types) },
    { key: "search_source", label: "Found via", type: "tags", render: (r) => tags("search_source", r.search_source) },
    { key: "source_files", label: "Source files", cls: "wide", render: (r) => clamp(r.source_files) },
    { key: "citations_source", label: "Citation index" },
    { key: "record_id", label: "Record ID", cls: "nobreak" },
    { key: "url", label: "URL", render: (r) => (r.url ? link(r.url, "link") : DASH) },
  ];

  const SOFTWARE_COLS = [
    { key: "name", label: "Repository", show: true, cls: "repo-cell", render: (r) => `<b>${link(r.url, r.name)}</b>` },
    { key: "stars", label: "Stars", type: "num", show: true, cls: "num", render: (r) => fmtInt(r.stars) },
    { key: "forks", label: "Forks", type: "num", cls: "num", render: (r) => fmtInt(r.forks) },
    { key: "description", label: "Description", show: true, cls: "wide", render: (r) => clamp(r.description) },
    { key: "lists", label: "Leaderboards", type: "list", show: true, render: (r) => tags("lists", r.lists) },
    { key: "source", label: "Source", type: "tags", show: true, render: (r) => tags("source", r.source) },
    { key: "papers", label: "Linked papers", type: "list", show: true, cls: "wide",
      render: (r) => (r.papers.length ? `<ul class="paper-list">${r.papers.map((t, i) => `<li>${link(r.paper_urls[i], t)}${r.paper_years[i] ? ` <span class="muted">(${r.paper_years[i]})</span>` : ""}</li>`).join("")}</ul>` : DASH) },
    { key: "n_papers", label: "# papers", type: "num", cls: "num", render: (r) => fmtInt(r.n_papers) },
    { key: "language", label: "Language", type: "tags", show: true, render: (r) => tags("language", r.language) },
    { key: "topics", label: "Topics", type: "list", cls: "wide", render: (r) => tags("topics", r.topics) },
    { key: "updated", label: "Last updated", type: "date", show: true, cls: "nobreak" },
    { key: "created", label: "Created", type: "date", cls: "nobreak" },
    { key: "host", label: "Host", type: "tags", render: (r) => tags("host", r.host) },
    { key: "url", label: "URL", render: (r) => link(r.url, "link") },
  ];

  const NEWS_COLS = [
    { key: "date", label: "Date", type: "date", show: true, cls: "nobreak" },
    { key: "source", label: "Source", type: "tags", show: true, render: (r) => tags("source", r.source) },
    { key: "story", label: "Story", show: true, cls: "title-cell", render: (r) => link(r.url, r.story) },
    { key: "snippet", label: "Snippet", show: true, cls: "wide", render: (r) => clamp(r.snippet) },
    { key: "topics", label: "Topics", type: "list", show: true, render: (r) => tags("topics", r.topics) },
    { key: "players", label: "Companies / tools", type: "list", show: true, render: (r) => tags("players", r.players) },
    { key: "paper", label: "Paper", show: true, cls: "wide", render: (r) => (r.paper ? `<span title="${esc(r.paper_title)}">${link(r.paper_url, r.paper)}</span>` : DASH) },
    { key: "paper_title", label: "Paper title", cls: "wide", render: (r) => clamp(r.paper_title) },
    { key: "issue_title", label: "Issue", cls: "wide", render: (r) => clamp(r.issue_title) },
    { key: "pediatric_terms", label: "Pediatric terms", type: "list", render: (r) => tags("pediatric_terms", r.pediatric_terms) },
    { key: "ai_terms", label: "AI terms", type: "list", render: (r) => tags("ai_terms", r.ai_terms) },
    { key: "year", label: "Year", type: "num" },
    { key: "url", label: "URL", render: (r) => link(r.url, "link") },
  ];

  const PRODUCT_COLS = [
    { key: "vendor", label: "Company", show: true, cls: "nobreak", render: (r) => `<b>${esc(r.vendor)}</b>` },
    { key: "product", label: "Product", show: true, render: (r) => (r.url ? link(r.url, r.product) : esc(r.product)) },
    { key: "modality", label: "Modality", type: "tags", show: true, render: (r) => tags("modality", r.modality) },
    { key: "task", label: "Functions", show: true, cls: "wide", render: (r) => text(r.task) },
    { key: "pediatric", label: "Pediatric / regulatory scope", show: true, cls: "wide", render: (r) => text(r.pediatric) },
    { key: "fda_entries", label: "Company-wide FDA AI entries", type: "num", show: true, cls: "num",
      render: (r) => {
        if (!r.fda_entries) return '<span class="muted">not listed</span>';
        const q = r.fda_companies.map((c) => `company:=${quoteVal(c)}`).join(" OR ");
        return `<a href="#" data-goto="commercial" data-preset="fda" data-q="${esc(q)}" title="Show these entries in the FDA device list">${r.fda_entries}</a> <span class="muted">(${esc(r.fda_years)})</span>`;
      } },
    { key: "fda_years", label: "FDA years", cls: "nobreak" },
    { key: "fda_companies", label: "FDA company names", type: "list", render: (r) => tags("fda_companies", r.fda_companies) },
    { key: "url", label: "URL", render: (r) => (r.url ? link(r.url, "link") : DASH) },
  ];

  const FDA_COLS = [
    { key: "date", label: "Decision date", type: "date", show: true, cls: "nobreak" },
    { key: "device", label: "Device", show: true, cls: "title-cell" },
    { key: "company", label: "Company", show: true, render: (r) => tag("company", r.company) },
    { key: "submission", label: "Submission", show: true, cls: "nobreak", render: (r) => link(r.submission_url, r.submission) },
    { key: "product_code", label: "Product code", type: "tags", show: true, render: (r) => tags("product_code", r.product_code) },
    { key: "pediatric_name", label: "Pediatric term in name", show: true, render: (r) => (r.pediatric_name ? '<span class="tag green" data-q="pediatric_name:yes">yes</span>' : "") },
    { key: "year", label: "Year", type: "num" },
    { key: "company_full", label: "Company (as filed)", cls: "wide" },
  ];

  const DATASET_COLS = [
    { key: "name", label: "Dataset", show: true, cls: "title-cell" },
    { key: "year", label: "Year", show: true, cls: "nobreak" },
    { key: "modality", label: "Modality", show: true, cls: "wide" },
    { key: "size", label: "Size", show: true, cls: "wide" },
    { key: "ages", label: "Ages", show: true },
    { key: "access", label: "Access", show: true },
    { key: "ref", label: "Reference", show: true },
  ];

  const FILES = {
    articles: { cols: ARTICLE_COLS, sort: { key: "year", order: "desc" } },
    software: { cols: SOFTWARE_COLS, sort: { key: "stars", order: "desc" } },
    news: { cols: NEWS_COLS, sort: { key: "date", order: "desc" } },
    products: { cols: PRODUCT_COLS, sort: null },
    fda: { cols: FDA_COLS, sort: { key: "date", order: "desc" } },
    datasets: { cols: DATASET_COLS, sort: null },
  };

  // --------------------------------------------------------------------- tabs

  const notScreened = (r) => r.record_type !== "screened out" && r.record_type !== "Embase, not retrieved";

  const TABS = [
    {
      id: "articles", label: "Articles",
      presets: [
        { id: "included", label: "Included studies", file: "articles", filter: (r) => r.record_type === "included study" },
        { id: "journal", label: "Journal articles", file: "articles", filter: (r) => notScreened(r) && r.publication_form === "journal article" },
        { id: "preprint", label: "Preprints", file: "articles", filter: (r) => notScreened(r) && r.publication_form === "preprint" },
        { id: "conference", label: "Conference papers", file: "articles", filter: (r) => notScreened(r) && r.publication_form === "conference paper" },
        { id: "all", label: "All records, incl. screened out", file: "articles" },
      ],
      examples: ['bone age', 'modality:MRI AND task:segmentation', 'year>=2024 AND release_status:open-source', 'age_groups:neonate', 'impact>=2 AND validation:external', '(fracture OR trauma) AND NOT modality:CT'],
      intro: (m) => `Every paper record the project holds: journal articles, preprints and conference papers. <b>Included studies</b> is the systematic-review corpus (primary pediatric radiology-AI studies), with model, modality, population, task and release status read from each abstract. <b>Release “unclear”</b> means the abstract does not say, not that the model is unavailable. <b>Impact</b> is field-normalized (FWCI, else iCite RCR; 1.0 = average paper of that field and year). Recent years undercount because of indexing lag. Snapshot ${m.snapshots.articles}.`,
    },
    {
      id: "software", label: "Open-source software",
      presets: [
        { id: "all", label: "All", file: "software" },
        { id: "papers", label: "Linked to papers", file: "software", filter: (r) => r.n_papers > 0 },
        { id: "known", label: "Well-known tools", file: "software", filter: (r) => r.lists.includes("well-known tool") },
        { id: "pediatric", label: "Pediatric / bone age", file: "software", filter: (r) => r.lists.includes("pediatric imaging AI") || r.lists.includes("bone age") },
      ],
      examples: ['segmentation', 'stars>=1000', 'lists:"bone age"', 'language:Python AND updated>=2025', 'papers:* AND host:GitHub'],
      intro: (m) => `Repositories from the GitHub leaderboards (searched by topic, plus well-known tools fetched by name; stars as of ${m.snapshots.software}) and every code link stated in a pediatric radiology-AI paper. Code links that are not on a leaderboard have no star count.`,
    },
    {
      id: "news", label: "Newsletters",
      presets: [
        { id: "all", label: "All stories", file: "news" },
        { id: "paper", label: "With a linked paper", file: "news", filter: (r) => !!r.paper },
      ],
      examples: ['bone age', 'source:"RSNA News"', 'date>=2026-01', 'players:*', 'topics:fracture'],
      intro: (m) => `Newsletter and trade-press stories in which pediatric and AI terms co-occur, with topic tags, the companies or tools named, and the paper a story links to. Not scanned: ${m.news_blocked.map((b) => `${esc(b.name)} (${esc(b.reason)})`).join("; ")}. Snapshot ${m.snapshots.news}.`,
    },
    {
      id: "commercial", label: "Commercial",
      presets: [
        { id: "products", label: "Pediatric products (curated)", file: "products" },
        { id: "fda", label: "FDA AI-enabled radiology devices", file: "fda" },
        { id: "fda-pediatric", label: "FDA devices with a pediatric term in the name", file: "fda", filter: (r) => r.pediatric_name === "yes" },
      ],
      examplesByPreset: {
        products: ['bone age', 'modality:MRI', 'fda_entries>=10'],
        fda: ['company:="GE HealthCare"', 'date>=2025', 'fetal OR pediatric', 'submission:DEN'],
      },
      intro: (m, preset) => preset === "products"
        ? `Selected commercial products with a pediatric indication or documented pediatric use, one row per company product, checked against vendor and FDA sources on ${m.snapshots.products}. <b>Company-wide FDA AI entries</b> counts every radiology-panel entry for that company in the FDA snapshot (${m.snapshots.fda}), including versions and unrelated products; it is not a count of this product or of pediatric indications. Click a count to see the entries.`
        : `The FDA's list of AI-enabled medical devices, Radiology panel only (snapshot ${m.snapshots.fda}; <a href="${esc(m.fda_source)}" target="_blank" rel="noopener">source</a>). One row per authorization, so a company appears once per device or version. The FDA describes the list as noncomprehensive. “Pediatric term in name” is a name match (e.g. pediatric, bone age, fetal), not an indication.`,
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
      const n = t.presets.map((p) => p.file).filter((f, i, a) => a.indexOf(f) === i)
        .reduce((s, f) => s + ((META && META.counts[f]) || 0), 0);
      const count = t.id === "commercial" ? (META ? META.counts.products : "") : n;
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
    const ex = (t.examplesByPreset && t.examplesByPreset[currentPreset().file]) || t.examples || [];
    $("examples").innerHTML = ex.map((q) => `<code data-example="${esc(q)}">${esc(q)}</code>`).join(" ");
    $("query").placeholder = ex.length ? `e.g.  ${ex[1] || ex[0]}` : "Search";
    renderFieldsHelp();
  }

  function renderFieldsHelp() {
    const cols = currentFile().cols;
    const typeLabel = { num: "number: = > >= < <=", date: "date: 2025, 2025-06, >=2025-06-01", list: "list: substring, := exact item", tags: "text: substring, := exact value" };
    $("fields-help").innerHTML =
      `<p class="muted" style="margin:0 0 6px">Bare words search every column. Combine with AND / OR / NOT and parentheses. <code>field:*</code> means the field is filled. Click any tag in the table to filter by it.</p>` +
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
    $("header-row").innerHTML = `<th class="expand-cell"></th>` + currentFile().cols.map((c) => {
      const arrow = sort && sort.key === c.key ? ` <span class="arrow">${sort.order === "asc" ? "▲" : "▼"}</span>` : "";
      return `<th data-col="${c.key}" data-sort="${c.key}" class="sortable">${esc(c.label)}${arrow}</th>`;
    }).join("");
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
      else if (/url$/.test(c.key) || c.key === "doi" || c.key === "pmid" || c.key === "arxiv_id" || c.key === "submission" || c.key === "fda_entries") html = c.render(r);
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
    run();
  }

  function addToQuery(term) {
    const q = $("query").value.trim();
    if (q.split(/\s+AND\s+|\s+/).includes(term)) return;
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
  document.addEventListener("click", (e) => { if (!e.target.closest(".columns-menu")) $("columns-panel").hidden = true; });
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
