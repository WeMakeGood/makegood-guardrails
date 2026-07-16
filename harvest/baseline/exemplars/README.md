# Synthetic Reference Set — Exemplars (frozen)

The **repeatable baseline** the tic-finder diffs target-model output against. One
exemplar per frozen battery-core brief (F01–F12), each written to the same
Harbor Bend context card and the same brief as the battery uses — so a diff
between a target's output and its exemplar is attributable to *how it's
written*, not to topic.

**Why synthetic, not collected human text:** economical (generated, not
hunted/screened), repeatable (a fixed yardstick every model is diffed against
→ results comparable across models over time), and task-matched (same brief as
the battery). This is the "exemplar" layer of the v4 reference design, promoted
to the primary baseline. (HARVEST_PLAN.md reference architecture; baseline/README.md §3.)

## Provenance (v1 — frozen 2026-07-16)

- **Generator:** Fable 5 (`claude-fable-5`), via isolated subagents, one per
  brief. Chosen as a **different model generation** than the Opus/Sonnet targets
  most harvests will test — the cross-generation guard that keeps the reference
  from mirroring the model under test.
- **No guardrails in the generator context:** exemplars were generated with **no
  S0, no F0, no backstop, no tic list.** This is deliberate and load-bearing —
  sourcing the reference with our own tic theory would re-close the discovery
  loop (the reference could then only reflect tics we already named). The
  reference must be neutral to what counts as a tic.
- **Craft-sourced (the "v2" method, chosen over blind generation):** each
  generator first *studied* the 14 measured human panel texts (~19K words,
  editorial/feature/appeal, many writers/disciplines) for craft — structure,
  movement, evidence use, rhythm, restraint — then wrote in its own voice,
  instructed **not** to imitate any single writer's idiolect. Craft in,
  guardrails out, no single-voice mimicry.
- **Human-approved once** (Chris, 2026-07-16), then frozen. Reused across
  harvests. Regeneration (new brief, new craft input, or exemplar-quality
  feedback from a harvest's judge findings) is a **versioned re-approval event**
  recorded here and in the harvest report's provenance block.

## Known residual (recorded, not fixed)

Craft-sourcing made the prose better *and* more stylistically assertive (short
punchy paragraphs, aphoristic closers, an occasional P.S.) — moves that are
craft when a human does them once but that an AI also overuses. Consequence: a
target sharing those assertive moves may look *similar* to the reference, so the
**statistical diff (4a) may under-flag them**. Mitigation: the blind-judge leg
(H4) never sees the reference and catches overuse independently, and the
grounding check confirms candidates against real human writing before admission.
The reference is a comparison instrument, never the authority on what is human.

## Layout

`exemplars/<prompt-id>/exemplar.md` — one per F01–F12. Rotating-pool briefs
(R01+) get exemplars when first selected for a harvest.

| ID | Brief | Words |
|---|---|---|
| F01 | About page | 366 |
| F02 | Case study | 617 |
| F03 | Donor appeal | 418 |
| F04 | Newsletter lead | 349 |
| F05 | Blog opening | 312 |
| F06 | Comparison (board) | 417 |
| F07 | Executive summary | 309 |
| F08 | Program page | 310 |
| F09 | LinkedIn post | 146 |
| F10 | Bio | 150 |
| F11 | FAQ | 316 |
| F12 | Partner email | 262 |
