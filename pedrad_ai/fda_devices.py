"""FDA AI-enabled medical device list: the commercial radiology-AI landscape.

The FDA maintains a public spreadsheet of every AI-enabled device it has
authorized (510(k), De Novo, PMA), with decision date, device name, company and
the lead review panel. Restricting to the Radiology panel gives, without any
scraping, the commercial counterpart of the publication counts: how many
products are cleared per year and which companies hold the most clearances.

The spreadsheet is parsed with the standard library only (zipfile + regex on
the sheet XML), in keeping with the collectors' no-dependency rule.
"""

from __future__ import annotations

import datetime as _dt
import io
import re
import urllib.request
import zipfile
from typing import Any

from . import config, utils

_PED = [re.compile(p, re.I) for p in config.FDA_PEDIATRIC_NAME_PATTERNS]


def _download() -> bytes | None:
    cache = utils.CACHE_DIR / "fda_ai_devices.xlsx"
    if cache.exists():
        return cache.read_bytes()
    req = urllib.request.Request(config.FDA_AI_DEVICES_URL, headers={"User-Agent": config.USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
    except Exception as exc:  # pragma: no cover - network
        print(f"  [warn] FDA list download failed: {exc}")
        return None
    cache.write_bytes(data)
    return data


def _xlsx_rows(data: bytes) -> list[dict[str, str]]:
    z = zipfile.ZipFile(io.BytesIO(data))
    strings: list[str] = []
    if "xl/sharedStrings.xml" in z.namelist():
        ss = z.read("xl/sharedStrings.xml").decode("utf-8", "replace")
        strings = [re.sub(r"<[^>]+>", "", m) for m in re.findall(r"<si>(.*?)</si>", ss, re.S)]
    sheet = sorted(n for n in z.namelist() if n.startswith("xl/worksheets/sheet"))[0]
    xml = z.read(sheet).decode("utf-8", "replace")
    rows: list[list[tuple[str, str]]] = []
    for raw in re.findall(r"<row[^>]*>(.*?)</row>", xml, re.S):
        cells: list[tuple[str, str]] = []
        for m in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)', raw, re.S):
            col, attrs, inner = m.groups()
            if not inner:
                continue
            v = re.search(r"<v>(.*?)</v>", inner, re.S)
            t = re.search(r"<t[^>]*>(.*?)</t>", inner, re.S)
            if 't="s"' in attrs and v:
                val = strings[int(v.group(1))]
            elif t:
                val = t.group(1)
            elif v:
                val = v.group(1)
            else:
                continue
            cells.append((col, _unescape(val).strip()))
        if cells:
            rows.append(cells)
    if not rows:
        return []
    header = {col: name for col, name in rows[0]}
    out = []
    for cells in rows[1:]:
        rec = {header.get(col, col): val for col, val in cells}
        if rec.get("Device") or rec.get("Company"):
            out.append(rec)
    return out


def _unescape(s: str) -> str:
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&apos;", "'"))


def _year(date_s: str) -> int | None:
    m = re.search(r"(\d{4})", date_s or "")
    if m:
        return int(m.group(1))
    # Excel serial date
    if re.fullmatch(r"\d+(\.\d+)?", date_s or ""):
        return (_dt.date(1899, 12, 30) + _dt.timedelta(days=int(float(date_s)))).year
    return None


# Conglomerates file under many legal entities; fold them to one name.
_CANON = [
    ("GE ", "GE HealthCare"), ("General Electric", "GE HealthCare"), ("Siemens", "Siemens Healthineers"),
    ("Philips", "Philips"), ("Canon", "Canon Medical"), ("Samsung", "Samsung"),
    ("Shanghai United Imaging", "United Imaging"), ("United Imaging", "United Imaging"),
    ("Fujifilm", "Fujifilm"), ("Hologic", "Hologic"), ("Aidoc", "Aidoc"), ("Qure", "Qure.ai"),
    ("Viz", "Viz.ai"), ("iSchemaView", "iSchemaView (RapidAI)"), ("Koninklijke Philips", "Philips"),
    ("Hyperfine", "Hyperfine"), ("Nuance", "Nuance / Microsoft"), ("Subtle", "Subtle Medical"),
    ("AIRS", "AIRS Medical"), ("Annalise", "Annalise.ai"), ("Lunit", "Lunit"), ("Imagen", "Imagen"),
    ("Brainomix", "Brainomix"), ("HeartFlow", "HeartFlow"), ("Gleamer", "Gleamer"), ("AZmed", "AZmed"),
    ("Arterys", "Arterys"), ("Perspectum", "Perspectum"), ("Quibim", "Quibim"), ("icometrix", "icometrix"),
    ("Cortechs", "Cortechs.ai"), ("Zebra", "Zebra Medical"), ("Nanox", "Nanox"), ("Infervision", "Infervision"),
    ("Shukun", "Shukun"), ("Deepwise", "Deepwise"), ("Bayer", "Bayer"), ("Riverain", "Riverain"),
    ("Coreline", "Coreline"), ("VUNO", "VUNO"), ("RadNet", "RadNet / DeepHealth"), ("DeepHealth", "RadNet / DeepHealth"),
    ("iCAD", "iCAD"), ("Volpara", "Volpara"), ("Kheiron", "Kheiron"), ("Butterfly", "Butterfly Network"),
    ("Caption", "Caption Health"), ("Koios", "Koios"), ("Esaote", "Esaote"), ("Mindray", "Mindray"),
    ("Hitachi", "Hitachi / Fujifilm"), ("Agfa", "Agfa"), ("Carestream", "Carestream"), ("Konica", "Konica Minolta"),
    ("Shimadzu", "Shimadzu"), ("Bracco", "Bracco"), ("Intrinsic", "Intrinsic Imaging"), ("Median", "Median Technologies"),
    ("Cercare", "Cercare Medical"), ("Circle", "Circle CVI"), ("Cleerly", "Cleerly"), ("Elucid", "Elucid"),
    ("Neusoft", "Neusoft"), ("Rapid", "iSchemaView (RapidAI)"),
]


def _norm_company(name: str) -> str:
    raw = (name or "").strip()
    for prefix, canon in _CANON:
        if raw.lower().startswith(prefix.lower()):
            return canon
    n = re.sub(r"[,.]", "", raw)
    n = re.sub(r"\b(inc|llc|ltd|limited|corp|corporation|co|gmbh|sa|sas|ag|bv|plc|pty|pte|kk|technologies|technology|medical systems|healthcare)\b", "", n, flags=re.I)
    return re.sub(r"\s+", " ", n).strip()


def collect() -> dict[str, Any]:
    """Return the radiology-panel subset of the FDA AI device list, summarised."""
    data = _download()
    if not data:
        return {}
    recs = _xlsx_rows(data)
    rad = [r for r in recs if (r.get("Panel (Lead)") or "").strip().lower() == "radiology"]
    devices = []
    for r in rad:
        name = r.get("Device", "")
        devices.append(
            {
                "date": r.get("Date of Final Decision", ""),
                "year": _year(r.get("Date of Final Decision", "")),
                "device": name,
                "company": r.get("Company", ""),
                "company_norm": _norm_company(r.get("Company", "")),
                "submission": r.get("Submission Number", ""),
                "product_code": r.get("Primary Product Code", ""),
                "pediatric_name_hit": bool(any(p.search(name) for p in _PED)),
            }
        )
    by_year: dict[int, int] = {}
    all_by_year: dict[int, int] = {}
    for d in devices:
        if d["year"]:
            by_year[d["year"]] = by_year.get(d["year"], 0) + 1
    for r in recs:
        y = _year(r.get("Date of Final Decision", ""))
        if y:
            all_by_year[y] = all_by_year.get(y, 0) + 1
    companies: dict[str, dict[str, Any]] = {}
    for d in devices:
        c = companies.setdefault(d["company_norm"], {"company": d["company_norm"], "devices": 0, "first_year": None, "last_year": None, "examples": []})
        c["devices"] += 1
        if d["year"]:
            c["first_year"] = min(c["first_year"] or d["year"], d["year"])
            c["last_year"] = max(c["last_year"] or d["year"], d["year"])
        if len(c["examples"]) < 3:
            c["examples"].append(d["device"])
    top = sorted(companies.values(), key=lambda c: (-c["devices"], c["company"]))
    return {
        "collected_on": _dt.date.today().isoformat(),
        "source": config.FDA_AI_DEVICES_PAGE,
        "total_devices_all_panels": len(recs),
        "radiology_devices": len(devices),
        "radiology_share": round(len(devices) / len(recs), 4) if recs else None,
        "by_year": dict(sorted(by_year.items())),
        "all_panels_by_year": dict(sorted(all_by_year.items())),
        "top_companies": top[:40],
        "pediatric_name_hits": [d for d in devices if d["pediatric_name_hit"]],
        "devices": devices,
    }


def company_lookup(fda: dict[str, Any], pattern: str) -> dict[str, Any]:
    """Find companies in the radiology list matching a ``|``-separated pattern."""
    if not fda:
        return {"devices": 0, "years": []}
    rx = re.compile("|".join(re.escape(p.strip()) for p in pattern.split("|") if p.strip()), re.I)
    hits = [d for d in fda.get("devices", []) if rx.search(d["company"] or "")]
    years = sorted({d["year"] for d in hits if d["year"]})
    return {"devices": len(hits), "years": years, "names": sorted({d["device"] for d in hits})[:6]}
