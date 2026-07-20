---
artifact: s0-backstop
artifact_name: S0 Revision Backstop — Current-Generation Prose Signature
version: 1.1.0
last_updated: 2026-07-20
spliced_into: "S0_natural_prose_standards.md between BACKSTOP:BEGIN / BACKSTOP:END markers (body only; this frontmatter is build metadata and is not spliced)"
provenance: >
  This module is a COMPILED ARTIFACT — bare thresholds and remedies only. Its body
  is spliced verbatim into the model's write-time context, so it carries no status
  tags, no per-harvest evidence, and no illustrative bad examples (describing a tic
  in-context primes it). All lifecycle state, measurement evidence, retire-track /
  metric-pending status, and worked examples live in harvest/BACKSTOP_TRACKER.md,
  which is compiled down to the ACTIVE rows here at release.
  v1.1.0 = first harvest-measured revision (2026-07-20; Opus 4.8 + Sonnet 5, both
  arms; reports/2026-07-opus48-sonnet5/). Admission = blind judge + human-baseline
  degree control (measure_density.py vs the sources/ corpus). Governance: enter on
  judge + degree-control corroboration; two consecutive clean harvests retire an
  entry; cap 25 entries / ~700 tokens — past the cap, change a gate in S0 core, not
  the list. See BACKSTOP_TRACKER.md for status and the harvest log.
---

**These entries are density thresholds, not bans.** Every pattern below is legitimate at a human writer's frequency; the machine signature is overuse. The signal lines describe the density at which the voice has slipped.

**Syntactic patterns** — the current generation's primary signature:

- **Em-dash overuse** — em-dashes past a human frequency, whether as a clause connector, an appositive introducing an elaboration, or a mid-sentence aside set off by a dash pair.
  Signal: more than ~2 per 250 words, consecutive sentences each carrying one, or a dash standing in for a colon or comma that would do the same work.
  Remedy: a colon or comma usually reads calmer; for an aside, commas (or parentheses, sparingly); for an elaboration, a full stop and a second sentence. Keep the few that earn the pause.

- **Chat-shape formatting** — the interface's native shape in a prose deliverable: bolded lead-in phrases announcing a paragraph, section headers breaking up a letter or essay, and bulleted or numbered lists carrying the argument.
  Signal: any header, bolded lead-in, or argument-carrying list in a letter, email, or essay; more than a quarter of paragraphs bolded or bulleted anywhere prose is the medium.
  Remedy: headers become paragraph transitions, bolded lead-ins become topic sentences, bullets become sentences with the connective reasoning restored.

- **Contrast-negation scaffolding** — a negated strawman standing in for the claim ("it's not X, it's Y"; "this isn't about A, it's about B"; "not just X").
  Signal: more than one instance per ~500 words.
  Remedy: state the positive claim directly.

- **Triadic rhythm** — a three-item parallel series as the default structure for description and emphasis.
  Signal: parallel triples in consecutive sentences, or more than one per paragraph.
  Remedy: one precise item beats three padded ones; vary series length.

- **Punch fragments** — sentence fragments deployed for emphasis.
  Signal: more than one per ~500 words.
  Remedy: attach the emphasis to a full sentence.

- **Signposting phrases** — a phrase announcing the point instead of making it ("Here's the thing"; "The reality is"; "Let's break this down"), including topic-sentence labels that name the argument move.
  Signal: any.
  Remedy: delete; a well-ordered point signposts itself.

- **Hedging** — qualifier stacking that softens a claim, whether as a closing gesture ("Ultimately," "At the end of the day") or mid-sentence hedges piled on a single assertion.
  Signal: any as a closing move; more than one qualifier on a single claim.
  Remedy: end on the substance; make the claim once, at the confidence the evidence supports.

**Vocabulary** — carried from the previous generation's signature; re-measured at each harvest:

- **No-practitioner words** — delve, foster, garner, holistic, synergy, elevate, harness, realm, myriad, unpack, tapestry, nestled, pivotal, cornerstone.
  Signal: any.
  Remedy: the practitioner's plain verb or noun.

- **Overused evaluators** — leverage, robust, navigate (figurative), journey (figurative), empower, transformative, seamless, cutting-edge, groundbreaking, game-changer, unlock, deep dive, crucial, vital, showcases, boasts, testament to, underscores, highlights, vibrant.
  Signal: flag and reconsider each use.
  Remedy: usually the Earn Every Claim gate — the word is standing in for missing evidence.

- **Bot-register phrases** — "I'd be happy to," "Great question!," "Thank you for sharing," empty "absolutely / definitely / certainly."
  Signal: any in a deliverable.
  Remedy: practitioners don't perform enthusiasm at documents.
