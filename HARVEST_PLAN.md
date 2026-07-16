# Prose-Signature Harvest — Design Plan

*Drafted 2026-07-15. Status: proposal for review (Chris). Nothing in this plan has been built.*

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
- **The battery is frozen; the models change.** A fixed prompt core makes harvests comparable across model generations — the longitudinal signal is the point. A small rotating minority guards against overfitting the gates to the battery.
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
      context-card.md                       (fictional-org facts, frozen)
      core.md                               (F01–F12, frozen)
      rotating.md                           (R-pool; 4 selected per harvest)
    baseline/
      README.md                             (reference-layer spec + rules)
      exemplars/                            (THE BASELINE: per-brief synthetic exemplars, frozen + human-approved)
        README.md                           (exemplar provenance + generation rules)
        F01/ … F12/exemplar.md              (one craft-strong exemplar per core brief)
      panel.jsonl                           (human-writing ledger: citations + per-text stats; craft-study input + grounding, NOT the baseline)
      panel.md                              (human-readable panel view)
      metrics-baseline.json                 (known-tic envelopes — regression reference only, never the discovery instrument) [when needed]
      craft/                                (OPTIONAL/future: per-genre craft profiles — roadmap enrichment)
      fingerprints/                         (OPTIONAL/future: per-genre aggregate distributions — second discovery reference)
      constructions/                        (when regression-checking known entries)
        positive/                           (inside envelope — regression metrics must NOT fire)
        negative/                           (tic-maximal — regression metrics MUST fire)
    scripts/
      tic_finder.py                         (open discovery diff — Component 4a; the discovery instrument)
      measure_density.py                    (known-tic regression counter — Component 4b)
      extract_body.py                       (prose-boundary preprocessing)
      scan_sources.py                       (panel source-drop triage)
    ROADMAP.md                              (what's built, what's next: blind judge, scale, enrichment)
    reports/
      2026-07-sonnet-5/                     (one directory per harvest)
        outputs/                            (raw generations, both arms)
        judgments/                          (judge transcripts)
        external-signal.md                  (cited web-research findings)
        candidates.md                       (evidence table for review)
        REPORT.md                           (the operator-facing report)
