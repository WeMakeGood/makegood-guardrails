# Reference Layer — Example Study, Synthetic Baseline, Differential Testing

**Status: panel collection in progress (see `panel.jsonl`); craft profiles, fingerprints, and exemplars NOT YET BUILT.** The first harvest cannot run until Layer 1's products exist and the exemplars are approved.

**Purpose (stated first — getting it wrong invalidated three designs):** this layer exists to make *currently unidentified* tics discoverable and testable in later models. It is not a known-tic scoreboard. Known-tic metrics live here only as a regression suite for existing backstop entries. (HARVEST_PLAN.md, "Reference architecture," fourth revision.)

```
real published writing ──study──▶ craft profiles + open fingerprints ──constrain──▶ task-matched exemplars
      (never stored)              (+ known-tic regression envelopes)                (the synthetic baseline)
                                                                                           │
model battery output ◀──────────────── open differential testing ◀────────────────────────┘
                        (statistical keyness diff + judge differential reading)
                                          │
                          candidates ──grounding check against real examples──▶ backstop
```

**Grounding invariant:** real examples are the arbiter. A discovered candidate enters `candidates.md` only after confirmation that the pattern does *not* occur at comparable rates in the collected excellent writing. Exemplars are the comparison instrument, never the authority for what counts as human.

---

## 1. The identification panel (real writing — studied, never stored)

Real, editorially excellent published writing that clears the contamination
guard, measured and studied **in situ at natural length** — no excerpting, no
fixed word-count bands, no stored text. Only derived data and citations are
retained. Ledger: `panel.jsonl` (source of truth), `panel.md` (readable view).

### Panel rules

