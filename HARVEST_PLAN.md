# Prose-Signature Harvest — Design Plan

*Drafted 2026-07-15. Design rationale for the harvest. Substantial parts are now
built (as of 2026-07-18): the replacement battery (`harvest/battery/core.jsonl`,
31 briefs / 8 registers), all 31 exemplars (`harvest/baseline/exemplars/`), the
blind judge (`harvest/scripts/run_judge.py`, primary detector, multi-sample +
two-level recurrence), `tic_finder.py`, and intake tooling. The current build
state and priorities live in [`harvest/ROADMAP.md`](harvest/ROADMAP.md); the
operator runbook in [`harvest/HARVEST.md`](harvest/HARVEST.md). Two design points
below were superseded by decisions on 2026-07-17/18 and are flagged inline: the
battery is now a **growing pool, not frozen**, and the judge is chosen as the
**most capable analytic model**, not merely a different generation.*

---

## The problem this solves

S0's Revision Backstop — the list of words and constructions that slip past the process gates — is authored from recollection of what AI-generated prose sounds like. Recollection is stale by construction, two ways:

1. **Cutoff staleness.** Any model's knowledge of "current AI tics" ends at its training cutoff, before the models the list must govern have shipped. The v1.0.0 backstop ("delve, tapestry, foster...") targets the 2023–2024 generation's vocabulary signature; the current generation's signature is mostly **syntactic** (contrast-negation scaffolding, em-dash density, triadic lists, bold lead-ins, punch fragments) and the list catches almost none of it.
2. **Self-observation bias.** A model is a poor witness to its own generation's tics. Prior generations' tics are well-documented in training data; a model's own signature is partially invisible to it from the inside.

The fix is to stop authoring the list and start **measuring** it: generate output under controlled conditions, detect the signature from the outside, compile candidates with evidence, and have a human approve what enters the backstop. The harvest is that measurement protocol. Its by-product — a dated report on what the current model generation sounds like — is a training artifact for operators and agent designers, and candidate raw material for LeadersPath / thought-leadership content.

---

## Design principles (settled)

- **Never rely on self-report.** No detector asks a model "what are your tics." All detection observes generated output from the outside: counting, blind judging, or external published analysis.
- **Discovery over confirmation.** The instrument must be able to surface a pattern nobody has named yet. Closed metric sets are regression suites for *known* entries; discovery runs on open feature spaces (distributional diffs) and open questions (differential reading) against a testable standard. Any layer that can only confirm what's already named must never be the headline.
- **Thresholds, not bans.** Most tics are legitimate techniques at human density — em-dashes and the rule of three are classical rhetoric. The machine signature is *overuse*. Backstop entries encode density thresholds relative to a human baseline, never absolute prohibitions.
- **Evidence earns a slot.** A pattern enters the backstop only when flagged by at least two of the three detectors (statistical, judge, external). A pattern with no observed leakage across two consecutive harvests is retired. The list can shrink.
- **Stable core + growing pool; the models change.** *(Revised 2026-07-17 — superseded the original "the battery is frozen.")* A stable brief core makes harvests comparable across model generations — the longitudinal signal is the point. But the battery is designed to **grow**: registers and briefs are added as coverage gaps surface, because a discovery instrument for tics we can't yet name needs room for an unknown tic to appear. Freezing optimizes for regression (watch a known tic move against fixed inputs) — the opposite of discovery. Regression tracking of known tics is a separate, smaller concern. See `[[harvest-battery-purpose]]`.
- **The reference numbers come from pre-2023 human writing.** Human writing is increasingly model-inflected, so the identification panel measures only verifiably pre-2023 published texts. The panel is measure-and-cite (no text stored); re-deriving the envelope is a versioned event, never a silent drift.
- **Distribution rides the existing lock pipeline.** The backstop is an independently versioned artifact in this repo, pinned via `guardrails.lock`, vendored by `--resolve-guardrails`. Libraries adopt updates by deliberate bump, exactly like F0/S0 today. No runtime lookup, ever — always-load content is in the system prompt from turn one, per the delivery principle in the skill's ARCHITECTURE.md.
- **Human review is non-negotiable.** The harvest proposes; a human disposes. A fully automated list would let one anomalous run ban ordinary English.

