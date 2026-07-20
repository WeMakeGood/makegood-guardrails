# CLAUDE.md — makegood-guardrails

Orientation for Claude Code sessions in this repo. `README.md` explains the
*product* (the F0/S0/backstop modules, versioning, how consumers pull them) —
read it for that. This file covers **the active work and how to hand off between
sessions**, which the README does not.

## What this repo is (one line)

The source of truth for Make Good's guardrail modules. `modules/S0_backstop.md`
is the current-generation prose-signature list; it is meant to be maintained by
**measurement, not recollection** — via the *harvest* under `harvest/`.

`S0_backstop.md` is a **clean compiled artifact**: bare thresholds + remedies, no
status tags, no evidence, no illustrative bad examples. Its body splices verbatim
into the model's write-time context, so describing a tic there would *prime* it.
All lifecycle state (active / provisional / metric-pending / retire-track),
per-harvest evidence, and worked examples live in `harvest/BACKSTOP_TRACKER.md`,
which is compiled by hand down to the ACTIVE rows in the shipped module at each
release. Edit the tracker when reasoning; edit the backstop only to ship.

## The harvest — active redesign (as of 2026-07-17)

The harvest is a **model-stress instrument**: it discovers a new model's unknown
writing tics so `S0_backstop.md` can be refactored to catch them. It is NOT a
demonstration of Make Good's work or a nonprofit-writing exercise. (This point
was lost repeatedly; see memory `[[harvest-battery-purpose]]`.)

**How it works:** generate target-model output for each battery brief → compare
against a neutral human-grade *exemplar* of the same brief → an LLM **judge**
reads the pair and enumerates how the target's writing differs. Recurring
target-side differences are candidate tics.

**Primary detector = the LLM judge** (`harvest/scripts/run_judge.py`), because it
finds tics we can't name in advance — build for the future, not for today's known
tics. `tic_finder.py` (keyness diff) is backward-looking and secondary.

### Current state — what's built, what's in flight

- **`harvest/scripts/run_judge.py`** — the judge leg. `prepare` (blinded packets +
  sealed key) → `dispatch` (Anthropic API, optional) → `tally` (+ optional
  `--cluster-model` LLM clustering). Verified live end-to-end.
- **`harvest/battery/COVERAGE_SPEC.md`** — the battery design (APPROVED in
  principle): 8 registers, domain/register-organized, `[invented]`/`[real]`
  tagged, stable-core + growing-pool. Replaces the retired single-org battery.
- **`harvest/battery/core.jsonl`** — the 31 approved briefs (source of truth;
  JSONL, one record per brief). `BRIEFS_DRAFT.md` is the human-readable draft.
- **`sources/`** — third-party craft corpus (gitignored; rebuildable — see below).
- **`harvest/baseline/exemplars/<ID>/`** — the 31 human-grade exemplars (the
  quality bar), DONE 2026-07-18: Fable-authored, corpus-sourced, guardrail-free,
  `[real]`-fact-verified, promoted with per-exemplar `provenance.json`. Rebuild via
  `harvest/scripts/promote_exemplars.py`. Uncommitted as of that date.
- **NEXT: run_judge.py scaling** — multi-sample-per-brief in `prepare` +
  clustering-stability, then the first full judge run against these exemplars.

### Where the moving pieces live

| Thing | Path |
|---|---|
| Battery briefs (truth) | `harvest/battery/core.jsonl` |
| Battery design | `harvest/battery/COVERAGE_SPEC.md` |
| Exemplars (quality bar) | `harvest/baseline/exemplars/<ID>/exemplar.md` + `provenance.json` |
| Judge tool | `harvest/scripts/run_judge.py` |
| Promote exemplars | `harvest/scripts/promote_exemplars.py` |
| Craft corpus | `sources/` (gitignored) + rebuild scripts in `harvest/scripts/` |
| Raw craft sources (durable) | `~/makegood-harvest-sources/` (NOT in repo) |
| First harvest run artifacts | `reports/2026-07-first-run/` (gitignored) |
| Design decisions + lessons | auto-memory (loads each session) |

## Operating lessons (learned the hard way this project)

- **Verify against files, never assume from names/memory.** Grep counts, filenames,
  and doc labels have all been wrong here. Open the file.
- **The user's stated decision is the state of the tool.** When a file's label
  (e.g. "FROZEN", "approved") contradicts a decision the user made, the *file* is
  out of date — fix it; don't report the stale label back as if it's true.
- **Think like a scientist whose work ships.** The backstop reaches clients. Favor
  reliability, coverage, repeated samples, auditable provenance over token economy.
- **Temp scratchpads are not sources of record.** Rescue anything that matters into
  a durable home before relying on it.
- **Never recreate content from memory** — only from the file, git history, or a
  backup. Extraction, not reconstruction.

## Rebuilding `sources/` (gitignored — absent on a fresh clone)

```
python harvest/scripts/build_sources.py       # raw sources → sources/ + MANIFEST.json
python harvest/scripts/recover_failures.py    # recover rendered-DOM saves (Economist/NYT)
```
Raw sources: `~/makegood-harvest-sources/`. Needs `pypdf` (in `.venv`). Full detail
in `sources/README.md`.

## Handoff checklist

**Start of session** (resuming harvest work):
1. Read this file + `harvest/battery/COVERAGE_SPEC.md` for current design.
2. Check auto-memory notes (`[[harvest-battery-purpose]]`,
   `[[harvest-synthetic-reference-pivot]]`) — they hold decisions + lessons.
3. Confirm `sources/` exists (`ls sources/`); if missing, rebuild (above).
4. `git status` — know what's uncommitted before starting.

**End of session** (before stopping):
1. Record any new decision/lesson in auto-memory (not just this file).
2. If the state changed materially, update the "Current state" section above.
3. Leave the working tree clean or clearly note what's half-done and where.
4. Nothing important left only in the session scratchpad — durable homes only.
