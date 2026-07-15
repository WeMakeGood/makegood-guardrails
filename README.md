# makegood-guardrails

The single source of truth for Make Good's behavioral guardrail modules — the always-load standards that govern how every agent in every Make Good context library reasons and writes.

This repo holds two modules and one spliced artifact:

- **`modules/F0_agent_behavioral_standards.md`** — process gates governing how *any* agent produces output (sourcing, marking inference vs. analysis, reframing, second-order checks, generalization). Loaded by every agent in every library.
- **`modules/S0_natural_prose_standards.md`** — writing standards for external-facing content (practitioner voice, earned claims, leading with the point, the medium's shape). Loaded by agents that produce external content. The durable *core*: gates and discipline only.
- **`modules/S0_backstop.md`** — the current-generation prose-signature list (tics, density thresholds, remedies). Independently versioned because it tracks the *model landscape* rather than the prose philosophy; spliced into the vendored S0 between `BACKSTOP:BEGIN/END` markers at resolve time, so consumers still receive a single S0 file. Maintained by measurement, not recollection — see `HARVEST_PLAN.md` for the harvest protocol that proposes each update (human-reviewed before release).

## Why this repo exists

These modules were previously copied by hand into every library and skill that used them, with no source of truth. They drifted: at one point F0 existed in three distinct on-disk versions and S0 in two, and the copy governing live agents differed from the copy seeded into new libraries. This repo makes the modules a **versioned dependency** instead of a copied file, so a change is made once and adopted deliberately rather than propagated by hand.

## How consumers use it

Consumers (context libraries, the `building-context-libraries` skill) **pull a pinned version**; this repo never pushes to a list of consumers. That direction is deliberate — a pushed list of destinations goes stale and silently skips consumers. Each consumer declares the version it wants and vendors that version into itself.

- A built **context library** records its pinned guardrail versions in a `guardrails.lock` at its root, vendors the locked module content into `modules/`, and builds its agent bundles from the vendored copy. Pinned by default; upgrading is a deliberate, committed act in the library's own repo.
- The **`building-context-libraries` skill** seeds a new library's `guardrails.lock` at a default version and pulls this repo's modules into its `templates/guardrails/` at release-build time.

See `IMPLEMENTATION_PLAN.md` for the full design, the per-library lock format, deploy-script integration, and the migration sequence.

## Versioning

Each module is versioned independently with its own semver git tags (`f0-vX.Y.Z`, `s0-vX.Y.Z`, `s0-backstop-vX.Y.Z`). They change on different cadences — the S0 core rarely, F0 occasionally, the backstop at every harvest — so a stable artifact is not re-versioned every time another moves.

- **Patch** — wording clarification, no change to what a gate makes an agent do.
- **Minor** — a gate added or extended additively.
- **Major** — a gate removed or changed such that an adopting consumer's agents would behave incompatibly with before.

The authoritative version is the git tag; the `version:` field in each module's frontmatter mirrors it for legibility inside a vendored copy.

See `CHANGELOG.md` for the per-module history.
