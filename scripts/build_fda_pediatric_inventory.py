#!/usr/bin/env python3
"""Build the dated, source-exhaustive FDA pediatric-use screening inventory."""
from __future__ import annotations
import collections, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/fda_pediatric_inventory/2026-09-16"
OUT = ROOT / "data/processed/fda_pediatric_inventory.json"

POS = re.compile(r"\b(?:pediatric|paediatric|child(?:ren)?|infant|neonate|newborn|fetal|foetal|adolescent|pregnan)", re.I)
NEG = re.compile(r"(?:not intended (?:for|to be used on) pediatric|not intended for pediatric|not leveraged to support.*pediatric|pediatric phantom|pediatric image quality|pediatric use summary)", re.I)
DIRECT = re.compile(r"(?:intended|indicated|population|patients?|use).{0,140}(?:pediatric|paediatric|child|infant|neonate|fetal|foetal|adolescent|pregnan)|(?:pediatric|paediatric|child|infant|neonate|fetal|foetal|adolescent).{0,140}(?:intended|indicated|population|patients?|use)", re.I)

def main():
    rows = json.loads((ROOT / "data/processed/fda_pediatric_screening.json").read_text())["records"]
    # Every gate of the screen is counted here as it is applied, so the funnel
    # figure and the inventory can never drift apart.
    panels = collections.Counter((r.get("Panel (Lead)") or "unstated").strip()
                                 for r in rows if (r.get("Panel (Lead)") or "").strip() != "Radiology")
    radiology = [r for r in rows if (r.get("Panel (Lead)") or "").strip() == "Radiology"]
    screened = 0
    out=[]
    for r in rows:
        txt = RAW / "text" / f"{r['Submission Number']}.txt"
        if not txt.exists() or r.get("Panel (Lead)") != "Radiology":
            continue
        screened += 1
        text = txt.read_text(errors="replace")
        pages=[]
        for page, body in enumerate(text.split("\f"), 1):
            # Favor the IFU / intended-use section, but retain a short evidence excerpt.
            for m in re.finditer(r"(?:intended|indicated|patient population|pediatric use)", body, re.I):
                excerpt = re.sub(r"\s+", " ", body[max(0,m.start()-80):m.start()+1050]).strip()
                if POS.search(excerpt) and len(excerpt) > 80:
                    pages.append((page, excerpt[:1100]))
                    break
        if not pages:
            continue
        evidence = " ".join(x[1] for x in pages[:2])
        neg = bool(NEG.search(evidence))
        direct = bool(DIRECT.search(evidence))
        # A direct label statement is a candidate. Negative-only statements are retained
        # in the screen log so the review is auditable but not presented as positive.
        status = "label-positive-candidate" if direct and not neg else "needs-label-review"
        out.append({"submission":r["Submission Number"], "decision_date":r["Date of Final Decision"],
                    "device":r["Device"], "company":r["Company"], "product_code":r["Primary Product Code"],
                    "status":status, "evidence_pages":[p for p,_ in pages[:2]], "evidence":evidence})
    out.sort(key=lambda x:(x["status"], x["submission"]))
    result={"retrieved_on":"2026-09-16", "source_csv":"data/raw/fda_pediatric_inventory/2026-09-16/ai_devices.csv",
            "scope":"All FDA AI-list records with Panel (Lead)=Radiology; keyword screening of linked decision-summary PDFs."
                    " Candidate status is not an automated determination of pediatric indication.",
            "screening_method":"A record is label-positive-candidate when its extracted intended-use evidence contains a direct pediatric/fetal patient-population statement; phantom, validation-only, and explicit exclusion mentions are retained as needs-label-review.",
            "records_screened":len(radiology), "screen_positive_candidates":sum(x["status"]=="label-positive-candidate" for x in out),
            "flow":{"snapshot":"2026-09-16",
                    "identified":len(rows),
                    "panels_removed":dict(panels.most_common()),
                    "radiology":len(radiology),
                    "no_document":len(radiology)-screened,
                    "documents_screened":screened,
                    "no_pediatric_evidence":screened-len(out),
                    "pediatric_evidence":len(out),
                    "needs_label_review":sum(x["status"]=="needs-label-review" for x in out),
                    "label_positive":sum(x["status"]=="label-positive-candidate" for x in out)},
            "records":out}
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(result["records_screened"],len(out),result["screen_positive_candidates"])
if __name__ == "__main__": main()
