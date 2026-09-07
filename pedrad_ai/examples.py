"""Fetch representative images for the "what it looks like" slides.

Three fetch kinds, all without a login:

* ``github_readme`` - the first raster image referenced in a repository README
  (resolved relative to the default branch).
* ``og_image`` - a vendor page's Open Graph preview image (``og:image``), which
  is normally the product hero shot.
* ``europepmc_fig`` - the first figure of an open-access article, located via
  the Europe PMC full-text XML.

Images are saved under ``figures/examples/<slug>.<ext>`` with a sidecar JSON
that records the source URL for attribution. Any failure is reported and
skipped so the slide build still runs (the slide shows the caption only).
"""

from __future__ import annotations

import base64
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from . import config, github_repos

OUT_DIR = config.FIGURE_DIR / "examples"
OUT_DIR.mkdir(parents=True, exist_ok=True)
_IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def _get(url: str, headers: dict[str, str] | None = None, timeout: float = 60) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), (r.headers.get("content-type") or "")


def _gh_headers() -> dict[str, str]:
    h = {"Accept": "application/vnd.github+json"}
    tok = github_repos._token()
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def _readme_image(repo: str) -> str | None:
    meta = json.loads(_get(f"https://api.github.com/repos/{repo}", _gh_headers())[0])
    branch = meta.get("default_branch", "main")
    readme = json.loads(_get(f"https://api.github.com/repos/{repo}/readme", _gh_headers())[0])
    text = base64.b64decode(readme.get("content", "")).decode("utf-8", "replace")
    cands = re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text) + re.findall(r'<img[^>]+src="([^"]+)"', text)
    for c in cands:
        low = c.lower().split("?")[0]
        if not low.endswith(_IMG_EXT) or "badge" in low or "shields.io" in low or "logo" in low:
            continue
        if c.startswith("http"):
            return c.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/") if "github.com" in c and "/blob/" in c else c
        return f"https://raw.githubusercontent.com/{repo}/{branch}/{c.lstrip('./')}"
    # fall back to the first image even if it looks like a logo
    for c in cands:
        if c.lower().split("?")[0].endswith(_IMG_EXT):
            return c if c.startswith("http") else f"https://raw.githubusercontent.com/{repo}/{branch}/{c.lstrip('./')}"
    return None


def _og_image(url: str) -> str | None:
    html = _get(url)[0].decode("utf-8", "replace")
    m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html) or re.search(
        r'<meta[^>]+content="([^"]+)"[^>]+property="og:image"', html
    )
    if m:
        return urllib.parse.urljoin(url, m.group(1))
    m = re.search(r'<img[^>]+src="([^"]+\.(?:png|jpg|jpeg|webp))"', html, re.I)
    return urllib.parse.urljoin(url, m.group(1)) if m else None


def _page_image(url: str) -> str | None:
    """Largest non-logo raster image on a page (product screenshots, not icons)."""
    html = _get(url)[0].decode("utf-8", "replace")
    cands = re.findall(r'(?:src|href|data-src)="([^"]+\.(?:png|jpg|jpeg|webp)(?:\?[^"]*)?)"', html, re.I)
    cands += [c.split()[0] for c in re.findall(r'srcset="([^"]+)"', html) if c.split()]
    seen: list[str] = []
    for c in cands:
        full = urllib.parse.urljoin(url, c.replace("&amp;", "&"))
        low = full.lower()
        if any(t in low for t in ("logo", "icon", "favicon", "avatar", "flag", "badge", "arrow", "linkedin", "twitter")):
            continue
        if full not in seen:
            seen.append(full)
    best, best_area = None, 0
    try:
        from PIL import Image  # type: ignore
        import io
    except Exception:
        return seen[0] if seen else None
    for full in seen[:12]:
        try:
            data = _get(full, timeout=30)[0]
            im = Image.open(io.BytesIO(data))
            w, h = im.size
            if w < 300 or h < 200:
                continue
            area = w * h
            if area > best_area:
                best, best_area = full, area
        except Exception:
            continue
    return best or (seen[0] if seen else None)


def _europepmc_figure(doi: str) -> str | None:
    """First figure of an open-access article.

    DOI -> PMCID via the Europe PMC search API, then the figure image URL is
    read from the PMC article page (figures are served from
    ``cdn.ncbi.nlm.nih.gov/pmc/blobs/...``; the file name carries ``Fig``,
    ``g001`` or ``f1`` so tables and equations are skipped).
    """
    q = urllib.parse.quote(f"DOI:{doi}")
    data = json.loads(_get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&resultType=lite")[0])
    res = (data.get("resultList") or {}).get("result") or []
    pmcid = next((r.get("pmcid") for r in res if r.get("pmcid")), None)
    if not pmcid:
        return None
    html = _get(f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/")[0].decode("utf-8", "replace")
    urls = re.findall(r'https://cdn\.ncbi\.nlm\.nih\.gov/pmc/blobs/[^"\s]+\.(?:jpg|png|jpeg)', html)
    for u in urls:
        name = u.rsplit("/", 1)[-1].lower()
        if re.search(r"fig|g00[1-9]|[._]f0?[1-9]", name) and not re.search(r"tbl|table|equ|_e0", name):
            return u
    return urls[0] if urls else None


def fetch_all(specs: list[dict[str, str]] | None = None) -> list[dict[str, Any]]:
    specs = specs or config.EXAMPLE_IMAGES
    manifest: list[dict[str, Any]] = []
    for s in specs:
        slug, kind, ref = s["slug"], s["kind"], s["ref"]
        existing = [p for p in OUT_DIR.glob(f"{slug}.*") if p.suffix.lower() in _IMG_EXT]
        entry: dict[str, Any] = {**s, "file": None, "source_url": None}
        try:
            if existing:
                side = OUT_DIR / f"{slug}.json"
                entry["file"] = existing[0].name
                entry["source_url"] = json.loads(side.read_text()).get("source_url") if side.exists() else None
                manifest.append(entry)
                print(f"  {slug}: cached")
                continue
            if kind == "github_readme":
                url = _readme_image(ref)
            elif kind == "og_image":
                url = _og_image(ref)
            elif kind == "europepmc_fig":
                url = _europepmc_figure(ref)
            elif kind == "page_image":
                url = _page_image(ref)
            else:
                url = ref
            if not url:
                print(f"  {slug}: no image found")
                manifest.append(entry)
                continue
            data, ctype = _get(url)
            ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
            if ext not in _IMG_EXT:
                ext = ".jpg" if "jpeg" in ctype or "jpg" in ctype else ".png"
            if ext in (".gif", ".webp") or kind == "page_image":
                ext = _convert(data, slug, ext)
                if not ext:
                    print(f"  {slug}: unsupported format {ctype}")
                    manifest.append(entry)
                    continue
            else:
                (OUT_DIR / f"{slug}{ext}").write_bytes(data)
            (OUT_DIR / f"{slug}.json").write_text(json.dumps({"source_url": url, "kind": kind, "ref": ref}, indent=2))
            entry["file"], entry["source_url"] = f"{slug}{ext}", url
            print(f"  {slug}: {url}")
        except Exception as exc:
            print(f"  {slug}: failed ({exc})")
        manifest.append(entry)
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def _convert(data: bytes, slug: str, ext: str) -> str | None:
    """Convert gif/webp (or any page image) to PNG for pdflatex via Pillow."""
    try:
        from PIL import Image  # type: ignore
        import io

        im = Image.open(io.BytesIO(data))
        im.seek(0)
        im.convert("RGB").save(OUT_DIR / f"{slug}.png")
        return ".png"
    except Exception:
        return None
