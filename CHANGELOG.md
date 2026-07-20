# Changelog

Per-module history. Each module is versioned independently with its own git tags
(`f0-vX.Y.Z`, `s0-vX.Y.Z`). Entries are grouped by module.

---

## F0 — Agent Behavioral Standards

### [2.0.0] — 2026-07-15

Recalibration for the current model generation, driven by the 2026-07-15
guardrails audit: literal instruction-following in Opus 4.6+ / Sonnet 4.6+
models made unconditional gates overtrigger (ritualized cross-domain parallels
and second-order sections on routine work) and made fixed example text
reproduce verbatim.

- **Arming conditions added to Gates 3, 4, and 5** — generalizing the
  arms-only-when pattern Gate 6 already used. Gate 3 arms when the task
  requires choosing an analysis direction; Gate 4 when a conclusion will be
  acted on; Gate 5 when a conclusion or method is offered beyond its instance.
  **Major bump per this repo's convention: gate triggers narrowed** — the gates
  no longer fire on fixed-framing, low-consequence, or instance-scoped work
  where they previously fired unconditionally.
- **New section "Where the Gates Run"** — gates execute in reasoning; outputs
  carry their products (citations, legible epistemic status, non-trivial
  second-order costs, scope limits), never their ceremony. Gate names and
  process headers never render in deliverables.
- **Gate 1's verbatim refusal template replaced** with a phrased-as-needed
  requirement. The fixed string was example-anchoring — the failure F0's own
  Example Anchoring section warns against — and literal models reproduced it
  word-for-word in registers where it read robotic.

### [1.3.0] — 2026-06-16

Added **Process Gate 6: New or Already Held** — guards against the agent
presenting as a fresh discovery something the provided context already holds
(silent rediscovery). Orthogonal to Gate 2: Gate 2 marks a claim's *origin*
(sourced/inferred/generated); Gate 6 marks whether it is *new relative to what
is already in hand*. The gate arms only when novelty or authorship is being
claimed and stays silent during faithful compilation/extraction — so it fires
for synthesis work without mis-firing on dossier/report/import skills where
restating context is the task.

Minor bump: additive gate, no change to the existing five. Origin: the failure
mode was surfaced by Glen's Gap Analysis Method; convergent with S0's existing
"Earn Every Claim" gate (same evidence-or-cut shape applied to hype rather than
false-novelty).

Gates at this version:
1. Source Before Statement
2. Mark the Move
3. Reframe Before Committing
4. Second-Order Check
5. Generalization Check
6. New or Already Held

### [1.2.0] — 2026-04-19 — baseline

Initial import into `makegood-guardrails`, establishing the source of truth.
Content is the canonical version that governed the live context library's agents
as of this date — five process gates plus the analytical-depth, uncertainty,
error-correction, and professional-challenge sections. No behavioral change from
the pre-import state; this release captures current behavior so later changes
have a versioned baseline to diff against.

Gates at this version:
1. Source Before Statement
2. Mark the Move
3. Reframe Before Committing
4. Second-Order Check
5. Generalization Check

> Process Gate 6 (New or Already Held) is finalized and approved but not yet
> applied. It lands as F0 1.3.0 (minor — additive gate) once this baseline is
> tagged and consumers can pin against it.

---

## S0 — Natural Prose Standards

### [2.0.1] — 2026-07-15

Sector-neutrality patch — wording only, no change to what any gate makes an
agent do. The guardrails are the sector-neutral floor for every library
(nonprofit and mission-driven for-profit clients alike); sector and
organizational identity belong in each library's own modules. Removed the two
"donor letter" examples the 2.0.0 medium's-shape gate introduced (now "a
letter" / "a letter over someone's signature") and neutralized "the nonprofit"
in the synonym-cycling example ("the institution"). Audit note: F0 and the
s0-backstop artifact were checked in the same pass and are sector-clean.
Sector flavor lives deliberately in the harvest instruments (battery, baseline
corpus) as register calibration — tics are genre-driven, so the harvested list
stays sector-agnostic.

### [2.0.0] — 2026-07-15

The core/backstop split plus two gate changes, driven by the 2026-07-15
guardrails audit. Design rationale and the harvest system the split enables:
`HARVEST_PLAN.md`.

- **Revision Backstop externalized** to the independently versioned
  `s0-backstop` artifact (see below), spliced between `BACKSTOP:BEGIN/END`
  markers at vendor time by `build-deploy-bundles.py --resolve-guardrails`.
  The gates are durable prose philosophy; the tic list is volatile (it tracks
  the model landscape, not the philosophy) and now versions on its own cadence.
  **Major bump: vendoring S0 2.0.0 without splice-aware tooling yields a
  module with an empty backstop.** Requires the corresponding
  `building-context-libraries` skill release and lock-format addition.
