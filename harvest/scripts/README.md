# Harvest Scripts

Zero-dependency Python (stdlib only, Python 3.9+), same conventions as
`build-deploy-bundles.py`. Each is versioned (`--version`) so a harvest report
can record which code produced its numbers.

The tools form the intake → discovery pipeline for one harvest:

```
saved sources ─ scan_sources.py ─▶ triage      (metadata present? guard cleared?)
     │
     └─ extract_body.py ─▶ prose bodies         (strip nav/ads/scaffolding)
                              │
        target model output ──┴──▶ tic_finder.py ──▶ ranked candidate tics   (4a: DISCOVERY)
                              │    measure_density.py ─▶ known-tic regression (4b: CONFIRM/RETIRE)
                              └──▶ run_judge.py ──▶ differential-reading tally (5:  BLIND JUDGE)
```

Two independent detector families — the statistical diff (4a/4b) and the blind
judge (5) — corroborate at compile time; agreement between them is the strongest
admission signal.

## tic_finder.py — the discovery instrument (Component 4a)

Diffs a target model's writing against the task-matched exemplar and
ranks the features the target **over-represents** (log-odds keyness: words,
n-grams, punctuation, sentence openings, sentence shapes). **No predefined tic
list** — an unnamed tic can surface. This is the tool that answers the whole
project's question: *what does this new model overdo?*

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

## run_judge.py — blind-judge leg (Component 5)

The **second, independent detector.** Where `tic_finder.py` ranks features a
target over-represents against a reference distribution, the judge reads two
concrete passages side by side and enumerates *how* they differ. It works at any
N (no pooled corpus needed), catches pattern-level tics no regex can rank, and
covers `tic_finder.py`'s blind spot — a tic **shared** by the exemplar generator
and the target cancels out of the keyness diff but still shows up to a judge that
never sees the reference distribution.

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

## measure_density.py — known-tic regression (Component 4b)

Measures the named Component-4 metrics (em-dash rate, contrast-negation, triadic,
etc.) per output, length-normalized. Role: confirm/retire **existing** backstop
entries, not discover new ones. `--self-test` runs metric sanity checks.
`fragment_rate` is a Phase-2 stub; `triadic_rate` is a documented proxy.

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
