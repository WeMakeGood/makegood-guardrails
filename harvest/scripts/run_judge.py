#!/usr/bin/env python3
"""
run_judge.py — blind-judge leg (harvest H4, Component 5).

The second, independent detector. Where tic_finder.py (4a) ranks features a
target OVER-represents against a task-matched reference distribution, the judge
reads two concrete passages side by side and enumerates HOW they differ in the
writing. Two properties make it worth building even though 4a already exists:

- It works at any N. It reads holistically, so it surfaces tics from a single
  pair — no pooled corpus needed — and it catches pattern-level tics no regex
  can rank ("every paragraph is the same three-move shape").
- It covers 4a's named blind spot. A tic SHARED by the exemplar generator and
  the target cancels out of the task-matched keyness diff and is invisible to
  tic_finder.py. The judge never sees the reference distribution — only two
  passages — so a shared tic still shows up as something present in the target.

Blindness is the whole point, and this harness enforces it structurally rather
than trusting the judge to look away:

  * A/B order is randomized per pair, independently.
  * Provenance is stripped from the packet the judge reads.
  * The order map (which of A/B is the target) is SEALED to key.json, which the
    judge never sees. Only `tally` opens it, to resolve differences back to a
    side (target vs. exemplar) after the judgment is in.
  * Each pair is its own packet — fresh context, no carryover.

The judge does hard analytic work — reading two passages and enumerating how
they differ — so it should be the **most capable analytic model available at
harvest time**, chosen on merit. (This supersedes an earlier "different
generation than the target" framing: capability is the criterion, not
generational distance.) As of 2026-07-17 that is `claude-opus-4-8`; pass the
newest most-capable model when a better one ships. Anthropic publishes no
"latest" alias — model IDs are always pinned — so the operator names the model
explicitly via --judge-model and records it in the report provenance block.

One overlap to note rather than forbid: when the target under test happens to be
the same model chosen as judge, say so in the provenance — a model judging output
from its own generation is a weaker independent check than a distinct judge.
The harness cannot enforce any of this; the operator records the actual model.

Three subcommands, one packet format, one judgment schema:

    # 1. Build blinded packets + sealed key from an arm's outputs.
    run_judge.py prepare \\
        --target-dir reports/<id>/outputs/<model>/B \\
        --exemplar-dir baseline/exemplars \\
        --out reports/<id>/judgments

    # 2. (offline) The judge reads each packet, writes pair-<pid>.json beside it
    #    per the schema printed into every packet. Or, optionally:
    run_judge.py dispatch --judgments reports/<id>/judgments \\
        --judge-model claude-sonnet-5   # needs `anthropic` SDK + ANTHROPIC_API_KEY

    # 3. Resolve blinding, cluster, and compile the difference tally.
    run_judge.py tally --judgments reports/<id>/judgments

`prepare` and `tally` are stdlib-only and offline, like every other harvest
script. `dispatch` is the one optional path that imports `anthropic` and touches
the network — it is never on the critical path; the offline flow is complete
without it.

Candidates, not verdicts. A target-side difference recurring across >= 3 pairs
is a CANDIDATE, named for the compile step (HARVEST.md H6) and grounding-checked
before it can reach the backstop. Exemplar-side recurrences are never dropped —
they route to the exemplar re-approval queue (HARVEST.md H4).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_VERSION = "0.2.0"  # 0.2.0: multi-sample per brief + two-level recurrence tally

# The differential-reading prompt. Kept verbatim in sync with HARVEST.md H4 — if
# one changes, change both. The judge compares two responses to the SAME brief
# and enumerates how they are written, NOT which is the machine. Asking "which is
# AI" would invite the judge to pattern-match against its prior of what AI writing
# looks like; asking "how do they differ" keeps it reading the passages in hand.
JUDGE_PROMPT = """\
These are two responses to the same brief, working from the same fact sheet.
Compare **how they are written**, not what they say. 1) Enumerate every
systematic difference in the writing — structure, rhythm, sentence and
paragraph shapes, word choice, emphasis habits, formatting, how evidence is
used. Quote exact phrases for each. 2) For each difference, name which
passage does it. 3) If either passage shows patterns that read as *generated
habits imposed on the content* rather than choices serving it, name them
specifically."""

# The schema the judge fills, one file per pair. Structured so `tally` never has
# to parse prose: each difference names the SIDE ("A"/"B") the packet showed, and
# tally resolves that back to target/exemplar via the sealed key.
SCHEMA_DOC = {
    "pair": "<prompt-id, copied from the packet>",
    "differences": [
        {
            "feature": "short human-named pattern, e.g. 'em-dash cascades' "
                       "or 'uniform three-move paragraph shape'",
            "side": "A | B | both  — which passage exhibits it (as labeled in "
                    "THIS packet; do not guess provenance)",
            "generated_habit": "true if it reads as a generated habit imposed "
                               "on the content rather than a choice serving it "
                               "(prompt step 3); else false",
            "quote": "exact phrase(s) from that passage evidencing it",
            "note": "optional: one line on structure/rhythm the quote can't show",
        }
    ],
}

# Stable, deterministic blinding. We must randomize A/B order per pair, but the
# harvest scripts forbid Math.random-style nondeterminism (reproducibility: a
# rerun of `prepare` on the same inputs must produce the same packets, or the
# sealed key stops matching a re-prepared packet). So the coin flip is a hash of
# a fixed seed + the prompt id: uniform-enough across ids, and identical on rerun.
_BLIND_SEED = "harvest-h4-blind-judge"


def _target_is_A(pid: str) -> bool:
    h = hashlib.sha256(f"{_BLIND_SEED}:{pid}".encode("utf-8")).hexdigest()
    # low bit of the digest as the coin. Seeded on the FULL sample-pair id
    # (e.g. "AN04.02"), so multiple samples of one brief get independent A/B
    # assignments rather than all landing on the same side — that independence
    # is what keeps the blinding from being guessable per brief.
    return int(h[-1], 16) % 2 == 0


def _brief_of(pid: str) -> str:
    """Brief id for a sample-pair id.

    Target samples are named <brief>.<NN>.md (e.g. AN04.02.md), so the pair id is
    "AN04.02" and the brief is "AN04". A plain <brief>.md (single-sample, the
    legacy shape) has no numeric suffix and is its own brief. Recognizing the
    suffix only when it is all digits avoids mangling a brief id that itself
    contains a dot.
    """
    head, _, tail = pid.rpartition(".")
    if head and tail.isdigit():
        return head
    return pid


def load(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _load_env_local() -> Path | None:
    """Load KEY=value pairs from the repo's gitignored .env.local into os.environ.

    Only for the `dispatch` API path. Keeps the credential in one gitignored file
    instead of a global export or a command-line arg (which would leak into shell
    history). Walks up from this script to find .env.local at the repo root.
    Does not overwrite a variable already set in the real environment — an
    explicit export still wins. Returns the file it loaded, or None.
    """
    import os
    for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        candidate = parent / ".env.local"
        if candidate.is_file():
            for raw in candidate.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
            return candidate
    return None


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# prepare — build blinded packets + sealed key.
# ---------------------------------------------------------------------------

def _match_pairs(target_dir: Path, exemplar_dir: Path):
    """Yield (pid, brief, target_path, exemplar_path) for every target sample.

    Each target file is one sample. Its stem is the sample-pair id (pid); the
    brief id is derived from it (see _brief_of). Every sample of a brief pairs
    against that brief's single exemplar (exemplars/<brief>/exemplar.md), so N
    samples of AN04 all compare against one AN04 exemplar. A single-sample run
    (target file AN04.md) still works: pid == brief == "AN04".
    """
    matched = []
    for tgt in sorted(target_dir.glob("*.md")):
        pid = tgt.stem
        brief = _brief_of(pid)
        ex = exemplar_dir / brief / "exemplar.md"
        if not ex.exists():
            print(f"# no exemplar for brief {brief} (sample {pid}), skipping",
                  file=sys.stderr)
            continue
        matched.append((pid, brief, tgt, ex))
    return matched


def _packet_text(pid: str, passage_a: str, passage_b: str) -> str:
    schema_json = json.dumps(SCHEMA_DOC, ensure_ascii=False, indent=2)
    return f"""\
