# Battery Coverage Spec — PROPOSAL (not approved)

> **Status: draft for review, 2026-07-17.** Replaces the frozen 12 Harbor Bend
> briefs (F01–F12), which were built from the wrong question ("what does Make
> Good do / how does a nonprofit write") and could only surface tics that
> manifest in nonprofit-promotional prose. Nothing here is approved. See
> `[[harvest-battery-purpose]]` for the corrected intent.

## What the battery is for

A **model-stress instrument.** Its only job: exercise a new model across the
range of real writing work so its unknown tics have somewhere to surface, so the
judge can name them, so `modules/S0_backstop.md` can be refactored to catch them.

It is **not** a demonstration of any organization's work, a writing sample, or a
"how should this be written" reference.

## Two design rules (load-bearing — this is where the old battery failed)

1. **Organize by domain/register, never by tendency.** We do NOT build briefs to
   provoke named tics (hedging, over-scaffolding, em-dashes). A brief built to
   catch hedging can only catch hedging — that is the backward-looking flaw of a
   known-tic detector, smuggled into the battery. We are testing models whose tics
   we cannot yet name. So: the **register is the stimulus**; the **judge discovers
   the tendency.** Each brief asks for a genuine piece of work in a register, as
   neutrally as possible, and imposes no theory about what the model will overdo.

2. **The register set is a working set, not a truth claim.** These are the
   registers we currently cover — expandable and adjustable as harvests reveal
   coverage gaps (a real tic that only shows up in a register we're not testing).
   The battery is designed to GROW. This is the opposite of the frozen design and
   the correct shape for discovery.

## Proposed starting coverage

Registers below are the starting set — several already backed by the human source
drop (`~/makegood-harvest-sources/`: news, feature, FAQ, editorial). The rest
extend into work the source drop doesn't yet cover but models are routinely asked
to do. **Count per register is a starting guess, not a rule.**

| # | Register | Why it stresses a model | Source-drop backing |
|---|----------|-------------------------|---------------------|
| R-ANALYTIC | Analytical / argumentative prose (make a case, weigh a tradeoff) | Persuasion + reasoning under a claim | editorial |
| R-TECH | Technical / instructional (how-to, explain a mechanism, doc a process) | Precision, sequencing, restraint | faq |
| R-NARRATIVE | Narrative / descriptive / feature (tell what happened, evoke a scene) | Description, pacing, sensory prose | feature |
| R-NEWS | Reportorial / news (neutral factual report) | Attribution, neutral register, lede discipline | news |
| R-TERSE | Terse / hard-constrained (one sentence; ≤40 words; a headline) | The model's ability to STOP; preamble reflex | — (new) |
| R-CORRESPONDENCE | Correspondence (email, reply, message) | Register-matching, brevity, closers | — (new) |
| R-REASONING | Long-form reasoning (work a problem, structure an argument at length) | Restatement, "let me break this down," summary reflex | — (new) |
| R-ADVERSARIAL | Edge / adversarial (ambiguous ask, refusal-adjacent, trap premise) | Over-caution, both-sides-ing, disclaimer stacking | — (new) |

Deliberately dropped from the old set: the nonprofit-specific genres (donor
appeal, grant narrative, about-page, program page) — they are one narrow slice of
one register (promotional), and promotional prose is uniquely tic-dense, which is
exactly what over-weighted the first run.

## Governing principle (decided 2026-07-17)

**Think like a scientist whose work will be used later. The output — a refactored
`S0_backstop.md` that ships to clients — must be RELIABLE and USEFUL, not
economically produced.** This harvest runs only every few months. Token cost and
speed are near the bottom of the priority list. Priorities, in order:

1. **Reliability of the finding** — recurrence you can trust, provenance you can
   audit, results comparable across harvests.
2. **Coverage** — more registers, more briefs, so tics have somewhere to surface.
3. **Repeated samples** — see below.
4. *(distant last)* cost/speed.

Anywhere a tradeoff pits quality against economy, quality wins. Do not offer
"cheap smoke test" shortcuts for the real harvest; do not size down for calls.

## Resolved design decisions (2026-07-17)

1. **Substrate — no fixed substrate; mix by register need.** Each register gets
   whatever background context that register's test actually requires — and some
   (terse, adversarial, reasoning) need none at all. No single org, no shared
   fact sheet. (Harbor Bend added no value and made every output "about the same
   thing.")

2. **Exemplar layer carries forward — the IDEA moves; the exemplars get
   regenerated.** Mechanism unchanged: a task-matched Fable exemplar per brief,
   broad-craft-sourced from `~/makegood-harvest-sources/`, NO S0/F0/backstop/tic
   list in the generator context. New briefs ⇒ new exemplars ⇒ **we must run the
   Fable sessions to generate them** (the existing 12 only cover the retired
   Harbor Bend briefs). The exemplars weren't the problem; the briefs were.

3. **Stable CORE + growing POOL — NOT frozen-single-org.** A comparable core set
   lets a model be compared to itself across harvests; an explicitly expandable
   pool adds registers/briefs as coverage gaps are discovered. This is the
   discovery-instrument shape.

4. **Size — bias toward MORE.** More briefs, more registers, and **multiple
   arm-A samples per brief** (vary sampling only) so a tic must recur across
   SAMPLES, not just briefs, to count — that is how N=1 noise is separated from a
   real signature. The 8 registers are the starting point; more battery options
   is always good. Reliability of recurrence > sample economy.

## Downstream implications this creates (track, don't lose)

- **Multiple samples per brief** changes the harvest shape: `prepare` currently
  pairs one target output per brief with one exemplar. Multi-sample means either
  multiple pairs per brief or a sample-aware recurrence count. Tool change needed.
- **Clustering non-determinism** (observed: a re-run swung 13→10 candidate
  families) is unacceptable for a scientific instrument's headline numbers.
  Before this drives a real refactor: stabilize clustering (consensus over
  repeated runs, or report variance as an explicit range), not a single
  non-reproducible pass.
- **Provenance is a deliverable.** Every harvest REPORT.md records: battery
  version, per-exemplar hash, target model IDs+versions, samples-per-brief, judge
  model, clustering method + stability, and the resulting candidate → S0 entry
  decisions. A finding must be auditable and two harvests comparable.

## Not in this spec (deliberately)

- The actual brief text (write after the design is approved).
- The exemplar regeneration (follows brief approval; runs the Fable sessions).
- `run_judge.py` changes for multi-sample + clustering stability (real work,
  scoped once the battery shape is set).
