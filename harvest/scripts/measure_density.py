#!/usr/bin/env python3
"""
Measure prose-signature density metrics on a text, for the harvest's counting
layer (HARVEST_PLAN.md Component 4).

Two roles, one code path:
- Identification pass: measure real, pre-2023, editorially-excellent published
  writing *in situ at natural length*. Every metric is length-normalized
  (per-1,000-words or per-sentence rates), so a 90-word bio and a 2,500-word
  feature are directly comparable. The per-genre aggregate of these numbers is
  the human envelope in metrics-baseline.json. NOTE: this script measures a
  single text; envelope aggregation (median + spread per genre) is a separate
  step that consumes these rows.
- Harvest counting: measure each battery output (arm A / arm B) with the same
  metrics, then compare against the envelope. Same arithmetic, no self-report.

The metrics are deliberately arithmetic — immune to a model's blindness to its
own tics. Phrase-pattern lists (signposts, hedges, contrast-negation) are
top-of-file constants so the catalog can grow without touching logic.

Design constraints (HARVEST_PLAN.md):
- Zero external dependencies. Python 3.9+ stdlib only, same convention as
  build-deploy-bundles.py. No nltk/spacy — sentence segmentation is a
  regex splitter with an abbreviation guard, applied identically to human and
  model text so the *ratio* stays valid even where the split is imperfect.
- Constructions never set thresholds; only measured panel texts do. This
  script does not know or care which role a text plays — it just measures.

Usage:
    scripts/measure_density.py <file> [<file> ...]        # measure each, print JSON rows
    scripts/measure_density.py --markdown <file>          # treat input as markdown (enables bold/header/bullet metrics)
    scripts/measure_density.py --genre appeal <file>      # tag the output row with a genre
    scripts/measure_density.py --self-test                # run built-in metric sanity checks

Output: one JSON object per input file to stdout (JSON Lines). Fields are the
metric names below plus word_count, sentence_count, genre, and source path.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# This is a Phase-2 instrument; version it so a metrics-baseline.json can record
# which measurement code produced its envelopes. Re-deriving with a changed
# script is a versioned identification event, never a silent drift.
SCRIPT_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Phrase catalogs — editable without touching logic.
# Seeded from HARVEST_PLAN.md Component 4 examples; grows as harvests find more.
# All matched case-insensitively at a word boundary.
# ---------------------------------------------------------------------------

SIGNPOST_PHRASES = [
    "here's the thing",
    "the reality is",
    "let's break down",
    "let's be honest",
    "make no mistake",
    "the truth is",
]

HEDGE_CLOSER_PHRASES = [
    "ultimately",
    "at the end of the day",
    "in the end",
    "when all is said and done",
]

# Contrast-negation scaffolding: "not X — it's Y", "isn't just", "it's not about".
# These are structural, so they're regexes rather than fixed phrases.
CONTRAST_NEGATION_PATTERNS = [
    r"\bit'?s not (?:just |only |about |that )",
    r"\bisn'?t just\b",
    r"\bisn'?t (?:about|only|merely)\b",
    r"\bnot (?:just|only|merely)\b[^.!?]*?\bbut\b",
    r"\bnot [A-Za-z]+\s*[—–-]\s*(?:it'?s|but)\b",
    r"\bthis isn'?t\b[^.!?]*?;?\s*it'?s\b",
]

# Common abbreviations that end in a period but do not end a sentence.
# Used to guard the regex sentence splitter against false breaks.
ABBREVIATIONS = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc", "eg",
    "ie", "no", "vol", "inc", "ltd", "co", "corp", "dept", "est", "fig",
    "al", "approx", "apt", "ave", "gen", "gov", "hon", "rev", "sen", "u.s",
    "u.k", "p.s", "a.m", "p.m",
}

# ---------------------------------------------------------------------------
# Tokenization / segmentation
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*")


def words(text: str) -> list[str]:
    """Word tokens for counting. Hyphenated/apostrophized words count once."""
    return _WORD_RE.findall(text)


def word_count(text: str) -> int:
    return len(words(text))


# Sentence splitter: break after . ! ? (and terminal quotes/brackets), unless
# the token before the period is a known abbreviation or a single initial.
_SENT_BOUNDARY_RE = re.compile(r'([.!?]+)(["”’\')\]]*)\s+')


def sentences(text: str) -> list[str]:
    """Regex sentence segmentation with an abbreviation guard.

    Imperfect by design (no parser), but applied identically to every text, so
    rate comparisons between human and model prose remain valid. Markdown
    structure (headers, list markers) is stripped upstream by strip_markdown()
    when --markdown is set; here we operate on whatever prose we're given.
    """
    # Flatten newlines to spaces for boundary detection, but keep paragraph
    # breaks recoverable elsewhere (paragraphs() works on the raw text).
    flat = re.sub(r"\s+", " ", text.strip())
    if not flat:
        return []

    out: list[str] = []
    start = 0
    for m in _SENT_BOUNDARY_RE.finditer(flat):
        end = m.end()
        candidate = flat[start:m.start()] + m.group(1)
        # Guard: if the word right before the terminator is an abbreviation or
        # a single capital letter (an initial), don't break here.
        prior = re.search(r"(\S+)$", flat[start:m.start()])
        token = prior.group(1).lower().rstrip(".") if prior else ""
        is_initial = len(token) == 1 and token.isalpha()
        if token in ABBREVIATIONS or is_initial:
            continue
        out.append(candidate.strip())
        start = end
    tail = flat[start:].strip()
    if tail:
        out.append(tail)
    return [s for s in out if words(s)]


def paragraphs(text: str) -> list[str]:
    """Blank-line-separated blocks that contain at least one word."""
    blocks = re.split(r"\n\s*\n", text.strip())
    return [b.strip() for b in blocks if words(b)]


# ---------------------------------------------------------------------------
# Markdown handling
# ---------------------------------------------------------------------------

_HEADER_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S", re.MULTILINE)
_BULLET_LINE_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\S", re.MULTILINE)
_BOLD_LEADIN_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+)?(?:\*\*|__)")


def strip_markdown(text: str) -> str:
    """Remove markdown structural syntax for prose-level metrics.

    Only strips markers (headers, emphasis, list bullets, links to their text)
    so that word/sentence/em-dash rates measure the prose, not the syntax.
    Structural metrics (header_density, bullet_share, bold_leadin_rate) read the
    raw markdown separately, before this runs.
    """
    t = text
    t = re.sub(r"^\s{0,3}#{1,6}\s+", "", t, flags=re.MULTILINE)   # headers
    t = re.sub(r"(\*\*|__|\*|_)(.+?)\1", r"\2", t)                # emphasis
    t = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", t, flags=re.MULTILINE)  # bullets
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)                # links -> text
    t = re.sub(r"`([^`]+)`", r"\1", t)                           # inline code
    return t


# ---------------------------------------------------------------------------
# Metric primitives
# ---------------------------------------------------------------------------

def _per_1000(count: int, n_words: int) -> float:
    return round(1000.0 * count / n_words, 3) if n_words else 0.0


def em_dash_rate(prose: str, n_words: int) -> float:
    # Em-dash proper, plus the spaced-hyphen and en-dash people use as one.
    count = prose.count("—") + len(re.findall(r"\s[–-]\s", prose))
    return _per_1000(count, n_words)


def contrast_negation_rate(prose: str, n_words: int) -> float:
    count = 0
    for pat in CONTRAST_NEGATION_PATTERNS:
        count += len(re.findall(pat, prose, flags=re.IGNORECASE))
    return _per_1000(count, n_words)


def _phrase_count(prose: str, phrases: list[str]) -> int:
    count = 0
    for p in phrases:
        count += len(re.findall(r"\b" + re.escape(p) + r"\b", prose, flags=re.IGNORECASE))
    return count


def signpost_rate(prose: str, n_words: int) -> float:
    return _per_1000(_phrase_count(prose, SIGNPOST_PHRASES), n_words)


def hedge_closer_rate(prose: str, n_words: int) -> float:
    return _per_1000(_phrase_count(prose, HEDGE_CLOSER_PHRASES), n_words)


def triadic_rate(sents: list[str]) -> float:
    """% of sentences containing a three-item parallel series.

    Broader-parallelism variant (per operator decision): catches both the
    comma-list form ("A, B, and C") and comma-less verb/clause triads
    ("we build, we grow, we thrive" / "she came, she saw, she conquered").

    PROXY, not true syntactic-parallelism detection — separating a real series
    from an appositive that contains an internal "and" ("Flagpole Field, an
    amazing and accessible space") is a parsing problem no regex resolves
    cleanly. Known residual: ~1–2 appositive false-positives per ~600 words.
    Accepted for Phase 1 because the SAME noise applies to both the human panel
    and the model outputs it is compared against, so the ratio (which the
    threshold uses) stays fair even though the absolute rate carries noise.
    Phase 2 replaces this with a parser-backed detector (paired with
    fragment_rate, the other parser-dependent metric).
    """
    if not sents:
        return 0.0
    hits = 0
    for s in sents:
        if _has_comma_list_triad(s) or _looks_like_clause_triad(s):
            hits += 1
    return round(100.0 * hits / len(sents), 2)


def _has_comma_list_triad(sentence: str) -> bool:
    """Detect a genuine three-item comma series: 'A, B, and C' / 'A, B and C'.

    The distinguishing feature vs. an appositive-then-conjunction sentence
    ("Matthew, an Ooch camper, shared ... and ganging up") is that a real
    series joins *short, parallel* items with the final and/or. So we require
    the item before the conjunction and the item after it to both be short
    (≤ 5 words) and the preceding comma item to be short too — a long clause
    before "and" means it's coordination, not a list.
    """
    # Find "... , <item> ,? and/or <item>" near the tail of a comma run.
    for mtch in re.finditer(
        r",\s*([^,]{1,60}?)\s*,?\s+(?:and|or)\s+([^,.;:!?]{1,40})", sentence
    ):
        before, after = mtch.group(1), mtch.group(2)
        if len(words(before)) <= 5 and len(words(after)) <= 5:
            # Require at least two commas earlier in the sentence (three items).
            head = sentence[:mtch.start() + 1]
            if head.count(",") >= 1:
                return True
    return False


def _looks_like_clause_triad(sentence: str) -> bool:
    """Heuristic: three *consecutive* comma segments of comparable short length.

    Targets rhythmic triads without a coordinating comma-list ('we build, we
    grow, we thrive'). Tightened after the loose first cut flagged ordinary
    sentences whose scattered commas merely happened to include short spans
    (e.g. "To me, the Magic of X is the infinite positives..."). A real triad
    is a contiguous run of three similarly-sized short clauses, so we require:
      - a window of 3 adjacent comma segments,
      - each 1–5 words,
      - lengths close together (max not more than ~2x the min),
    which keeps comma-less parallel triads while rejecting incidental commas.
    """
    segs = [seg.strip() for seg in sentence.split(",") if seg.strip()]
    if len(segs) < 3:
        return False
    lens = [len(words(seg)) for seg in segs]
    for i in range(len(lens) - 2):
        window = lens[i:i + 3]
        if all(1 <= n <= 5 for n in window) and max(window) <= 2 * min(window):
            return True
    return False


def header_density(raw_md: str, n_words: int) -> float:
    """Headings per 500 words (markdown inputs only)."""
    count = len(_HEADER_RE.findall(raw_md))
    return round(500.0 * count / n_words, 3) if n_words else 0.0


def bullet_share(raw_md: str) -> float:
    """% of body lines that are list items (markdown inputs only)."""
    lines = [ln for ln in raw_md.splitlines() if ln.strip()]
    if not lines:
        return 0.0
    bullets = len([ln for ln in lines if _BULLET_LINE_RE.match(ln)])
    return round(100.0 * bullets / len(lines), 2)


def bold_leadin_rate(raw_md: str) -> float:
    """% of paragraphs whose first non-space content is bold (markdown only)."""
    paras = paragraphs(raw_md)
    if not paras:
        return 0.0
    lead = len([p for p in paras if _BOLD_LEADIN_RE.match(p)])
    return round(100.0 * lead / len(paras), 2)


def sentence_length_cv(sents: list[str]) -> float | None:
    """Coefficient of variation of sentence length in words (burstiness).

    Humans run higher; models cluster near the mean. None if <2 sentences.
    """
    lengths = [word_count(s) for s in sents]
    if len(lengths) < 2:
        return None
    mean = statistics.mean(lengths)
    if mean == 0:
        return None
    return round(statistics.pstdev(lengths) / mean, 4)


def paragraph_uniformity(paras: list[str]) -> float | None:
    """Std-dev of paragraph length in words. Lower = eerily uniform (model-ish).

    None if <2 paragraphs. Reported raw (not normalized) — the envelope holds
    the human spread; a per-genre comparison is what makes it meaningful.
    """
    lengths = [word_count(p) for p in paras]
    if len(lengths) < 2:
        return None
    return round(statistics.pstdev(lengths), 3)


def fragment_rate(prose: str, n_words: int) -> None:
    """Sentence fragments per 1,000 words.

    STUB (Phase 1): reliable fragment detection needs a grammar parser; a
    heuristic misclassifies imperatives, quotes, and headers and would pollute
    the envelope. Returns None until Phase 2 ships a parser-backed detector.
    The judge and external-signal detectors cover fragments meanwhile.
    """
    return None


# ---------------------------------------------------------------------------
# Top-level measurement
# ---------------------------------------------------------------------------

def measure(text: str, *, is_markdown: bool = False, genre: str | None = None,
            source: str | None = None) -> dict:
    raw = text
    prose = strip_markdown(raw) if is_markdown else raw

    n_words = word_count(prose)
    sents = sentences(prose)
    paras = paragraphs(raw if is_markdown else prose)

    row: dict = {
        "source": source,
        "genre": genre,
        "script_version": SCRIPT_VERSION,
        "is_markdown": is_markdown,
        "word_count": n_words,
        "sentence_count": len(sents),
        "paragraph_count": len(paras),
        # length-normalized prose metrics
        "em_dash_rate": em_dash_rate(prose, n_words),
        "contrast_negation_rate": contrast_negation_rate(prose, n_words),
        "triadic_rate": triadic_rate(sents),
        "signpost_rate": signpost_rate(prose, n_words),
        "hedge_closer_rate": hedge_closer_rate(prose, n_words),
        "sentence_length_cv": sentence_length_cv(sents),
        "paragraph_uniformity": paragraph_uniformity(paras),
        "fragment_rate": fragment_rate(prose, n_words),  # None (Phase-1 stub)
    }
    # Markdown-structure metrics only meaningful when the input is markdown.
    if is_markdown:
        row["header_density"] = header_density(raw, n_words)
        row["bullet_share"] = bullet_share(raw)
        row["bold_leadin_rate"] = bold_leadin_rate(raw)
    else:
        row["header_density"] = None
        row["bullet_share"] = None
        row["bold_leadin_rate"] = None
    return row


# ---------------------------------------------------------------------------
# Self-test — metric sanity checks (not a substitute for the negative-control
# artifacts, which test the counters against the envelope end-to-end).
# ---------------------------------------------------------------------------

def _self_test() -> int:
    failures = []

    def check(name, cond):
        if not cond:
            failures.append(name)

    tic = ("It's not about the money — it's about the mission. We build, we "
           "grow, we thrive. Ultimately, this matters. Here's the thing: it "
           "isn't just work.")
    r = measure(tic)
    check("em_dash fires", r["em_dash_rate"] > 0)
    check("contrast_negation fires", r["contrast_negation_rate"] > 0)
    check("triadic fires", r["triadic_rate"] > 0)
    check("signpost fires", r["signpost_rate"] > 0)
    check("hedge_closer fires", r["hedge_closer_rate"] > 0)

    plain = ("The land trust stewards sixty-two homes. Each family signs a "
             "ground lease. When they sell, a formula caps the resale price. "
             "This keeps the homes affordable for the next household.")
    rp = measure(plain)
    check("plain: no contrast-negation", rp["contrast_negation_rate"] == 0)
    check("plain: no signpost", rp["signpost_rate"] == 0)
    check("cv computed", rp["sentence_length_cv"] is not None)

    md = "# Title\n\n**Bold lead.** Body text here.\n\n- item one\n- item two\n"
    rm = measure(md, is_markdown=True)
    check("header_density fires on md", rm["header_density"] > 0)
    check("bullet_share fires on md", rm["bullet_share"] > 0)
    check("bold_leadin fires on md", rm["bold_leadin_rate"] > 0)

    check("abbrev guard: 'Dr. Smith left.' is 1 sentence",
          len(sentences("Dr. Smith left.")) == 1)
    check("two sentences split",
          len(sentences("He ran. She walked.")) == 2)
    check("fragment_rate is stubbed None", rp["fragment_rate"] is None)

    if failures:
        print("SELF-TEST FAILURES:", ", ".join(failures), file=sys.stderr)
        return 1
    print("self-test: all checks passed", file=sys.stderr)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version",
                        version=f"measure_density.py {SCRIPT_VERSION}")
    parser.add_argument("files", nargs="*", type=Path,
                        help="text/markdown files to measure")
    parser.add_argument("--markdown", action="store_true",
                        help="treat inputs as markdown (enables structural metrics)")
    parser.add_argument("--genre", default=None,
                        help="tag output rows with this battery genre")
    parser.add_argument("--self-test", action="store_true",
                        help="run built-in metric sanity checks and exit")
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if not args.files:
        parser.error("no input files (or use --self-test)")

    for path in args.files:
        text = path.read_text(encoding="utf-8", errors="replace")
        is_md = args.markdown or path.suffix.lower() in {".md", ".markdown"}
        row = measure(text, is_markdown=is_md, genre=args.genre, source=str(path))
        print(json.dumps(row, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
