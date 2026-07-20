# Prose-Signature Harvest — Roadmap

Where the harvest tooling stands and what comes next, in priority order. The
goal the roadmap serves: *run a new model's writing through the harvest and get
back a trustworthy list of its tics.* Everything here is measured against that.

Design rationale lives in `../HARVEST_PLAN.md`; the operator checklist in
`HARVEST.md`; the reference layer in `baseline/README.md`.

> **STATUS (2026-07-18): battery replaced; exemplars REGENERATED + committed.**
> The single-org (Harbor Bend) promotional battery and its 12 exemplars were
> deleted and replaced by the domain/register battery in
> [`battery/COVERAGE_SPEC.md`](battery/COVERAGE_SPEC.md) (31 briefs, 8 registers).
> All 31 exemplars are now regenerated, verified, and committed at
> `baseline/exemplars/<ID>/` with per-exemplar provenance (commit f0ff32c). They
> were generated `v2-learn-decisions`: the generator learns the DECISIONS behind
> the craft corpus rather than imitating voice — this cut the generator's own
> em-dash tic from 2.94 to 1.35 per 250w (human-corpus baseline 0.67) WITHOUT
> naming any tic, directly retiring the "exemplar-generator tics leaking into the
> reference" risk below. The **blind judge (`run_judge.py`) is the primary
> detector**; `tic_finder.py` is backward-looking and deprioritized. Remaining
> new work: multi-sample per brief, clustering stability, provenance-as-
> deliverable — see the spec, `[[harvest-battery-purpose]]`, and
> `[[harvest-exemplar-learning-instruction]]`. The "Next / priority order" below
> is largely superseded by the spec; item 2 (scale) is the live tooling task.

---

## Built and working

- **Exemplar quality-bar set — 31 exemplars, one per brief in `battery/core.jsonl`.**
  REGENERATED + committed 2026-07-18 (commit f0ff32c) at `baseline/exemplars/<ID>/`
  with per-exemplar `provenance.json`. Fable-authored, guardrail-free,
  `v2-learn-decisions` method (learn the corpus's decisions, don't imitate voice).
  Rebuild via `scripts/promote_exemplars.py`. Replaced the retired 12 Harbor Bend
  exemplars. (Note: `baseline/fingerprints/`, `baseline/craft/`,
  `baseline/constructions/` remain empty stubs — optional enrichment, see below.)
- **`run_judge.py`** (Component 5, blind judge) — the PRIMARY detector. prepare /
  dispatch / tally + optional LLM clustering; verified live end-to-end against the
  API 2026-07-17. Reads whatever target/exemplar pairs it's given — register-
  agnostic, so it survives the battery replacement.
- **`tic_finder.py`** (Component 4a, discovery) — open log-odds keyness diff.
  Proven end-to-end: Opus-4.8 arm-A × 12 briefs pooled surfaced real current-gen
  tics (dash-overuse, spaced-dash, colon elaboration, formulaic openings). Works,
  but DEPRIORITIZED — it can only rank features a human still recognizes as a
  known tic, so it's backward-looking. Kept as a secondary cross-check.
- **`measure_density.py`** (Component 4b, regression) — known-tic counter, demoted
  to a regression suite for existing backstop entries.
- **Intake:** `scan_sources.py` (triage), `extract_body.py` (prose extraction);
  14-text human panel (`panel.jsonl`) as craft-study input + grounding reference.

---

## Next, in priority order

### 1. First judge run — DONE 2026-07-20 (`reports/2026-07-opus48-sonnet5/`)

Ran end-to-end: Opus 4.8 + Sonnet 5, both arms, 3 samples/brief (372 outputs →
372 judgments, 0 failures), judge `claude-opus-4-8`. `dispatch` API path
exercised live at scale for the first time. See `REPORT.md` + `candidates.md`.

**Corrected detector logic (reviewer steer, 2026-07-20):** admission is the
**judge (primary) + the human-baseline degree control** (`measure_density.py`
against `sources/`). **tic_finder is NOT in the admission logic** — backward-
looking; its `diff-findings.md` is kept as an artifact only. The judge names a
pattern and flags habit-vs-craft but does not quantify *degree*; the human corpus
decides whether the rate is overuse. This run's control rejected two judge-named
patterns (triadic, contrast-negation) as craft — humans use them at/above the
target rate — and challenged the matching seeded S0_backstop v1.0.0 entries.

**Tooling that this run produced:** `run_judge.py` 0.3.0 (batched clustering +
graceful degrade on a bad batch — the ~1000-label clustering call blew the output
budget and one batch/dir returned malformed JSON); `family_rollup.py` (a
deterministic recount of judge output, reliable where LLM clustering degraded);
`generate_corpus.py` (API-based, fresh-context, arm-clean generation).

**Remaining follow-through:** the highest-value gap is **metric coverage** —
hedging, signposting, aphoristic closings, and parentheticals recur in the judge
output but no arithmetic metric yet quantifies their degree, so they cannot be
calibrated into backstop thresholds. Build those metrics before the release step
(H8) admits them.

