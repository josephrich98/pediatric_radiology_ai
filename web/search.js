/*
 * Boolean search over one table, in the browser.
 *
 * Grammar ported from conference-agent's search.js, made generic: instead of a
 * fixed field registry, each tab passes its column definitions, and the column
 * type decides how a scoped term compares.
 *
 *   bone age                   both words, anywhere in the row (implicit AND)
 *   "bone age"                 the phrase
 *   modality:MRI               substring of one column (case-insensitive)
 *   company:="GE HealthCare"   whole value equals (case-insensitive)
 *   year>=2023  citations>100  numeric comparison (number columns)
 *   date:2026-05  date>2025    partial ISO dates (date columns)
 *   code_url:*   NOT doi:*     column is filled / empty
 *   (CT OR MRI) AND NOT task:segmentation
 *
 * Exposes PedradSearch.buildPredicate(query, columns) -> (row) => boolean, or
 * null for an empty query, and PedradSearch.sortRows(rows, column, order).
 *
 * Column filters (the header dropdowns) are ordinary clauses of the same
 * query, one top-level AND clause per column:
 *
 *   (modality:="MRI" OR modality:="CT")      keep these values
 *   (NOT year:="2026" AND NOT year:="2025")  drop these values
 *   NOT code_url:*  /  code_url:*            the blank value in / out
 *
 * topClauses(query, columns) splits a query into its top-level clauses and
 * says which of them are such a filter; joinClauses puts them back together.
 */
