# Prose-Signature Harvest — Runbook

Operational steps for running one harvest. Design rationale, detector
definitions, admission/retirement rules, and the report template live in
[`../HARVEST_PLAN.md`](../HARVEST_PLAN.md) — this file is the checklist an
operator (with Claude Code assisting) executes. Phase 1 is manual; the
counting stage gets a script (`scripts/measure_density.py`) in Phase 2.

**When to run:** a new model enters the deployment-target set (before
libraries move to it); annually regardless; or ad-hoc (core battery only,
single model) when an operator flags a suspected new pattern in production.

---

## H0 — Preconditions

- [ ] Layer-1 products exist (`baseline/README.md §2`): `panel.jsonl` at target scale for the genres in play; `craft/<genre>.md` craft profiles; `fingerprints/<genre>.json` open fingerprints; `metrics-baseline.json` regression envelopes. **First harvest only:** run the identification pass first.
- [ ] Exemplars exist for every battery prompt in play (`baseline/exemplars/<prompt-id>/`), craft-profile-checked and **human-approved** (`baseline/README.md §3`).
- [ ] Positive and negative controls exist in `baseline/constructions/` and the 4b regression metrics behave correctly on both (fire on negative, silent on positive).
- [ ] Target model list confirmed = the models Make Good libraries currently deploy on.
- [ ] Judge model AND exemplar-generator model recorded — each a **different generation** than any harvest target, and different from each other where possible.
- [ ] Create `reports/<YYYY-MM>-<models>/` with `outputs/`, `judgments/` subdirectories.

## H1 — Compose the battery

- [ ] Core F01–F12 (`battery/core.md`) + **four** prompts from `battery/rotating.md`, avoiding the previous harvest's four.
- [ ] Record the selection in `battery/rotating.md`'s rotation log and the report's provenance block.

## H2 — Generate the corpus

Per model × per arm × per prompt, **fresh context every prompt**:

| Arm | System prompt | Purpose |
|---|---|---|
| A — control | `battery/context-card.md` only | Raw signature; gate-effectiveness denominator |
| B — gates-only | context card + **S0 core** at the harvest's target version, with the BACKSTOP region left empty | Primary corpus — what leaks past the gates is the backstop's job |

- [ ] Save each output to `outputs/<model>/<arm>/<prompt-id>.md`, verbatim, no edits.
- [ ] No voice profiles, no other modules, no backstop in either arm.

## H3 — Statistical detection: open diff (discovery) + known-tic regression

- [ ] **Preprocess identically to the panel:** strip non-prose scaffolding before any measurement (the rule in `baseline/README.md §1`; `scripts/extract_body.py`). The same rule must govern panel texts, exemplars, and battery outputs, or nothing is comparable.
- [ ] **4a — open diff (the discovery layer):** pooled per (model, genre), compute over-representation rankings (log-odds keyness on unigrams, n-grams, punctuation marks, sentence shapes, openings, formatting elements) of arm-B outputs against **both** references: the pooled exemplars for the same prompts (task-matched) and `fingerprints/<genre>.json` (real writing, genre-level). Agent-assisted in Phase 1. Write ranked findings to `reports/<id>/diff-findings.md`. **Discovery rule:** a feature over-represented in both comparisons (or strongly in one with judge corroboration), recurring across prompts, is a candidate — named by a human at compile time.
- [ ] **4b — known-tic regression:** measure the named metrics per output with `scripts/measure_density.py`; compare against `metrics-baseline.json` envelopes. Write per-output rows and per-(model, arm) aggregates to `reports/<id>/counts.md`. **Regression rule:** a known metric flags in ≥ 60% of arm-B outputs → the corresponding backstop entry is confirmed; entries with no leakage move toward retirement.
- [ ] Control check the 4b suite both directions: every metric must **fire** on `constructions/negative/` and stay **silent** on `constructions/positive/`. A metric failing either is broken or mis-thresholded; fix before trusting its numbers.

## H4 — Judge: same-brief differential reading

- [ ] Pair each arm-B output with the **exemplar for the same battery prompt** (`baseline/exemplars/<prompt-id>/`). Randomize A/B order; strip provenance; the judge is not told which is which.
- [ ] Judge model (recorded at H0; different generation than target and exemplar generator), fresh context per pair, this prompt:

> These are two responses to the same brief, working from the same fact sheet.
> Compare **how they are written**, not what they say. 1) Enumerate every
> systematic difference in the writing — structure, rhythm, sentence and
> paragraph shapes, word choice, emphasis habits, formatting, how evidence is
> used. Quote exact phrases for each. 2) For each difference, name which
> passage does it. 3) If either passage shows patterns that read as *generated
> habits imposed on the content* rather than choices serving it, name them
> specifically.

- [ ] Save transcripts to `judgments/`. Compile the **difference tally**: differences clustered across pairs, each tagged with direction (target-side vs. exemplar-side). Target-side differences recurring across ≥ 3 pairs are candidates. **Exemplar-side recurring patterns are never dropped** — they are exemplar-quality feedback or the exemplar generator's signature; route them to the exemplar re-approval queue and the next identification pass.
- [ ] Compute **gate effectiveness**: arm A vs. arm B difference volume and severity — which patterns the gates suppressed, which passed untouched.

## H5 — External signal

- [ ] Agentic web research: editor/writing-community discussion, AI-detection research, published style analyses of the specific target models.
- [ ] Write `reports/<id>/external-signal.md`. **Every candidate needs a citation and a date** — uncited or undated claims don't count as corroboration.

## H6 — Compile candidates

- [ ] Write `reports/<id>/candidates.md`, one row per candidate: pattern (human-named for open-diff discoveries) · evidence (over-representation stats and/or 4b regression delta, judge mentions with direction, external citations) · 2–3 example excerpts · proposed threshold + remedy · proposed action (add / amend / retire / no action).
- [ ] **Grounding check (before admission):** confirm each discovered candidate against the real examples — via `fingerprints/<genre>.json`, or by re-fetching cited panel texts. A pattern occurring at comparable rates in the collected excellent writing is craft, not tic: reject it. Record the check's result in the row.
- [ ] Apply the admission rule (≥ 2 of 3 detector families) and the retirement rule (no leakage in two consecutive harvests) from HARVEST_PLAN.md Component 7. Include the current backstop's every entry in the table — confirmed, or moved toward retirement. Newly admitted entries each get a 4b regression metric.

## H7 — Human review (the merge gate)

- [ ] Reviewer (Chris or designee) accepts/prunes per row. The review's judgment calls: overuse vs. legitimate technique at observed density; threshold placement; remedy points at the right gate. Cap: 25 entries / ~700 tokens — growth past the cap means a gate change in S0 core, not a longer list.

## H8 — Release

- [ ] Edit `modules/S0_backstop.md` per accepted rows; clear `provisional` markers on confirmed entries.
- [ ] CHANGELOG entry under **s0-backstop**; bump version (minor for entry changes); tag `s0-backstop-vX.Y.Z`; push with tags.
- [ ] Libraries adopt on their own schedule via `--update-guardrails S0_BACKSTOP=<version>`; their `--check` will surface `[NEWER]` until they do.

## H9 — Report

- [ ] Write `reports/<id>/REPORT.md` per the template in HARVEST_PLAN.md Component 8 — including the provenance block (models + versions, judge model, battery composition, baseline hash, reviewer) and the operator-facing "What to listen for in review" section.
- [ ] Publication beyond the team (LeadersPath / thought leadership) is a separate editorial decision, made per report.
