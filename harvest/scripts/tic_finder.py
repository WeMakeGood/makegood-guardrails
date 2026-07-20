#!/usr/bin/env python3
"""
Tic-finder — open discovery diff (harvest H3, leg 4a).

Takes a target model's writing and the frozen synthetic exemplar for the same
brief, and returns the features the target *over-represents* relative to the
exemplar — ranked. Unlike measure_density.py (leg 4b), this does NOT work from a
predefined tic list: it ranks ALL features (words, n-grams, punctuation,
sentence openings, sentence shapes) by over-representation, so a tic we have
never named can surface. That is the whole point — discovery over confirmation.

The comparison is *task-matched*: target output vs. the exemplar written to the
same brief and fact sheet. So a difference is attributable to how it's written,
not what it's about. Over-representation is scored by log-odds-ratio with a
Dirichlet prior (Monroe/Colaresi/Quinn "fightin' words" keyness) — the standard
method for "which features distinguish corpus A from corpus B," robust to the
frequency/rareness confound a raw ratio suffers.

What it is NOT:
- Not a verdict. A high-ranked feature is a *candidate*, named by a human at
  compile time and grounding-checked against real human writing before it can
  become a backstop entry (a feature over-represented here but also common in
  excellent human prose is craft, not a tic).
- Not the whole detector. Pair it with the blind judge (differential reading)
  and, for known entries, measure_density.py's regression. Admission needs
  corroboration across detector families (HARVEST_PLAN Component 7).

Usage:
    scripts/tic_finder.py --target OUT.md --exemplar EX.md          # one pair
    scripts/tic_finder.py --target-dir outputs/ --exemplar-dir baseline/baseline/exemplars/
        # pool by matching <prompt-id>: outputs/<id>.md vs exemplars/<id>/exemplar.md
    scripts/tic_finder.py --target OUT.md --exemplar EX.md --top 40 --json

Output: ranked over-represented features with their log-odds z-score and raw
counts in each side. Grouped by feature family (words / bigrams / trigrams /
punctuation / openings / shapes).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

SCRIPT_VERSION = "0.1.0"

# Reuse the panel's prose-vs-scaffolding discipline: this tool assumes it is
# handed already-stripped prose (extract_body.py output), same as the exemplars.

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*")
_SENT_SPLIT = re.compile(r'(?<=[.!?])["”’\')\]]*\s+')


def words(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text)]


def sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text.strip())
    return [s for s in _SENT_SPLIT.split(flat) if s.strip()]


# ---------------------------------------------------------------------------
# Feature extraction — each family is a Counter of feature -> count.
# Deliberately broad and un-curated: we are NOT selecting for known tics.
# ---------------------------------------------------------------------------

def features(text: str) -> dict[str, Counter]:
    ws = words(text)
    sents = sentences(text)

    fam: dict[str, Counter] = {
        "word": Counter(ws),
        "bigram": Counter(" ".join(b) for b in zip(ws, ws[1:])),
        "trigram": Counter(" ".join(t) for t in zip(ws, ws[1:], ws[2:])),
        "punct": Counter(),
        "opening": Counter(),
        "shape": Counter(),
    }

    # Punctuation marks (every mark, not a chosen subset)
    for ch in text:
        if ch in "—–-;:,.!?…()\"'“”‘’":
            fam["punct"][ch] += 1
    # Em-dash and spaced-dash usage as its own feature
    fam["punct"]["<em_dash>"] = text.count("—")
    fam["punct"]["<spaced_dash>"] = len(re.findall(r"\s[–-]\s", text))

    for s in sents:
        sw = _WORD_RE.findall(s)
        if not sw:
            continue
        # Sentence opening: first 1-2 lowercased tokens
        fam["opening"][sw[0].lower()] += 1
        if len(sw) >= 2:
            fam["opening"][f"{sw[0].lower()} {sw[1].lower()}"] += 1
        # Sentence shape features (structural, tic-agnostic)
        n = len(sw)
        if n <= 4:
            fam["shape"]["very_short_sentence(<=4w)"] += 1
        elif n >= 35:
            fam["shape"]["very_long_sentence(>=35w)"] += 1
        if "—" in s:
            fam["shape"]["sentence_with_em_dash"] += 1
        # 3-item comma series (rough): "a, b, and c"
        if re.search(r"\w+,\s+\w[\w ]*,\s+(?:and|or)\s+\w", s):
            fam["shape"]["triadic_series"] += 1
        # Colon-led elaboration
        if ":" in s:
            fam["shape"]["colon_in_sentence"] += 1
        # Fragment-ish: no finite-verb heuristic is unreliable; use "starts with
        # conjunction" as a stylistic-opening shape instead (And/But/Because...)
        if sw[0].lower() in ("and", "but", "because", "so", "yet", "or"):
            fam["shape"]["conjunction_opening"] += 1
    return fam


# ---------------------------------------------------------------------------
# Keyness: log-odds-ratio with informative Dirichlet prior (Monroe et al.).
# Positive z => over-represented in target vs exemplar.
# ---------------------------------------------------------------------------

def log_odds_keyness(target: Counter, ref: Counter, alpha: float = 0.01):
    vocab = set(target) | set(ref)
    nt = sum(target.values())
    nr = sum(ref.values())
    a0 = alpha * len(vocab)
    results = []
    for w in vocab:
        yt = target.get(w, 0)
        yr = ref.get(w, 0)
        # log-odds with prior
        lt = math.log((yt + alpha) / (nt + a0 - yt - alpha))
        lr = math.log((yr + alpha) / (nr + a0 - yr - alpha))
        delta = lt - lr
        var = 1.0 / (yt + alpha) + 1.0 / (yr + alpha)
        z = delta / math.sqrt(var)
        results.append((w, z, yt, yr))
    results.sort(key=lambda r: r[1], reverse=True)
    return results


def diff_pair(target_text: str, ref_text: str, top: int):
    tf = features(target_text)
    rf = features(ref_text)
    out: dict[str, list] = {}
    for fam in tf:
        ranked = log_odds_keyness(tf[fam], rf[fam])
        # keep only over-represented (z>0) with a real target presence
        over = [(w, round(z, 2), yt, yr) for (w, z, yt, yr) in ranked
                if z > 0 and yt >= 2]
        out[fam] = over[:top]
    return out


def load(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def print_report(pairs: list[tuple[str, dict]], top: int):
    for label, fams in pairs:
        print(f"\n{'='*60}\n{label}\n{'='*60}")
        for fam in ("shape", "opening", "punct", "trigram", "bigram", "word"):
            rows = fams.get(fam, [])
            if not rows:
                continue
            print(f"\n  [{fam}] over-represented in target (z / target# / ref#):")
            for w, z, yt, yr in rows[: (8 if fam in ("word", "bigram") else top)]:
                print(f"    {z:6.2f}  {yt:>3} vs {yr:<3}  {w}")
    print("\n(Candidates, not verdicts — grounding-check against real human "
          "writing before admission; corroborate with the blind judge.)\n")


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"tic_finder.py {SCRIPT_VERSION}")
    p.add_argument("--target", type=Path, help="target model output (prose)")
    p.add_argument("--exemplar", type=Path, help="frozen exemplar for the same brief")
    p.add_argument("--target-dir", type=Path, help="dir of <prompt-id>.md target outputs")
    p.add_argument("--exemplar-dir", type=Path, help="baseline/exemplars/ dir")
    p.add_argument("--top", type=int, default=25, help="max features per family")
    p.add_argument("--pooled", action="store_true",
                   help="with --target-dir/--exemplar-dir: pool all briefs into one "
                        "keyness diff (where the statistical signal reaches significance)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    pairs: list[tuple[str, dict]] = []
    if args.target and args.exemplar:
        pairs.append((f"{args.target.name}  vs  {args.exemplar.name}",
                      diff_pair(load(args.target), load(args.exemplar), args.top)))
    elif args.target_dir and args.exemplar_dir:
        # Collect brief-matched pairs.
        matched = []
        for tgt in sorted(args.target_dir.glob("*.md")):
            pid = tgt.stem
            # Multi-sample outputs are <brief>.<NN>.md (e.g. AN04.02); every
            # sample of a brief pairs against that brief's single exemplar. Strip
            # an all-digits trailing suffix to recover the brief id (mirrors
            # run_judge.py's _brief_of). A plain <brief>.md still maps to itself.
            head, _, tail = pid.rpartition(".")
            brief = head if head and tail.isdigit() else pid
            ex = args.exemplar_dir / brief / "exemplar.md"
            if not ex.exists():
                print(f"# no exemplar for {brief} (sample {pid}), skipping",
                      file=sys.stderr)
                continue
            matched.append((pid, tgt, ex))
        if not matched:
            p.error("no <prompt-id>.md targets matched an exemplar")
        if args.pooled:
            # Pool all targets vs all exemplars — one keyness diff. Genre cancels
            # because both sides are matched brief-for-brief. This is where the
            # statistical signal actually reaches significance (N=1 pairs are
            # underpowered — keyness needs corpus-scale counts).
            tpool = "\n\n".join(load(t) for _, t, _ in matched)
            rpool = "\n\n".join(load(e) for _, _, e in matched)
            label = (f"POOLED: {len(matched)} briefs "
                     f"({', '.join(pid for pid, _, _ in matched)}) "
                     f"— target vs exemplar")
            pairs.append((label, diff_pair(tpool, rpool, args.top)))
        else:
            for pid, tgt, ex in matched:
                pairs.append((f"{pid}: {tgt.name} vs exemplar",
                              diff_pair(load(tgt), load(ex), args.top)))
    else:
        p.error("give --target and --exemplar, or --target-dir and --exemplar-dir")

    if args.json:
        print(json.dumps({label: fams for label, fams in pairs}, ensure_ascii=False, indent=2))
    else:
        print_report(pairs, args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
