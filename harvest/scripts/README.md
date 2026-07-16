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
                                   measure_density.py ─▶ known-tic regression (4b: CONFIRM/RETIRE)
```

## tic_finder.py — the discovery instrument (Component 4a)

Diffs a target model's writing against the frozen task-matched exemplar and
ranks the features the target **over-represents** (log-odds keyness: words,
n-grams, punctuation, sentence openings, sentence shapes). **No predefined tic
list** — an unnamed tic can surface. This is the tool that answers the whole
project's question: *what does this new model overdo?*

```
# one pair
scripts/tic_finder.py --target OUT.md --exemplar baseline/exemplars/F03/exemplar.md
# pooled across all briefs (where the signal reaches significance)
scripts/tic_finder.py --target-dir OUTPUTS/ --exemplar-dir baseline/exemplars/ --pooled
```

Output is **candidates, not verdicts.** Content-word hits are noise; a human
names the structural/stylistic candidates and grounding-checks them against real
writing before anything reaches the backstop. Single short pairs are
underpowered — pool.

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
