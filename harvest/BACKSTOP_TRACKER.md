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

**Statuses**
- `ACTIVE` — confirmed by measurement; appears in the shipped backstop.
- `PROVISIONAL` — seeded (recollection) or not yet measurable; shipped, but
  awaiting confirmation. (No metric to confirm/reject it yet.)
- `METRIC-PENDING` — the judge sees it recurring, but no arithmetic metric
  quantifies its degree, so it can't be calibrated. Shipped as a terse entry;
  the real work is building the metric.
- `RETIRE-TRACK (n of 2)` — measured at/below the human rate. Still shipped (the
  two-harvest retirement rule), but removed after a second consecutive clean
  harvest.
- `RETIRED` — removed from the shipped list; kept here for history.

**Governance (from S0_backstop provenance):** admission this generation = blind
judge (primary) + human-baseline **degree** control (`measure_density.py` vs the
`sources/` corpus). A pattern is a tic only where the target's *rate* exceeds real
human writing, not where it merely appears. tic_finder is not in the admission
logic. Cap: 25 shipped entries / ~700 tokens — past the cap, change a gate in S0
core, not the list.

---

## Syntactic entries

### em-dash overuse — `ACTIVE`
- **Shipped threshold:** > ~2 per 250 words, consecutive sentences each carrying
  one, or a dash standing in for a colon/comma.
- **Shipped remedy:** appositive dash → colon or comma; aside → commas or
  parentheses (sparingly); elaboration → a full stop and a second sentence.
- **Leaking construction (do NOT put in the shipped list):** appositive/aside
  dash. Examples from the 2026-07 run:
  - `bottled dressing — thin, sweet, nothing like the emulsified anchovy punch` (sonnet B AN03)
  - `the high end for the neighborhood — $34 for the short rib — and that's hard to justify` (sonnet B AN03)
  - `squash — acorn, delicata, a heap of sugar pumpkins` (sonnet B NA02)
- **Evidence 2026-07:** human median 3.01/1000w (p90 7.47). Opus 10.1 (3.4×, 69% >
  p90) → arm B 8.9 (57%). Sonnet 13.2 (4.4×, 75%) → arm B 12.8 (75%). Judge top
  candidate every model/arm. **S0 barely bites Sonnet** — the live gap.
- **History:** v1.0.0 seeded as "em-dash chaining"; v1.1.0 re-specified to the
  appositive/aside construction + confirmed by degree.

### chat-shape formatting (headers / bold lead-ins / bulleted lists) — `ACTIVE`
- **Shipped threshold:** any header, bolded lead-in, or argument-carrying bullet
  list in a letter/email/essay; > ¼ of paragraphs bolded/bulleted where prose is
  the medium.
- **Shipped remedy:** headers → paragraph transitions; bold lead-ins → topic
  sentences; bullets → sentences with the connective reasoning restored.
- **Evidence 2026-07:** humans p90 = 0 in these registers. Arm A above p90:
  headers Opus 56% / Sonnet 58%; bold Opus 37% / Sonnet 46%; bullets Opus 28% /
  Sonnet 30%. **S0 core's Medium's-Shape gate suppresses most** (Sonnet headers
  58%→8%). Entry catches the residue (Opus headers still 39% in arm B).
- **History:** v1.0.0 "bolded lead-ins"; v1.1.0 broadened to add headers + bullets
  (both measured leaks) and renamed.

### punch fragments — `PROVISIONAL`
- **Shipped threshold:** > 1 per ~500 words. **Remedy:** attach the emphasis to a
  full sentence.
- **Status why:** `fragment_rate` is stubbed in `measure_density.py`; this pass
  could neither confirm nor reject. Build the parser-backed metric, then re-test.

### signposting phrases — `METRIC-PENDING`
- **Shipped threshold:** any. **Remedy:** delete; a well-ordered point signposts
  itself.
- **Status why:** the judge saw signposting (incl. topic-sentence labels like
  "The first reason is", "It's worth noting that") recurring across the range, but
  the signpost phrase-list metric fired 0% — too narrow. Widen the metric (add
  topic-sentence-label detection) before the next harvest.

### hedging closers — `METRIC-PENDING`
- **Shipped threshold:** any as a closing move. **Remedy:** end on the substance.
- **Status why:** the closer-only metric showed 0–4% > p90, BUT the judge saw
  heavy mid-sentence qualifier-STACKING ("somewhat / arguably / tends to / in some
  sense"), which this metric doesn't capture. Build a qualifier-density metric;
  the broad hedging pattern is real and uncalibrated.

### triadic rhythm — `RETIRE-TRACK (1 of 2)`
- **Evidence 2026-07:** target 0.4–0.8× the human rate (human median 7.6/1000w).
  Skilled humans use triads *more* than these models. No leakage.
- **Action:** kept shipped per the two-harvest rule; a second clean harvest
  retires it. Reject as a target tic for this generation.

### contrast-negation scaffolding — `RETIRE-TRACK (1 of 2)`
- **Evidence 2026-07:** target 2–5% > human p90 — at the human rate. No leakage.
- **Action:** kept shipped per the two-harvest rule; a second clean harvest
  retires it.

---

## Vocabulary entries — `PROVISIONAL` (unmeasured)

Carried from the previous generation's signature. The 2026-07 harvest measured
*structure*, not the word lists, so these are neither confirmed nor rejected.
Build a lexical-frequency measurement (target vs `sources/`) before the next
harvest.

- **no-practitioner words** — delve, foster, garner, holistic, synergy, elevate,
  harness, realm, myriad, unpack, tapestry, nestled, pivotal, cornerstone.
- **overused evaluators** — leverage, robust, navigate (fig.), journey (fig.),
  empower, transformative, seamless, cutting-edge, groundbreaking, game-changer,
  unlock, deep dive, crucial, vital, showcases, boasts, testament to, underscores,
  highlights, vibrant.
- **bot-register phrases** — "I'd be happy to," "Great question!," "Thank you for
  sharing," empty "absolutely / definitely / certainly." *(v1.0.0 flagged as a
  retirement candidate — rare in current document output; still unmeasured.)*

---

## Harvest log

- **2026-07-20** — first harvest-measured revision → `s0-backstop` v1.1.0. Opus
  4.8 + Sonnet 5, both arms, 3 samples/brief, 372 outputs. Report:
  `reports/2026-07-opus48-sonnet5/`. Em-dash re-specified + confirmed;
  headers/bullets added; triadic + contrast-negation → retire-track; signposting +
  hedging → metric-pending.
- **2026-07-15** — v1.0.0 seeded (recollection, not measurement).
