# Prose-Signature Harvest — Roadmap

Where the harvest tooling stands and what comes next, in priority order. The
goal the roadmap serves: *run a new model's writing through the harvest and get
back a trustworthy list of its tics.* Everything here is measured against that.

Design rationale lives in `../HARVEST_PLAN.md`; the operator checklist in
`HARVEST.md`; the reference layer in `baseline/README.md`.

> **STATUS (2026-07-17): battery + exemplars retired; priorities changed.** The
> single-org (Harbor Bend) promotional battery and its 12 exemplars are DELETED —
> replaced by the domain/register battery in
> [`battery/COVERAGE_SPEC.md`](battery/COVERAGE_SPEC.md). The **blind judge
> (`run_judge.py`) is now the primary detector**; `tic_finder.py` is backward-
> looking (keyed to already-known tics) and deprioritized. New work is scoped in
> the spec (multi-sample per brief, clustering stability, provenance-as-deliverable)
> and `[[harvest-battery-purpose]]`. The "Next / priority order" section below
> predates this and is superseded by the spec.

---

## Built and working

- ~~**Frozen synthetic baseline** — 12 exemplars, one per Harbor Bend core brief.~~
  **RETIRED 2026-07-17.** Deleted with the single-org battery it matched. The
  exemplar *mechanism* carries forward (Fable, broad-craft-sourced, guardrail-free)
  but is regenerated against the new briefs. See the spec.
- **`run_judge.py`** (Component 5, blind judge) — the PRIMARY detector. prepare /
  dispatch / tally + optional LLM clustering; verified live end-to-end against the
  API 2026-07-17. Reads whatever target/exemplar pairs it's given — register-
  agnostic, so it survives the battery replacement.
- **`tic_finder.py`** (Component 4a) — open log-odds keyness diff. Works, but
  DEPRIORITIZED: it can only rank features a human still recognizes as a known
  tic, so it's backward-looking. Kept as a secondary cross-check, not the
  instrument.
- **`tic_finder.py`** (Component 4a, discovery) — open log-odds keyness diff.
  Proven end-to-end: Opus-4.8 arm-A × 12 briefs pooled surfaced real current-gen
  tics (dash-overuse, spaced-dash, colon elaboration, formulaic openings).
- **`measure_density.py`** (Component 4b, regression) — known-tic counter, demoted
  to a regression suite for existing backstop entries.
- **Intake:** `scan_sources.py` (triage), `extract_body.py` (prose extraction);
  14-text human panel (`panel.jsonl`) as craft-study input + grounding reference.
- **`run_judge.py`** (Component 5, blind-judge leg) — the second independent
  detector, working at **any N**. `prepare` builds A/B-randomized, provenance-
  stripped packets from an arm's outputs plus a sealed `key.json`; the judge
  (the most capable analytic model available, fresh context per pair) writes structured
  `pair-<pid>.json` per the H4 differential prompt; `tally` resolves the blinding,
  clusters differences by distinct-pair recurrence, and reports target-side
  candidates (≥3 pairs) and exemplar-side recurrences (routed to re-approval,
  never dropped). Offline stdlib-only like the other scripts; an optional
  `dispatch` subcommand runs the pairs through the Anthropic API. **Not yet
  exercised end-to-end against a real judge run** — the offline flow (prepare →
  tally) is verified on a fixture; `dispatch` (API path) is structurally complete
  but untested (no SDK/key in the build environment).

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

**Do:** generate **multiple arm-B outputs per brief** (e.g. 3–5 samples each,
varying nothing but sampling), pool them. Also wire the two arms properly: arm A
(no S0) vs arm B (S0 core) so the harvest reports **gate effectiveness** (what
S0 already suppresses vs. what leaks) — currently the tooling only exercises one
arm at a time. Add a `--min-z` / significance note to `tic_finder.py` output so
weak hits are visibly weak.

**Done when:** a pooled run reports which candidates clear a stated significance
bar, and arm-A-vs-arm-B shows S0's current gate effectiveness.

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

- **Exemplar-generator tics leaking into the reference.** Craft-sourcing made the
  exemplars more stylistically assertive (moves AI overuses). The statistical
  diff may under-flag those; the blind judge (`run_judge.py`) is the primary
  mitigation.
  Re-examine at the next exemplar re-approval.
- **Content-word noise in the diff.** `tic_finder.py` ranks topic words too;
  admission always requires a human to name the structural candidate and a
  grounding check. Never wire the ranker straight to the backstop.
- **Single-generation reference.** The reference is one Fable snapshot. If Fable
  and a future target converge stylistically, the guard weakens — track the
  generator/target generation gap at each harvest.
