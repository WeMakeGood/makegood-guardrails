# Backstop Entry Tracker

**This file never ships.** It is the note-taking device behind
`modules/S0_backstop.md`. The backstop itself is a *clean compiled artifact* —
bare thresholds and remedies, no status tags, no illustrative bad examples —
because its body is spliced verbatim into the model's write-time context by the
deploy pipeline (`build-deploy-bundles.py --resolve-guardrails`, in the
building-context-libraries skill). Any description or example of a bad pattern in
the shipped list *primes that pattern* in the context it governs. So all
lifecycle state, per-harvest evidence, and worked examples live here; only the
`ACTIVE` rows below, stripped to threshold + remedy, are hand-copied into the
shipped module at release.

## How admission works (the judge decides)

The harvest exists to find model tics we haven't named yet, and bend the context
back toward human — normalize, not ban. That job can only be done by a reader,
not a pre-coded metric: you cannot write a regex for a tic you have not named yet.
So:

1. **The judge is the arbiter.** It reads the model's samples against the human
   **ideal** (the exemplar for that brief) and names what the model *over-does* —
   including whether the pattern reads as a *generated habit imposed on the
   content* rather than a choice serving it. "Is this overused" is the judge's
   call, made against the ideal in front of it; it is not an arithmetic threshold.

2. **Recurrence is the over-style signal.** Multiple generated samples per brief
   exist for exactly this: compare the varied-but-similar model samples against
   the one human ideal and find what recurs. A pattern the model reaches for
   sample after sample, against the fixed ideal, is a *preference* — the model's
   hand showing — not a one-off choice. The two-level tally (≥ K samples of a
   brief, ≥ N briefs) is this test. Recurrence promotes a judge observation to a
   tic; a one-off is sampling noise.

3. **Metrics do NOT gate admission.** `measure_density.py` / the human baseline
   are **not** an arbiter and never veto a judge finding. Two legitimate uses only:
   (a) *research/reporting color* in the user-facing report ("em-dash ~3–4× human"
   is useful to show); (b) *harvest-to-harvest tracking* of a tic the judge has
   ALREADY named — a metric gets defined *from* the judge's finding, and its job is
   continuity: did this named tic get better or worse next harvest. A metric that
   contradicts the judge is context for a human to route the finding *back to the
   judge*, never a reason to demote it.

   > **Lesson (2026-07-20, Chris).** The first pass let a crude/missing density
   > metric override the judge: triadic + contrast-negation were "rejected as
   > craft" on a human-rate number, and signposting/hedging were parked in a
   > "metric-pending" limbo. But the judge had flagged all of them as generated
   > habits, repeatedly. The metric counted *presence* (humans triad plenty) and
   > missed what the judge saw — the *habit* shape (escalating tricolon closers,
   > negation-triple cadences). The judge was right; the metric flattened the
   > distinction. Never let a metric sideline a recurring judge finding again.

**Statuses**
- `ACTIVE` — the judge named it recurring across samples/briefs against the ideal;
  it ships.