### 2. Scale the statistical signal — cheap, compounding

**Why.** 12 short single-output pairs gave suggestive z-scores (~2.4 top). Real
confidence needs volume. The mechanism is proven; only the power is thin.

**Multi-sample: BUILT 2026-07-18 (`run_judge.py` 0.2.0).** Generate N samples per
brief named `<prompt-id>.<NN>.md` (default 3, operator step per H2). `prepare`
pairs every sample against the brief's one exemplar and blinds each sample
independently; `tally` uses **two-level recurrence** — a tic must recur across
≥`--min-samples` samples of a brief (noise filter, default 2) AND ≥`--min-briefs`
distinct briefs (range proof, default 3). Legacy single-sample runs work with
`--min-samples 1`; `--min-pairs` kept as a deprecated alias. Verified on a
fixture (two-level gating, back-compat, footgun guard).

**Still open under "scale":** (1) wire arm A (no S0) vs arm B (S0 core) so the
harvest reports **gate effectiveness** — what S0 already suppresses vs. what
leaks; the tooling still exercises one arm at a time. (2) Add a `--min-z` /
significance note to `tic_finder.py` so weak hits read as weak.

**Done when:** arm-A-vs-arm-B shows S0's current gate effectiveness, and weak
`tic_finder` hits are visibly flagged.

### 3. Merge the branch to main — the only remaining coordination debt

**Why.** The doc set is reconciled (2026-07-18: `HARVEST_PLAN.md`, `HARVEST.md`,
`baseline/README.md`, `COVERAGE_SPEC.md` all agree with the committed state).
There is no longer a separate design session to confirm a merged design with —
one owner drives design + tooling now. What remains is a decision, not a
reconciliation: the branch `harvest/measurement-tool` is not yet merged to main.

**Do:** decide and execute the merge of `harvest/measurement-tool` to main
(Chris's call).

### 4. First real harvest → replace provisional backstop entries

**Why.** `s0-backstop-v1.0.0`'s entries are provisional (training-recollection).
The point of all this tooling is to replace them with **measured** ones.

**Do:** run `HARVEST.md` H1–H9 against the current target model(s): compose
battery, generate both arms, run 4a + 4b + judge, external-signal pass, compile
candidates, grounding-check, human review, release `s0-backstop-v1.1.0`. The
dash/colon/opening candidates from the proof run are the first things to confirm
or reject with real rigor.

---

## Further improvements (lower priority / opportunistic)

- **Optional enrichment references** (`baseline/fingerprints/`, `baseline/craft/`).
  Aggregate real-writing distributions per genre give `tic_finder.py` a *second*
  diff reference immune to exemplar-generator contamination, and sharpen the
  grounding check. Worth building if the exemplar-generator-cancellation blind
  spot proves to bite in practice — not before.
- **Rotating-pool exemplars.** Core F01–F12 have exemplars; generate an exemplar
  the first time each rotating brief (R01+) is selected for a harvest.
- **Regression controls** (`baseline/constructions/positive|negative/`). Only
  needed once known-tic entries are being regression-checked at scale; build with
  the first harvest that exercises 4b seriously.
- **Phase-2 metric upgrades in `measure_density.py`:** parser-backed
  `fragment_rate` (currently stubbed) and `triadic_rate` (currently a proxy).
- **News genre (R09).** Added to the rotating pool; needs its own exemplar and,
  if pursued, an `extract_body.py` path for archive.ph-wrapped and
  graphics-interactive pages (both currently return no body).
- **Automate the harvest** (HARVEST_PLAN Phase 3) — only after the manual harvest
  has run at least twice and the protocol has stabilized.

---

## Named risks to watch

- **Exemplar-generator tics leaking into the reference.** MEASURED + MITIGATED
  2026-07-18. v1 craft-sourcing did leak a tic: em-dashes at 2.94/250w vs a
  human-corpus baseline of 0.67. Fix was the `v2-learn-decisions` generation
  instruction (learn the corpus's decisions, don't imitate voice), which cut it
  to 1.35/250w without naming any tic — so no tic theory entered the yardstick.
  Residual risk persists at the punctuation level (still above human), so: for
  punctuation-level tics use the `sources/` human corpus as the baseline, not the
  exemplars; the blind judge remains the primary mitigation. ALWAYS run the human
  corpus as a control before treating a raw count as a finding. Re-examine at each
  exemplar re-approval. See `[[harvest-exemplar-learning-instruction]]`.
- **Content-word noise in the diff.** `tic_finder.py` ranks topic words too;
  admission always requires a human to name the structural candidate and a
  grounding check. Never wire the ranker straight to the backstop.
- **Single-generation reference.** The reference is one Fable snapshot. If Fable
  and a future target converge stylistically, the guard weakens — track the
  generator/target generation gap at each harvest.