- **Practitioner Voice gate gains voice-profile precedence routing** — a
  loaded voice profile *is* the practitioner (no parallel generic inference);
  the profile wins on voice, and never against the claims gates. Fixes an
  undefined-precedence gap: agents ran generic practitioner inference alongside
  loaded founder voice profiles with nothing saying which won.
- **New fourth gate: Write in the Medium's Shape** — catches chat-native
  formatting (headers-per-paragraph, bolded lead-ins, bullet-carried arguments)
  leaking into prose deliverables. Targets the current generation's most
  visible deliverable-level failure, which is structural rather than lexical.

### [1.0.0] — 2026-03-10 — baseline

Initial import into `makegood-guardrails`. Content is the canonical version
governing external-facing content in the live context library as of this date:
three process gates (Write From a Practitioner's Voice, Earn Every Claim, Start
From the Point) plus the writing-discipline and revision-backstop sections.
Conditional module — loaded by external-facing agents only.

---

## s0-backstop — S0 Revision Backstop (current-generation prose signature)

### [1.1.0] — 2026-07-20 — first harvest-measured revision

First revision driven by measurement rather than recollection. Source: the first
real judge pass (Opus 4.8 + Sonnet 5, both arms, 3 samples/brief, 372 outputs;
`reports/2026-07-opus48-sonnet5/`). Admission this generation = the blind judge
(primary) + the human-baseline **degree** control (`measure_density.py` vs the
`sources/` human corpus). tic_finder is **not** in the admission logic
(backward-looking; reviewer steer 2026-07-20).

**Module is now a clean compiled artifact.** The backstop body splices verbatim
into the model's write-time context, so it carries no status tags, no per-harvest
evidence, and no illustrative bad examples (describing a tic in-context primes it).
All lifecycle state and evidence moved to `harvest/BACKSTOP_TRACKER.md`, which
compiles down to the ACTIVE rows shipped here.

Changes (status/evidence tracked in `BACKSTOP_TRACKER.md`):
- **Em-dash chaining → em-dash overuse.** Re-specified to the construction that
  actually leaks — the appositive/aside dash — and confirmed at **3–4× the human
  rate** (57–75% of outputs above the human p90); S0's prior remedy did not bite
  on Sonnet. Remedy sharpened per construction. Stated as degree, not presence
  (humans and the exemplars use dashes too).
- **Bolded lead-ins → chat-shape formatting.** Broadened to add the two other
  measured formatting leaks — markdown **headers** and argument-carrying **bulleted
  lists** (human p90 = 0 in prose registers). S0 core's Medium's-Shape gate already
  suppresses most; the entry catches the residue.
- **Triadic rhythm** and **contrast-negation scaffolding** → **RETIRE-TRACK.**
  Measured at/below the human rate (triadic at 0.4–0.8×; humans use triads *more*).
  No leakage, 1 of 2 harvests; a second clean harvest retires them per the
  two-harvest rule.
- **Signposting** and **hedging closers** → **METRIC-PENDING.** The judge sees both
  recurring (hedging as mid-sentence qualifier-stacking; signposting as
  topic-sentence labels), but the current arithmetic metrics can't quantify the
  degree, so they can't be calibrated this pass. Confirmed patterns, uncalibrated;
  new metrics needed before the next harvest.
- **Punch fragments** kept provisional — `fragment_rate` is still stubbed in
  `measure_density.py`, so this pass could neither confirm nor reject it.
- **Vocabulary lists** carried **unmeasured** — this harvest measured structure,
  not the word lists.

Entry count 10 (7 syntactic incl. 2 retire-track + 3 vocabulary), well under the
25-entry cap. Report + candidate table: `reports/2026-07-opus48-sonnet5/`
(`REPORT.md`, `candidates.md`).

### [1.0.0] — 2026-07-15 — seeded

New artifact created by the S0 2.0.0 split. Spliced into vendored S0 between
`BACKSTOP:BEGIN/END` markers; versioned independently (`s0-backstop-vX.Y.Z`)
so the tic list can track the model landscape without re-versioning the gates.

Seed content — **recollection, not measurement**: the S0 1.0.0 vocabulary
lists (carried; bot-register phrases flagged as a retirement candidate) plus
seven syntactic entries from the 2026-07-15 audit (contrast-negation
scaffolding, em-dash chaining, triadic rhythm, bolded lead-ins, punch
fragments, signposting phrases, hedging closers). All entries are provisional
until the first harvest confirms, corrects, or retires them — see
`HARVEST_PLAN.md` for the measurement protocol, admission rule (≥2-of-3
detectors), retirement rule (two clean harvests), and the 25-entry/~700-token
cap.

Versioning semantics for this artifact: patch = wording/remedy clarification;
minor = entries added or retired by a harvest (the normal per-harvest bump);
major = entry-format change or threshold-philosophy change.
