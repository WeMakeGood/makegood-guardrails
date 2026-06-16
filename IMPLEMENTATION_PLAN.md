# Guardrails Versioning — Implementation Plan

*Drafted 2026-06-16. Status: proposal for review (Chris, Glen). Nothing in this plan has been built.*

---

## The problem this solves

The behavioral guardrail modules — `F0_agent_behavioral_standards` and `S0_natural_prose_standards` — govern how every agent in every Make Good context library reasons and writes. They currently exist as **nine independent on-disk copies** with no source of truth, and have **already drifted**: F0 exists in three distinct versions, S0 in two. The copy that governs the live agents (dated `2026-04-19`) differs from the copy the `building-context-libraries` skill seeds into new libraries (which carries an unfilled `YYYY-MM-DD` placeholder date).

"Canonical" today means "whichever copy was edited last." There is no mechanism to:

1. Make a behavioral change once and propagate it deliberately, or
2. Hold a client library stable while another adopts a change, or
3. Record, in a client's own repo, which guardrail version their agents run on.

The triggering case: Glen's Gap Analysis Method surfaced a new behavioral gate (F0 "Process Gate 6 — New or Already Held"). Integrating it across all existing client libraries, each used differently, is impossible to do safely without a versioning system. This plan builds that system.

---

## Design principles (settled)

- **Single source, versioned.** A dedicated `makegood-guardrails` repository is the only place F0/S0 are authored. It publishes semver-tagged releases.
- **Consumers pull; the source never enumerates consumers.** This is the specific fix for the failure that has bitten us before — a push-based sync script whose destination list goes stale and silently skips a consumer. No file anywhere lists "all the places guardrails go." Each library declares the version it wants.
- **Two facts, not one** (the npm `package.json`/`package-lock.json` split). Declared *intent* (a version or range) and resolved *actuality* (the exact version built from) are separate recorded facts. Builds run from the resolved fact.
- **Pinned by default; upgrade is deliberate.** A built library pins its guardrail versions and does not move. Upgrading is an explicit, committed act in the client's own repo — never a side effect of redeploying.
- **Per-library, not per-agent.** One guardrail version governs all agents in a library. Per-agent versions would let agents in a single library disagree on F0 — the within-corpus contradiction the guardrails exist to prevent.
- **Reproducible and offline.** The locked guardrail content is vendored into the library repo (like `node_modules`), so a library can be rebuilt years later even if `makegood-guardrails` has changed or disappeared. The lock records provenance; the vendored copy guarantees the build.
- **The existing build mechanism is sound and is not reworked.** `build-deploy-bundles.py` resolves `@`-include directives relative to repo root and already has `--check` (drift detection) and `--all-inclusive` modes. The version layer sits *above* it: a resolve-and-materialize step that runs before the unchanged bundle build.

---

## Architecture

```
makegood-guardrails  (new repo — single source of truth)
  modules/
    F0_agent_behavioral_standards.md   (semver via git tags)
    S0_natural_prose_standards.md
  CHANGELOG.md                          (per-module behavioral change log)
  tags: f0-v1.3.0, s0-v1.1.0, ...       (or a unified guardrails-vX.Y.Z)
        │
        │  pinned version, pulled + vendored at lock time
        ▼
client context library  (e.g. library/context-library)
  guardrails.lock                        (NEW — declared + resolved per library)
  modules/foundation/F0_...md            (VENDORED from lock, marked generated)
  modules/shared/S0_...md                (VENDORED from lock, marked generated)
  agents/*.md                            (UNCHANGED — @modules/foundation/F0... )
  deploy/agents/*.md                     (compiled bundles, unchanged mechanism)
        ▲
        │  the skill SEEDS a new library's guardrails.lock at a default version
        │
building-context-libraries skill
  templates/guardrails/                  (becomes a pinned pull, fixes placeholder drift)
        │  vendored via skills.yaml tag-pin + sync_skills.py (UNCHANGED path)
        ▼
makegood-skills / makegood-skills-internal plugins
```

Every arrow is a *pull at a pinned version*. No arrow is a push to an enumerated destination list. That property is what makes the system immune to the stale-destinations failure.

---

## Component 1 — The `makegood-guardrails` repository

**Contents.** F0 and S0 (and any future shared guardrail modules), each with real semver in frontmatter, plus a `CHANGELOG.md` recording what behavioral change each version represents.

**Versioning convention** (F0/S0 do not have semver today — only `last_updated`):

- **Patch** (1.3.0 → 1.3.1): wording clarification, typo, no change to what the gate makes an agent do.
- **Minor** (1.2.0 → 1.3.0): a gate added, or a gate's behavior extended, in a way that is additive. *Gate 6 is a minor bump* — it adds a behavioral requirement without removing or contradicting an existing one.
- **Major** (1.x → 2.0.0): a gate removed or changed such that an adopting library's agents would behave incompatibly with how they behaved before (e.g., a gate's trigger narrowed so it no longer fires where it used to, changing existing output).

