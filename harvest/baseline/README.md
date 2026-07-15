# Baseline Corpus — Provenance Ledger

**Status: NOT YET ASSEMBLED.** The first harvest cannot run its counting stage
until this corpus is assembled, frozen, and calibrated. This README is the
assembly specification and, once assembled, the permanent provenance record.

## What this corpus is

The frozen human-writing baseline that defines *human density* for every
metric in HARVEST_PLAN.md Component 4. All backstop thresholds are ratios
against it.

Two things this corpus must never be (HARVEST_PLAN.md, "Baseline corpus
protocol" — both rejected designs):

1. **Model-authored.** A model-written baseline carries the measured
   generation's own densities and collapses the deltas to zero.
2. **Make Good's own writing.** S0 is a *normalizer* — a generic practitioner
   floor; voice specificity is the voice profiles' job (S0 2.0.1 precedence).
   Calibrating on the org's or founders' writing would define "human density"
   as one house style's density and blind the detector wherever that style
   runs hot. The baseline is normed on the population of excellent
   professional writers, not on one speaker.

## Assembly protocol (hybrid — settled 2026-07-15, revised same day)

- **The model does:** specification, sourcing, screening, structure-preserving
  anonymization, normalization, dedupe, calibration computation, and this
  ledger. It authors nothing that enters the corpus.
- **Humans authored — generic and excellent.** Published pre-2023 professional
  writing from many authors and organizations, selected genre-by-genre.
  Candidate pools: celebrated appeal-letter archives (e.g. SOFII's showcase),
  exemplary organizational copy cited in the copywriting and nonprofit-
  communications literature, well-edited annual-report and foundation-letter
  prose, strongly edited pre-2023 editorial/op-ed writing, newspaper
  profile/obit bios. Sector-shaped genres (appeals, grant narratives) use
  excellent examples from *other* organizations; generic genres draw across
  sectors deliberately. Sources are proposed by the model and vetoed/extended
  by the operator. <!-- TODO: collect Chris's suggested sources (writers, orgs, editors he trusts) into the pool before assembly. -->
- **Screening criteria (all required per sample):**
  1. Verifiable pre-2023 publication (contamination guard — human writing is
     increasingly model-inflected).
  2. Human-authorship confidence.
  3. Genre fit to the battery.
  4. **Quality screen:** the sample would itself pass S0's gates (earned
     claims, point-first, medium's shape). Baseline on average professional
     writing and you calibrate the floor to the failure.
- **Diversity cap:** no author or organization contributes more than ~2
  samples — the guard against one famous voice becoming "human normal."
- **Frozen once assembled** — the corpus never grows.

## Anonymization (structure-preserving)

Proper nouns are swapped 1:1 with fictional equivalents of the same shape —
organization → fictional organization, person → fictional person, place →
fictional place. **Nothing else is edited.** Genericizing a name to "the
organization" would distort the noun-repetition and rhythm metrics this
corpus exists to calibrate. Anonymization also removes a judge shortcut
(recognizing a real org's copy as human) and keeps an internal corpus of
third-party text low-sensitivity. The corpus file holds the anonymized text;
the ledger below holds the true source — auditability survives.

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

One row per sample, added at assembly time. True source stays here; the
corpus file carries the anonymized text.

| ID | Genre | True source (publication/org) | Pub. date | Words | Anonymization map ref | Split | Screened by | Notes |
|---|---|---|---|---|---|---|---|---|
| *(none yet)* | | | | | | | | |