---

## Component 1 — The S0 core / backstop split

S0 splits into a durable core and a volatile backstop, applying the skill's own volatile-vs-durable test to the module itself:

| Artifact | Contains | Changes when | Tags |
|---|---|---|---|
| **S0 core** | The process gates (Practitioner Voice, Earn Every Claim, Start From the Point), Writing Discipline, purpose/scope | The prose *philosophy* changes | `s0-vX.Y.Z` (existing) |
| **S0 backstop** | The current-generation tic list: patterns, thresholds, remedies | The *model landscape* changes (each harvest) | `s0-backstop-vX.Y.Z` (new) |

### Splice mechanism — delivered artifact stays one file

S0 core's Revision Backstop section is replaced by splice markers:

```markdown
## Revision Backstop

The three process gates handle the architecture. This backstop catches the
statistical defaults of the current model generation — measured by harvest,
not recalled. When an entry fires, don't just fix the instance: return to the
practitioner voice gate and rewrite from that person's perspective.

<!-- BACKSTOP:BEGIN -->
<!-- Resolved from s0-backstop at vendor time. Do not hand-edit. -->
<!-- BACKSTOP:END -->
```

`--resolve-guardrails` fetches S0 core and the backstop at their locked versions, splices the backstop content between the markers, and writes the vendored `S0_natural_prose_standards.md` as a **single file**. Consequences:

- Agent files, `## Required Reading` directives, the F0/S0 hard rule, and every validation script are untouched — they continue to see one S0 file.
- The vendored file's `<!-- GENERATED -->` banner records both versions (`s0@v2.0.0 + s0-backstop@v1.2.0`).

### Lock format addition

```yaml
declared:
  F0: 1.3.0
  S0: 2.0.0
  S0_BACKSTOP: 1.0.0
resolved:
  S0_BACKSTOP:
    version: 1.0.0
    tag: s0-backstop-v1.0.0
    sha: <sha>
    spliced_into: modules/shared/S0_natural_prose_standards.md
```

### Backstop versioning semantics

- **Patch** — wording/remedy clarification, no threshold or entry change.
- **Minor** — entries added or retired by a harvest (the normal per-harvest bump).
- **Major** — entry format change (e.g., new fields), or a threshold philosophy change that would alter behavior of agents already following the old entries.

### `--check` addition: upstream-newer notice

`--check` currently reports hand-edit drift. It gains a report-only notice when the upstream repo has a newer tagged backstop (or F0/S0) than the library's lock: *"s0-backstop v1.2.0 available (locked: v1.0.0) — run --update-guardrails to adopt."* Stale libraries surface themselves; nothing auto-updates.

### Backstop entry format

Entries are threshold-phrased and point back to the gates as the remedy:

```markdown
- **Contrast-negation scaffolding** — "it's not X — it's Y," "this isn't about
  A; it's about B," "Not X. Not Y. Z."
  Signal: more than one instance per ~500 words.
  Remedy: state the positive claim directly; the negated strawman is filler.

- **Em-dash chaining** — em-dashes as the default clause connector.
  Signal: more than ~2 per 250 words, or consecutive sentences each carrying one.
  Remedy: most em-dashes are a comma, a period, or a cut in disguise.
```

**Cap: 25 entries / ~700 tokens.** The gates are the mechanism; the backstop is the net under them. If the list wants to grow past the cap, the correct response is a gate change (S0 core version bump), not a longer list.

---

## Component 2 — Repository layout

