#!/usr/bin/env python3
"""
Extract the article prose body from a saved full-page HTML file, for the
identification panel's measurement step.

Full-page browser saves bury the article among nav, ads, related-article
cards, captions, and comments. Measuring the wrong paragraphs silently
corrupts the density numbers, so this tool is built to be *verifiable*: it
isolates the publication's known article container, strips known non-prose
elements (figure captions, pull-quotes, related-link cards, promo), and prints
what it extracted so a human can spot-check it against the visible article
before the text is measured. It never measures and never writes into the repo.

Per-publication container rules live in SITE_RULES (keyed by a signature found
in the page). A file whose publication isn't recognized falls back to a generic
`<article>` / longest-paragraph-run heuristic AND is flagged low-confidence, so
an unrecognized page is never silently trusted.

Extraction is paragraph-level: within the article container, keep <p> text,
drop elements inside <figure>/<figcaption>/<aside>/<blockquote class=pull*> and
anything matching the drop-class list. Output is plain text, paragraphs
separated by blank lines — ready for measure_density.py after the operator
confirms the boundary (recorded in panel.md).

Usage:
    scripts/extract_body.py <file.html>                 # print extracted prose + a report
    scripts/extract_body.py <file.html> --out body.txt  # also write the prose to a file
    scripts/extract_body.py <file.html> --quiet         # prose only, no report (for piping)
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

SCRIPT_VERSION = "0.1.0"

# Per-publication rules. `signature` is matched against the raw HTML to pick the
# rule; `container` is a regex whose FIRST group captures the article-body inner
# HTML. Order matters — first matching signature wins.
SITE_RULES = [
    {
        "name": "Fast Company",
        "signature": r"fastcompany\.com|post__article",
        "container": r'<div[^>]*class=["\'][^"\']*post__article[^"\']*["\'][^>]*>(.*?)</div>\s*(?:<footer|<aside|<div[^>]*recirc)',
    },
    {
        "name": "Pitchfork",
        "signature": r"pitchfork\.com|ArticlePageChunks|article-body",
        "container": r'data-testid=["\']ArticlePageChunks["\'][^>]*>(.*?)<(?:footer|aside|div[^>]*ContentFooter)',
    },
    {
        "name": "NYT",
        "signature": r"nytimes\.com|StoryBodyCompanionColumn",
        # NYT splits body into several StoryBodyCompanionColumn blocks; grab all.
        "container": r'(StoryBodyCompanionColumn.*?)(?:<aside|<footer|role=["\']complementary)',
        "multi": True,
    },
    {
        "name": "archive.ph wrapper",
        "signature": r"archive\.(?:ph|today|is|li)",
        # archive wrappers reproduce the original body; fall back to <article> or
        # the main text region. Flagged low-confidence because the wrapper varies.
        "container": r'<article[^>]*>(.*?)</article>',
        "low_confidence": True,
    },
]

DROP_BLOCKS = re.compile(
    r"<figure\b.*?</figure>|<figcaption\b.*?</figcaption>|<aside\b.*?</aside>"
    r"|<script\b.*?</script>|<style\b.*?</style>"
    r"|<blockquote[^>]*class=[\"'][^\"']*pull[^\"']*[\"'].*?</blockquote>",
    re.S | re.I,
)
DROP_CLASS_P = re.compile(
    r'class=["\'][^"\']*(?:caption|credit|recirc|related|promo|newsletter|ad-|share)',
    re.I,
)

# A trailing author-bio / credit line ("Jane Doe is a staff writer at X covering
# Y.") is scaffolding, not article prose — strip it per the "measure prose, not
# scaffolding" rule (baseline/README.md §1). Conservative: only fires on a
# short paragraph with the bio verb pattern, and only when it's the last one.
AUTHOR_BIO = re.compile(
    r"^[A-Z][\w.'-]+(?:\s+[A-Z][\w.'-]+){0,3}\s+is\s+(?:a|an|the)\s+"
    r"[^.]*\b(?:editor|writer|reporter|journalist|columnist|correspondent|"
    r"contributor|author|staff)\b",
    re.I,
)


def pick_rule(raw: str) -> dict | None:
    for rule in SITE_RULES:
        if re.search(rule["signature"], raw, re.I):
            return rule
    return None


def paragraphs_from(container_html: str) -> list[str]:
    cleaned = DROP_BLOCKS.sub(" ", container_html)
    out = []
    for m in re.finditer(r"<p\b([^>]*)>(.*?)</p>", cleaned, re.S | re.I):
        attrs, inner = m.group(1), m.group(2)
        if DROP_CLASS_P.search(attrs):
            continue
        text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        text = re.sub(r"\s+", " ", text)
        if len(text.split()) >= 3:  # drop stubs (bylines, "Advertisement")
            out.append(text)
    # Strip a trailing author-bio/credit line if present (only the last one, and
    # only when it's short enough to be a credit rather than a closing paragraph).
    if out and len(out[-1].split()) <= 45 and AUTHOR_BIO.match(out[-1]):
        out.pop()
    return out


def extract(raw: str) -> tuple[list[str], str, bool]:
    """Return (paragraphs, publication_name, low_confidence)."""
    rule = pick_rule(raw)
    if rule is None:
        # Generic fallback: the single largest <article> block, else all <p>.
        arts = re.findall(r"<article\b.*?</article>", raw, re.S | re.I)
        block = max(arts, key=len) if arts else raw
        return paragraphs_from(block), "UNKNOWN (generic fallback)", True

    if rule.get("multi"):
        blocks = re.findall(rule["container"], raw, re.S | re.I)
        paras: list[str] = []
        for b in blocks:
            paras.extend(paragraphs_from(b))
        return paras, rule["name"], rule.get("low_confidence", False)

    m = re.search(rule["container"], raw, re.S | re.I)
    if not m:
        arts = re.findall(r"<article\b.*?</article>", raw, re.S | re.I)
        block = max(arts, key=len) if arts else raw
        return paragraphs_from(block), f"{rule['name']} (container miss → fallback)", True
    return paragraphs_from(m.group(1)), rule["name"], rule.get("low_confidence", False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version",
                        version=f"extract_body.py {SCRIPT_VERSION}")
    parser.add_argument("file", type=Path)
    parser.add_argument("--out", type=Path, help="also write extracted prose here")
    parser.add_argument("--quiet", action="store_true", help="prose only, no report")
    args = parser.parse_args()

    raw = args.file.read_text(encoding="utf-8", errors="replace")
    paras, pub, low = extract(raw)
    prose = "\n\n".join(paras)
    words = len(re.findall(r"[A-Za-z0-9']+", prose))

    if args.out:
        args.out.write_text(prose, encoding="utf-8")

    if args.quiet:
        print(prose)
        return 0

    # Verification report: publication, paragraph count, word count, and the
    # first/last paragraph so the operator can confirm the boundary is right.
    print(f"# extract_body v{SCRIPT_VERSION}")
    print(f"# file:        {args.file.name}")
    print(f"# publication: {pub}")
    print(f"# confidence:  {'LOW — verify carefully' if low else 'container matched'}")
    print(f"# paragraphs:  {len(paras)}   words: {words}")
    if paras:
        print(f"# FIRST ¶: {paras[0][:160]}")
        print(f"# LAST  ¶: {paras[-1][:160]}")
    print("# --- extracted prose below (spot-check against the visible article) ---\n")
    print(prose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
