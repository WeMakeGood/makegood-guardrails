#!/usr/bin/env python3
"""Build the third-party source corpus into sources/ (gitignored).

Consolidates raw third-party writing (saved HTML, cleaned .txt, PDFs) into
clean body-text .md files with provenance, organized by register — the craft
corpus the exemplar generator studies to set a "best-word-prediction"
disposition (NOT per-register training). See sources/README.md.

Principles (2026-07-17):
- COPY, never move; originals untouched.
- Body text only, as .md, each with a provenance header.
- NO rewriting: extract HTML/PDF to prose; copy already-clean .txt verbatim.
- Failures are FLAGGED in MANIFEST.json, never written as empty files.

Raw sources live durably in ~/makegood-harvest-sources/ (never committed — the
source-text-never-committed rule). Override with --raw-root. Some publications
(rendered-DOM saves like the Economist) don't extract cleanly here; those were
recovered separately — see recover_failures.py and sources/README.md.

Usage:
    scripts/build_sources.py                      # default raw-root, write sources/
    scripts/build_sources.py --raw-root DIR --out DIR
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXTRACT = REPO / "harvest/scripts/extract_body.py"
MIN_WORDS = 40  # below this, treat extraction as failed (nav page / blocked)

# Same article saved twice (cleaned .txt AND raw HTML) — map raw slug -> clean slug
# so dedup treats them as one (clean wins; it's copied verbatim, no extraction).
_CANONICAL = {
    "why-u-k-bus-stops-suddenly-smell-like-roses-and-cucumber": "busstops",
    "the-cardboard-real-estate-boom-is-here": "cardboard",
    "soman-chainani-is-revolutionizing-ya-fiction": "chainani",
    "ka-ryyn-s-curiously-powerful-experimental-pop-_-pitchfork": "karyyn",
    "is-kyrie-irving-s-rant-about-his-nikes-the-next-step-of-athl": "kyrie",
    "will-mental-health-resources-evaporate-post-pandemic_": "mentalhealth",
    "why-nike-infused-its-olympic-designs-with-so-much-neon": "neon",
    "management-changed-productivity-measures": "productivity",
    "the-hidden-way-the-tokyo-olympics-could-forever-change-the-c": "tokyo",
    "weaponizing-the-first-amendment-how-free-speech-became-a-con": "firstamend",
}


def _slug(s: str) -> str:
    keep = "".join(c if c.isalnum() or c in " -_" else " " for c in s.lower())
    return "-".join(keep.split())[:60]


def extract_html(path: Path, py: str) -> str:
    r = subprocess.run([py, str(EXTRACT), str(path), "--quiet"],
                       capture_output=True, text=True)
    return r.stdout.strip()


def extract_pdf(path: Path) -> str:
    try:
        import pypdf
    except ImportError:
        return ""
    try:
        reader = pypdf.PdfReader(str(path))
        return "\n\n".join((pg.extract_text() or "") for pg in reader.pages).strip()
    except Exception:
        return ""


def collect(raw_root: Path):
    """Yield (register, slug, provenance, (kind, path)). Cleaned .txt FIRST so it
    claims the canonical slug before the raw-HTML copy of the same article."""
    reg_map = {"faq": "technical", "feature": "feature", "editorial": "analytic",
               "news": "news"}
    rec = raw_root / "_scratchpad-recovered"
    # 1. cleaned craft-input .txt bodies (copy verbatim)
    ci = rec / "craft-input"
    txt_reg = {"atl-murphy": "feature", "atl-reisner": "analytic", "atl-serwer": "analytic",
               "firstamend": "analytic", "appeal-camp": "appeal", "karyyn": "feature"}
    if ci.is_dir():
        for f in sorted(ci.glob("*.txt")):
            stem = f.stem.replace("-body", "")
            yield (txt_reg.get(stem, "feature"), _slug(stem),
                   {"source_file": str(f), "origin": "craft-input (cleaned)",
                    "note": "already-cleaned body, copied verbatim"}, ("txt", f))
    # 2. raw HTML in genre folders
    for f in sorted(raw_root.rglob("*.html")):
        if "_scratchpad-recovered" in f.parts:
            genre = "appeal" if "casestudies" in str(f.parent) else f.parent.name
        else:
            genre = f.parent.name
        reg = reg_map.get(genre, genre if genre != "appeals-casestudies" else "appeal")
        yield (reg, _slug(f.stem),
               {"source_file": str(f), "origin": "raw-html"}, ("html", f))
    # 3. PDFs in the recovered appeals folder
    ac = rec / "appeals-casestudies"
    if ac.is_dir():
        for f in sorted(ac.glob("*.pdf")):
            yield ("appeal", _slug(f.stem),
                   {"source_file": str(f), "origin": "raw-pdf"}, ("pdf", f))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw-root", type=Path, default=Path.home() / "makegood-harvest-sources",
                    help="durable raw-source collection (default ~/makegood-harvest-sources)")
    ap.add_argument("--out", type=Path, default=REPO / "sources",
                    help="output corpus dir (default repo sources/, gitignored)")
    args = ap.parse_args()
    if not args.raw_root.is_dir():
        print(f"raw-root not found: {args.raw_root}", file=sys.stderr)
        return 2

    py = sys.executable
    args.out.mkdir(parents=True, exist_ok=True)
    manifest, seen = [], set()
    for register, slug, prov, (kind, path) in collect(args.raw_root):
        canon = _CANONICAL.get(slug, slug)
        if canon in seen:
            manifest.append({"register": register, "slug": slug, "status": "dup-skipped",
                             "kind": kind, **prov})
            continue
        if kind == "txt":
            body = path.read_text(encoding="utf-8", errors="replace").strip()
        elif kind == "html":
            body = extract_html(path, py)
        else:
            body = extract_pdf(path)
        wc = len(body.split())
        status = "ok" if wc >= MIN_WORDS else "FAILED-empty"
        manifest.append({"register": register, "slug": canon, "status": status,
                         "word_count": wc, "kind": kind, **prov})
        if status != "ok":
            continue  # never write empty/near-empty files
        seen.add(canon)
        regdir = args.out / register
        regdir.mkdir(exist_ok=True)
        header = (f"---\nslug: {canon}\nregister: {register}\n"
                  f"source_file: {prov.get('source_file')}\norigin: {prov.get('origin')}\n"
                  f"extracted_via: {kind}\nword_count: {wc}\n"
                  "provenance_note: >\n  Third-party source, body text only, for internal\n"
                  "  craft-study. Not rewritten. Original retained at source_file.\n---\n\n")
        (regdir / f"{canon}.md").write_text(header + body + "\n", encoding="utf-8")

    (args.out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    ok = [m for m in manifest if m["status"] == "ok"]
    fail = [m for m in manifest if m["status"] == "FAILED-empty"]
    dup = [m for m in manifest if m["status"] == "dup-skipped"]
    print(f"consolidated {len(ok)} items into {args.out}/  ({len(fail)} failed, {len(dup)} dup)")
    print("by register:", dict(Counter(m["register"] for m in ok)))
    if fail:
        print("\nFAILED extraction (raw retained, body NOT written — see recover_failures.py):")
        for m in fail:
            print(f"  [{m['register']}] {m['slug']} ({m['kind']}, {m['word_count']}w)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
