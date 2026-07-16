# Reference Layer — Identification Panel & Synthetic Constructions

**Status: IDENTIFICATION PASS NOT YET RUN.** The first harvest cannot run its
counting stage until the panel is measured and `metrics-baseline.json` exists.

Two artifacts live here, with a strict one-way relationship:

```
real published writing  ──measure──▶  human envelopes  ──constrain/validate──▶  synthetic constructions
     (never stored)                (metrics-baseline.json)                    (the only stored passages)
```

**Constructions never set thresholds.** Thresholds derive only from the
measured panel. A synthetic passage that disagrees with the numbers is wrong
by definition and is regenerated. (HARVEST_PLAN.md, "Reference architecture.")

---

## 1. The identification panel (measure, never store)

Real, editorially excellent published writing that clears the contamination
guard (pre-2023 by default, or a documented stronger authorship guarantee —
see Panel rules), measured **in situ at natural length**. Every metric is length-normalized
(per-1,000-words and per-sentence rates), so an essay is measured at its
full natural length and a bio at its natural 90 words — no excerpting, no
fixed word-count bands, no anonymization, no stored text. Only derived
statistics and citations are retained.

**Why not a stored sample corpus** (rejected designs, HARVEST_PLAN.md):
fixed-length excerpts distort the density profiles being measured; any
hand-curated human set is too small to test against; the org's own archives
would calibrate the normalizer to one house style; and freely synthesized
"human" text carries the measuring generation's own densities.

### Panel rules

- **Sources:** published pre-2023 professional writing, genre-matched to the
  battery — celebrated appeal letters (e.g. SOFII's showcase), exemplary
  organizational copy, well-edited annual-report/foundation-letter prose,
  strongly edited editorial and feature writing, newspaper profile bios.
  Model proposes; operator vetoes/extends.
  <!-- TODO: collect Chris's suggested sources (writers, orgs, editors he trusts) before the first pass. -->
- **Screening (all required per text):** human-authorship confidence; genre
  fit; editorial excellence (the text would pass S0's gates — earned claims,
  point-first, medium's shape); **and the contamination guard below.**
- **Contamination guard (the date is a proxy, authorship is the target).** The
  panel exists to measure *human* density; the risk is model-inflected writing
  poisoning the pool. The pre-2023 date is a cheap, conservative proxy for "a
  human wrote this, not an LLM" — 2023 being when LLM-assisted writing went
  mainstream. A text clears the guard when **either** holds, recorded per text
  in `panel.md`:
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
- **Diversity cap:** no author or organization contributes more than ~2 texts.
- **Scale:** 15–25 texts per battery genre, ~150–250 total. Measuring is
  cheap; curation was the bottleneck, and there is none.
- **Outputs:**
  - `panel.md` — one row per text: citation, publication date, genre,
    natural length, per-metric stats, archive link where available, and the
    **prose-boundary note** (see Preprocessing) recording exactly what was
    measured vs. stripped.
  - `metrics-baseline.json` — per-genre, per-metric human envelopes
    (median + spread). This file is what thresholds ratio against.
- **Versioning:** an identification pass is a versioned event (recorded in
  `panel.md` and the harvest report's provenance block). Re-running with new
  texts or new metrics produces a new version — never a silent drift.

### Preprocessing — measure prose, not scaffolding

S0 governs *prose*, so the counters measure prose. Before measuring any text —
panel text or battery output — strip non-prose structural scaffolding that
would anchor the metrics on elements S0 does not address. **The identical rule
applies to panel texts and to battery outputs (HARVEST.md H3); if it doesn't,
the human envelope and the model measurements aren't comparable and every
threshold is invalid.**

- **Strip:** postal/mailing address blocks; dates and merge-field lines
  (`<Name>`, `<Salutation>`); letterhead and contact-info footers; email
  headers (To/From/Subject); bylines and datelines; credential/title lines
  under a signature (e.g. "Alex Robertson, CEO"); figure captions; pull-quotes;
  boilerplate (unsubscribe footers, legal disclaimers).
- **Keep:** the salutation and sign-off *words* — these are prose a human wrote
  ("Dear friend,", "Yours, forever believing in magic,") — and everything
  between them. Strip only the name/title/address scaffolding around them.
- **Headings:** keep body headings only for markdown/web-target genres, where
  the structural metrics (`header_density`, `bullet_share`, `bold_leadin_rate`)
  measure them on purpose. Strip headings for letter/email/bio genres, where a
  heading is scaffolding. (`measure_density.py` reads the raw text for the
  structural metrics and the stripped text for the prose metrics, so pass it
  the text with prose-appropriate headings intact and `--markdown` when the
  genre is a markdown/web target.)
- **Record the boundary.** Because the identification pass is a versioned,
  reproducible event, each `panel.md` row carries a short prose-boundary note —
  what was treated as body vs. stripped (e.g. "body = salutation→P.S.; stripped
  mailing block, dateline, signature name/title"). A second operator with the
  same source and the same note re-derives the same numbers. Phase 1 does this
  by agent-assisted judgment per text; a Phase 2 helper may standardize the
  common cases.

## 2. Synthetic constructions (`constructions/`)

Every stored passage in the reference layer is synthetic — constructed to
highlight elements identified in real samples without being a sample — and
**counter-validated against the envelope before use**.

| Directory | Built to be | Counters must | Role |
|---|---|---|---|
| `positive/` | Inside the human envelope | **NOT fire** | Specificity unit tests — a metric that fires here is mis-thresholded |
| `negative/` | Deliberately tic-maximal | **Fire** | Sensitivity unit tests — a metric that stays silent here is broken |
| `foils/` | Inside the envelope; genre- and length-matched to each battery output | Not fire | Judge pairing material (Component 5) |

**Foil rules:** generated by a **different model generation** than the
harvest's target model; validated by the counters; out-of-envelope foils are
discarded and regenerated. Foils are per-harvest artifacts — store them under
the harvest's report directory if preferred, or here with a harvest-id prefix.

**Known residual:** a foil's unmeasured dimensions carry its generator's
signature. Judge giveaways are reviewed with this in mind; a giveaway that
points at the foil rather than the target is itself useful — it becomes a
candidate metric for the next identification pass.