```
makegood-guardrails/
  modules/
    F0_agent_behavioral_standards.md
    S0_natural_prose_standards.md          (core, with splice markers)
    S0_backstop.md                          (NEW — the versioned tic list)
  harvest/
    HARVEST.md                              (the runbook — protocol below)
    battery/
      core.jsonl                            (31 briefs / 8 registers; [invented]/[real] tagged; stable core + growing pool)
      COVERAGE_SPEC.md                      (battery design: registers, tagging, growth)
      BRIEFS_DRAFT.md                       (human-readable draft of the briefs)
    baseline/
      README.md                             (reference-layer spec + rules)
      exemplars/                            (THE REFERENCE: per-brief synthetic exemplars, versioned + re-approved)
        README.md                           (exemplar provenance + generation rules)
        <ID>/exemplar.md + provenance.json  (one craft-strong exemplar per brief; 31 committed)
      panel.jsonl                           (human-writing ledger: citations + per-text stats; craft-study input + grounding, NOT the baseline)
      panel.md                              (human-readable panel view)
      metrics-baseline.json                 (known-tic envelopes — regression reference only, never the discovery instrument) [when needed]
      craft/                                (OPTIONAL/future: per-genre craft profiles — roadmap enrichment; empty stub)
      fingerprints/                         (OPTIONAL/future: per-genre aggregate distributions — second discovery reference; empty stub)
      constructions/                        (when regression-checking known entries; empty stub)
        positive/                           (inside envelope — regression metrics must NOT fire)
        negative/                           (tic-maximal — regression metrics MUST fire)
    scripts/
      run_judge.py                          (blind judge — Component 5; PRIMARY detector; multi-sample + two-level recurrence)
      tic_finder.py                         (open discovery diff — Component 4a; backward-looking secondary)
      measure_density.py                    (known-tic regression counter — Component 4b)
      promote_exemplars.py                  (promote staged exemplars → baseline/exemplars/ + provenance)
      extract_body.py                       (prose-boundary preprocessing)
      scan_sources.py                       (panel source-drop triage)
      build_sources.py / recover_failures.py (rebuild the sources/ craft corpus)
    ROADMAP.md                              (what's built, what's next: first judge run, scale, enrichment)
  sources/                                  (gitignored craft corpus Fable studies; rebuildable)
    reports/
      2026-07-sonnet-5/                     (one directory per harvest)
        outputs/                            (raw generations, both arms)
        judgments/                          (judge transcripts)
        external-signal.md                  (cited web-research findings)
        candidates.md                       (evidence table for review)
        REPORT.md                           (the operator-facing report)
```

### Reference architecture: synthetic exemplar reference → differential testing (working design; battery replaced 2026-07-17, exemplars committed 2026-07-18)

**The purpose, stated first because getting it wrong invalidated three designs:** the reference layer must make it possible to identify problems that appear in *later* models — patterns nobody has named yet — and to test for them reproducibly. A closed set of known-tic metrics can only re-measure what's already named; a baseline expressed as tic-count envelopes is the stale-recollection failure mode wearing a quantitative costume. Four rejected designs:

