#!/usr/bin/env python3
"""
Triage a directory of saved source pages for the identification panel.

Walks a source drop directory (kept OUTSIDE the repo — panel is measure-and-cite,
source text is never committed), and for each file reports what metadata is
already present and what a human still has to supply. It does not measure and it
does not move anything; it produces a triage table so the operator sees, at a
glance, which files are ready to measure and which need a date or an
authorship rationale.

Extraction priority, per file:
  1. Embedded schema.org JSON-LD (`<script type="application/ld+json">`) —
     NewsArticle/Article datePublished, author, headline, publisher. Most
     reliable; present in a full-page browser save, absent in reader-view saves.
  2. <meta> tags — article:published_time, author, og:title, og:site_name.
  3. A sibling `sources.txt` line ("filename | url | note") — operator fallback
     for files that saved without metadata, and the place the authorship basis
     for post-2023 texts is recorded.

Genre is guessed from the containing folder name first (the operator's sort),
then from lightweight content cues; low-confidence guesses are flagged for
review. The date proxy is checked (pre-2023 clears automatically; post-2023
needs an authorship rationale from the operator per baseline/README.md).

Usage:
    scripts/scan_sources.py ~/makegood-harvest-sources           # triage the whole tree
    scripts/scan_sources.py ~/makegood-harvest-sources/appeal    # one genre
    scripts/scan_sources.py --json ~/makegood-harvest-sources    # machine-readable rows

Output: a human triage table to stdout (or JSON lines with --json). READY means
date + author + title all found and the date clears the guard; NEEDS-INPUT lists
exactly what is missing.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

SCRIPT_VERSION = "0.1.0"

GENRE_FOLDERS = {
    "editorial", "feature", "appeal", "bio", "exec-summary", "correspondence",
    "faq", "newsletter", "social", "about-program", "comparison",
    "grant-narrative",
}

# Content cues for a genre guess when the folder doesn't already name one.
# Deliberately conservative — a weak guess is flagged, not trusted.
GENRE_CUES = [
    ("appeal", [r"\bdear\b.{0,40}\bdonor|\byour gift\b|\bdonate\b|\bmake a gift\b"]),
    ("correspondence", [r"^\s*dear\b", r"\bsincerely\b|\byours (?:truly|faithfully)\b"]),
    ("faq", [r"\bfrequently asked\b|\bQ:\s|\bA:\s|\?\s*$"]),
    ("bio", [r"\bis (?:the|a) (?:founder|director|ceo|author|professor)\b"]),
    ("exec-summary", [r"\bexecutive summary\b|\bannual report\b"]),
]

PRE_2023 = 2023  # the contamination-guard proxy year


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def _flatten_authors(val) -> str | None:
    """schema.org author may be a dict, a list, or a string."""
    if val is None:
        return None
    if isinstance(val, str):
        return val.strip() or None
    if isinstance(val, dict):
        return (val.get("name") or "").strip() or None
    if isinstance(val, list):
        names = [_flatten_authors(v) for v in val]
        names = [n for n in names if n]
        return ", ".join(names) or None
    return None


def from_jsonld(raw: str) -> dict:
    """Pull date/author/title/publisher from any NewsArticle/Article JSON-LD."""
    out: dict = {}
    for m in re.finditer(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        raw, re.S | re.I,
    ):
        blob = m.group(1).strip()
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            # Some pages emit multiple concatenated objects or trailing commas;
            # skip rather than guess.
            continue
        candidates = data if isinstance(data, list) else [data]
        # @graph nesting is common
        graph = []
        for c in candidates:
            if isinstance(c, dict) and "@graph" in c and isinstance(c["@graph"], list):
                graph.extend(c["@graph"])
            else:
                graph.append(c)
        for node in graph:
            if not isinstance(node, dict):
                continue
            t = node.get("@type", "")
            types = t if isinstance(t, list) else [t]
            if not any("Article" in str(x) for x in types):
                continue
            out.setdefault("date", (node.get("datePublished") or "")[:10] or None)
            out.setdefault("author", _flatten_authors(node.get("author")))
            out.setdefault("title", (node.get("headline") or "").strip() or None)
            pub = node.get("publisher")
            if isinstance(pub, dict):
                out.setdefault("publication", (pub.get("name") or "").strip() or None)
    return {k: v for k, v in out.items() if v}


def from_meta(raw: str) -> dict:
    out: dict = {}

    def meta(attr, name):
        m = re.search(
            rf'<meta[^>]*{attr}=["\']{re.escape(name)}["\'][^>]*content=["\'](.*?)["\']',
            raw, re.I,
        ) or re.search(
            rf'<meta[^>]*content=["\'](.*?)["\'][^>]*{attr}=["\']{re.escape(name)}["\']',
            raw, re.I,
        )
        return html.unescape(m.group(1).strip()) if m else None

    date = meta("property", "article:published_time") or meta("name", "date") \
        or meta("itemprop", "datePublished")
    if date:
        out["date"] = date[:10]
    author = meta("name", "author") or meta("property", "article:author")
    if author:
        out["author"] = author
    title = meta("property", "og:title") or None
    if title:
        out["title"] = title
    pub = meta("property", "og:site_name")
    if pub:
        out["publication"] = pub
    return out


def parse_sidecar(folder: Path) -> dict:
    """Read an optional sources.txt: 'filename | url | note' per line."""
    sc = folder / "sources.txt"
    rows: dict = {}
    if not sc.exists():
        return rows
    for line in sc.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if not parts or not parts[0]:
            continue
        rows[parts[0]] = {
            "url": parts[1] if len(parts) > 1 else None,
            "note": parts[2] if len(parts) > 2 else None,
        }
    return rows


def visible_text(raw: str) -> str:
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", body)))


def guess_genre(folder_name: str, text: str) -> tuple[str | None, str]:
    if folder_name in GENRE_FOLDERS:
        return folder_name, "folder"
    head = text[:1500].lower()
    for genre, pats in GENRE_CUES:
        if any(re.search(p, head, re.I | re.M) for p in pats):
            return genre, "content-cue (low confidence)"
    return None, "unknown"


# ---------------------------------------------------------------------------
# Per-file triage
# ---------------------------------------------------------------------------

def triage_file(path: Path, sidecar: dict) -> dict:
    raw = read(path)
    is_html = path.suffix.lower() in {".html", ".htm"} or "<html" in raw[:500].lower()

    meta: dict = {}
    if is_html:
        meta.update(from_meta(raw))
        meta.update({k: v for k, v in from_jsonld(raw).items() if k not in meta or not meta[k]})
        # jsonld is more reliable for date/author; let it override meta there
        j = from_jsonld(raw)
        for k in ("date", "author", "title", "publication"):
            if j.get(k):
                meta[k] = j[k]

    side = sidecar.get(path.name, {})
    genre, genre_basis = guess_genre(path.parent.name, visible_text(raw) if is_html else raw)

    # date: prefer embedded, then sidecar note if it carries a year
    date = meta.get("date")
    if not date and side.get("note"):
        ym = re.search(r"\b(19|20)\d{2}\b", side["note"])
        date = ym.group(0) if ym else None

    year = None
    if date:
        ym = re.search(r"\b(19|20)\d{2}\b", date)
        year = int(ym.group(0)) if ym else None

    missing = []
    if not date:
        missing.append("date")
    if not meta.get("author"):
        missing.append("author")
    if not meta.get("title"):
        missing.append("title")
    if not genre:
        missing.append("genre")

    # guard status
    if year is None:
        guard = "UNKNOWN (no date)"
    elif year < PRE_2023:
        guard = "clears (pre-2023)"
    else:
        has_rationale = bool(side.get("note") and re.search(
            r"inference|verified|deceased|closed corpus|named author|print origin",
            side["note"], re.I))
        guard = "post-2023 — needs authorship rationale" if not has_rationale \
            else "post-2023 — rationale on file"
        if not has_rationale:
            missing.append("authorship-basis")

    ready = not missing and "clears" in guard or (
        not missing and guard == "post-2023 — rationale on file")

    return {
        "file": str(path),
        "genre": genre,
        "genre_basis": genre_basis,
        "date": date,
        "year": year,
        "author": meta.get("author"),
        "title": meta.get("title"),
        "publication": meta.get("publication"),
        "url": side.get("url"),
        "guard": guard,
        "missing": missing,
        "status": "READY" if ready else "NEEDS-INPUT",
    }


def walk(root: Path) -> list[dict]:
    rows = []
    folders = [root] if (root / "sources.txt").exists() or any(
        root.glob("*.htm*")) else sorted(p for p in root.iterdir() if p.is_dir())
    if not folders:
        folders = [root]
    for folder in folders:
        sidecar = parse_sidecar(folder)
        for path in sorted(folder.glob("*")):
            if path.suffix.lower() in {".html", ".htm", ".md", ".markdown", ".txt"} \
                    and path.name != "sources.txt" and path.name != "README.txt":
                rows.append(triage_file(path, sidecar))
    return rows


def print_table(rows: list[dict]) -> None:
    if not rows:
        print("No source files found.", file=sys.stderr)
        return
    ready = [r for r in rows if r["status"] == "READY"]
    needs = [r for r in rows if r["status"] == "NEEDS-INPUT"]
    print(f"\n{len(rows)} files — {len(ready)} READY, {len(needs)} NEEDS-INPUT\n")
    for r in rows:
        name = Path(r["file"]).name
        flag = "✅" if r["status"] == "READY" else "⚠️ "
        print(f"{flag} [{r['genre'] or '??':<15}] {name}")
        bits = []
        bits.append(f"date={r['date'] or '—'}")
        bits.append(f"author={r['author'] or '—'}")
        bits.append(f"guard: {r['guard']}")
        print(f"     {'  '.join(bits)}")
        if r["missing"]:
            print(f"     NEEDS: {', '.join(r['missing'])}")
        if r["genre_basis"].startswith("content"):
            print(f"     genre guessed from {r['genre_basis']} — confirm")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version",
                        version=f"scan_sources.py {SCRIPT_VERSION}")
    parser.add_argument("root", type=Path, help="source drop dir (or one genre folder)")
    parser.add_argument("--json", action="store_true", help="emit JSON lines")
    args = parser.parse_args()

    if not args.root.exists():
        parser.error(f"no such directory: {args.root}")

    rows = walk(args.root)
    if args.json:
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))
    else:
        print_table(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
