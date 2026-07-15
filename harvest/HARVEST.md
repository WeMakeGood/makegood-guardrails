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

- [ ] Baseline corpus assembled, frozen, and split (`baseline/README.md` ledger populated). **First harvest only:** assemble it first — the counting stage has no denominators without it.
- [ ] `baseline/metrics-baseline.json` exists (first harvest: computed in H3 from the calibration split).
- [ ] Target model list confirmed = the models Make Good libraries currently deploy on.
- [ ] Judge model chosen — a **different generation** than any generator; record it now.
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

## H3 — Count (statistical detector)

- [ ] **First harvest only:** compute per-metric human densities from the baseline's *calibration split* → write `baseline/metrics-baseline.json`, and replace HARVEST_PLAN.md Component 4's provisional thresholds with calibrated ones.
- [ ] Measure every Component-4 metric per output (agent-assisted counting until `measure_density.py` ships). Write per-output rows and per-(model, arm) aggregates to `reports/<id>/counts.md`.
- [ ] Flag candidates per the rule: metric over threshold in ≥ 60% of arm-B outputs for a model.
- [ ] Run the metrics against `baseline/negative-controls/` — every metric must fire there. A metric that doesn't is broken; fix it before trusting its arm-B numbers.

## H4 — Judge (blind cross-model detector)

- [ ] Pair each arm-B output with a genre- and length-matched human sample from the baseline's **held-out split**. Randomize A/B order; strip provenance.
- [ ] Judge model, fresh context per pair, this prompt:

> One of these two passages was written by a person, one by an AI model.
> 1) Which is the model's, A or B? 2) Confidence (low/medium/high). 3) List
> the specific features that gave it away — quote the exact phrases or
> describe the exact constructions. 4) List any features that made the
> *other* passage feel human.

- [ ] Save transcripts to `judgments/`. Compute: **detectability rate** (the harvest's headline number), **gate effectiveness** (arm B vs. arm A detectability), and the **giveaway tally** (a giveaway mentioned across ≥ 3 pairs is a candidate).

## H5 — External signal

- [ ] Agentic web research: editor/writing-community discussion, AI-detection research, published style analyses of the specific target models.
- [ ] Write `reports/<id>/external-signal.md`. **Every candidate needs a citation and a date** — uncited or undated claims don't count as corroboration.

## H6 — Compile candidates

- [ ] Write `reports/<id>/candidates.md`, one row per candidate: pattern · statistical evidence (metric, delta vs. baseline, % of outputs) · judge mentions · external citations · 2–3 example excerpts · proposed threshold + remedy · proposed action (add / amend / retire / no action).
- [ ] Apply the admission rule (≥ 2 of 3 detectors) and the retirement rule (no leakage in two consecutive harvests) from HARVEST_PLAN.md Component 7. Include the current backstop's every entry in the table — confirmed, or moved toward retirement.

## H7 — Human review (the merge gate)

- [ ] Reviewer (Chris or designee) accepts/prunes per row. The review's judgment calls: overuse vs. legitimate technique at observed density; threshold placement; remedy points at the right gate. Cap: 25 entries / ~700 tokens — growth past the cap means a gate change in S0 core, not a longer list.

## H8 — Release

- [ ] Edit `modules/S0_backstop.md` per accepted rows; clear `provisional` markers on confirmed entries.
- [ ] CHANGELOG entry under **s0-backstop**; bump version (minor for entry changes); tag `s0-backstop-vX.Y.Z`; push with tags.
- [ ] Libraries adopt on their own schedule via `--update-guardrails S0_BACKSTOP=<version>`; their `--check` will surface `[NEWER]` until they do.

## H9 — Report

- [ ] Write `reports/<id>/REPORT.md` per the template in HARVEST_PLAN.md Component 8 — including the provenance block (models + versions, judge model, battery composition, baseline hash, reviewer) and the operator-facing "What to listen for in review" section.
- [ ] Publication beyond the team (LeadersPath / thought leadership) is a separate editorial decision, made per report.