1. A freely model-*synthesized* baseline — carries the measuring generation's own densities; the ruler measures itself. (Escaped by generating with a *different* generation than the target and craft-sourcing from real human writing.)
2. A **Make Good–archives baseline** — S0 is a *normalizer* (generic practitioner floor; voice specificity is the voice profiles' job per S0 2.0.1 precedence); one house style must not define "human normal."
3. A **curated fixed-length human-sample corpus** — fixed word-count bands ignore genre length reality, and any hand-curated human set is too small to test against.
4. An **identification panel reduced to known-tic envelopes** — structurally incapable of surfacing an unnamed tic, because there is no column for it. Measuring real writing only on the 12 named metrics answers "how much do humans use the tics we already know?" — not the question.

A fifth design (the "v4" three-layer plan: collected panel → craft profiles + fingerprints → exemplars → differential testing) was **correct but heavier than needed.** In practice the collect/screen/discard corpus work was the bottleneck and wasn't required to reach the goal. The **working design** keeps v4's principle (*discovery over confirmation*) and its invariants, and simplifies the machinery: the synthetic exemplars **are** the baseline; the human panel is craft-input + grounding, not a required product pipeline.

**The reference — a synthetic exemplar set (the quality bar).** For every battery brief, a craft-strong **exemplar** (`baseline/exemplars/<ID>/exemplar.md`), written to the *same brief* (and substrate, where the register has one) the battery uses. Task-matching is the property only synthesis provides and the reason this works — a diff against real text is confounded by topic; against a task-matched exemplar, every difference is attributable to *how it's written*. The exemplar is the human-grade **quality bar**: what the best available model produces disposed to write like the skilled humans in the craft corpus. Generation rules (full detail in `baseline/exemplars/README.md`): **different model generation** than the targets (the cross-generation guard); **no S0/F0/backstop/tic-list** in the generator's context (sourcing the reference with our tic theory would re-close the discovery loop); **craft-sourced via `v2-learn-decisions`** (the generator learns the *decisions* behind the `sources/` corpus rather than imitating voice — reaches sub-tone mechanics a "write like this" prompt misses); **versioned + re-approved**, not frozen-forever. Economical (no collection treadmill), repeatable (one task-matched yardstick per brief across models over time). 31 exemplars committed 2026-07-18. See `[[harvest-exemplar-learning-instruction]]`.

**The human panel — craft input + grounding, not the baseline.** The measured human texts (`panel.jsonl`) are what the generator *studies* to write craft-strong exemplars, and the reference a discovered candidate is grounding-checked against. It never grows on a schedule; it is enrichment, not a harvest blocker.

**Differential testing (the discovery engine).** Same brief, model output vs. exemplar:

- **Open statistical diff (`scripts/tic_finder.py`, Component 4a):** pooled arm-B outputs vs. pooled exemplars, ranked by log-odds over-representation (words, n-grams, punctuation, sentence openings, sentence shapes). No pre-named columns; a new tic surfaces as an over-representation. *Proven:* Opus-4.8 arm-A × 12 briefs pooled surfaced dash-overuse, spaced-dash, colon-led elaboration, and formulaic openings — known current-gen syntactic tics, discovered not recalled.
- **Holistic judge diff (`scripts/run_judge.py`, Component 5 — the PRIMARY detector):** the judge reads both responses to the same brief and enumerates every systematic difference in *how* they are written — not "which is the machine." Finds tics at any N (no pooling needed). Built and verified; supports multiple samples per brief with two-level recurrence (a tic must recur across samples of a brief AND across briefs). It is now the headline detector; `tic_finder.py` is a backward-looking secondary cross-check.
- **Known-tic regression (`scripts/measure_density.py`, Component 4b):** the named metrics, run against outputs and (when present) envelopes to confirm/retire current backstop entries.

**Grounding invariant:** real writing remains the arbiter. A candidate from any diff enters `candidates.md` only after a **confirmation check against real writing** — if the pattern occurs at comparable rates in excellent human prose (the panel, optional fingerprints, or a fresh check), it is craft, not tic. Synthetic exemplars are the *instrument* of comparison, never the *authority* for what counts as human.

**Named blind spot (measured + mitigated 2026-07-18):** a tic shared by the exemplar generator and the target cancels out of the task-matched diff. This was measured, not just feared — the v1 exemplars carried an em-dash tic at 2.94/250w against a human-corpus baseline of 0.67. The `v2-learn-decisions` generation instruction cut it to 1.35/250w without naming any tic. Residual risk persists at the punctuation level (still above human), so for punctuation-level tics use the `sources/` human corpus as the baseline, not the exemplars, and always run the human corpus as a control before treating a raw count as a finding. Coverage: the blind judge (never sees provenance), the external-signal detector (Component 6), the cross-generation guard, and grounding against real writing. **Optional future enrichment** (`baseline/fingerprints/`, `baseline/craft/`) would add a second, real-writing diff reference immune to exemplar-generator contamination; on the roadmap, not the critical path.

---

## Component 3 — The bait battery (v1)

### Run conditions

Every prompt runs against **each model in the current deployment-target set**, in **two arms**:

Each brief carries its own prompt and, where the register needs it, its own
substrate (in `core.jsonl`); there is no single shared fixed context card.

| Arm | System prompt | Purpose |
|---|---|---|
| **A — control** | no guardrail modules (brief + its own substrate only) | Measures the raw signature; also the denominator for gate effectiveness |
| **B — gates-only** | S0 core (no backstop) | The primary corpus: what leaks through the gates is the backstop's job |

Same harness, same order, fresh context per prompt. Arm B minus arm A is the **gate-effectiveness** measure — a free health check on S0 core itself. If a tic is equally dense in both arms, the gates never touched it; if the gates suppress it, it may not need a backstop entry at all.

> **Superseded 2026-07-17.** The original v1 battery — a frozen single-org
> promotional set (Harbor Bend Community Land Trust context card + 12 prompts
> F01–F12, all one org, all evaluative/promotional register) — was **retired.**
> A single org in one register can only surface tics *within that genre*, and the
> first real run confirmed it: the top non-known "discoveries" were donor-appeal
> genre artifacts, not model tics. The current battery organizes by
> **domain/register** instead, so the register is the stimulus and the judge names
> whatever the model overdoes. The subsections below are kept only as the record of
> what was replaced and why; the live battery spec is authoritative.

**The current battery** (source of truth: `battery/core.jsonl`; design:
`battery/COVERAGE_SPEC.md`): 31 briefs across **8 registers** — analytical,
technical, narrative, news, terse, correspondence, reasoning, adversarial. Every
brief is tagged `[invented]` (writing-without-priors) or `[real]` (writing-with-
priors / trained-data recall), and carries its own prompt plus, where the register
needs one, its own substrate — there is no single shared context card. It is a
**stable core + growing pool**: the core recurs every harvest for longitudinal
comparability, and registers/briefs are added as coverage gaps surface (a
discovery instrument needs room for an unnamed tic to appear). Multiple samples
per brief per arm (default 3) so a tic must recur across samples, not just briefs.

<details><summary>Retired v1 battery (Harbor Bend F01–F12) — historical record</summary>

The v1 battery was a one-page fact sheet for a fictional **Harbor Bend Community
Land Trust** plus 12 frozen prompts (About page, case study, donor appeal,
newsletter, blog opening, board comparison, exec summary, program page, LinkedIn
post, bio, FAQ, partner email) and a rotating pool (event invitation, op-ed, grant
narrative, etc.). All one org, all promotional register. Retired because that
scope structurally cannot distinguish a model tic from a genre convention. See
`[[harvest-battery-purpose]]`.

</details>

---

## Component 4 — Statistical detection: open diff (discovery) + known-tic regression

Two statistical layers with different jobs. Both are arithmetic, immune to model self-blindness.

### 4a — Open differential analysis (the discovery layer)

No pre-named metrics. Pooled per (model, genre), compute over-representation rankings (log-odds or log-likelihood keyness) of arm-B outputs against two references:

1. **Task-matched:** the pooled exemplars for the same prompts — differences attributable purely to *how it's written*.
2. **Genre-level:** the Layer-1 fingerprints from real writing — immune to exemplar-generator contamination.

Feature spaces, deliberately generic: unigrams/lemmas, bigrams/trigrams, all punctuation marks, sentence-length and paragraph-shape distributions, sentence-opening patterns, formatting elements. **Discovery rule:** a feature over-represented in both comparisons (or strongly in one with judge corroboration), recurring across prompts, is a candidate — named by a human at compile time, not pre-named by the instrument.

### 4b — Known-tic regression (the confirmation layer)

The named metrics below, measured per output against the per-genre envelopes in `metrics-baseline.json`. Their job is **confirming and retiring existing backstop entries** and placing thresholds for newly admitted ones — not discovery; a pattern must already be named to have a row here. Every admitted backstop entry gets a regression metric; retired entries keep theirs (retirement is reversible). Thresholds below are provisional until measured envelopes replace them.

| Metric | Definition | Flag when (provisional) |
|---|---|---|
| `em_dash_rate` | Em-dashes per 1,000 words | ≥ 2× baseline |
| `contrast_negation_rate` | "not X — it's Y" / "isn't just" / "it's not about" constructions per 1,000 words | ≥ 2× baseline |
| `triadic_rate` | % of sentences containing a 3-item parallel series | ≥ 2× baseline |
| `bold_leadin_rate` | % of paragraphs opening with a bolded phrase (markdown outputs) | ≥ 25% |
| `fragment_rate` | Sentence fragments per 1,000 words | ≥ 2× baseline |
| `signpost_rate` | "Here's the thing," "The reality is," "Let's break down" per 1,000 words | > 0 sustained across outputs |
| `hedge_closer_rate` | "Ultimately," / "At the end of the day" / "In the end" closers per output | ≥ 2× baseline |
| `header_density` | Headings per 500 words in prose-target outputs | any, in letter/email/bio genres |
| `bullet_share` | % of body text inside list items in prose-target outputs | ≥ 15% in prose genres |
| `legacy_vocab_rate` | Hits against the v1.0.0 word list (kept as a metric even after entries retire) | > 0 |
| `sentence_length_cv` | Coefficient of variation of sentence length (burstiness — humans higher) | ≤ 0.75× baseline |
| `paragraph_uniformity` | Std-dev of paragraph length (models produce eerily uniform paragraphs) | ≤ 0.5× baseline |

**Regression rule:** a known metric flags when it exceeds threshold in ≥ 60% of arm-B outputs for a model. Tooling: `scripts/measure_density.py` covers 4b today; 4a's keyness pass is agent-assisted in Phase 1 and gets a script in Phase 2.

---

## Component 5 — Judge protocol: same-brief differential reading

The open *qualitative* detector — catches pattern-level differences neither statistical layer can represent (structural moves, emphasis habits, how evidence is deployed).

- **Pairing.** Each arm-B output is paired with the **exemplar for the same battery prompt** (`baseline/exemplars/<prompt-id>/`). Same brief, same facts — the comparison is purely about the writing.
- **Judge.** The **most capable analytic model available** at harvest time, chosen on merit (the judge does hard analytic work) — *not* selected merely for being a different generation. *(Revised 2026-07-17 — superseded the earlier "different generation than target and exemplar generator" framing.)* Fresh context per pair, no S0 loaded. No "latest" alias exists — record the pinned model id in the report; if the judge equals the target model, note that overlap as a weaker independent check.
- **Presentation.** Randomized A/B order, no provenance metadata; the judge is not told which is which.
- **Judge prompt (template):**

  > These are two responses to the same brief, working from the same fact sheet. Compare **how they are written**, not what they say. 1) Enumerate every systematic difference in the writing — structure, rhythm, sentence and paragraph shapes, word choice, emphasis habits, formatting, how evidence is used. Quote exact phrases for each. 2) For each difference, name which passage does it. 3) If either passage shows patterns that read as *generated habits imposed on the content* rather than choices serving it, name them specifically.

