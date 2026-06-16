# Changelog

Per-module history. Each module is versioned independently with its own git tags
(`f0-vX.Y.Z`, `s0-vX.Y.Z`). Entries are grouped by module.

---

## F0 — Agent Behavioral Standards

### [1.3.0] — 2026-06-16

Added **Process Gate 6: New or Already Held** — guards against the agent
presenting as a fresh discovery something the provided context already holds
(silent rediscovery). Orthogonal to Gate 2: Gate 2 marks a claim's *origin*
(sourced/inferred/generated); Gate 6 marks whether it is *new relative to what
is already in hand*. The gate arms only when novelty or authorship is being
claimed and stays silent during faithful compilation/extraction — so it fires
for synthesis work without mis-firing on dossier/report/import skills where
restating context is the task.

Minor bump: additive gate, no change to the existing five. Origin: the failure
mode was surfaced by Glen's Gap Analysis Method; convergent with S0's existing
"Earn Every Claim" gate (same evidence-or-cut shape applied to hype rather than
false-novelty).

Gates at this version:
1. Source Before Statement
2. Mark the Move
3. Reframe Before Committing
4. Second-Order Check
5. Generalization Check
6. New or Already Held

### [1.2.0] — 2026-04-19 — baseline

Initial import into `makegood-guardrails`, establishing the source of truth.
Content is the canonical version that governed the live context library's agents
as of this date — five process gates plus the analytical-depth, uncertainty,
error-correction, and professional-challenge sections. No behavioral change from
the pre-import state; this release captures current behavior so later changes
have a versioned baseline to diff against.

Gates at this version:
1. Source Before Statement
2. Mark the Move
3. Reframe Before Committing
4. Second-Order Check
5. Generalization Check

> Process Gate 6 (New or Already Held) is finalized and approved but not yet
> applied. It lands as F0 1.3.0 (minor — additive gate) once this baseline is
> tagged and consumers can pin against it.

---

## S0 — Natural Prose Standards

### [1.0.0] — 2026-03-10 — baseline

Initial import into `makegood-guardrails`. Content is the canonical version
governing external-facing content in the live context library as of this date:
three process gates (Write From a Practitioner's Voice, Earn Every Claim, Start
From the Point) plus the writing-discipline and revision-backstop sections.
Conditional module — loaded by external-facing agents only.
