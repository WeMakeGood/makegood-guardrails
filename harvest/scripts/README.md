# Harvest Scripts

Zero-dependency Python (stdlib only, Python 3.9+), same conventions as
`build-deploy-bundles.py`. Each is versioned (`--version`) so a harvest report
can record which code produced its numbers.

The tools form the generate → judge → track pipeline for one harvest:

```
saved sources ─ scan_sources.py ─▶ triage      (metadata present? guard cleared?)
     │
     └─ extract_body.py ─▶ prose bodies         (strip nav/ads/scaffolding)

battery + exemplars ─ generate_corpus.py ─▶ N samples/brief/arm  (H2: fresh context, arm-clean)
                              │
                              ├──▶ run_judge.py ──▶ differential-reading tally  (H4: THE ARBITER)
                              │        └─ family_rollup.py ─▶ deterministic recount of judge diffs
                              │
                              ├──▶ measure_density.py ─▶ per-metric rates  (tracking + reporting color)
                              └──▶ tic_finder.py ──▶ ranked over-representations  (optional artifact)
```

**The blind judge (`run_judge.py`) is the arbiter.** It reads the model's samples
against the human ideal (the exemplar) and names what recurs as over-style;
recurrence across samples and briefs is the signal (two-level tally). Admission is
the judge's call, degree included. `measure_density.py` / the human baseline do
**not** gate admission — they are reporting color and harvest-to-harvest tracking
of a tic the judge already named. `tic_finder.py` is a backward-looking artifact,
kept for a sanity glance, **out of the admission logic** (a keyness diff mislabels
degree and content as signal — see the reviewer steer, 2026-07-20).

## generate_corpus.py — target corpus generation (H2)

Generates target-model output for every battery brief, one fresh-context API call
per output (no carried history), arm-clean: arm A carries no system prompt, arm B
carries the S0 core body (backstop region empty). Varies only sampling across the
N samples of a brief. Writes `outputs/<model>/<arm>/<pid>.<NN>.md` and an auditable
`generation-provenance.json` (model IDs, arm prompt hashes, battery hash, per-output
sha/wordcount/stop_reason). Chosen over subagents so fresh context is structural and
the exact target model is pinned.

## run_judge.py — blind judge, THE arbiter (H4)

Diffs each target sample against the same-brief exemplar; the judge enumerates how
they differ in *how* they are written and flags generated habits. `prepare`
(blinded packets + sealed key) → `dispatch` (Anthropic API) → `tally` (two-level
recurrence + optional batched LLM clustering). See its own section below.

## family_rollup.py — deterministic recount of judge output

Groups the judge's raw differences by a fixed keyword-family map (readable in the
script), same two-level gate as `tally`. A transparent cross-check on the LLM
clustering, reliable where a clustering batch degrades. Reads a `tally --json` file.

## tic_finder.py — backward-looking artifact (optional; Component 4a, demoted)

Diffs a target model's writing against the task-matched exemplar and
ranks the features the target **over-represents** (log-odds keyness). **Not in the
admission logic** — kept only as an optional sanity glance. It can only rank
features a human still recognizes as a known tic, so it cannot surface the unnamed
tics the harvest exists to catch; that is the judge's job.

```
# one pair
scripts/tic_finder.py --target OUT.md --exemplar baseline/exemplars/AN04/exemplar.md
# pooled across all briefs (where the signal reaches significance)
scripts/tic_finder.py --target-dir OUTPUTS/ --exemplar-dir baseline/exemplars/ --pooled
```

Output is **candidates, not verdicts.** Content-word hits are noise; a human
names the structural/stylistic candidates and grounding-checks them against real
writing before anything reaches the backstop. Single short pairs are
underpowered — pool.

## run_judge.py — blind judge, the arbiter (Component 5 / H4) — full reference

*(Also summarized above; this is the operational detail.)* The judge reads two
concrete passages for the same brief side by side and enumerates *how* they
differ, flagging generated habits. It works at any N (no pooled corpus needed),
catches pattern-level tics no regex can rank, and — unlike a keyness diff — sees a
tic even when it is **shared** by the exemplar generator and the target (the judge
never sees a reference distribution, only two passages). Recurrence across samples
and briefs is what promotes a difference to a candidate; the judge's naming is the
admission decision.

Three subcommands, one packet format, one judgment schema:

```
# 1. Build blinded packets (A/B randomized, provenance stripped) + sealed key.json
#    OUTPUTS/ holds N samples per brief named <prompt-id>.<NN>.md (e.g. AN04.01.md);
#    every sample pairs against baseline/exemplars/<brief>/exemplar.md.
scripts/run_judge.py prepare --target-dir OUTPUTS/ \
    --exemplar-dir baseline/exemplars --out reports/<id>/judgments

# 2. The judge (most capable analytic model available, fresh context per pair)
#    writes pair-<pid>.json per the schema printed in each packet. OR, optionally:
scripts/run_judge.py dispatch --judgments reports/<id>/judgments \
    --judge-model <most-capable-available>   # needs `anthropic` SDK + a key

# 3. Resolve the blinding, cluster, and report candidates (two-level recurrence)
scripts/run_judge.py tally --judgments reports/<id>/judgments \
    --min-samples 2 --min-briefs 3        # single-sample run: --min-samples 1
```

`prepare` and `tally` are offline stdlib-only like the rest. `dispatch` is the
one optional path that imports `anthropic` and touches the network — the offline
flow is complete without it. Blindness is structural: the A/B→target/exemplar
map is sealed in `key.json`, which the judge never reads and only `tally` opens;
each sample of a brief is blinded independently. **Two-level recurrence:** a
target-side tic must recur across ≥`--min-samples` samples of a brief (noise
filter) AND ≥`--min-briefs` distinct briefs (range proof) to be a candidate;
exemplar-side recurrences are never dropped — they route to the exemplar
re-approval queue. Candidates, not verdicts — corroborate against `tic_finder.py`
before admission. (Judge = the most capable analytic model available at harvest
time, chosen on merit; if it equals the target model, note that overlap in
provenance — a weaker independent check.)

## measure_density.py — tracking + reporting metrics (Component 4b)

Measures the named metrics (em-dash rate, contrast-negation, triadic, etc.) per
output, length-normalized. Role: **track** an already-named tic harvest-to-harvest
(did it get better or worse) and supply reporting color — NOT confirm, retire, or
gate an entry (the judge decides that; a count sees presence, not habit shape).
Run it against the `sources/` corpus for the human reference. `--self-test` runs
metric sanity checks. `fragment_rate` is a Phase-2 stub; `triadic_rate` is a
documented proxy.

## extract_body.py — prose-vs-scaffolding extraction

Pulls the article body out of a saved full-page HTML (per-publication container
rules + generic fallback), stripping nav, ads, related-cards, captions, and a
trailing author-bio. Prints a first/last-paragraph report for human spot-check
before the text is trusted. Implements the "measure prose, not scaffolding" rule
(`baseline/README.md §1`).

## scan_sources.py — source-drop triage

Walks the (out-of-repo) source drop directory and reports, per file, what
metadata is present (JSON-LD → meta tags → sidecar) and whether the
contamination guard clears (pre-2023, or a recorded authorship rationale).
Produces a READY / NEEDS-INPUT table. Used when growing the human panel.