(function () {
  class QueryError extends Error {}

  const OP_ALT = ">=|<=|=>|=<|>|<|=";
  const OP_NORMALIZE = { "=>": ">=", "=<": "<=" };
  const OPERATORS = new Set(["AND", "OR", "NOT"]);

  const TOKEN_RE = new RegExp(
    [
      "\\s+",
      "(?<lparen>\\()",
      "(?<rparen>\\))",
      "(?<field>[A-Za-z_]\\w*)" +
        "(?:" + `\\s*:\\s*(?<colon_op>${OP_ALT})?` + "|" + `\\s*(?<bare_op>${OP_ALT})` + ")\\s*" +
        '(?<val>"[^"]*"|\\*|[^\\s()]+)',
      '(?<quoted>"[^"]*")',
      '(?<word>[^\\s()"]+)',
    ].join("|"),
    "y"
  );

  function tokenize(query, columns) {
    const tokens = [];
    let pos = 0;
    while (pos < query.length) {
      TOKEN_RE.lastIndex = pos;
      const m = TOKEN_RE.exec(query);
      if (!m || m.index !== pos) throw new QueryError(`Unexpected character at position ${pos}`);
      const start = pos;
      pos = TOKEN_RE.lastIndex;
      const g = m.groups;
      const push = (tok) => tokens.push(Object.assign(tok, { start, end: pos }));
      if (g.lparen) push({ kind: "lparen" });
      else if (g.rparen) push({ kind: "rparen" });
      else if (g.field !== undefined) {
        const col = columns[g.field.toLowerCase()];
        if (!col) {
          // "http://x" or "10:30" are words, not fields; only complain about
          // things that look like an intended field name.
          if (/^[a-z_]+$/i.test(g.field) && !/^https?$/i.test(g.field)) {
            throw new QueryError(`Unknown field: ${g.field} (see "show fields")`);
          }
          push({ kind: "term", term: { col: null, value: m[0], presence: false } });
          continue;
        }
        let op = g.colon_op || g.bare_op || null;
        op = OP_NORMALIZE[op] || op;
        if (g.val === "*") push({ kind: "term", term: { col, presence: true } });
        else {
          const value = g.val.startsWith('"') ? g.val.slice(1, -1) : g.val;
          push({ kind: "term", term: { col, op, value, presence: false } });
        }
      } else if (g.quoted !== undefined) {
        push({ kind: "term", term: { col: null, value: g.quoted.slice(1, -1) } });
      } else if (g.word !== undefined) {
        const upper = g.word.toUpperCase();
        if (OPERATORS.has(upper)) push({ kind: upper.toLowerCase() });
        else push({ kind: "term", term: { col: null, value: g.word } });
      }
    }
    return tokens;
  }

  // Every node carries start/end offsets into the query text.
  const span = (node, first, last) => Object.assign(node, { start: first.start, end: last.end });

  class Parser {
    constructor(tokens) { this.tokens = tokens; this.i = 0; }
    peek() { return this.i < this.tokens.length ? this.tokens[this.i] : null; }
    next() { return this.tokens[this.i++]; }
    parse() {
      if (this.tokens.length === 0) return null;
      const node = this.parseOr();
      if (this.peek() !== null) throw new QueryError("Unbalanced parentheses or trailing tokens");
      return node;
    }
    parseOr() {
      const children = [this.parseAnd()];
      while (this.peek() && this.peek().kind === "or") { this.next(); children.push(this.parseAnd()); }
      return children.length === 1 ? children[0] : span({ op: "OR", children }, children[0], children[children.length - 1]);
    }
    parseAnd() {
      const children = [this.parseNot()];
      for (;;) {
        const tok = this.peek();
        if (tok === null || tok.kind === "or" || tok.kind === "rparen") break;
        if (tok.kind === "and") this.next();
        children.push(this.parseNot());
      }
      return children.length === 1 ? children[0] : span({ op: "AND", children }, children[0], children[children.length - 1]);
    }
    parseNot() {
      if (this.peek() && this.peek().kind === "not") {
        const tok = this.next();
        const inner = this.parseNot();
        return span({ not: inner }, tok, inner);
      }
      return this.parseAtom();
    }
    parseAtom() {
      const tok = this.peek();
      if (tok === null) throw new QueryError("Unexpected end of query");
      if (tok.kind === "lparen") {
        this.next();
        const node = this.parseOr();
        if (!this.peek() || this.peek().kind !== "rparen") throw new QueryError("Missing closing parenthesis");
        return Object.assign(span(node, tok, this.next()), { paren: true });
      }
      if (tok.kind === "term") { this.next(); return span({ term: tok.term }, tok, tok); }
      throw new QueryError(`Unexpected ${tok.kind.toUpperCase()}`);
    }
  }

  const isEmpty = (v) => v === null || v === undefined || v === "" || (Array.isArray(v) && v.length === 0);

  function asText(v) {
    if (isEmpty(v)) return "";
    return Array.isArray(v) ? v.join(" ; ") : String(v);
  }

  function dateBounds(value) {
    const parts = value.split("-");
    if (!parts.every((p) => /^\d+$/.test(p)) || parts.length > 3) throw new QueryError(`Invalid date: ${value}`);
    const y = parts[0].padStart(4, "0");
    if (parts.length === 1) return [`${y}-01-01`, `${y}-12-31`];
    const mm = parts[1].padStart(2, "0");
    if (parts.length === 2) return [`${y}-${mm}-01`, `${y}-${mm}-31`];
    const iso = `${y}-${mm}-${parts[2].padStart(2, "0")}`;
    return [iso, iso];
  }

  function compare(op, v, lower, upper) {
    switch (op || "=") {
      case "=": return v >= lower && v <= upper;
      case ">": return v > upper;
      case ">=": return v >= lower;
      case "<": return v < lower;
      case "<=": return v <= upper;
    }
    throw new QueryError(`Unsupported operator: ${op}`);
  }

  function compileTerm(t) {
    if (t.col === null) {
      const needle = t.value.toLowerCase();
      return (row) => row._hay.includes(needle);
    }
    const key = t.col.key;
    if (t.presence) return (row) => !isEmpty(row[key]);

    if (t.col.type === "num") {
      const n = Number(t.value);
      if (Number.isNaN(n)) throw new QueryError(`${key} needs a number, got ${t.value}`);
      return (row) => typeof row[key] === "number" && compare(t.op, row[key], n, n);
    }
    if (t.col.type === "date" && t.op && t.op !== "=") {
      const [lower, upper] = dateBounds(t.value);
      return (row) => !isEmpty(row[key]) && compare(t.op, String(row[key]), lower, upper);
    }
    const needle = t.value.toLowerCase();
    if (t.op === "=") {
      return (row) => {
        const v = row[key];
        const vals = Array.isArray(v) ? v : t.col.type === "tags" ? String(v ?? "").split(/;\s*/) : [v];
        return vals.some((x) => !isEmpty(x) && String(x).toLowerCase() === needle);
      };
    }
    if (t.op) throw new QueryError(`${key} is text; use ${key}:value or ${key}:="exact value"`);
    return (row) => asText(row[key]).toLowerCase().includes(needle);
  }

  function compile(node) {
    if (node.term) return compileTerm(node.term);
    if (node.not) { const c = compile(node.not); return (row) => !c(row); }
    const cs = node.children.map(compile);
    return node.op === "AND" ? (row) => cs.every((p) => p(row)) : (row) => cs.some((p) => p(row));
  }

  // columns: array of {key, type}. Search also accepts each column's aliases.
  function parse(query, columns) {
    if (!query || !query.trim()) return null;
    const byName = {};
    for (const c of columns) {
      byName[c.key.toLowerCase()] = c;
      for (const a of c.aliases || []) byName[a.toLowerCase()] = c;
    }
    return new Parser(tokenize(query, byName)).parse();
  }

  function buildPredicate(query, columns) {
    const node = parse(query, columns);
    return node ? compile(node) : null;
  }

  // ----------------------------------------------------------- column filters

  // The empty value in a filter's value sets (other values are lowercased).
  const BLANK = "\u0000blank";

  // The values one cell holds, split exactly as `field:="x"` compares them.
  function cellValues(col, row) {
    const v = row[col.key];
    const vals = Array.isArray(v) ? v : col.type === "tags" ? String(v ?? "").split(/;\s*/) : [v];
    return vals.filter((x) => !isEmpty(x)).map(String);
  }

  // What a top-level clause does to one column's values:
  // {key, include: Set} or {key, exclude: Set}, else null.
  function clauseFilter(node) {
    const t = (n) => (n && n.term && n.term.col ? n.term : null);
    const keep = (n) => {
      if (t(n) && t(n).op === "=") return { key: t(n).col.key, v: t(n).value.toLowerCase() };
      if (n.not && t(n.not) && t(n.not).presence) return { key: t(n.not).col.key, v: BLANK };
      return null;
    };
    const drop = (n) => {
      if (n.not && t(n.not) && t(n.not).op === "=") return { key: t(n.not).col.key, v: t(n.not).value.toLowerCase() };
      if (t(n) && t(n).presence) return { key: t(n).col.key, v: BLANK };
      return null;
    };
    const collect = (nodes, fn, mode) => {
      const xs = nodes.map(fn);
      if (xs.some((x) => !x) || xs.some((x) => x.key !== xs[0].key)) return null;
      return { key: xs[0].key, [mode]: new Set(xs.map((x) => x.v)) };
    };
    if (node.op === "OR") return collect(node.children, keep, "include");
    if (node.op === "AND") return collect(node.children, drop, "exclude");
    return collect([node], keep, "include") || collect([node], drop, "exclude");
  }

  // Split a query into top-level AND clauses: [{text, sep, node, filter}],
  // where sep is the text that separated a clause from the one before it.
  // Throws QueryError like buildPredicate.
  function topClauses(query, columns) {
    const root = parse(query, columns);
    if (!root) return [];
    const nodes = root.op === "AND" ? root.children : [root];
    return nodes.map((n, i) => ({
      text: query.slice(n.start, n.end),
      sep: i ? query.slice(nodes[i - 1].end, n.start) : "",
      bare: n.op === "OR" && !n.paren, // needs parentheses once ANDed with anything
      filter: clauseFilter(n),
    }));
  }

  function joinClauses(clauses) {
    return clauses.map((c, i) => {
      const text = c.bare && clauses.length > 1 ? `(${c.text})` : c.text;
      return i ? (c.sep || " AND ") + text : text;
    }).join("");
  }

  // Lowercased text of every column, built once per row so bare words are a
  // single substring test.
  function haystack(row, columns) {
    return columns.map((c) => asText(row[c.key])).join("  ").toLowerCase();
  }

  function sortRows(rows, col, order) {
    const desc = order === "desc";
    const key = col.sortKey || col.key;
    const numeric = col.type === "num";
    return rows.slice().sort((a, b) => {
      const va = a[key], vb = b[key];
      const ea = isEmpty(va), eb = isEmpty(vb);
      if (ea || eb) return ea && eb ? 0 : ea ? 1 : -1; // empty always last
      let c;
      if (numeric) c = va - vb;
      else c = asText(va).localeCompare(asText(vb), undefined, { sensitivity: "base", numeric: true });
      return desc ? -c : c;
    });
  }

  window.PedradSearch = {
    buildPredicate, sortRows, haystack, QueryError, asText, isEmpty,
    BLANK, cellValues, topClauses, joinClauses,
  };
})();