- `PROVISIONAL` — seeded from recollection, not yet put to a judge run (or the
  register that would provoke it wasn't exercised); ships pending a judge verdict.
- `RETIRED` — a judge run found it no longer recurs; removed from the shipped list,
  kept here for history. (Retirement is a *judge* call across harvests, not a
  metric call.)

**Cap:** 25 shipped entries / ~700 tokens. Past the cap, the fix is a gate change
in S0 core, not a longer list.

---

## Syntactic entries

### em-dash overuse — `ACTIVE`
- **Shipped threshold:** > ~2 per 250 words, consecutive sentences each carrying
  one, or a dash standing in for a colon/comma.
- **Shipped remedy:** appositive dash → colon or comma; aside → commas or
  parentheses (sparingly); elaboration → a full stop and a second sentence.
- **Judge verdict 2026-07:** top target-side candidate in every model/arm; the
  leaking construction is the appositive/aside dash. Recurs across samples + briefs.
- **Leaking examples (do NOT ship):** `bottled dressing — thin, sweet, nothing
  like the emulsified anchovy punch` (sonnet B AN03); `squash — acorn, delicata, a
  heap of sugar pumpkins` (sonnet B NA02); `the high end — $34 for the short rib —`
  (sonnet B AN03).
- **Tracking metric (harvest-to-harvest):** em-dash /1000w vs `sources/`. 2026-07:
  human median 3.01; Opus 10.1→8.9 (A→B), Sonnet 13.2→12.8. **S0 barely bites
  Sonnet** — the live gap. (Number tracks the named tic; it did not admit it.)

### chat-shape formatting (headers / bold lead-ins / bulleted lists) — `ACTIVE`
- **Shipped threshold:** any header, bolded lead-in, or argument-carrying list in a
  letter/email/essay; > ¼ of paragraphs bolded/bulleted where prose is the medium.
- **Shipped remedy:** headers → paragraph transitions; bold lead-ins → topic
  sentences; bullets → sentences with the connective reasoning restored.
- **Judge verdict 2026-07:** recurs in arm A; S0 core's Medium's-Shape gate
  suppresses most (entry catches the residue).
- **Tracking metric:** header/bold/bullet rates vs `sources/` (human p90 = 0 in
  these registers). Arm A→B: Sonnet headers 58%→8% above human p90 — S0 working.

### triadic rhythm — `ACTIVE`
- **Shipped threshold:** parallel triples in consecutive sentences, or more than one
  per paragraph; escalating tricolon/quadcolon enumerations; tricolon punchy closer.
- **Shipped remedy:** one precise item beats three padded ones; vary series length.
- **Judge verdict 2026-07:** flagged as a **generated habit 35× vs 18 not**, across
  ~38 model/arm/brief slots. "escalating tricolon and quadcolon enumerations,"
  "tricolon punchy closer." **This is over-style, not the presence of triads.**
- **Note on the metric:** aggregate triadic_rate shows targets at 0.4–0.8× the
  human rate — because humans use *plain* triads freely while the model's tic is
  the *habit shape* (escalating/closer tricolons). The count can't see the shape;
  the judge can. Do NOT use the density number to reject this. (This is the
  2026-07 lesson above, concretely.)

### contrast-negation scaffolding — `ACTIVE`
- **Shipped threshold:** more than one instance per ~500 words; negation-triple
  cadence ("no X, no Y, no Z"); negation-reversal openings.
- **Shipped remedy:** state the positive claim directly.
- **Judge verdict 2026-07:** flagged as a generated habit **18× vs 1 not**
  (near-unanimous). "negation-triple cadence," "negation-reversal rhythmic pattern."
- **Note on the metric:** contrast_negation_rate is at the human rate — same
  presence-vs-habit blind spot as triadic. Judge decides; kept ACTIVE.

### signposting phrases — `ACTIVE`
- **Shipped threshold:** any ("Here's the thing," "The reality is," "Let's break
  this down"), including topic-sentence labels that name the argument move.
- **Shipped remedy:** delete; a well-ordered point signposts itself.
- **Judge verdict 2026-07:** recurs across the range (topic-sentence labels,
  argument-move openers). NOT parked — the judge's finding is the admission.
- **Tracking metric:** none yet. The signpost phrase-list metric fired 0% (too
  narrow). Build a topic-sentence-label detector to *track* it harvest-to-harvest;
  its absence does not affect this entry's ACTIVE status.

### hedging — `ACTIVE`
- **Shipped threshold:** any as a closing gesture; more than one qualifier stacked
  on a single claim.
- **Shipped remedy:** end on the substance; make the claim once, at the confidence
  the evidence supports.
- **Judge verdict 2026-07:** the judge saw heavy mid-sentence qualifier-stacking
  ("somewhat / arguably / tends to / in some sense"), broader than the seeded
  "closers" framing. Recurs. ACTIVE on the judge's finding.
- **Tracking metric:** the closer-only metric misses the stacking; build a
  qualifier-density metric to track it. Absence does not demote the entry.

### punch fragments — `PROVISIONAL`
- **Shipped threshold:** > 1 per ~500 words. **Remedy:** attach the emphasis to a
  full sentence.
- **Status why:** seeded from recollection; the 2026-07 judge did not surface it as
  a recurring target-side habit (nor rule it out). Kept pending a clearer judge
  verdict next harvest.

---

## Vocabulary entries — `PROVISIONAL`

Carried from the previous generation's signature; not yet put to a judge run
focused on lexis (the 2026-07 pass surfaced structural habits, not word choice).
Kept shipped pending a judge verdict.

- **no-practitioner words** — delve, foster, garner, holistic, synergy, elevate,
  harness, realm, myriad, unpack, tapestry, nestled, pivotal, cornerstone.
- **overused evaluators** — leverage, robust, navigate (fig.), journey (fig.),
  empower, transformative, seamless, cutting-edge, groundbreaking, game-changer,
  unlock, deep dive, crucial, vital, showcases, boasts, testament to, underscores,
  highlights, vibrant.
- **bot-register phrases** — "I'd be happy to," "Great question!," "Thank you for
  sharing," empty "absolutely / definitely / certainly."

---

## Harvest log

- **2026-07-20** — first harvest-measured revision → `s0-backstop` v1.1.0. Opus
  4.8 + Sonnet 5, both arms, 3 samples/brief, 372 outputs. Report:
  `reports/2026-07-opus48-sonnet5/`. Judge-as-arbiter established: em-dash
  re-specified + confirmed; headers/bullets added; triadic + contrast-negation
  ACTIVE (judge flagged as habits — corrected an initial metric-driven "reject");
  signposting + hedging ACTIVE (judge findings — corrected an initial
  "metric-pending" park). Metrics reframed as cross-harvest tracking only.
- **2026-07-15** — v1.0.0 seeded (recollection, not measurement).
