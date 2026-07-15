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
- **Thresholds, not bans.** Most tics are legitimate techniques at human density — em-dashes and the rule of three are classical rhetoric. The machine signature is *overuse*. Backstop entries encode density thresholds relative to a human baseline, never absolute prohibitions.
- **Evidence earns a slot.** A pattern enters the backstop only when flagged by at least two of the three detectors (statistical, judge, external). A pattern with no observed leakage across two consecutive harvests is retired. The list can shrink.
- **The battery is frozen; the models change.** A fixed prompt core makes harvests comparable across model generations — the longitudinal signal is the point. A small rotating minority guards against overfitting the gates to the battery.
- **The baseline is frozen too.** Human writing is increasingly model-inflected. The human baseline corpus is a fixed, pre-2023-weighted sample set that does not grow with new writing.
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
      README.md                             (corpus provenance ledger; frozen)
      metrics-baseline.json                 (calibrated densities, written once)
      negative-controls/                    (synthetic tic-maximal samples — detector unit tests, never baseline)
    scripts/
      measure_density.py                    (Phase 2 — spec in Component 4)
    reports/
      2026-07-sonnet-5/                     (one directory per harvest)
        outputs/                            (raw generations, both arms)
        judgments/                          (judge transcripts)
        external-signal.md                  (cited web-research findings)
        candidates.md                       (evidence table for review)
        REPORT.md                           (the operator-facing report)
```

### Baseline corpus protocol (settled 2026-07-15)

**Hybrid: model-spec'd and model-screened, human-authored.** A model-*synthesized* baseline was considered and rejected — the baseline defines human density for the constructions the model overuses, so a model-authored baseline carries the measured generation's own densities and collapses the deltas toward zero (and would duplicate arm A while wearing a "human" label).

- **The model does:** corpus specification (genre stratification matched to the battery, length bands, register), sourcing and screening (criteria: verifiable pre-2023 publication, human-authorship confidence, genre fit), normalization/dedupe, calibration computation, and the provenance ledger in `baseline/README.md`.
- **Humans authored:** Make Good archives (Managed Word–era published copy, newsletters, appeal letters, the founder writing samples behind the library's voice profiles) plus published pre-2023 nonprofit-sector writing mined from public sources. Internal measurement use only; never redistributed. Nothing model-authored enters the baseline.
- **Synthesis gets the negative-control job:** deliberately tic-maximal model-generated samples live in `baseline/negative-controls/` as detector *sensitivity* unit tests — if a metric doesn't fire on them, the metric is broken. They are never part of the baseline and never used for calibration.
- Target size: 4–6 samples per battery genre at ~400–700 words (~40–70 samples). Assembled and frozen before the first harvest; a held-out split is reserved for judge pairing (Component 5).

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

## Component 4 — Statistical detection (the counting layer)

Measured per output, aggregated per (model, arm). Immune to model self-blindness because it is arithmetic. All thresholds below are **provisional defaults — the first run calibrates them against the frozen baseline** (TODO: replace after calibration).

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

**Candidate rule:** a metric flags as a backstop candidate when it exceeds threshold in ≥ 60% of arm-B outputs for a model. Phase 1 counts by hand/agent-assisted; Phase 2 implements `measure_density.py` (plain Python, no external deps, same convention as `build-deploy-bundles.py`).

---

## Component 5 — Blind judge protocol

Catches pattern-level tics the counters don't have a regex for.

- **Pairing.** Each arm-B output is paired with a genre- and length-matched human sample from a **held-out split** of the baseline corpus (never the calibration split).
- **Judge.** A model from a *different generation* than the generator, fresh context, no S0 loaded. Cross-generation judging partially defeats shared blindness; the statistical layer covers the rest. (TODO: pick the judge model per harvest; record it in the report.)
- **Presentation.** Randomized A/B order, no provenance metadata.
- **Judge prompt (template):**

  > One of these two passages was written by a person, one by an AI model. 1) Which is the model's, A or B? 2) Confidence (low/medium/high). 3) List the specific features that gave it away — quote the exact phrases or describe the exact constructions. 4) List any features that made the *other* passage feel human.

- **Outputs.** Two numbers and one list:
  - **Detectability rate** — % of pairs correctly identified. This is the harvest's headline number and the long-term trend line. If judges can't beat chance against gates-only output, the gates alone are sufficient and the backstop can shrink.
  - **Gate effectiveness** — detectability of arm B vs. arm A.
  - **Giveaway tally** — the "what gave it away" answers, clustered. A giveaway mentioned across ≥ 3 pairs is a candidate.

---

## Component 6 — External-signal pass

An agentic web-research pass at harvest time, because the freshest tic catalogs are published within weeks of a model release — far fresher than any training cutoff:

- Sources: editor and writing-community discussion, AI-detection research, published style analyses of the specific target models.
- Deliverable: `external-signal.md` — candidate patterns **with citations and dates**. Uncited or undated claims don't count as corroboration.
- This is the only detector that can see a tic *before* the battery does (e.g., a pattern the battery's genres don't elicit) — such candidates may enter the backstop on external + judge corroboration even without a statistical flag, but must be marked as externally sourced pending next-harvest measurement.

---

## Component 7 — Compilation, review, release

1. **Compile `candidates.md`:** one row per candidate — pattern, statistical evidence (metric, delta vs. baseline, % of outputs), judge mentions, external citations, 2–3 example excerpts, proposed threshold + remedy, proposed action (add / amend / retire / no action).
2. **Admission rule:** ≥ 2 of 3 detectors corroborate. **Retirement rule:** an existing entry with no leakage in two consecutive harvests is proposed for retirement (its metric stays in the counter set — retirement is reversible).
3. **Human review:** Chris (or designated reviewer) accepts/prunes per row. The reviewer's specific judgment calls: is this overuse or legitimate technique at observed density? Is the threshold right? Does the remedy point back to the right gate?
4. **Release:** update `modules/S0_backstop.md`, changelog entry, tag `s0-backstop-vX.Y.Z`. Libraries adopt by `--update-guardrails S0_BACKSTOP=<version>` on their own schedule.

---

## Component 8 — The report (operator education)

`reports/<harvest-id>/REPORT.md`, written for operators and agent designers, not for agents:

```markdown
# Prose-Signature Harvest — <models>, <date>

## Headline
- Detectability rate (gates-only): X% (prior harvest: Y%)
- Gate effectiveness: control X% → gates-only Y%
- Backstop: N entries added, M retired → s0-backstop-vX.Y.Z

## What this generation sounds like
[2–4 paragraphs: the signature in plain language, with excerpts.
What changed from the previous generation and the likely why.]

## Metric table
[All Component-4 metrics: baseline / control / gates-only / prior harvest]

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
rotating prompts), baseline corpus hash, who reviewed.]
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
| Baseline contamination (humans writing like models) | Baseline frozen, pre-2023-weighted, provenance recorded; never grows |
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