**Frontmatter gains a `version:` field.** Today F0 has `last_updated: 2026-04-19` and nothing else; S0 the same. Add `version: 1.3.0`. Keep `last_updated` for human reference. The git tag is the authoritative version; the frontmatter field mirrors it for legibility inside a vendored copy.

**Seed content for v1.x.** The `2026-04-19` F0 from `library/context-library/modules/foundation/` is the most-current canonical content and is what the repo is initialized from — *not* the placeholder-dated vendored copies. S0 similarly from the live library copy.

---

## Component 2 — The `guardrails.lock` manifest (per library)

A small file at each library's root. Holds both facts:

```yaml
# guardrails.lock — governs all agents in this library.
# Managed by build-deploy-bundles.py. Do not hand-edit the resolved block.
source: WeMakeGood/makegood-guardrails

declared:           # intent — optional range, human-authored
  F0: "1.3.0"       # exact pin (default), or a range like "^1.x" if tracking
  S0: "1.1.0"

resolved:           # actuality — written by the resolve step, built from
  F0:
    version: 1.3.0
    tag: f0-v1.3.0
    sha: <commit-sha>
    vendored: modules/foundation/F0_agent_behavioral_standards.md
  S0:
    version: 1.1.0
    tag: s0-v1.1.0
    sha: <commit-sha>
    vendored: modules/shared/S0_natural_prose_standards.md
```

- **`declared`** is what the library is willing to accept. For a pinned library this equals the resolved version. For a library tracking a range, it's `^1.x`.
- **`resolved`** is what was actually fetched and vendored. Bundles are built from the vendored files this block points at. This block is machine-written; hand-editing it is the lock-file anti-pattern and the materialized files would carry a generated-file banner discouraging it.

One lock per library governs every agent. Agent definitions are untouched — they keep `@modules/foundation/F0_agent_behavioral_standards.md`, which resolves to the vendored file the lock produced.

---

## Component 3 — Deploy script changes

The version layer is a **resolve-and-materialize** step kept *separate* from the pure-local bundle build, so the bundle build retains its offline guarantee.

**New: `--resolve-guardrails` (online, deliberate).**
1. Read `guardrails.lock`.
2. For each module, fetch the declared version from `source` (git tag or release artifact).
3. Write the module content into the path named in `vendored` (e.g. `modules/foundation/F0...`), prepending a generated-file banner: `# GENERATED — vendored from makegood-guardrails@f0-v1.3.0 (sha …). Do not edit here; edit upstream and re-lock.`
4. Write the `resolved:` block back into `guardrails.lock` (version, tag, sha).
5. If `declared` is an exact pin, resolving is idempotent. If it's a range, this is where a newer version gets picked up — and only here, never on a plain build.

**New: `--update-guardrails [F0=1.4.0]` (the upgrade action).** Bumps `declared`, then runs `--resolve-guardrails`. This is how a client adopts Gate 6: one command, producing a diff to `guardrails.lock` and the vendored module — a reviewable, committable change *in the client's repo*.

**Unchanged: default build.** `build-deploy-bundles.py` (no flag) still resolves `@`-includes from the local vendored files and writes `deploy/agents/`. It does **not** touch the network. A library checked out with its vendored guardrails present builds fully offline and reproducibly. This preserves the Claude.ai-upload / atomic-bundle property.

**Extended: `--check`.** Today it detects bundle drift (bundles out of sync with sources). Extend it to also flag: vendored guardrail content not matching the `resolved` sha (someone hand-edited a vendored copy), and — for range-tracking libraries — a newer upstream version available. The check *reports*; it never auto-updates.

---

## Component 4 — The skill and the plugin collections

**The skill (`building-context-libraries`).**
- `templates/guardrails/F0` and `S0` become a **pinned pull** from `makegood-guardrails` at the skill's release-ZIP build (in `.github/workflows/release.yml`), replacing the hand-maintained placeholder-dated files. This fixes the skill's own drift at its root.
- **PHASE_4 / build instructions** gain one step: when scaffolding a new library, write a `guardrails.lock` seeded at the skill's bundled guardrails version and run `--resolve-guardrails` so the new library starts with vendored, locked, current guardrails. The skill stops being a *content* source for guardrails and becomes a *seeder of the lock*.
- The skill's role as the **worked example** (F0 as the mixed-shape reference in ARCHITECTURE.md) is unaffected — it teaches from whatever guardrails version it bundles.

**The plugin collections (`makegood-skills`, `makegood-skills-internal`).**
- **No new mechanism.** They already vendor the skill via `skills.yaml` (pinned tag, e.g. `building-context-libraries: v1.6.0`) + `sync_skills.py`. Guardrails ride *inside* the skill's vendored copy, baked at the skill's ZIP build. When the skill bumps to a version carrying new guardrails, the collections pick it up through the existing tag-bump → `sync_skills.py` → aggregator-version-bump → tag flow already documented in their CLAUDE.md.

---

## How Gate 6 propagates (the original goal, end to end)