- **Outputs.**
  - **Difference tally** — differences clustered across pairs, each tagged with its direction (target-side vs. exemplar-side). A target-side difference recurring across ≥ 3 pairs is a candidate. An *exemplar-side* recurring pattern is exemplar feedback or the exemplar generator's signature — reviewed either way, never silently dropped.
  - **Gate effectiveness** — arm A vs. arm B difference volume and severity: which patterns the gates suppressed, which passed untouched.

---

## Component 6 — External-signal pass

An agentic web-research pass at harvest time, because the freshest tic catalogs are published within weeks of a model release — far fresher than any training cutoff:

- Sources: editor and writing-community discussion, AI-detection research, published style analyses of the specific target models.
- Deliverable: `external-signal.md` — candidate patterns **with citations and dates**. Uncited or undated claims don't count as corroboration.
- This is the only detector that can see a tic *before* the battery does (e.g., a pattern the battery's genres don't elicit) — such candidates may enter the backstop on external + judge corroboration even without a statistical flag, but must be marked as externally sourced pending next-harvest measurement.

---

## Component 7 — Compilation, review, release

1. **Compile `candidates.md`:** one row per candidate — pattern (human-named at compile time for open-diff discoveries), evidence (over-representation stats and/or regression delta, judge mentions with direction, external citations), 2–3 example excerpts, proposed threshold + remedy, proposed action (add / amend / retire / no action).
2. **Grounding check before admission:** every discovered candidate is confirmed against the real examples — via the fingerprints, or by re-fetching cited panel texts. A pattern occurring at comparable rates in the collected excellent writing is craft, not tic: rejected. Real writing is the arbiter; exemplars are only the instrument.
3. **Admission rule:** ≥ 2 of 3 detectors corroborate (open statistical diff and known-tic regression count as one detector family — statistical). **Retirement rule:** an existing entry with no leakage in two consecutive harvests is proposed for retirement (its regression metric stays in the counter set — retirement is reversible).
4. **Human review:** Chris (or designated reviewer) accepts/prunes per row. The reviewer's specific judgment calls: is this overuse or legitimate technique at observed density? Is the threshold right? Does the remedy point back to the right gate?
5. **Release:** update `modules/S0_backstop.md` (each newly admitted entry gains a 4b regression metric), changelog entry, tag `s0-backstop-vX.Y.Z`. Libraries adopt by `--update-guardrails S0_BACKSTOP=<version>` on their own schedule.

