# Synthetic Reference Set — Exemplars

The neutral, task-matched yardstick each battery brief's target output is judged
against. One Fable-authored exemplar per brief in
[`../../battery/core.jsonl`](../../battery/core.jsonl), **broad-craft-sourced**
from the human writing in `~/makegood-harvest-sources/` (surfaced through
`sources/` — real, general, cross-domain, not nonprofit) and generated with
**no S0 / F0 / backstop / tic list** in the generator context.

The exemplar is the **quality bar** — what the best available model produces when
disposed to write like the skilled humans in the craft corpus (deliberate word
choice over likely-next-token). It is not a null machine baseline whose own tics
subtract out, and it is not the authority on what is "human." The judge measures
how far a target model's writing falls short of this bar; a recurring target-side
shortfall is a candidate tic. See `[[harvest-battery-purpose]]` in memory.

## State (2026-07): rebuilt and promoted

Regenerated to match the replacement battery (8 registers, domain/register
coverage, `[invented]`/`[real]` tagged — see
[`../../battery/COVERAGE_SPEC.md`](../../battery/COVERAGE_SPEC.md)). The retired
single-org Harbor Bend exemplars (F01–F12) were deleted with the battery they
matched. All 31 current exemplars are promoted with per-exemplar
`provenance.json` (generator model, corpus manifest hash, brief prompt,
exemplar sha256, word count).

## The mechanism (unchanged)

Target and exemplar write the same brief, so a difference between them is
attributable to *how it's written*, not the topic. The exemplar generator
(Fable 5) is a different model generation than the targets under test — the
cross-generation guard that keeps the reference from mirroring the model being
measured.

## Generation method

Each exemplar was written by an isolated `claude-fable-5` subagent that first
**learned from** the whole `sources/` craft corpus (66 files, ~60K words), then
wrote the one brief in its own voice — no single-source mimicry, prose only,
honoring the brief's word target. `[real]` briefs were fact-verified before
promotion (flag-only, no prose edits); the two false-premise adversarial briefs
(AD01 Great Wall, AD04 10%-brain) correctly **reject** the myth rather than
asserting it. Reproduce via `harvest/scripts/promote_exemplars.py`.

**Generation instruction (`v2-learn-decisions`, recorded per exemplar in
`provenance.json`).** The generator was told to read the corpus for the
*decisions* behind the prose — how clauses are joined, what habits are
conspicuously absent — and to internalize that judgment, NOT to imitate voice.
This matters: an earlier "read this and write like this" framing (v1) suppressed
voice-visible tics but left sub-tone mechanics at the model's default — the v1
exemplars carried em-dashes at 2.94/250w against a human-corpus baseline of
0.67/250w. The v2 framing cut that to ~1.35/250w with equal-or-better prose, and
did so **without naming any tic** (which would have imported tic theory into the
yardstick and broken the no-guardrails-in-generator rule). See memory
`[[harvest-exemplar-learning-instruction]]`. Always measure a candidate tic
against the `sources/` human corpus before treating it as a finding.

## Provenance table

| ID | register | substrate | words | exemplar sha256 (short) |
|----|----------|-----------|------:|-------------------------|
| AN01 | analytic | invented | 514 | `32546a6180d1` |
| AN02 | analytic | invented | 460 | `2087be65b50a` |
| AN03 | analytic | invented | 405 | `f2889d7f5de9` |
| AN04 | analytic | real | 441 | `f68f2562d26c` |
| AN05 | analytic | real | 431 | `17290922be09` |
| TE01 | tech | invented | 270 | `8eb1492a96ac` |
| TE02 | tech | invented | 329 | `a0a34bfa0203` |
| TE03 | tech | real | 426 | `e95a90581955` |
| TE04 | tech | real | 345 | `6d046c199dcd` |
| NA01 | narrative | invented | 419 | `04c3f78f0ce2` |
| NA02 | narrative | invented | 298 | `bb8820c35747` |
| NA03 | narrative | invented | 440 | `2fa0be64905f` |
| NA04 | narrative | real | 417 | `28203bde85ee` |
| NA05 | narrative | real | 293 | `26a5453c4635` |
| NE01 | news | invented | 222 | `462171e4a224` |
| NE02 | news | invented | 240 | `9c6e95ceaa86` |
| NE03 | news | real | 295 | `7f881d0a97da` |
| TS01 | terse | invented | 15 | `c13c158de4c1` |
| TS02 | terse | invented | 34 | `f7f8dcba6991` |
| TS03 | terse | real | 29 | `700ea6daa906` |
| TS04 | terse | real | 23 | `ae625968d848` |
| CO01 | correspondence | invented | 58 | `eeb9791bc858` |
| CO02 | correspondence | invented | 107 | `a12bb25c1aee` |
| CO03 | correspondence | invented | 131 | `5fb7fd4d453f` |
| RE01 | reasoning | invented | 518 | `7fd9e9f8bec3` |
| RE02 | reasoning | invented | 509 | `729bed76ffae` |
| RE03 | reasoning | real | 460 | `f828d7c0e948` |
| AD01 | adversarial | real | 177 | `adf99dbda7ac` |
| AD02 | adversarial | invented | 722 | `0b1e7d4cd411` |
| AD03 | adversarial | invented | 237 | `3dad94c26639` |
| AD04 | adversarial | real | 200 | `8adf87d9130e` |

Full provenance for each exemplar is in `<ID>/provenance.json`. Word counts are
whitespace-token counts and are advisory except where a brief sets a hard cap
(TS01 ≤20, TS04 ≤25, TS02 ≤40) — those are within cap.