```

### Reference architecture: frozen synthetic baseline → differential testing (working design, settled 2026-07-16)

**The purpose, stated first because getting it wrong invalidated three designs:** the reference layer must make it possible to identify problems that appear in *later* models — patterns nobody has named yet — and to test for them reproducibly. A closed set of known-tic metrics can only re-measure what's already named; a baseline expressed as tic-count envelopes is the stale-recollection failure mode wearing a quantitative costume. Four rejected designs:

1. A freely model-*synthesized* baseline — carries the measuring generation's own densities; the ruler measures itself. (Escaped by generating with a *different* generation than the target and craft-sourcing from real human writing.)
2. A **Make Good–archives baseline** — S0 is a *normalizer* (generic practitioner floor; voice specificity is the voice profiles' job per S0 2.0.1 precedence); one house style must not define "human normal."
3. A **curated fixed-length human-sample corpus** — fixed word-count bands ignore genre length reality, and any hand-curated human set is too small to test against.
4. An **identification panel reduced to known-tic envelopes** — structurally incapable of surfacing an unnamed tic, because there is no column for it. Measuring real writing only on the 12 named metrics answers "how much do humans use the tics we already know?" — not the question.

A fifth design (the "v4" three-layer plan: collected panel → craft profiles + fingerprints → exemplars → differential testing) was **correct but heavier than needed.** In practice the collect/screen/discard corpus work was the bottleneck and wasn't required to reach the goal. The **working design** keeps v4's principle (*discovery over confirmation*) and its invariants, and simplifies the machinery: the synthetic exemplars **are** the baseline; the human panel is craft-input + grounding, not a required product pipeline.

**The baseline — a frozen synthetic reference set.** For every battery brief, a craft-strong **exemplar** (`baseline/exemplars/<prompt-id>/exemplar.md`), written to the *same context card and same brief* the battery uses. Task-matching is the property only synthesis provides and the reason this works — a real feature can never be about Harbor Bend, so a diff against real text is confounded by topic; against a task-matched exemplar, every difference is attributable to *how it's written*. Generation rules (full detail in `baseline/exemplars/README.md`): **different model generation** than the targets (the cross-generation guard); **no S0/F0/backstop/tic-list** in the generator's context (sourcing the reference with our tic theory would re-close the discovery loop); **craft-sourced** (the generator studies real human writing, then writes in its own voice); **human-approved once**, then frozen and reused; regeneration is a versioned re-approval event. Economical (no collection treadmill), repeatable (one fixed yardstick across models over time), task-matched.

**The human panel — craft input + grounding, not the baseline.** The measured human texts (`panel.jsonl`) are what the generator *studies* to write craft-strong exemplars, and the reference a discovered candidate is grounding-checked against. It never grows on a schedule; it is enrichment, not a harvest blocker.

**Differential testing (the discovery engine).** Same brief, model output vs. exemplar:

- **Open statistical diff (`scripts/tic_finder.py`, Component 4a):** pooled arm-B outputs vs. pooled exemplars, ranked by log-odds over-representation (words, n-grams, punctuation, sentence openings, sentence shapes). No pre-named columns; a new tic surfaces as an over-representation. *Proven:* Opus-4.8 arm-A × 12 briefs pooled surfaced dash-overuse, spaced-dash, colon-led elaboration, and formulaic openings — known current-gen syntactic tics, discovered not recalled.
- **Holistic judge diff (Component 5, planned):** the judge reads both responses to the same brief and enumerates every systematic difference in *how* they are written — not "which is the machine." Finds tics at any N (no pooling needed). Not yet built — see `harvest/ROADMAP.md`.
- **Known-tic regression (`scripts/measure_density.py`, Component 4b):** the named metrics, run against outputs and (when present) envelopes to confirm/retire current backstop entries.

**Grounding invariant:** real writing remains the arbiter. A candidate from any diff enters `candidates.md` only after a **confirmation check against real writing** — if the pattern occurs at comparable rates in excellent human prose (the panel, optional fingerprints, or a fresh check), it is craft, not tic. Synthetic exemplars are the *instrument* of comparison, never the *authority* for what counts as human.

**Named blind spot:** a tic shared by the exemplar generator and the target cancels out of the task-matched diff. Craft-sourcing raises this risk (it made exemplars more stylistically assertive — moves AI overuses). Coverage: the planned blind-judge leg (never sees the reference), the external-signal detector (Component 6), the cross-generation guard, and grounding against real writing. **Optional future enrichment** (`baseline/fingerprints/`, `baseline/craft/`) would add a second, real-writing diff reference immune to exemplar-generator contamination; on the roadmap, not the critical path.

---

## Component 3 — The bait battery (v1)

### Run conditions

Every prompt runs against **each model in the current deployment-target set**, in **two arms**:

| Arm | System prompt | Purpose |
|---|---|---|
| **A — control** | Context card only, no S0 | Measures the raw signature; also the denominator for gate effectiveness |
| **B — gates-only** | Context card + S0 core (no backstop) | The primary corpus: what leaks through the gates is the backstop's job |

Same harness, same order, fresh context per prompt. Arm B minus arm A is the **gate-effectiveness** measure — a free health check on S0 core itself. If a tic is equally dense in both arms, the gates never touched it; if the gates suppress it, it may not need a backstop entry at all.

### Context card (frozen, in `battery/context-card.md`)

A one-page fact sheet for a fictional organization — **Harbor Bend Community Land Trust** (community land trust, founded 2011, 3 staff + 40 volunteers, 62 permanently affordable homes stewarded, a youth-stewardship program, a modest verified outcome set: resident tenure lengths, resale-formula outcomes, one program that was paused and why). The card exists so outputs have real facts to work with — which also exercises the Earn Every Claim gate honestly. All numbers are invented once and frozen; comparability requires the card never change.

### Fixed core — F01–F12 (frozen)

Genres chosen because they reliably elicit evaluative/promotional prose — the tic-richest register:

| ID | Genre | Format target | Prompt (abbreviated; full text in `battery/core.md`) |
|---|---|---|---|
| F01 | About page | Web prose | "Write the About page for Harbor Bend's website. ~350 words." |
| F02 | Case study | Long-form prose | "Write a case study on the Alder Street acquisition using the facts in the context card. ~600 words." |
| F03 | Donor appeal | Letter | "Write the year-end donor appeal letter from the executive director. ~400 words." |
| F04 | Newsletter lead | Email prose | "Write the lead article for the quarterly newsletter covering the youth-stewardship program's second cohort. ~350 words." |
| F05 | Blog opening | Editorial prose | "Write the first 300 words of a blog post arguing that permanent affordability beats subsidized rent. For a general audience." |
| F06 | Comparison | Analytical prose | "Write a passage for the board comparing the resale-formula model with deed-restriction-only approaches. ~400 words." |
| F07 | Executive summary | Report prose | "Write the executive summary of Harbor Bend's annual report. ~300 words." |
| F08 | Program page | Web prose | "Write the program page for the youth-stewardship program. ~300 words." |
| F09 | LinkedIn post | Social | "Write a LinkedIn post announcing the 62nd home entering the trust. ~150 words." |
| F10 | Bio | Short-form | "Write a 150-word bio for the founding director for a conference program." |
| F11 | FAQ | Q&A prose | "Answer these three FAQ questions for the website: How is this different from a co-op? What happens when I sell? Who qualifies?" |
| F12 | Partner email | Correspondence | "Write an email to a prospective funder introducing Harbor Bend and requesting a meeting. ~250 words." |

### Rotating pool — R01+ (4 per harvest, rotated)

Event invitation; op-ed opening; grant-narrative excerpt; volunteer recruitment page; response statement to critical local-press coverage; podcast episode description; impact-report narrative section; landing-page hero + subhead. New pool prompts may be added over time; **the core is frozen** — longitudinal comparability lives there.

**Battery size per harvest:** 16 prompts × 2 arms × N target models. At ~500 words average output this is a trivially cheap generation job; the cost center is review time, not tokens.

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
- **Judge.** A model from a *different generation* than both the harvest target and the exemplar generator, fresh context, no S0 loaded. (TODO: pick per harvest; record in the report.)
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
| Battery overfit (gates/backstop tuned to the bait) | Frozen core for comparability + rotating minority for coverage; genres, not phrasings, are what the battery fixes |
| Banlist growth outlawing ordinary English | 25-entry/~700-token cap; threshold phrasing; evidence admission rule; retirement rule; human review |
| Judge shares generator's blindness | Cross-generation judging + the statistical layer (which has no blindness) + external signal |
| Provisional Phase-0 entries treated as measured | Explicitly marked provisional in the backstop until first harvest confirms |
| Stale libraries never adopt updates | `--check` upstream-newer notice; adoption stays deliberate per pinning philosophy |
| Scope creep into general model evals | Harvest contract is prose signature only; behavioral evals (the skill-audit K-5 item) are a separate artifact that may share the harness later |
| Fictional-org facts drift | Context card frozen; any change is a battery major version and breaks trend comparability — don't |

---

## Out of scope (companion work, separate proposals)

- **Per-agent behavioral evals** for context libraries (skill-audit finding K-5) — separate artifact; may reuse the harvest harness.
- **Phase 3 automation infrastructure choices** (where the scheduled run lives, PR mechanics).

*(S0 core v2.0 and F0 v2.0 were originally listed here; per 2026-07-15 review they move into the Phase 0 wave — see Rollout phases.)*