---

## Component 8 — The report (operator education)

`reports/<harvest-id>/REPORT.md`, written for operators and agent designers, not for agents:

```markdown
# Prose-Signature Harvest — <models>, <date>

## Headline
- Discovered: N new candidate patterns (open diff X, judge Y, external Z);
  K survived the grounding check and review
- Known-tic regression: [entries confirmed / moved toward retirement / drifted]
- Gate effectiveness: [what the gates suppressed vs. passed, arm A → arm B]
- Backstop: N entries added, M retired → s0-backstop-vX.Y.Z

## What this generation sounds like
[2–4 paragraphs: the signature in plain language, with excerpts.
What changed from the previous generation and the likely why.]

## Discovery findings
[Top over-representations from the open diff (4a), each with its grounding-
check result; the judge's recurring differences with direction.]

## Known-tic regression table
[All 4b metrics: envelope / control / gates-only / prior harvest]

## What the gates caught and missed
[Arm A vs. B — which tics the gates suppress, which pass through untouched.
Implications for S0 core, if any.]

## What to listen for in review
[The operator-facing payoff: the 3–5 constructions a human reviewer should
be tuned to this generation, with before/after examples.]

## Backstop diff
[Entries added/amended/retired, each with its one-line evidence summary.]

## Provenance
[Models + versions tested, judge model, battery composition (core + which
rotating prompts), identification-pass version + panel hash, foil generator
model, who reviewed.]
```