1. Land Gate 6 in `makegood-guardrails` → cut **F0 v1.3.0** (minor; CHANGELOG: "Added Process Gate 6 — New or Already Held").
2. **Nothing changes in any client library automatically.** Pinned libraries stay exactly as built. This is the point — no client's agents change reasoning mid-engagement without a recorded decision.
3. **Per client, when chosen:** `build-deploy-bundles.py --update-guardrails F0=1.3.0` → rewrites that library's `guardrails.lock`, re-vendors F0, recompiles bundles. The resulting commit *in that client's repo* records the adoption. Auditable, deliberate, per-client.
4. **New libraries:** bump the skill's bundled guardrails default to 1.3.0, tag a skill release, sync the two collections. New builds start on Gate 6.

"How do I integrate Glen's notes across all these versions" resolves to: publish once, adopt per-client on each client's own schedule, every adoption recorded as a commit.

---

## Migration sequence

**Phase A — Stand up the source.**
1. Create `WeMakeGood/makegood-guardrails`. Seed F0/S0 from the live `library/context-library` copies (the 2026-04-19 F0). Add `version:` frontmatter, `CHANGELOG.md`. Tag `f0-v1.2.0` / `s0-v1.0.0` (or unified `guardrails-v1.0.0`) as the pre-Gate-6 baseline — capturing current behavior before any change.

**Phase B — Convert one library (the live `library/context-library`) as the pilot.**
2. Add `guardrails.lock` pinned to the baseline versions.
3. Implement `--resolve-guardrails` / `--update-guardrails` / extended `--check` in that library's `scripts/build-deploy-bundles.py`.
4. Run `--resolve-guardrails`; confirm vendored F0/S0 + banners + resolved block; recompile bundles; confirm byte-identical agent bundles to today (baseline = no behavior change yet). This validates the whole machine on a real library before fanning out.

**Phase C — Land Gate 6 upstream.**
5. Finalize Gate 6 wording in `makegood-guardrails`; cut F0 v1.3.0.
6. Adopt on the pilot library: `--update-guardrails F0=1.3.0`; review the diff; recompile; commit. First real adoption.

**Phase D — Wire the skill, then the collections.**
7. Point the skill's `templates/guardrails/` at a pinned guardrails pull in `release.yml`; add the `guardrails.lock`-seeding step to PHASE_4; bump skill version (minor) with CHANGELOG; tag.
8. Bump the skill tag in both `skills.yaml`; run each `sync_skills.py`; bump each aggregator plugin version; tag each aggregator release. (Existing documented flow — no new mechanism.)

**Phase E — Fan out to remaining client libraries** on each client's own schedule, repeating Phase B steps 2–4 then optionally Phase C step 6 per library. No library is forced; adoption is per-engagement.

---

## Decisions (settled 2026-06-16)

1. **Tag granularity — per-module** (`f0-v1.3.0`, `s0-v1.1.0`). F0 and S0 version independently. S0 rarely changes; F0 (universal, six agents) moves more often than S0 (conditional, four agents). Independent tags keep an S0 that hasn't changed from being re-versioned every time F0 moves.

2. **Fetch transport — git tags.** Clone/checkout a tag; no release-artifact tooling. Add tarball-by-checksum only if reproducibility ever demands it.

3. **CI `--check` — report-only, never auto-PR.** Adopting a guardrail change is always a human decision. Critical reason beyond pinned-by-default: **some client library repos are no longer owned by us** — the client owns the upgrade choice, and a bot opening lock-bump PRs against repos we don't control is both wrong and impossible. Report-only respects that boundary uniformly.

4. **Pre-seed F0 audit — DONE.** Three-way diff run before Phase A. Result:
   - **A** — live `library/context-library` F0, `last_updated: 2026-04-19`, 5 process gates: **the canonical baseline. Seed `makegood-guardrails` from A.**
   - **B** — skill `templates/guardrails/` seed: A's body *verbatim* but with a stale placeholder date AND a typo'd `module_id: F#` (should be `F0`). Not a behavioral fork — a corrupted copy. The `F#` typo would propagate into every newly built library; **fix at the skill when wiring Phase D.**
   - **C** — anthropic-skills copy, 145 lines, **missing Process Gate 5 (Generalization Check)**: a stale pre-Gate-5 ancestor. The `anthropic-skills` collection was deprecated (an early single-repo experiment) and its local clone was deleted 2026-06-16; the C variant no longer exists locally (remote `WeMakeGood/anthropic-skills` retained as archive). Removing it dropped the F0 copy count from 9 to 8.
   - Conclusion: no genuine content divergence to reconcile. One real version (A), one typo'd copy (B); the outdated copy (C) is gone. Baseline is unambiguous.

---

## What this plan deliberately does not do

- It does not change the `@`-include + relative-path bundle mechanism. That is sound.
- It does not introduce a push-based sync script. Every propagation is a pinned pull.
- It does not make any client library adopt a guardrail change automatically. Adoption is always a recorded, per-client act.
- It does not break skill atomicity. Locked guardrails are vendored into each library and baked into each skill ZIP; offline rebuilds remain reproducible.
```
