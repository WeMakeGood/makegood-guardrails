#!/usr/bin/env python3
"""
family_rollup.py — independent keyword-family rollup of judge raw_differences.

A cross-check on run_judge.py's LLM clustering, NOT a replacement. The judge
phrases nearly every difference uniquely (~1000 distinct labels / arm), so
exact-string tally collapses to ~zero and the LLM clusterer is the primary
grouping. This script groups the SAME raw_differences by a fixed keyword-family
map, applies the same two-level recurrence gate (>= min_samples of a brief to
qualify it, >= min_briefs qualifying briefs to be a candidate), and reports
target-side families ranked by qualifying-brief breadth.

Value: it is deterministic and transparent (you can read the keyword map), so
where it AGREES with the LLM clustering that agreement is robust; where they
differ, a human looks. Keyword families are broad on purpose — a family is a
hypothesis a human names precisely at compile time (HARVEST.md H6).

    family_rollup.py --tally-json tally-offline-<m>-<a>.json [--min-samples 2 --min-briefs 3]
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import defaultdict
from pathlib import Path

# Broad keyword families over the judge's free-text feature labels. A label can
# match several; it counts under each it matches (families are overlapping
# hypotheses, not a partition). Ordered roughly by the tics the harvest cares
# about; content-word families are deliberately absent (those are noise).
FAMILIES = {
    "em-dash / dash habits":        r"\bem[- ]?dash|\bdash(es|ing)?\b|—",
    "contrast-negation scaffolding": r"not (just|only|about)|isn'?t (about|just)|rather than|it'?s not\b|negat",
    "triadic / rule-of-three":      r"triad|rule of three|tricolon|three[- ]part|triple|list of three",
    "uniform paragraph shape":      r"uniform|formulaic|template|repeated (structure|shape|pattern)|same (shape|structure|rhythm)|mechanical|parallel structure",
    "aphoristic / button endings":  r"aphoris|button|clincher|snap|neat clos|epigram|punch(y)? clos|closing (line|aphorism)|chiasm|antithe",
    "signposting / meta-structure": r"signpost|meta[- ]?(comment|structur)|scaffold|enumerat|labeled|topic sentence|transition(al)? phras|firstly|in conclusion",
    "hedging / over-qualification": r"hedg|qualif|caveat|equivocat|both[- ]sides|on the one hand|balanced (view|framing)|noncommit",
    "listy / bulleted formatting":  r"bullet|numbered list|list(-| )(format|heavy)|header|sub[- ]?head",
    "inflated / abstract diction":  r"inflat|abstract (noun|diction)|elevated|grandiose|lofty|nominal|jargon|corporate",
    "hype / evaluative adjectives": r"hype|superlativ|promotional|evaluative adjectiv|booster|intensifier|adverb",
    "conversational / chatty register": r"conversational|chatty|informal|colloquial|contraction|second person|direct address|\byou\b",
    "parenthetical asides":         r"parenthe|aside|\(.*\)|interject",
    "metaphor / imagery (craft)":   r"metaphor|imagery|sensory|concrete detail|vivid|figurative|analogy",
    "rhetorical questions":         r"rhetorical question|\bquestion(s)? as\b|posing a question",
}


def rollup(raw, min_samples, min_briefs):
    fam_brief_samples = defaultdict(lambda: defaultdict(set))  # fam -> brief -> {pid}
    fam_habit = defaultdict(set)                               # fam -> {pid flagged habit}
    fam_examples = defaultdict(list)
    for d in raw:
        if d["side"] != "target":
            continue
        feat = d["feature"]
        low = feat.lower()
        for fam, pat in FAMILIES.items():
            if re.search(pat, low):
                fam_brief_samples[fam][d["brief"]].add(d["pair"])
                if d.get("generated_habit"):
                    fam_habit[fam].add(d["pair"])
                if len(fam_examples[fam]) < 4:
                    fam_examples[fam].append((d["pair"], feat))
    rows = []
    for fam, briefs in fam_brief_samples.items():
        qual = {b: sorted(s) for b, s in briefs.items() if len(s) >= min_samples}
        allpairs = {p for s in briefs.values() for p in s}
        rows.append({
            "family": fam,
            "n_qualifying_briefs": len(qual),
            "n_pairs": len(allpairs),
            "n_briefs_touched": len(briefs),
            "n_habit_pairs": len(fam_habit[fam]),
            "qualifying_briefs": sorted(qual),
            "candidate": len(qual) >= min_briefs,
            "examples": fam_examples[fam],
        })
    rows.sort(key=lambda r: (-r["n_qualifying_briefs"], -r["n_pairs"]))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tally-json", type=Path, required=True,
                    help="a run_judge.py tally --json file (uses its raw_differences)")
    ap.add_argument("--min-samples", type=int, default=2)
    ap.add_argument("--min-briefs", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    data = json.loads(args.tally_json.read_text())
    rows = rollup(data["raw_differences"], args.min_samples, args.min_briefs)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2)); return 0
    print(f"\nFAMILY ROLLUP  ({args.tally_json.name})")
    print(f"two-level gate: >= {args.min_samples} samples/brief to qualify, "
          f">= {args.min_briefs} qualifying briefs = candidate (*)")
    print(f"{'qual':>4} {'pairs':>5} {'habit':>5}  family")
    for r in rows:
        mark = " *" if r["candidate"] else "  "
        print(f"{r['n_qualifying_briefs']:>4} {r['n_pairs']:>5} "
              f"{r['n_habit_pairs']:>5}{mark} {r['family']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
