#!/usr/bin/env python3
"""Duplicate-screening reliability for the automated title/abstract screen.

The review protocol requires that the automated screen's error rate be measured
rather than asserted. The definitive check is two humans screening a random
sample (see reports/06_search_strategy.md). This script provides the machine
half of that: it draws a reproducible random sample of screened records, writes
them out for an INDEPENDENT second screener, and then scores the second screen
against the first.

What it measures is **inter-screener agreement between two independent automated
passes** — a necessary condition, not a sufficient one. Two models sharing a
blind spot agree with each other and are both wrong. Report it as what it is and
do not describe it as human validation.

    python scripts/screen_reliability.py --sample 150 --seed 20260909
    #   ... second screener writes data/processed/screen_check/recheck.json ...
    python scripts/screen_reliability.py --score data/processed/screen_check/recheck.json
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from pedrad_ai import config

CHECK_DIR = config.PROCESSED_DIR / "screen_check"


def load_first_pass() -> dict[str, bool]:
    """PMID -> include decision, from the merged first-pass rows."""
    out: dict[str, bool] = {}
    for f in sorted((config.PROCESSED_DIR / "review_rows").glob("rows_*.json")):
        for k, v in json.loads(f.read_text(encoding="utf-8")).items():
            out[k] = bool(v.get("is_pediatric_radiology_ai"))
    return out


def load_records() -> dict[str, dict]:
    wl = json.loads((config.PROCESSED_DIR / "review_worklist.json").read_text(encoding="utf-8"))
    return {p["pmid"]: p for p in wl["papers"]}


def draw(n: int, seed: int) -> None:
    first = load_first_pass()
    recs = load_records()
    pool = sorted(set(first) & set(recs))
    if not pool:
        print("No screened records yet.")
        return
    rng = random.Random(seed)
    sample = rng.sample(pool, min(n, len(pool)))
    CHECK_DIR.mkdir(parents=True, exist_ok=True)
    # The second screener must not see the first decision.
    payload = {
        "seed": seed,
        "n": len(sample),
        "task": (
            "For each record decide ONLY whether it is eligible for a systematic review of "
            "artificial intelligence in pediatric radiology. Eligible = primary or review work in "
            "which an AI/ML method (deep learning, classical ML, radiomics with an ML classifier, "
            "foundation model or LLM) is developed, applied, validated or evaluated on diagnostic "
            "radiologic imaging (radiography, fluoroscopy, CT, MRI, ultrasound/echo, nuclear/PET/SPECT, "
            "angiography) in humans under 18 years or in fetal/prenatal imaging. Mixed-age cohorts count "
            "only with a separate pediatric subgroup or a pediatric-specific model. NOT eligible: "
            "adult-only work that merely mentions children; ophthalmic (fundus/OCT), dental, endoscopic, "
            "dermoscopic, histopathologic or microscopic imaging; EEG/ECG or other non-imaging signals; "
            "laboratory- or clinical-variable-only prediction; no AI/ML component; AI mentioned only in "
            "passing. Fetal and prenatal imaging IS eligible. Developmental neuroimaging in children that "
            "applies machine learning IS eligible."
        ),
        "return": "A JSON object mapping each pmid string to {\"eligible\": true|false, \"reason\": \"<short>\"}",
        "records": [
            {k: recs[p].get(k) for k in ("pmid", "title", "journal", "year", "abstract")}
            for p in sample
        ],
    }
    out = CHECK_DIR / "sample.json"
    out.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"Wrote {len(sample)} records to {out} (seed {seed})")
    print("Have an INDEPENDENT screener decide each one, then score with --score.")


def score(path: Path) -> None:
    first = load_first_pass()
    second_raw = json.loads(path.read_text(encoding="utf-8"))
    second = {k: bool(v.get("eligible") if isinstance(v, dict) else v)
              for k, v in second_raw.items()}
    common = sorted(set(first) & set(second))
    if not common:
        print("No overlapping records to score.")
        return
    a = b = c = d = 0  # both-yes, first-yes-second-no, first-no-second-yes, both-no
    disagreements = []
    for k in common:
        f, s = first[k], second[k]
        if f and s: a += 1
        elif f and not s: b += 1; disagreements.append((k, "first include, second exclude"))
        elif not f and s: c += 1; disagreements.append((k, "first exclude, second include"))
        else: d += 1
    n = len(common)
    po = (a + d) / n
    py = ((a + b) / n) * ((a + c) / n) + ((c + d) / n) * ((b + d) / n)
    kappa = (po - py) / (1 - py) if py < 1 else 1.0
    # Treating the second screen as the reference, how much did the first screen miss?
    recall = a / (a + c) if (a + c) else None
    precision = a / (a + b) if (a + b) else None
    result = {
        "n_compared": n,
        "both_include": a, "first_only": b, "second_only": c, "both_exclude": d,
        "percent_agreement": round(100 * po, 1),
        "cohens_kappa": round(kappa, 3),
        "first_pass_recall_vs_second": round(recall, 3) if recall is not None else None,
        "first_pass_precision_vs_second": round(precision, 3) if precision is not None else None,
        "n_disagreements": len(disagreements),
        "caveat": ("Agreement between two automated screeners. Not human validation: "
                   "shared blind spots produce agreement without correctness."),
    }
    (CHECK_DIR / "reliability.json").write_text(json.dumps(
        {**result, "disagreements": disagreements}, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"\nwrote {CHECK_DIR / 'reliability.json'}")
    if disagreements:
        print(f"\nFirst 15 disagreements (these are the records a human should adjudicate):")
        for k, why in disagreements[:15]:
            print(f"  {k}: {why}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", type=int, default=150)
    ap.add_argument("--seed", type=int, default=20260909)
    ap.add_argument("--score", metavar="PATH")
    args = ap.parse_args()
    if args.score:
        score(Path(args.score))
    else:
        draw(args.sample, args.seed)


if __name__ == "__main__":
    main()