- **Sources:** published pre-2023 professional writing, genre-matched to the
  battery — celebrated appeal letters (e.g. SOFII's showcase), exemplary
  organizational copy, well-edited annual-report/foundation-letter prose,
  strongly edited editorial and feature writing, newspaper profile bios.
  Model proposes; operator vetoes/extends.
  <!-- TODO: collect Chris's suggested sources (writers, orgs, editors he trusts) before the first pass completes. -->
- **Screening (all required per text):** human-authorship confidence; genre
  fit; editorial excellence (the text would pass S0's gates — earned claims,
  point-first, medium's shape); **and the contamination guard below.**
- **Contamination guard (the date is a proxy, authorship is the target).** The
  panel exists to characterize *human* writing; the risk is model-inflected
  writing poisoning the pool. The pre-2023 date is a cheap, conservative proxy
  for "a human wrote this, not an LLM" — 2023 being when LLM-assisted writing
  went mainstream. A text clears the guard when **either** holds, recorded per
  text in `panel.jsonl`:
  1. **Verifiable pre-2023 publication** (the default proxy), **or**
  2. **A documented stronger authorship guarantee** than the date provides —
     a closed corpus, a deceased author, a verifiable pre-2023 print origin
     read later, or a named individual author whose circumstances make LLM
     drafting implausible. Weaker per-author inferences (e.g. "writes
     critically about AI") are admissible **only when labeled as inference,
     not verified**, so a re-derivation sees the assumption rather than
     inheriting it silently.

  Two things are **not** sufficient on their own: a publisher's stated LLM
  policy (institutional, unverifiable per-article, doesn't bind freelancers or
  quoted text), and any institutional/anonymous copy without a byline
  (about pages, FAQs, marketing, reports) — for these the date proxy stays
  hard, because post-2023 they are the most heavily AI-assisted and carry no
  authorship guarantee to relax it. Relax the date only for a named human whose
  authorship is more certain than the date would establish.
- **Diversity cap (keyed on idiolect, not organization).** The contaminant the
  cap guards against is *one voice becoming "human normal"* — a single writer's
  sentence rhythm, em-dash habit, and tics dominating the reference. That is a
  **writer**-level property, so the cap is ~2 texts per **named writer** per
  genre. An organization is not a voice: one outlet's writers are many, and its
  house style is a far weaker contaminant than a single idiolect — so the org is
  a soft secondary note, not a hard limit. **Fallback:** when a text is unsigned
  (e.g. house-style news) or agency-driven (the voice is the agency, not one
  person), cap on the organization/agency instead, since that is then the
  idiolect-source.
- **Scale:** 15–25 texts per battery genre, ~150–250 total. Studying is cheap;
  curation was the bottleneck, and there is none.
- **Versioning:** an identification pass is a versioned event (recorded in
  `panel.jsonl` and the harvest report's provenance block). New texts, new
  craft-profile revisions, or new fingerprint features produce a new version —
  never a silent drift.

### Preprocessing — study prose, not scaffolding

S0 governs *prose*, so every measurement and study pass works on prose. Before
processing any text — panel text or battery output — strip non-prose
structural scaffolding. **The identical rule applies to panel texts and to
battery outputs (HARVEST.md H3); if it doesn't, the reference and the model
measurements aren't comparable.**

- **Strip:** postal/mailing address blocks; dates and merge-field lines
  (`<Name>`, `<Salutation>`); letterhead and contact-info footers; email
  headers (To/From/Subject); bylines and datelines; credential/title lines
  under a signature (e.g. "Alex Robertson, CEO"); figure captions; pull-quotes;
  boilerplate (unsubscribe footers, legal disclaimers).
- **Keep:** the salutation and sign-off *words* — these are prose a human wrote
  ("Dear friend,", "Yours, forever believing in magic,") — and everything
  between them. Strip only the name/title/address scaffolding around them.
- **Headings:** keep body headings only for markdown/web-target genres, where
  the structural measurements (`header_density`, `bullet_share`,
  `bold_leadin_rate`) study them on purpose. Strip headings for
  letter/email/bio genres, where a heading is scaffolding.
  (`measure_density.py` reads the raw text for the structural metrics and the
  stripped text for the prose metrics; `extract_body.py` implements the rule.)
- **Record the boundary.** Each `panel.jsonl` row carries a prose-boundary note
  — what was treated as body vs. stripped — so a second operator with the same
  source re-derives the same result.

## 2. What the panel yields (Layer 1 products)

| Product | Location | What it is | Role |
|---|---|---|---|
| **Craft profiles** | `craft/<genre>.md` | Extracted characterization of how excellent writing in the genre works — structure, movement, evidence use, rhythm, restraint, register | Constrain and validate exemplars; teach operators |
| **Open fingerprints** | `fingerprints/<genre>.json` | Aggregate distributions pooled per genre: token/n-gram frequency tables, all punctuation marks, sentence-length and paragraph-shape histograms. Aggregated across texts — no individual text reconstructible | The open reference for discovery diffs (4a) and grounding checks |
| **Known-tic regression envelopes** | `metrics-baseline.json` | Per-genre envelopes for the named Component-4b metrics | Confirm/retire existing backstop entries; place thresholds. **Never the discovery instrument** |

## 3. The synthetic baseline (`exemplars/`)

For each battery prompt, one or more **exemplar responses** — written to the
same context card and the same brief, embodying the genre's craft profile.
Task-matching is the property only synthesis provides: against a real text the
diff is confounded by topic; against a task-matched exemplar, every difference
is attributable to *how it's written*.

**Exemplar rules:**

- Generated by a **different model generation** than any harvest target.
- Checked against the genre's craft profile before proposal.
- **Human-approved once** (bounded review of ~16 short texts — review, not
  authoring), then reused across harvests. Layout: `exemplars/<prompt-id>/`.
- Regeneration (new battery prompt, revised craft profile, or quality feedback
  from a harvest's exemplar-side judge findings) is a **versioned re-approval
  event**, recorded in the harvest report's provenance block.

## 4. Regression-suite controls (`constructions/`)

Unit tests for the 4b known-tic metrics only — they play no role in discovery.

| Directory | Built to be | 4b metrics must | Role |
|---|---|---|---|
| `positive/` | Inside the human envelope | **NOT fire** | Specificity — a metric that fires here is mis-thresholded |
| `negative/` | Deliberately tic-maximal | **Fire** | Sensitivity — a metric that stays silent here is broken |