# Judge packet — pair {pid}

{JUDGE_PROMPT}

---

## Passage A

{passage_a.strip()}

---

## Passage B

{passage_b.strip()}

---

## How to record your judgment

Write your answer as `pair-{pid}.json` in this directory, matching this schema
exactly. One object per systematic difference you found. Use the passage labels
A and B as they appear above — do not speculate about which passage is
machine-generated or human; that is not your task and the mapping is withheld
from you on purpose.

```json
{schema_json}
```
"""


def cmd_prepare(args: argparse.Namespace) -> int:
    matched = _match_pairs(args.target_dir, args.exemplar_dir)
    if not matched:
        print("no <prompt-id>.md targets matched an exemplar", file=sys.stderr)
        return 2

    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    key = {
        "_script_version": SCRIPT_VERSION,
        "_blind_seed": _BLIND_SEED,
        "target_dir": str(args.target_dir),
        "exemplar_dir": str(args.exemplar_dir),
        "pairs": {},
    }

    for pid, brief, tgt, ex in matched:
        tgt_text = load(tgt)
        ex_text = load(ex)
        if _target_is_A(pid):
            passage_a, passage_b = tgt_text, ex_text
            a_side, b_side = "target", "exemplar"
        else:
            passage_a, passage_b = ex_text, tgt_text
            a_side, b_side = "exemplar", "target"

        packet = out / f"packet-{pid}.md"
        packet.write_text(_packet_text(pid, passage_a, passage_b), encoding="utf-8")

        key["pairs"][pid] = {
            "brief": brief,  # two-level tally groups sample-pairs by their brief
            "A": a_side,
            "B": b_side,
            "target_file": str(tgt),
            "exemplar_file": str(ex),
            # hashes let tally verify the packet the judge saw is the one we sealed
            "target_sha256": sha256_text(tgt_text),
            "exemplar_sha256": sha256_text(ex_text),
        }

    key_path = out / "key.json"
    key_path.write_text(json.dumps(key, ensure_ascii=False, indent=2), encoding="utf-8")

    n_briefs = len({brief for _pid, brief, _t, _e in matched})
    print(f"Prepared {len(matched)} blinded packets "
          f"({len(matched)} samples across {n_briefs} briefs) in {out}/")
    print(f"  packets:  packet-<pid>.md   (judge reads these — NO provenance)")
    print(f"  key:      {key_path.name}   (SEALED — judge must NOT read this)")
    print()
    print("The judge writes pair-<pid>.json beside each packet, per the schema in")
    print("the packet. Then run:  run_judge.py tally --judgments", out)
    print()
    print("Keep key.json out of the judge's context. It exists only so `tally`")
    print("can resolve each A/B difference back to target vs. exemplar.")
    return 0


# ---------------------------------------------------------------------------
# tally — resolve blinding, cluster differences, report candidates.
# ---------------------------------------------------------------------------

def _norm_feature(name: str) -> str:
    """Exact-match key: lowercase + collapse whitespace only.

    This is the OFFLINE default. It does NOT stem or synonym-merge, so a judge
    that phrases the same tic differently each pair ("em-dash appositive
    insertions" vs "em-dash for appositive elaboration") lands in separate
    buckets and the ≥3 threshold is never reached — the tally reads empty even
    when the tic recurs. That under-clustering is a KNOWN limitation of the
    offline path; the first real run (2026-07) hit it directly. Use
    `--cluster-model` for the LLM clustering pass that groups by meaning
    (`_cluster_features`), or read the always-emitted raw list and group by eye.
    """
    return " ".join(name.lower().split())


# Schema for the clustering pass: map each raw label to a canonical family.
# The clusterer groups LABELS ONLY — it never sees sides or pairs and never
# re-judges. Side/pair come from the sealed key, untouched.
_CLUSTER_SCHEMA = {
    "families": [
        {
            "canonical": "short human-readable family name, e.g. 'em-dash overuse' "
                         "or 'bulleted-list scaffolding'",
            "members": ["exact raw label strings, copied verbatim, that belong "
                        "to this family"],
        }
    ],
}

_CLUSTER_INSTRUCTION = """\
You are grouping free-text feature labels that a writing judge produced across \
many document pairs. Different labels often name the SAME underlying stylistic \
pattern in different words (e.g. "em-dash appositive insertions", "em-dash for \
elaboration", "dash cascades" are one family: em-dash overuse). Group the labels \
below into canonical families by the pattern they describe. Rules: every input \
label must appear in exactly one family's `members`, copied verbatim; do not \
invent labels that weren't given; group only labels that name the same writing \
move, not merely the same topic. Respond with ONLY a JSON object matching this \
schema, no prose:

{schema}

Labels to group:
{labels}
"""


def _cluster_features(labels: list[str], model: str) -> dict[str, str]:
    """LLM clustering pass: map each raw feature label -> canonical family name.

    Opt-in (only called when --cluster-model is set). Groups by meaning so a real
    judge's phrasing variance doesn't fragment one tic across many buckets. Sees
    labels only — never sides, pairs, or provenance. Returns {raw_label: family};
    any label the model drops falls back to itself (so nothing is silently lost).
    """
    import os
    _load_env_local()
    from anthropic import Anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("--cluster-model needs ANTHROPIC_API_KEY (see .env.local)")

    uniq = sorted(set(labels))
    prompt = _CLUSTER_INSTRUCTION.format(
        schema=json.dumps(_CLUSTER_SCHEMA, ensure_ascii=False, indent=2),
        labels="\n".join(f"- {lab}" for lab in uniq))
    client = Anthropic()
    # Clustering is mechanical grouping, not deep analysis — no extended thinking
    # (adaptive thinking here spent the whole budget reasoning and emitted no text,
    # stopping at max_tokens). Give generous output room: the reply restates every
    # input label inside the families, so it scales with the label count.
    msg = client.messages.create(
        model=model, max_tokens=16000, thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt}])
    raw = "".join(b.text for b in msg.content
                  if getattr(b, "type", None) == "text").strip()
    if msg.stop_reason == "max_tokens":
        raise SystemExit("clustering response hit max_tokens (truncated JSON) — "
                         "raise max_tokens in _cluster_features or cluster fewer "
                         "labels at once")
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end <= start:
        raise SystemExit(f"clustering model returned no JSON object "
                         f"(stop_reason={msg.stop_reason}, {len(raw)} chars of text)")
    data = json.loads(raw[start:end + 1])

    mapping: dict[str, str] = {}
    for fam in data.get("families", []):
        canon = (fam.get("canonical") or "").strip()
        for member in fam.get("members", []):
            m = (member or "").strip()
            if m and canon:
                mapping[_norm_feature(m)] = canon
    # Any label the clusterer dropped maps to itself — never silently lost.
    dropped = [lab for lab in uniq if _norm_feature(lab) not in mapping]
    if dropped:
        print(f"# clustering: {len(dropped)} label(s) not grouped, kept as-is: "
              f"{', '.join(dropped[:5])}{'...' if len(dropped) > 5 else ''}",
              file=sys.stderr)
        for lab in dropped:
            mapping[_norm_feature(lab)] = lab
    return mapping


def _load_key(judgdir: Path) -> dict:
    key_path = judgdir / "key.json"
    if not key_path.exists():
        raise SystemExit(
            f"no key.json in {judgdir} — run `prepare` first, and keep the key "
            f"in the same directory as the judgments.")
    return json.loads(load(key_path))


def _load_judgments(judgdir: Path) -> dict[str, dict]:
    """Read pair-<pid>.json files. Return {pid: judgment}. Warn on malformed."""
    judgments = {}
    for jf in sorted(judgdir.glob("pair-*.json")):
        pid = jf.stem[len("pair-"):]
        try:
            data = json.loads(load(jf))
        except json.JSONDecodeError as e:
            print(f"# {jf.name}: invalid JSON ({e}); skipping", file=sys.stderr)
            continue
        if not isinstance(data.get("differences"), list):
            print(f"# {jf.name}: no 'differences' list; skipping", file=sys.stderr)
            continue
        judgments[pid] = data
    return judgments


def cmd_tally(args: argparse.Namespace) -> int:
    # Back-compat: --min-pairs reproduces the old single-level behavior (count
    # distinct pairs, no per-brief sample gate) by forcing min_samples=1 and
    # using its value as the brief threshold.
    if args.min_pairs is not None:
        args.min_samples = 1
        args.min_briefs = args.min_pairs
        print(f"# --min-pairs is deprecated; interpreting as --min-samples 1 "
              f"--min-briefs {args.min_pairs}", file=sys.stderr)

    judgdir = args.judgments
    key = _load_key(judgdir)
    judgments = _load_judgments(judgdir)

    prepared = set(key.get("pairs", {}))
    judged = set(judgments)
    missing = prepared - judged
    extra = judged - prepared
    if missing:
        print(f"# WARNING: {len(missing)} prepared pair(s) not yet judged: "
              f"{', '.join(sorted(missing))}", file=sys.stderr)
    if extra:
        print(f"# WARNING: {len(extra)} judgment(s) with no sealed key entry "
              f"(ignored): {', '.join(sorted(extra))}", file=sys.stderr)

    # Footgun guard: with only one sample per brief (a legacy single-output run),
    # the default min_samples=2 can never be met, so every candidate is silently
    # filtered out. Warn and point at the right flag rather than return an
    # inexplicable empty tally.
    samples_per_brief = defaultdict(int)
    for p in prepared:
        samples_per_brief[key["pairs"][p].get("brief") or _brief_of(p)] += 1
    max_samples = max(samples_per_brief.values(), default=0)
    if max_samples < args.min_samples:
        print(f"# WARNING: no brief has >= {args.min_samples} samples "
              f"(max is {max_samples}); with --min-samples {args.min_samples} "
              f"nothing can qualify. For a single-sample run pass --min-samples 1 "
              f"(or the legacy --min-pairs).", file=sys.stderr)

    # Build the cluster-key function. Default (offline): exact-match _norm_feature.
    # With --cluster-model: an LLM pass groups labels by meaning, so a real
    # judge's phrasing variance ("em-dash insertions" / "em-dash elaboration")
    # collapses into one family and the ≥3 threshold can actually be reached.
    all_labels = [d.get("feature", "").strip()
                  for j in judgments.values() for d in j["differences"]
                  if d.get("feature", "").strip()]
    if args.cluster_model:
        family_of = _cluster_features(all_labels, args.cluster_model)
        cluster_key = lambda feat: family_of.get(_norm_feature(feat), _norm_feature(feat))
        clustering = f"llm:{args.cluster_model}"
    else:
        cluster_key = _norm_feature
        clustering = "exact-string"

    # Resolve every difference to a real side (target/exemplar) via the key, and
    # cluster by feature family. Recurrence is counted in DISTINCT SAMPLE-PAIRS,
    # not raw mentions, so one verbose judgment listing a habit twice can't
    # inflate the count. `brief_samples` groups those sample-pairs by their brief
    # so the two-level test can run: a tic must recur across SAMPLES of a brief
    # (filters sampling noise) AND across the range of BRIEFS (proves it isn't
    # topic-specific).
    # cluster -> side -> {display, pairs:set, habit_pairs:set,
    #                     brief_samples:{brief:set(pid)}, examples:[]}
    clusters: dict[str, dict[str, dict]] = defaultdict(
        lambda: defaultdict(lambda: {
            "display": None, "pairs": set(), "habit_pairs": set(),
            "brief_samples": defaultdict(set), "examples": []
        }))
    raw_differences = []  # always emitted, ungrouped, for by-eye grouping

    for pid, judgment in judgments.items():
        keyrow = key["pairs"].get(pid)
        if not keyrow:
            continue  # already warned as 'extra'
        brief = keyrow.get("brief") or _brief_of(pid)  # fallback for pre-brief keys
        for diff in judgment["differences"]:
            feat = diff.get("feature", "").strip()
            if not feat:
                continue
            raw_side = str(diff.get("side", "")).strip().lower()
            # Map packet label -> real side. "both" fans out to target AND exemplar.
            if raw_side == "a":
                sides = [keyrow["A"]]
            elif raw_side == "b":
                sides = [keyrow["B"]]
            elif raw_side == "both":
                sides = [keyrow["A"], keyrow["B"]]
            else:
                print(f"# {pid}: difference '{feat}' has unrecognized side "
                      f"{diff.get('side')!r}; skipping", file=sys.stderr)
                continue

            ckey = cluster_key(feat)
            habit = bool(diff.get("generated_habit"))
            quote = (diff.get("quote") or "").strip()
            for side in sides:
                raw_differences.append({"pair": pid, "brief": brief, "side": side,
                                        "feature": feat, "family": ckey,
                                        "generated_habit": habit})
                bucket = clusters[ckey][side]
                # When clustering, the family name IS the cluster key — show it,
                # so the display reflects the group, not one arbitrary member.
                if bucket["display"] is None:
                    bucket["display"] = ckey if args.cluster_model else feat
                bucket["pairs"].add(pid)
                bucket["brief_samples"][brief].add(pid)
                if habit:
                    bucket["habit_pairs"].add(pid)
                if quote:
                    bucket["examples"].append((pid, quote))

    # Two-level recurrence. A brief QUALIFIES for a tic when the tic appears in
    # >= min_samples of that brief's sample-pairs (sampling noise filter). The
    # tic is a CANDIDATE when it qualifies in >= min_briefs distinct briefs
    # (range-of-work proof). With single-sample runs (one sample per brief),
    # min_samples=1 makes every present brief qualify, so this reduces exactly to
    # the old "distinct briefs >= threshold" behavior.
    min_samples = args.min_samples
    min_briefs = args.min_briefs
    target_candidates = []
    exemplar_recurrences = []
    for _ckey, sides in clusters.items():
        for side, b in sides.items():
            qualifying = {br: sorted(s) for br, s in b["brief_samples"].items()
                          if len(s) >= min_samples}
            row = {
                "feature": b["display"],
                "side": side,
                "pairs": sorted(b["pairs"]),
                "n_pairs": len(b["pairs"]),            # distinct sample-pairs
                "n_briefs": len(b["brief_samples"]),   # distinct briefs touched
                "n_qualifying_briefs": len(qualifying),
                "qualifying_briefs": qualifying,       # brief -> its qualifying samples
                "habit_pairs": sorted(b["habit_pairs"]),
                "examples": b["examples"][:3],
            }
            if len(qualifying) >= min_briefs:
                if side == "target":
                    target_candidates.append(row)
                elif side == "exemplar":
                    exemplar_recurrences.append(row)

    # Rank by breadth of range first (qualifying briefs), then raw volume.
    target_candidates.sort(
        key=lambda r: (-r["n_qualifying_briefs"], -r["n_pairs"], r["feature"]))
    exemplar_recurrences.sort(
        key=lambda r: (-r["n_qualifying_briefs"], -r["n_pairs"], r["feature"]))

    if args.json:
        print(json.dumps({
            "script_version": SCRIPT_VERSION,
            "judgments_dir": str(judgdir),
            "clustering": clustering,
            "min_samples": min_samples,
            "min_briefs": min_briefs,
            "n_pairs_prepared": len(prepared),
            "n_pairs_judged": len(judged),
            "n_pairs_missing": len(missing),
            "n_briefs_prepared": len({(key["pairs"][p].get("brief") or _brief_of(p))
                                      for p in prepared}),
            "target_candidates": target_candidates,
            "exemplar_recurrences": exemplar_recurrences,
            "raw_differences": raw_differences,
        }, ensure_ascii=False, indent=2))
        return 0

    _print_tally(judgdir, key, prepared, judged, min_samples, min_briefs,
                 target_candidates, exemplar_recurrences, clustering, raw_differences)
    return 0


def _fmt_qual(r):
    """One-line recap of a row's two-level counts."""
    return (f"{r['n_qualifying_briefs']} qualifying briefs, "
            f"{r['n_pairs']} sample-pairs across {r['n_briefs']} briefs")


def _print_tally(judgdir, key, prepared, judged, min_samples, min_briefs,
                 target_candidates, exemplar_recurrences, clustering, raw_differences):
    n_briefs_prep = len({(key["pairs"][p].get("brief") or _brief_of(p))
                         for p in prepared})
    print(f"\n{'='*66}")
    print(f"BLIND-JUDGE DIFFERENCE TALLY   ({judgdir})")
    print(f"{'='*66}")
    print(f"sample-pairs prepared: {len(prepared)}   judged: {len(judged)}   "
          f"(across {n_briefs_prep} briefs)")
    print(f"two-level threshold: a tic must appear in >= {min_samples} sample(s) "
          f"of a brief to\n             qualify it, and qualify in >= {min_briefs} "
          f"briefs to be a candidate")
    print(f"target_dir:  {key.get('target_dir')}")
    print(f"exemplar_dir: {key.get('exemplar_dir')}")
    print(f"clustering:  {clustering}", end="")
    if clustering == "exact-string":
        print("  (labels grouped only if byte-identical — a judge that varies "
              "phrasing\n             will under-cluster to zero; use --cluster-model)")
    else:
        print("  (labels grouped by meaning; LLM-assisted, not byte-reproducible "
              "— record in provenance)")

    print(f"\n--- TARGET-SIDE recurrences — CANDIDATES ---")
    if not target_candidates:
        print("  (none cleared the two-level threshold)")
    for r in target_candidates:
        habit = f"  [reads-as-generated-habit in {len(r['habit_pairs'])}/{r['n_pairs']}]" \
            if r["habit_pairs"] else ""
        print(f"\n  • {r['feature']}   ({_fmt_qual(r)}){habit}")
        print(f"      qualifying briefs: "
              f"{', '.join(f'{br}[{len(s)}]' for br, s in sorted(r['qualifying_briefs'].items()))}")
        for pid, q in r["examples"]:
            q1 = q if len(q) <= 100 else q[:97] + "..."
            print(f"      {pid}: “{q1}”")

    print(f"\n--- EXEMPLAR-SIDE recurrences ---")
    print("  Never dropped. Route to the exemplar re-approval queue: these are")
    print("  either exemplar-quality feedback or the exemplar generator's own")
    print("  signature (HARVEST.md H4).")
    if not exemplar_recurrences:
        print("  (none cleared the two-level threshold)")
    for r in exemplar_recurrences:
        print(f"\n  • {r['feature']}   ({_fmt_qual(r)})")
        for pid, q in r["examples"]:
            q1 = q if len(q) <= 100 else q[:97] + "..."
            print(f"      {pid}: “{q1}”")

    # Always show the raw target-side labels, grouped by family, so a human can
    # regroup by eye even when clustering under-reports (and can sanity-check the
    # LLM grouping when it doesn't). This is the safety net for the exact-string
    # under-clustering failure.
    tgt_raw = [d for d in raw_differences if d["side"] == "target"]
    from collections import defaultdict as _dd
    by_fam_briefs = _dd(set)   # family -> set of briefs it qualified in
    by_fam_pairs = _dd(set)    # family -> set of sample-pairs (for the raw count)
    fam_brief_samples = _dd(lambda: _dd(set))  # family -> brief -> samples
    for d in tgt_raw:
        br = d.get("brief") or _brief_of(d["pair"])
        fam_brief_samples[d["family"]][br].add(d["pair"])
        by_fam_pairs[d["family"]].add(d["pair"])
    for fam, briefs in fam_brief_samples.items():
        for br, samples in briefs.items():
            if len(samples) >= min_samples:
                by_fam_briefs[fam].add(br)
    print(f"\n--- RAW target-side labels by family ({len(tgt_raw)} total, "
          f"below-threshold included) ---")
    for fam in sorted(by_fam_pairs,
                      key=lambda f: (-len(by_fam_briefs[f]), -len(by_fam_pairs[f]), f)):
        qb = len(by_fam_briefs[fam])
        mark = " *" if qb >= min_briefs else ""
        print(f"  {qb:>2} qual-briefs / {len(by_fam_pairs[fam]):>2} pairs{mark}  "
              f"{fam[:66]}")

    print(f"\n{'-'*66}")
    print("Candidates, not verdicts. A target-side recurrence is a candidate for")
    print("the compile step (H6): a human names it, grounding-checks it against")
    print("real human writing, and corroborates against tic_finder.py before it")
    print("can reach the backstop. Cross-check these against diff-findings.md —")
    print("agreement between the two detectors is the strongest admission signal.\n")


# ---------------------------------------------------------------------------
# dispatch — OPTIONAL: send prepared packets to the judge via the Anthropic API.
# Off the critical path. Imports `anthropic` lazily so the offline flow never
# requires it. Writes the same pair-<pid>.json the offline judge would.
# ---------------------------------------------------------------------------

_DISPATCH_INSTRUCTION = """\
You are comparing two passages. Respond with ONLY a JSON object matching this \
schema — no prose, no markdown fence:

{schema}

Use the passage labels A and B exactly as they appear. Do not speculate about \
which passage is machine-generated; the mapping is withheld from you.
"""


def cmd_dispatch(args: argparse.Namespace) -> int:
    import os
    env_file = _load_env_local()  # pull the key from gitignored .env.local, if present
    try:
        import anthropic  # noqa: F401
    except ImportError:
        print("dispatch needs the `anthropic` SDK (pip install anthropic). The "
              "offline flow does not: have the judge read the packets and write "
              "pair-<pid>.json by hand, then run `tally`.", file=sys.stderr)
        return 2
    from anthropic import Anthropic

    if not os.environ.get("ANTHROPIC_API_KEY"):
        hint = f" (checked {env_file})" if env_file else \
            " (no .env.local found — copy .env.local.example to .env.local and fill it in)"
        print(f"no ANTHROPIC_API_KEY set{hint}", file=sys.stderr)
        return 2

    judgdir = args.judgments
    key = _load_key(judgdir)  # ensures prepare has run; NOT sent to the judge
    packets = sorted(judgdir.glob("packet-*.md"))
    if not packets:
        print(f"no packet-*.md in {judgdir} — run `prepare` first", file=sys.stderr)
        return 2

    client = Anthropic()  # reads ANTHROPIC_API_KEY from env (loaded above)
    schema_json = json.dumps(SCHEMA_DOC, ensure_ascii=False, indent=2)
    system = _DISPATCH_INSTRUCTION.format(schema=schema_json)

    n_ok = 0
    for packet in packets:
        pid = packet.stem[len("packet-"):]
        if pid not in key.get("pairs", {}):
            print(f"# {packet.name}: no key entry; skipping", file=sys.stderr)
            continue
        outfile = judgdir / f"pair-{pid}.json"
        if outfile.exists() and not args.overwrite:
            print(f"# {outfile.name} exists; skipping (use --overwrite)",
                  file=sys.stderr)
            continue

        # Fresh context per pair: one message, no history carried between packets.
        # Adaptive thinking is opt-in on current models (a request with no
        # `thinking` field runs without thinking) — a differential reading is
        # exactly the careful-comparison task that benefits from it, so enable it.
        # No temperature/top_p: current models reject sampling params with a 400.
        msg = client.messages.create(
            model=args.judge_model,
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=system,
            messages=[{"role": "user", "content": load(packet)}],
        )
        raw = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Salvage a fenced or embedded object rather than losing the call.
            start, end = raw.find("{"), raw.rfind("}")
            if start == -1 or end == -1:
                print(f"# {pid}: judge returned no JSON; saving raw for inspection",
                      file=sys.stderr)
                (judgdir / f"pair-{pid}.raw.txt").write_text(raw, encoding="utf-8")
                continue
            data = json.loads(raw[start:end + 1])
        data.setdefault("pair", pid)
        data["_judge_model"] = args.judge_model
        outfile.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                           encoding="utf-8")
        n_ok += 1
        print(f"  judged {pid} -> {outfile.name}")

    print(f"\nDispatched {n_ok} pair(s) via {args.judge_model}. Now run: "
          f"run_judge.py tally --judgments {judgdir}")
    print("Record the judge model + version in the report provenance block — "
          "confirm it was the most capable analytic model available, and note if "
          "it equals the target model. This tool cannot verify either.")
    return 0


# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version",
                   version=f"run_judge.py {SCRIPT_VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("prepare", help="build blinded packets + sealed key")
    pp.add_argument("--target-dir", type=Path, required=True,
                    help="dir of <prompt-id>.md target outputs (one arm)")
    pp.add_argument("--exemplar-dir", type=Path, required=True,
                    help="baseline/exemplars/ dir")
    pp.add_argument("--out", type=Path, required=True,
                    help="judgments dir to create (packets + key.json)")
    pp.set_defaults(func=cmd_prepare)

    pt = sub.add_parser("tally", help="resolve blinding, cluster, report candidates")
    pt.add_argument("--judgments", type=Path, required=True,
                    help="dir with key.json + pair-<pid>.json judgments")
    pt.add_argument("--min-samples", type=int, default=2,
                    help="a tic must appear in >= this many of a brief's sample-pairs "
                         "to QUALIFY that brief (sampling-noise filter; default 2). "
                         "Set to 1 for single-sample runs so every present brief qualifies.")
    pt.add_argument("--min-briefs", type=int, default=3,
                    help="a tic must qualify in >= this many distinct briefs to be a "
                         "CANDIDATE (range-of-work proof; default 3, per H4).")
    pt.add_argument("--min-pairs", type=int, default=None,
                    help="DEPRECATED alias: sets --min-briefs and forces --min-samples 1 "
                         "(reproduces the old single-level 'distinct pairs' behavior).")
    pt.add_argument("--cluster-model", default=None,
                    help="group the judge's free-text feature labels by MEANING via "
                         "this model (e.g. claude-opus-4-8) before counting recurrence. "
                         "Without it, clustering is exact-string and a judge that varies "
                         "phrasing under-reports to zero. LLM-assisted / not "
                         "byte-reproducible — record it in the report provenance.")
    pt.add_argument("--json", action="store_true")
    pt.set_defaults(func=cmd_tally)

    pd = sub.add_parser("dispatch",
                        help="OPTIONAL: judge the packets via the Anthropic API")
    pd.add_argument("--judgments", type=Path, required=True,
                    help="dir with packets + key.json from `prepare`")
    pd.add_argument("--judge-model", required=True,
                    help="judge model id — the most capable analytic model "
                         "available at harvest time (claude-opus-4-8 as of "
                         "2026-07-17; pass the newest when a better one ships). "
                         "Recorded in the report provenance block; if it equals "
                         "the target model, note that overlap there.")
    pd.add_argument("--overwrite", action="store_true",
                    help="re-judge pairs that already have a pair-<pid>.json")
    pd.set_defaults(func=cmd_dispatch)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
