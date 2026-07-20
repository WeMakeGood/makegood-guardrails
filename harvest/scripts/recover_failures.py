#!/usr/bin/env python3
"""Recover the extraction failures build_sources.py flags (rendered-DOM saves).

Some publications save as fully-rendered DOM (prose in styled <div>s, or minified),
which extract_body.py's <p>-oriented rules miss. This does per-publication
read-and-trim: strip tags, anchor on the article's real start/end, cut nav/footer
chrome. NOT a reusable extractor — a one-off recovery, run after build_sources.py.

NO rewriting — only tag-strip + trim. Prints HEAD/TAIL of each so a human verifies
the cut is real article text before trusting it. Writes into sources/<register>/.

Raw sources: ~/makegood-harvest-sources/ (override --raw-root). Publications that
save clean via extract_body.py should NOT be listed here.

NB: 3 SOFII case-study pages (bush-letter, bush-letter2, ucl-...) were tried and
DROPPED — their extractable text is SOFII site chrome, not the appeal prose.
Gmail Help.html is a nav page with no article. These are correctly unrecoverable.
"""
from __future__ import annotations
import argparse
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _div_body_text(raw: str) -> str:
    """Economist rendered-DOM: balance-match the first class='body' div → text."""
    start = raw.find('class="body"')
    if start < 0:
        return ""
    open_lt = raw.rfind("<div", 0, start)
    depth, end = 0, None
    for m in re.finditer(r'<div\b|</div>', raw[open_lt:], re.I):
        if m.group().lower().startswith('<div'):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = open_lt + m.end()
                break
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', raw[open_lt:end], flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def economist(raw: str) -> str:
    body = _div_body_text(raw)
    e = body.find("■")           # article ends at the closing black square
    if e > 0:
        body = body[:e]
    m = re.search(r'(Briefing|Europe|United States|The Americas|Asia|China|Middle East'
                  r'|Finance|International|Britain|Science)\s+\w+ \d+\w* \d{4} edition', body)
    if m:                        # nav ends at "<section> <Mon Nth YYYY> edition"
        body = body[m.end():]
    body = re.sub(r"Listen to this story\.?.*?OK ", "", body)
    body = re.sub(r"Listen to this story Save time.*?OK ", "", body)
    return body.strip()


def nyt(raw: str) -> str:
    """Real prose in <p> with >=12 words; skip minified-JS <p> noise."""
    ps = [html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
          for p in re.findall(r'<p\b[^>]*>(.*?)</p>', raw, re.S | re.I)]
    keep = [p for p in ps if len(p.split()) >= 12
            and not re.search(r'[{}\[\]=|]{2,}|>>|function|var ', p)]
    return "\n\n".join(keep).strip()


def jobs(raw_root: Path):
    n = raw_root / "news"
    return [
        ("news", "the-economist-western-sanctions-russia", economist,
         n / "Western sanctions on Russia are like none the world has seen _ The Economist.html"),
        ("news", "the-economist-macron-re-election", economist,
         n / "Emmanuel Macron bids for re-election as war roils Europe _ The Economist.html"),
        ("news", "the-economist-zaporizhzhia-nuclear-plant", economist,
         n / "Europe’s largest nuclear plant shuts down after a Russian attack _ The Economist.html"),
        ("news", "the-economist-russian-convoy-kyiv", economist,
         n / "Why a huge Russian convoy remains stalled north of Kyiv _ The Economist.html"),
        ("news", "nyt-cost-to-be-smuggled-us-border", nyt,
         n / "What It Costs to Be Smuggled Across the U.S. Border - The New York Times.html"),
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw-root", type=Path, default=Path.home() / "makegood-harvest-sources")
    ap.add_argument("--out", type=Path, default=REPO / "sources")
    args = ap.parse_args()

    for register, slug, fn, path in jobs(args.raw_root):
        if not path.exists():
            print(f"[MISSING] {slug}: {path}")
            continue
        body = fn(path.read_text(encoding="utf-8", errors="replace"))
        wc = len(body.split())
        print(f"\n{'='*70}\n{slug} ({register}) — {wc} words")
        print(f"HEAD: {' '.join(body.split()[:30])}")
        print(f"TAIL: {' '.join(body.split()[-20:])}")
        if wc < 40:
            print("  ** LOW — not writing **")
            continue
        regdir = args.out / register
        regdir.mkdir(parents=True, exist_ok=True)
        header = (f"---\nslug: {slug}\nregister: {register}\nsource_file: {path}\n"
                  f"origin: recovered (read-and-trim)\nword_count: {wc}\n"
                  "provenance_note: >\n  Rendered-DOM save; body recovered by hand-anchored\n"
                  "  trim, not rewritten. Some files may retain minor leading nav (cosmetic).\n---\n\n")
        (regdir / f"{slug}.md").write_text(header + body + "\n", encoding="utf-8")
        print(f"  wrote sources/{register}/{slug}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
