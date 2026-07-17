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

SCRIPT_VERSION = "0.1.0"

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
    # low bit of the digest as the coin
    return int(h[-1], 16) % 2 == 0


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
    """Yield (pid, target_path, exemplar_path) for every target with an exemplar.

    Mirrors tic_finder.py's matching: target file <pid>.md pairs with
    exemplars/<pid>/exemplar.md.
    """
    matched = []
    for tgt in sorted(target_dir.glob("*.md")):
        pid = tgt.stem
        ex = exemplar_dir / pid / "exemplar.md"
        if not ex.exists():
            print(f"# no exemplar for {pid}, skipping", file=sys.stderr)
            continue
        matched.append((pid, tgt, ex))
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

    for pid, tgt, ex in matched:
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

    print(f"Prepared {len(matched)} blinded packets in {out}/")
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
    # cluster by feature family. Track which pairs each cluster spans —
    # recurrence is counted in DISTINCT PAIRS, not raw mentions, so one verbose
    # judgment listing a habit twice can't inflate the count.
    # cluster -> side -> {display_name, pairs:set, habit_pairs:set, examples:[]}
    clusters: dict[str, dict[str, dict]] = defaultdict(
        lambda: defaultdict(lambda: {
            "display": None, "pairs": set(), "habit_pairs": set(), "examples": []
        }))
    raw_differences = []  # always emitted, ungrouped, for by-eye grouping

    for pid, judgment in judgments.items():
        keyrow = key["pairs"].get(pid)
        if not keyrow:
            continue  # already warned as 'extra'
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
                raw_differences.append({"pair": pid, "side": side, "feature": feat,
                                        "family": ckey, "generated_habit": habit})
                bucket = clusters[ckey][side]
                # When clustering, the family name IS the cluster key — show it,
                # so the display reflects the group, not one arbitrary member.
                if bucket["display"] is None:
                    bucket["display"] = ckey if args.cluster_model else feat
                bucket["pairs"].add(pid)
                if habit:
                    bucket["habit_pairs"].add(pid)
                if quote:
                    bucket["examples"].append((pid, quote))

    threshold = args.min_pairs
    target_candidates = []
    exemplar_recurrences = []
    for _ckey, sides in clusters.items():
        for side, b in sides.items():
            n = len(b["pairs"])
            row = {
                "feature": b["display"],
                "side": side,
                "pairs": sorted(b["pairs"]),
                "n_pairs": n,
                "habit_pairs": sorted(b["habit_pairs"]),
                "examples": b["examples"][:3],
            }
            if side == "target" and n >= threshold:
                target_candidates.append(row)
            elif side == "exemplar" and n >= threshold:
                exemplar_recurrences.append(row)

    target_candidates.sort(key=lambda r: (-r["n_pairs"], r["feature"]))
    exemplar_recurrences.sort(key=lambda r: (-r["n_pairs"], r["feature"]))

    if args.json:
        print(json.dumps({
            "script_version": SCRIPT_VERSION,
            "judgments_dir": str(judgdir),
            "clustering": clustering,
            "min_pairs": threshold,
            "n_pairs_prepared": len(prepared),
            "n_pairs_judged": len(judged),
            "n_pairs_missing": len(missing),
            "target_candidates": target_candidates,
            "exemplar_recurrences": exemplar_recurrences,
            "raw_differences": raw_differences,
        }, ensure_ascii=False, indent=2))
        return 0

    _print_tally(judgdir, key, prepared, judged, threshold,
                 target_candidates, exemplar_recurrences, clustering, raw_differences)
    return 0


def _print_tally(judgdir, key, prepared, judged, threshold,
                 target_candidates, exemplar_recurrences, clustering, raw_differences):
    print(f"\n{'='*66}")
    print(f"BLIND-JUDGE DIFFERENCE TALLY   ({judgdir})")
    print(f"{'='*66}")
    print(f"pairs prepared: {len(prepared)}   judged: {len(judged)}   "
          f"recurrence threshold: >= {threshold} distinct pairs")
    print(f"target_dir:  {key.get('target_dir')}")
    print(f"exemplar_dir: {key.get('exemplar_dir')}")
    print(f"clustering:  {clustering}", end="")
    if clustering == "exact-string":
        print("  (labels grouped only if byte-identical — a judge that varies "
              "phrasing\n             will under-cluster to zero; use --cluster-model)")
    else:
        print("  (labels grouped by meaning; LLM-assisted, not byte-reproducible "
              "— record in provenance)")

    print(f"\n--- TARGET-SIDE recurrences (>= {threshold} pairs) — CANDIDATES ---")
    if not target_candidates:
        print("  (none cleared the threshold)")
    for r in target_candidates:
        habit = f"  [reads-as-generated-habit in {len(r['habit_pairs'])}/{r['n_pairs']}]" \
            if r["habit_pairs"] else ""
        print(f"\n  • {r['feature']}   ({r['n_pairs']} pairs: "
              f"{', '.join(r['pairs'])}){habit}")
        for pid, q in r["examples"]:
            q1 = q if len(q) <= 100 else q[:97] + "..."
            print(f"      {pid}: “{q1}”")

    print(f"\n--- EXEMPLAR-SIDE recurrences (>= {threshold} pairs) ---")
    print("  Never dropped. Route to the exemplar re-approval queue: these are")
    print("  either exemplar-quality feedback or the exemplar generator's own")
    print("  signature (HARVEST.md H4).")
    if not exemplar_recurrences:
        print("  (none cleared the threshold)")
    for r in exemplar_recurrences:
        print(f"\n  • {r['feature']}   ({r['n_pairs']} pairs: "
              f"{', '.join(r['pairs'])})")
        for pid, q in r["examples"]:
            q1 = q if len(q) <= 100 else q[:97] + "..."
            print(f"      {pid}: “{q1}”")

    # Always show the raw target-side labels, grouped by family, so a human can
    # regroup by eye even when clustering under-reports (and can sanity-check the
    # LLM grouping when it doesn't). This is the safety net for the exact-string
    # under-clustering failure.
    tgt_raw = [d for d in raw_differences if d["side"] == "target"]
    from collections import defaultdict as _dd
    by_fam = _dd(set)
    for d in tgt_raw:
        by_fam[d["family"]].add(d["pair"])
    print(f"\n--- RAW target-side labels by family ({len(tgt_raw)} total, "
          f"below-threshold included) ---")
    for fam, pairs in sorted(by_fam.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        mark = " *" if len(pairs) >= threshold else ""
        print(f"  {len(pairs):>2} pairs{mark}  {fam[:70]}")

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
    pt.add_argument("--min-pairs", type=int, default=3,
                    help="recurrence threshold in distinct pairs (default 3, per H4)")
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