The "What to listen for in review" section is deliberately reusable: it is the seed for LeadersPath material and thought-leadership content, per the open-methodology positioning — publication is a separate editorial decision made per report, not automatic.

---

## Cadence

- **Event-driven (primary):** a new model enters the deployment-target set → harvest before libraries move to it.
- **Annual sweep:** one harvest per year regardless, to keep the trend line alive.
- **Ad-hoc:** an operator flags a suspected new pattern in production output → mini-harvest (battery core only, single model).

---

## Rollout phases

**Phase 0 — the split (no harvest yet).** *(Scope approved 2026-07-15, including the cascade.)*
Split S0 into core + backstop; seed `s0-backstop-v1.0.0` with the current v1.0.0 list *plus* the audit-identified syntactic candidates (contrast-negation, em-dash chaining, triadic lists, bold lead-ins, fragments, signposting), each **marked provisional** — they are training-derived recollection, exactly the failure mode this system replaces, and the first harvest confirms or corrects them. **S0 core lands as v2.0 in the same change**: the split, plus voice-profile precedence routing (a loaded voice profile is the practitioner; the profile's specifics override generic practitioner inference — S0 is the floor, the profile is the voice) and the medium-shape gate (write in the deliverable's shape, not chat's). Lock-format and `--resolve-guardrails`/`--check` changes in `build-deploy-bundles.py` (coordinated change with the `building-context-libraries` skill — new skill minor version + Phase M migration for existing libraries). **F0 v2.0** (arming conditions for Gates 3–5, "Where the Gates Run" guidance, de-templated Gate 1 refusal text) lands in the same coordinated wave — a *major* bump, not the originally-drafted v1.4, because arming conditions narrow gate triggers and this repo's semver convention classifies trigger-narrowing as major.

**Phase 1 — first manual harvest.**
Write `harvest/HARVEST.md` as a runbook an operator executes with Claude Code assistance: assemble + freeze baseline, calibrate thresholds, run battery (two arms), hand/agent-count metrics, run judge protocol, external-signal pass, compile, review, release `s0-backstop-v1.1.0`. Everything is files and prompts; no new tooling required.

**Phase 2 — instrument.**
`measure_density.py` (zero-dep Python); a judge-harness prompt file; the runbook drops to a half-day of operator time.

**Phase 3 — schedule (optional).**
A recurring agentic run (scheduled agent or skill invocation) that executes battery + counting + judging + external pass and opens a PR with `candidates.md` and a draft report. Human review remains the merge gate. Do not build Phase 3 until Phase 1 has run at least twice — the protocol should stabilize before it is automated.

---

## Risks and second-order effects

| Risk | Mitigation |
|---|---|
| Baseline contamination (humans writing like models) | Panel texts verifiably pre-2023, provenance recorded; envelope re-derivation is a versioned event |
| Exemplars drifting into authority over what counts as human | Grounding invariant: every discovered candidate is confirmed against real examples before admission; exemplars are the comparison instrument, never the arbiter |
| Shared tics between exemplar generator and target cancel out of the task-matched diff | Fingerprint-level diff against real writing + external signal + cross-generation exemplar production; exemplar-side judge findings reviewed, never dropped |
| Discovery layer quietly regressing into a fixed metric list | "Discovery over confirmation" principle: 4a runs on open feature spaces; named metrics live only in 4b as regression |
| Battery overfit (gates/backstop tuned to the bait) | Stable core for comparability + growing pool for coverage; registers, not phrasings, are what the battery fixes — the register is the stimulus, the judge names the tic |
| Banlist growth outlawing ordinary English | 25-entry/~700-token cap; threshold phrasing; evidence admission rule; retirement rule; human review |
| Judge shares generator's blindness | Cross-generation judging + the statistical layer (which has no blindness) + external signal |
| Provisional Phase-0 entries treated as measured | Explicitly marked provisional in the backstop until first harvest confirms |
| Stale libraries never adopt updates | `--check` upstream-newer notice; adoption stays deliberate per pinning philosophy |
| Scope creep into general model evals | Harvest contract is prose signature only; behavioral evals (the skill-audit K-5 item) are a separate artifact that may share the harness later |
| `[real]`-brief facts drift or provoke hallucination | Exemplars fact-verified before promotion; the judge is form-only by design (a hallucination leaves a stylistic fingerprint the judge catches without fact-checking) — see `[[harvest-battery-purpose]]` |

---

## Out of scope (companion work, separate proposals)

- **Per-agent behavioral evals** for context libraries (skill-audit finding K-5) — separate artifact; may reuse the harvest harness.
- **Phase 3 automation infrastructure choices** (where the scheduled run lives, PR mechanics).

*(S0 core v2.0 and F0 v2.0 were originally listed here; per 2026-07-15 review they move into the Phase 0 wave — see Rollout phases.)*
