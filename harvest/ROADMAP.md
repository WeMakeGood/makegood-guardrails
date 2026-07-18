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

### 1. First judge run — exercise `run_judge.py` against real pairs

**Why first.** The blind-judge harness is built but has only been run on a
synthetic fixture. Its first real job is to corroborate (or challenge)
`tic_finder.py`'s existing dash/colon/opening findings on the Opus-arm-A ×
exemplar pairs — the two detectors agreeing is the strongest admission signal.

**Do:** run `run_judge.py prepare` on the arm-A outputs, dispatch the packets to a
most-capable-available judge (via `dispatch`, or an operator running the packets by
hand), then `tally`. Confirm the differences tally lines up with
`diff-findings.md`. Exercise the `dispatch` API path once so it's no longer
untested.

**Done when:** a real judge run produces a difference tally, and the target-side
candidates are cross-checked against `tic_finder.py`'s.

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

### 3. Close the doc/spec reconciliation — coordination debt

**Why.** This session's working design simplified the design session's v4. Docs
were updated to match (2026-07-16), but the two sessions should confirm the
merged design together, and the branch `harvest/measurement-tool` is not yet
merged to main.

**Do:** design + tooling sessions confirm the working design; decide the branch
merge; ensure `HARVEST_PLAN.md`, `HARVEST.md`, `baseline/README.md` agree.

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
