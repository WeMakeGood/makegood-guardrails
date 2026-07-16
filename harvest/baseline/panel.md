# Identification Panel — Provenance & Measurements

Per-text provenance and length-normalized measurements for the identification
pass (`baseline/README.md §1`). **No source text is stored here** — only
citation, publication metadata, the prose-boundary note recording what was
measured, and the numbers `measure_density.py` produced. `metrics-baseline.json`
aggregates these into per-genre envelopes (median + spread); this file is the
audit trail behind those envelopes.

**Pass version:** `2026-07` (in progress — not yet enough texts per genre to
freeze an envelope). Measured with `measure_density.py` v0.1.0.

## Screening recap (all required per text)

Verifiable pre-2023 publication **OR** a documented stronger authorship
guarantee (closed corpus / deceased author / verifiable pre-2023 origin;
a publisher's stated LLM policy is *not* by itself sufficient) · human-authorship
confidence · genre fit · editorial excellence (would pass S0's gates).
Diversity cap: ~2 texts per author/organization per genre.

## Index

| ID | Citation | Author | Pub. date | Genre | Natural len | Date basis |
|---|---|---|---|---|---|---|
| ED-01 | *The Atlantic*, "The See-No-Evil Supreme Court" | Adam Serwer | 2026-07-14 | editorial | 1,471 w | authorship-guarantee (see note) |
| ED-02 | *The Atlantic*, "Generative AI Is an Engineering Disaster" | Alex Reisner | 2026-07-14 | editorial | 1,693 w | authorship-guarantee (see note) |
| FE-01 | *The Atlantic*, "How the Elite See Rome" | Cullen Murphy | 2026-08 (print) | feature | 4,312 w | authorship-guarantee (see note) |
| APP-01 | Camp Oochigeas mid-value direct mail appeal (SOFII) | John Lepp / Agents of Good; sig. Alex Robertson | 2018 (Spring) | appeal | 597 w | pre-2023 ✓ |

> **Diversity-cap note:** ED-01 + ED-02 put *The Atlantic* at the ~2-per-source
> cap for the **editorial** genre. Further editorial texts must come from other
> publications. The feature genre has one Atlantic text (FE-01) and one slot
> left before its cap.

## Detail

### ED-01 — Serwer, "The See-No-Evil Supreme Court"
- **Source:** *The Atlantic*, published 2026-07-14. Retrieved from the
  full-text syndication feed (feeds.feedburner.com/TheAtlantic), 2026-07-15.
- **Date basis:** Post-2023, admitted under the authorship-guarantee test —
  named *Atlantic* staff writer; individual byline; human-authorship confidence
  high. Not date-cleared; rationale recorded here per the relaxed-date rule.
- **Prose boundary:** body = article paragraphs only. Stripped: lead promo
  paragraph ("This article was featured in the One Story to Read Today
  newsletter. Sign up for it here."). No trailing scaffolding.
- **Measurements (v0.1.0):** words 1471 · sentences 55 · paragraphs 17 ·
  em_dash_rate 11.557 · contrast_negation_rate 0.0 · triadic_rate 5.45 ·
  signpost_rate 0.0 · hedge_closer_rate 0.0 · sentence_length_cv 0.4167 ·
  paragraph_uniformity 39.189 · fragment_rate n/a (Phase-2 stub).

### ED-02 — Reisner, "Generative AI Is an Engineering Disaster"
- **Source:** *The Atlantic*, published 2026-07-14 (part of the "AI Watchdog"
  series). Retrieved from the full-text feed, 2026-07-15.
- **Date basis:** Post-2023, admitted under the authorship-guarantee test —
  named *Atlantic* staff writer; **subject-matter AI critic, self-LLM-use
  judged unlikely.** This is an *inference, not verified* — recorded as such so
  a later re-derivation sees the assumption rather than inheriting it silently.
- **Prose boundary:** body = article paragraphs only. Stripped: lead editor's
  note ("Editor's note: This work is part of AI Watchdog..."). No trailing
  scaffolding.
- **Measurements (v0.1.0):** words 1693 · sentences 75 · paragraphs 22 ·
  em_dash_rate 5.316 · contrast_negation_rate 0.0 · triadic_rate 8.0 ·
  signpost_rate 0.0 · hedge_closer_rate 1.181 · sentence_length_cv 0.5565 ·
  paragraph_uniformity 38.137 · fragment_rate n/a (Phase-2 stub).

### FE-01 — Murphy, "How the Elite See Rome"
- **Source:** *The Atlantic*, August 2026 print edition (headline "The
  Cicerone"). Retrieved from the full-text feed, 2026-07-15.
- **Date basis:** Post-2023, admitted under the authorship-guarantee test —
  named contributing writer; individual byline; human-authorship confidence
  high. Not date-cleared; rationale recorded here.
- **Prose boundary:** body = article paragraphs only. Stripped: lead photo
  credit ("Photographs by Benedetta Ristori") and trailing print-edition
  tagline ("This article appears in the August 2026 print edition...").
- **Measurements (v0.1.0):** words 4312 · sentences 226 · paragraphs 40 ·
  em_dash_rate 13.219 · contrast_negation_rate 0.0 · triadic_rate 11.5 ·
  signpost_rate 0.0 · hedge_closer_rate 0.232 · sentence_length_cv 0.5105 ·
  paragraph_uniformity 38.014 · fragment_rate n/a (Phase-2 stub).

### APP-01 — Camp Oochigeas mid-value direct mail appeal
- **Source:** SOFII (Showcase of Fundraising Innovation and Inspiration),
  case study "Camp Oochigeas: Mid-value direct mail appeal"; letter first
  appeared Spring 2018. Retrieved via curl 2026-07-15; letter copy from the
  case study's letter-front-back PDF (image PDF, read verbatim).
  Archive: https://sofii.org/case-study/camp-oochigeas-mid-value-direct-mail-appeal
- **Date basis:** Verifiable pre-2023 publication (2018) — clears the
  contamination guard on the default proxy. Sector-shaped genre correctly
  sourced from another organization (not Make Good / not a client).
- **Prose boundary:** body = salutation through P.S. Stripped: dateline, the
  mailing address block, merge-field placeholders in the address, letterhead
  contact footer, and the signature name/title line ("Alex Robertson, CEO").
  Kept the sign-off words ("Yours, forever believing in magic,").
- **Measurements (v0.1.0):** words 597 · sentences 38 · paragraphs 15 ·
  em_dash_rate 6.7 · contrast_negation_rate 0.0 · triadic_rate 7.89 ·
  signpost_rate 0.0 · hedge_closer_rate 0.0 · sentence_length_cv 0.6422 ·
  paragraph_uniformity 30.226 · fragment_rate n/a (Phase-2 stub).

<!-- Next: other-publication editorial texts (Atlantic at cap for editorial);
     more features and appeals; then the remaining genres. Envelope math in
     metrics-baseline.json waits for ~15-25 texts/genre. -->
