# Prose-Signature Harvest — Roadmap

Where the harvest tooling stands and what comes next, in priority order. The
goal the roadmap serves: *run a new model's writing through the harvest and get
back a trustworthy list of its tics.* Everything here is measured against that.

Design rationale lives in `../HARVEST_PLAN.md`; the operator checklist in
`HARVEST.md`; the reference layer in `baseline/README.md`.

---

## Built and working (2026-07-16)

- **Frozen synthetic baseline** — 12 Fable-authored, craft-sourced, guardrail-free
  exemplars, one per core brief (`baseline/exemplars/`). Human-approved, frozen,
  reusable against any future target. This replaced the collected-human-corpus
  approach.
- **`tic_finder.py`** (Component 4a, discovery) — open log-odds keyness diff.
  Proven end-to-end: Opus-4.8 arm-A × 12 briefs pooled surfaced real current-gen
  tics (dash-overuse, spaced-dash, colon elaboration, formulaic openings).
- **`measure_density.py`** (Component 4b, regression) — known-tic counter, demoted
  to a regression suite for existing backstop entries.
- **Intake:** `scan_sources.py` (triage), `extract_body.py` (prose extraction);
  14-text human panel (`panel.jsonl`) as craft-study input + grounding reference.

---

## Next, in priority order

### 1. Blind-judge leg (Component 5) — highest value, not yet built

**Why first.** It is the second independent detector, and the one that works at
**any N** — it reads holistically, so it finds tics without needing a pooled
corpus, and it catches pattern-level tics no regex ranks (a diff over tokens
can't see "every paragraph follows the same three-move shape"). It also covers
the statistical diff's named blind spot: the judge never sees the reference, so a
tic shared by exemplar-generator and target — invisible to `tic_finder.py` —
still gets caught.

**Do:** a `judge` pass — different-generation model, fresh context per pair, given
(target output, exemplar) in randomized order with the same-brief differential
prompt already drafted in `HARVEST.md` H4 ("enumerate how they are written, not
which is the machine"). Cluster recurring differences into a tally; target-side
recurrences across ≥3 pairs are candidates. Ship as `scripts/run_judge.py` (a
harness that dispatches the pairs) or an operator-run prompt file.

**Done when:** running it on the existing Opus-arm-A vs exemplar pairs produces a
differences tally that corroborates (or challenges) `tic_finder.py`'s dash/colon
findings.

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
  diff may under-flag those; the blind judge (item 1) is the primary mitigation.
  Re-examine at the next exemplar re-approval.
- **Content-word noise in the diff.** `tic_finder.py` ranks topic words too;
  admission always requires a human to name the structural candidate and a
  grounding check. Never wire the ranker straight to the backstop.
- **Single-generation reference.** The reference is one Fable snapshot. If Fable
  and a future target converge stylistically, the guard weakens — track the
  generator/target generation gap at each harvest.
