# Baseline Corpus — Provenance Ledger

**Status: NOT YET ASSEMBLED.** The first harvest cannot run its counting stage
until this corpus is assembled, frozen, and calibrated. This README is the
assembly specification and, once assembled, the permanent provenance record.

## What this corpus is

The frozen human-writing baseline that defines *human density* for every
metric in HARVEST_PLAN.md Component 4. All backstop thresholds are ratios
against it. It is the one artifact in the harvest that must never contain
model-authored text — a model-written baseline carries the measured
generation's own densities and collapses the deltas to zero
(HARVEST_PLAN.md, "Baseline corpus protocol").

## Assembly protocol (hybrid — settled 2026-07-15)

- **The model does:** specification, sourcing, screening, normalization,
  dedupe, calibration computation, and this ledger. It authors nothing that
  enters the corpus.
- **Humans authored the content.** Sources, in priority order:
  1. Make Good archives — Managed Word–era published copy, newsletters,
     appeal letters, and the founder writing samples behind the library's
     voice profiles. <!-- TODO: Determine where the raw founder writing samples and Managed Word archives live on disk. -->
  2. Published pre-2023 nonprofit-sector writing mined from public sources —
     real annual reports, donor letters, program pages, case studies.
- **Screening criteria (all three required per sample):** verifiable pre-2023
  publication; human-authorship confidence; genre fit to the battery.
- **Weighting:** pre-2023 because human writing is increasingly
  model-inflected. The corpus is frozen once assembled — it never grows.

## Target composition

4–6 samples per battery genre, ~400–700 words each (~40–70 samples total):

| Battery genre | Target samples | Assembled |
|---|---|---|
| About / program / web pages (F01, F08) | 6 | 0 |
| Case study / impact narrative (F02, R07) | 5 | 0 |
| Appeal / donor letters (F03) | 5 | 0 |
| Newsletter articles (F04) | 5 | 0 |
| Editorial / blog / op-ed (F05, R02) | 5 | 0 |
| Analytical / board / comparison prose (F06) | 4 | 0 |
| Report prose / exec summaries (F07) | 5 | 0 |
| Social / short promo (F09, R06, R08) | 5 | 0 |
| Bios (F10) | 4 | 0 |
| FAQ / Q&A prose (F11) | 4 | 0 |
| Correspondence (F12) | 5 | 0 |

## Splits

- **Calibration split (~60%):** used once to compute `metrics-baseline.json`
  (the per-metric human densities that thresholds ratio against).
- **Held-out split (~40%):** reserved for judge pairing (Component 5). Never
  used for calibration; never shown during threshold work.

Split assignment is per-sample, recorded in the ledger below, and frozen.

## Negative controls (`negative-controls/`)

Model-generated, deliberately tic-maximal samples — detector *sensitivity*
unit tests. If a metric doesn't fire on these, the metric is broken. They are
never part of the baseline, never used for calibration, and never paired in
judging. This is the only sanctioned model-authored content in `baseline/`.

## Provenance ledger

One row per sample, added at assembly time. The ledger is what makes the
corpus auditable and the freeze enforceable.

| ID | Genre | Source (publication/archive) | Pub. date | Words | Split | Screened by | Notes |
|---|---|---|---|---|---|---|---|
| *(none yet)* | | | | | | | |
