# G1 / G2 4.0.0 redesign — proposal for review

*Drafted 2026-11-07 on branch `redesign/v4` for Chris. Status: draft. Nothing is tagged, pushed or released, and no consumer (context libraries, skills, `~/.claude`, `claude-config`) has been touched. Both modules carry `version: 4.0.0-draft`.*

## What this proposes, in one paragraph

G1 is rewritten at less than half its size and G2's core at two thirds, with every v3 requirement kept or listed below as cut with a reason. The gates stay gates. What changes is how they're written: each gate is now stated as an operation plus what it's for, in short paragraphs, instead of numbered sub-procedures followed by explanatory sections that restate them. G1's sections that restated gates (Analytical Depth, Uncertainty, Where the Gates Run) are folded into the gates they restated, and the maintainer note moves to the README. G2's core loses the quoted bad phrases and the wrong/right example pair, loses its numbered steps and bolded lead-ins, and is written in the prose shape its own fourth gate asks for. The backstop artifact and splice markers are unchanged.

## Sizes

Measured on the files (`wc`-equivalent; tokens estimated as words ÷ 0.75, the same estimate `building-context-libraries/scripts/count_tokens.py` uses).

| File | v3 bytes | v4 bytes | Change | v3 lines | v4 lines | v3 words | v4 words | Est. tokens v3 → v4 |
|---|---|---|---|---|---|---|---|---|
| `G1_agent_behavioral_standards.md` | 16,146 | 7,268 | −55% | 202 | 64 | 2,534 | 1,195 | ~3,380 → ~1,590 |
| `G2_natural_prose_standards.md` (core, backstop region empty) | 8,164 | 5,482 | −33% | 109 | 49 | 1,208 | 853 | ~1,610 → ~1,140 |
| G2 as delivered (core + spliced backstop body, 3,729 bytes) | ~11,900 | ~9,200 | −23% | | | | | |

Line counts fell further than bytes because v4 uses fewer, longer paragraphs. Bytes and words are the honest measure; the docs' 200-line target is met either way.

**Claude Code's always-loaded payload.** `~/.claude/CLAUDE.md` is 9,662 bytes and imports the deployed G1 (16,306 bytes with its deploy banner). The Claude Code docs say imports "don't reduce its context cost, because imported files load together with the CLAUDE.md that imports them" (code.claude.com/docs/en/memory). So G1 is about 63% of those two files' combined 25,968 bytes. With v4 that pair drops to about 17,000 bytes. (`claude-config`'s check-config recorded 27,922 bytes on 2026-11-07, which also counts skill descriptions.)

## Why, and what the design rests on

Three sources, each scoped to what it actually says:

1. **Claude Code docs** (code.claude.com/docs/en/memory, read 2026-11-07): "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence," and "If two instructions contradict each other, Claude may pick one arbitrarily." The docs also say "group related instructions under markdown headers and bullets," which I followed for G1 (headers per gate) but not for G2's interior, for the reason under change 3 below.
2. **Anthropic's prompting guide** (platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, read 2026-11-07): "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can give Claude more information about your goals," with "Claude can generalize from the explanation"; "Tell Claude what to do instead of what not to do"; and "The formatting style used in your prompt might influence Claude's response style... removing markdown from your prompt can reduce the volume of markdown in the output."
3. **"Components of agent memory"** (anthropic.com/research/components-of-agent-memory). The always-loaded layer "has to stay relatively small" because "an incorrect note can be carried into every session." The purpose-over-procedure finding is narrower than the brief that started this work suggested: it was tested on memory-writing rules only ("record only failures" cost Opus 5 −0.234 in memory gain), so applying it to G1 is my hypothesis, not a result. One correction to that brief: the article doesn't test "a rule is stronger with its basis stated." It observes that Opus 5's own notes recorded a rule "and also how it knew the rule was true." The better source for stating the basis is the prompting guide's "add context" section (item 2).

Your own test, from `claude-config` commit 4b7183c (2026-11-07, the dream skill), is the one I applied line by line: "would Claude get this wrong or vary on it in most sessions without it? A rule only some kinds of work need belongs in a skill. A rule Claude follows anyway, or that duplicates another file, is cut." Everything in G1 v4 is there because I judged it passes that test. Where it's a close call I've said so in the mapping.

**The architecture principle is kept.** Each gate is still an upstream operation the agent performs before or while producing output, not a failure to watch for. My reading of what changes: v3 defines a gate by its numbered steps ("complete this sequence: 1. Locate 2. Cite 3. Scope"). v4 defines it by the operation and what it's for, and leaves the sequencing to the model. That's compatible with the principle as G1's closing note states it ("requiring incompatible upstream steps"), and the prompting guide supports stating the purpose. Each gate's basis sentence says what the operation secures, as v3's own "This gate interrupts..." sentences already did. No gate gains a catalog of failures.

## The three most consequential changes

1. **G1's restating sections are folded into the gates (−55%).** Cross-domain reasoning and the framework half of contextual sourcing now live inside Gates 3 and 5. Uncertainty is split between Gate 2 (calibrated wording) and Gate 1 (name the gap; don't approximate around it). The "never render gate names or process headers" rule from Where the Gates Run becomes the module's second paragraph, because it's an instruction to the model, added in 2.0.0 to fix measured ceremony. One behavioral change comes with the fold. v3's Analytical Depth told the agent to "actively look for structural parallels" whenever analyzing. v4 asks for a parallel only when Gate 3 arms. Under this repo's semver (2.0.0 precedent), that narrowing is major.
2. **G2's core no longer quotes the patterns it's trying to suppress.** Gone: "delve into," "transformative," "In today's rapidly evolving landscape," "We are pleased to present," "Are you looking to," "Groundbreaking results," the "serves as / demonstrates / leverages" verbs, "Experts say," "Despite challenges, [positive spin]," and the "Reduced onboarding time from 6 weeks to 10 days" example. Each operation is now stated positively: start with the point; delete scene-setting, a description of the reader's situation, or an announcement. The reason is the repo's own (see the review of observation 3 below). The vocabulary items survive in the backstop's lists, which is where the repo already keeps them.
3. **G2's core is written in the shape it asks for.** v3 sets nine headers, numbered steps in all four gates, and bolded lead-ins in the discipline section and the precedence note. That is the chat shape its own Medium's Shape gate and the backstop's chat-shape entry flag. v4 keeps one header per gate, so the backstop's "Earn Every Claim" reference and the splice markers resolve, and writes everything inside them as prose. The prompting guide says prompt style influences output style. The harvest measured chat-shape formatting as the leak G2 suppresses best (Sonnet headers above human p90: 58% → 8%, A → B). So this is both a consistency fix and a testable hypothesis: does a prose-shaped G2 suppress formatting further, or does dropping the numbered steps weaken the gates? See "How to evaluate."

## The earlier observations, checked against the text

| Observation | Verdict | What the text shows |
|---|---|---|
| Analytical Depth restates Gates 3 and 5 | **Partly holds** | Cross-Domain Reasoning restates Gate 3's second question but adds a quality test (structure, not surface), which v4 keeps. Contextual Sourcing's second paragraph is Gate 5 applied to the agent's own methods. Its first paragraph applies the same check to frameworks, so it merges into Gate 5. **Convergence as Signal and Example Anchoring restate nothing.** They're kept under Working Habits. |
| Uncertainty restates Gate 2 | **Holds, with one addition** | The calibration content is Gate 2's. The missing-information clause ("name it clearly, describe what kind of information would fill it, and help the user find a path") is Gate 1's gap clause plus "don't approximate or hedge around the gap," which v4 adds to Gate 1. |
| Where the Gates Run and A Note on This Document are maintainer notes | **Half holds** | The Note is a maintainer note. It moves to the README verbatim in substance. Where the Gates Run is mostly an instruction to the model: CHANGELOG 2.0.0 records it fixing "ritualized cross-domain parallels and second-order sections" on literal models. v4 keeps its rules and drops its per-gate commentary. |
| G2's core quotes the phrases the backstop's no-examples rule warns against | **Holds, scoped** | The tracker's stated reason is that the backstop body "is spliced verbatim into the model's write-time context," and "any description or example of a bad pattern... primes that pattern." G2's core is spliced into the same context, so the reason applies to it identically. Two caveats. First, the backstop itself names patterns by template ("it's not X, it's Y," "Here's the thing," the vocabulary lists), so the repo in practice separates naming a pattern from showing illustrative passages. Second, priming is the repo's stated principle and hasn't been measured here; see the evaluation plan for a direct test. |
| G2 has a duplicated load-for ending and a Why This Matters section that may not change behavior | **Holds, with one thing worth keeping** | The ending duplicates the purpose section's load and skip lines. Why This Matters does carry a basis the prompting guide supports stating: the practitioner's perspective produces better prose, which isn't the same as hiding the AI. v4 keeps that reason in the opening paragraph and drops the section. |
| G2 isn't deployed in Claude Code and might suit a skill | **Holds** | `~/.claude` has no G2 and `claude-config/scripts/deploy.sh` deploys only G1. The skill version is proposed below (it's a consumer change, so I didn't make it). v4's text is written so the same body works as a SKILL.md body. |

## What that list missed

1. **G1 was written for library agents but runs in every Claude Code session.** v3's Gate 1 locates sources in "documents, transcripts, user input, modules." In Claude Code, the sources are mostly files and tool output. v4's list is environment-neutral: "files, documents, transcripts, tool output, loaded modules, what the user said."
2. **G2 v3's Earn Every Claim example could be copied as a fabricated statistic.** "Reduced onboarding time from 6 weeks to 10 days" is exactly the kind of fixed example text that CHANGELOG G1 2.0.0 says literal models "reproduce verbatim," and G1's own Example Anchoring warns about wrong/right pairs. Copied, it becomes an invented metric in a deliverable.
3. **The harvest's generator can't run against the current file names.** `harvest/scripts/generate_corpus.py` hard-codes `modules/S0_natural_prose_standards.md` (line 51), which hasn't existed since the 3.0.0 rename. Arm B fails until that's fixed, so G2 can't be compared old against new without the change proposed below. `harvest/BACKSTOP_TRACKER.md` and `harvest/HARVEST.md` still say S0 too.
4. **The harvest already measured a displacement effect.** REPORT.md for 2026-07 records parentheticals and aphoristic closings *rising* from arm A to arm B, so G2 pushes the signature somewhere else as well as suppressing it. Any G2 change should be judged on the families it might push habits into, not only on total suppression.
5. **Consumers depend on G1's section names.** `building-context-libraries` `references/ARCHITECTURE.md` uses G1 as its worked example of module shapes. It quotes the Uncertainty section as the "pure reasoning context" example and still says "G1's five process gates" (stale since 1.3.0). Its `SKILL.md` and `PHASE_2_COMPREHEND.md` cite "G1's Analytical Depth Requirements (Reframe Before Committing, Cross-Domain Reasoning, Convergence as Signal)." v4 keeps every gate name and HIGH-STAKES, so name-based references like "Source Before Statement" in drafting-articles and designing-websites still resolve. The Analytical Depth and Uncertainty references won't, and the skill needs a matching edit when it adopts v4.
6. **The CHANGELOG has no G2 3.0.0 or g2-backstop 2.0.0 entry.** Both were tagged by the rename commit, but the G2 and backstop sections stop at 2.0.1 and 1.1.0. The release step for v4 should backfill them.
7. **G2's precedence rule names the wrong gates.** v3 says a voice profile "never wins against the claims gates below," then lists a buried lead and chat formatting, which belong to Start From the Point and Medium's Shape. v4 says "the claims and shape gates," which matches v3's own list.
8. **The deployed G1 carries its YAML frontmatter into every session.** 193 bytes of build metadata (`tier`, `purpose`) the model doesn't need. A `deploy.sh` change could strip it (question 6).

## Mapping: every v3 requirement to its v4 home

### G1

| v3 section and requirement | v4 home |
|---|---|
| Purpose: minimum standards, not guidelines | Opening ¶1: "They are a floor" |
| Purpose: gates rather than evaluation criteria (architecture) | README "Design principle" (maintainer-facing) |
| Purpose: "All agents load this module" | **Cut.** A loading note. The import or bundle does the loading, and the line changes no behavior. |
| Gate 1: locate, cite, scope | Gate 1 ¶1 |
| Gate 1: if no source, don't state; name the gap, what fills it, where; not a script | Gate 1 ¶2 |
| Gate 1: applies to facts, figures, names, dates, quotes, positions, anything actionable | Gate 1 ¶1 |
| Gate 1: doesn't apply to marked reasoning or inference | Gate 1 ¶3 |
| Gate 2: three legitimate kinds; reader can always tell | Gate 2 ¶1 |
| Gate 2: no required format; language makes status legible | Gate 2 ¶1 ("let the language carry it") |
| Gate 2: carrying source language satisfies the gate; paraphrase obscures | Gate 2 ¶2 |
| Gate 2: reported speech distinguished | Gate 2 ¶2 |
| Gate 2: method visible for non-trivial paths | Gate 2 ¶3 |
| Gate 3: arming condition and non-arming cases | Gate 3 ¶2 |
| Gate 3: best or first framing; generate an alternative | Gate 3 ¶1 |
| Gate 3: name a cross-domain parallel even if unused | Gate 3 ¶1 |
| Gate 3: HIGH-STAKES needs two framings | Gate 3 ¶1 |
| Gate 3: purpose (interrupt reinforcing the first direction; more defensible answer) | Gate 3 ¶2 |
| Gate 4: arming; three questions; include if non-trivial; incomplete otherwise | Gate 4 |
| Gate 5: arming (beyond the instance; instance-scoped doesn't arm) | Gate 5 ¶1 |
| Gate 5: three questions (features, would the method hold, falsifier; else anecdotal) | Gate 5 ¶1 |
| Gate 5: the method exploiting the evaluation context | Gate 5 ¶1 ("Be most wary of a method that worked because of how this case was framed, evaluated or sourced") |
| Gate 5: not necessarily weaker; scope stated; revise the method if it fails | Gate 5 ¶1 |
| Gate 6: trigger list; what counts as context | Gate 6 |
| Gate 6: confirmation, not discovery; name source; independent support | Gate 6 |
| Gate 6: extension says what it adds and against what; genuinely new is accurate | Gate 6 |
| Gate 6: arms only on novelty claims; compiling and restating is silent | Gate 6 |
| Gate 6: orthogonal to Gate 2 (explanation) | **Cut.** It explains the design to a maintainer and the Gate 6 operation stands without it. Already recorded in CHANGELOG 1.3.0. |
| Where the Gates Run: execute in reasoning | Opening ¶2 |
| Where the Gates Run: per-gate surfacing (citation or gap; legible status; 3–5 only when non-trivial; attribution) | Opening ¶2 ("a citation, a named gap, a cost someone will bear, a stated scope"; "A gate whose answer is trivial leaves no trace") plus each gate's own text |
| Where the Gates Run: never render gate names, checklists or headers | Opening ¶2 |
| Where the Gates Run: "an output that performs the gates has confused the discipline with its evidence" | **Cut.** It's the reason for the line above, and the rule now stands with its own reason ("never their scaffolding"). |
| Where the Gates Run: Gate 2's visible path is the reasoning, not the scaffolding | Opening ¶2 plus Gate 2 ¶3 |
| HIGH-STAKES: both conditions | HIGH-STAKES ¶ |
| HIGH-STAKES: "not whether it belongs to a category"; one condition absent means normal gates | Compressed into "when both hold." **Close call.** The sentence guarded against category-matching. If you want it explicit, it's one clause. |
| HIGH-STAKES: cite, reproduce exactly, flag before external audience | HIGH-STAKES ¶ |
| HIGH-STAKES: never extrapolate; stop, name what's missing and what's needed | HIGH-STAKES ¶ |
| Cross-Domain Reasoning: look for structural parallels | Gate 3 ¶1. **Narrowed** to when Gate 3 arms (see change 1). |
| Cross-Domain Reasoning: value is the shared structure; drop it if it doesn't hold | Gate 3 ¶1 |
| Convergence as Signal | Working Habits ¶1 |
| Contextual Sourcing: bring a framework's context; check the originating situation resembles this one | Gate 5 ¶2 |
| Contextual Sourcing: own prior methods; past success is a hypothesis | Gate 5 ¶2 |
| Example Anchoring (three bullets) | Working Habits ¶2 |
| Uncertainty: calibration is epistemic; language reflects knowledge | Gate 2 ¶1 |
| Uncertainty: notice the impulse to state the unverified confidently | Gate 2 ¶1 |
| Uncertainty: missing information means name it, what fills it, a path; don't approximate or hedge | Gate 1 ¶2 |
| Error Correction (correct, state what and why, continue; don't minimize) | Working Habits ¶3 |
| Professional Challenge (when; cite the concern; alternative; direct, not adversarial; outcomes over winning) | Working Habits ¶4 |
| Agent-Specific Application: agents may add requirements; none can weaken | Opening ¶1 ("agent and project instructions can add to them, never weaken them") |
| A Note on This Document | README "Design principle" |

### G2

| v3 section and requirement | v4 home |
|---|---|
| Purpose: write like a human domain expert | Opening ¶1 |
| Load for (content types) and skip for (internal docs) | Opening ¶1 |
| Floor, not the voice | Opening ¶2 |
| Practitioner gate 1: identify; a loaded profile is the practitioner, with no parallel generic one; otherwise name the role | Practitioner ¶1 |
| Practitioner gate 2: adopt vocabulary, rhythm, formality; the profile overrides generic guidance on voice | Practitioner ¶1 plus Opening ¶2 |
| Practitioner gate 2: "A consultant writing a proposal uses different language than a director writing a newsletter" | **Cut.** An illustration whose point the step itself carries. |
| Practitioner gate 3: test each sentence; rewrite if it sounds like a model | Practitioner ¶2 |
| Primary defense; habits belong to no human voice | Practitioner ¶2 |
| "A senior consultant doesn't 'delve into'... 'transformative.' They describe what they did and what happened." | Positive half kept (Practitioner ¶1). **Quoted tics cut** (change 2). Both words remain in the backstop's lists. |
| Precedence: the profile wins on voice, never against the gates | Opening ¶2 (corrected to "claims and shape gates," see missed item 7) |
| Earn: find evidence; lead with it; cut if none, don't soften | Earn ¶ |
| Earn: "Groundbreaking results" vs "6 weeks to 10 days" example | **Cut** (change 2; missed item 2) |
| Earn: superlatives, vague benefits and formulaic positivity fail at step 1 | Earn ¶ |
| Start: identify the most useful thing; start with it; delete context-setting first | Start ¶ |
| Start: quoted formulaic openings, throat-clearing, "Are you looking to" | **Quotes cut.** Restated as operations: scene-setting, describing the reader's situation back to them, announcing what's coming. Buried leads are covered by the gate itself. |
| Medium: name the medium and its native shape (all five examples kept); chat is the one medium for headers, lead-ins and bullets | Medium ¶1 |
| Medium: check against the medium, not scannability; the printed-and-handed-over test; the letter example | Medium ¶2 |
| Medium: rewrite rules (bullets, lead-ins, headers); the argument improves | Medium ¶2 |
| Medium: why (the interface shape leaks) | Medium ¶1 |
| Discipline: not a checklist; consequences of the gates; defaults resist | Discipline ¶1 |
| Discipline: simplest verb; slip means the voice slipped, return to the gate | Discipline ¶1–2. **Verb example pairs cut.** The lexical side is in the backstop. |
| Discipline: repeat nouns; synonym cycling | Discipline ¶2. Example cut; reason added (readers think a new thing was introduced). |
| Discipline: name the source or state directly | Discipline ¶2. Quoted phrases cut. |
| Discipline: challenges and outcomes separately | Discipline ¶2. Template cut. |
| Backstop intro: gates handle the architecture; measured, not recalled; versioned separately | Backstop ¶ |
| Backstop intro: when an entry fires, return to the practitioner gate | Backstop ¶ |
| Splice markers | Unchanged. The comment inside them now says g2-backstop, not s0-backstop. The splice replaces everything between the markers anyway (`splice_backstop` in `build-deploy-bundles.py`). |
| Why This Matters | **Section cut.** Its basis (better prose builds trust, not hiding the AI) moves to Opening ¶1. |
| Closing "load for external-facing only" | **Cut** as a duplicate of the opening. |

## Changes proposed outside the modules (written only, not made)

- **`G2_backstop.md`: no change needed.** Its remedy cites "the Earn Every Claim gate," and v4 keeps that name. Its frontmatter is accurate. One observation for the next backstop release: its own entries quote templates ("it's not X, it's Y," "Here's the thing," "I'd be happy to"). If the priming test below shows quoted examples hurt, the same question applies to those, and the answer would come from measurement, not this proposal.
- **`harvest/scripts/generate_corpus.py`: add an `--arm-b-file` argument**, defaulting to `modules/G2_natural_prose_standards.md`, and record its sha in provenance as now. That fixes the broken path from the rename and lets the old and new cores run as separate arms. Update the S0 names in `BACKSTOP_TRACKER.md` and `HARVEST.md` in the same change.
- **`building-context-libraries` (when it adopts 4.0.0):** rework the ARCHITECTURE.md "G1 as a Worked Example" section (gate count; the Uncertainty quote; the 40/20/40 shape mix). Point the "Analytical Depth Requirements" references in `SKILL.md` and `PHASE_2_COMPREHEND.md` at Gate 3 and the convergence habit. Add a PHASE_M migration note.
- **`claude-config`:** (a) optionally strip G1's frontmatter in `deploy.sh`; (b) if you want G2 in Claude Code, deploy it as a skill whose body is G2 core with the backstop spliced (deploy.sh would need the same splice step `--resolve-guardrails` does), triggered on writing external-facing content. Name to be decided by you (question 2).
- **CHANGELOG at release:** backfill G2 3.0.0 and g2-backstop 2.0.0. The 4.0.0 entries are left for the release commit, since this is a draft.

## Risks, and what acting on this makes harder

- **Shorter may mean weaker.** I can't show from the text alone that a gate stated as purpose binds as tightly as a numbered sequence. The research finding behind the purpose-first approach was about memory-writing rules, not reasoning gates. That's why the evaluation below comes before any tag.
- **The cross-domain narrowing is a real behavior change.** Library-building synthesis (PHASE_2's lateral moves) relied on the unconditional "actively look for structural parallels." In practice those tasks arm Gate 3, so I expect little loss, but it's an expectation.
- **The harvest baseline moves.** Every harvest so far measured arm B against the v3-equivalent core (sha `d5d49a79…`). Adopting G2 v4 means the next harvest's gate-effectiveness numbers aren't directly comparable unless one run carries both cores. The evaluation does that once, which costs a full extra arm of generation and judging.
- **Consumers pay a migration.** Every library pinned to `g1-v3.0.0` or `g2-v3.0.0` keeps working (pinned by design), but adopting 4.0.0 means editing the skill's teaching material (missed item 5). The skill's worked example then teaches from a module with a different shape mix: less "reasoning context," more gates.
- **Removing quoted examples removes information.** If the examples were doing real steering work, the backstop alone may not recover it. The priming test isolates this.
- **Who bears the cost:** you, for review and the two evaluation runs, and whoever next upgrades a client library. Client libraries themselves bear nothing until someone chooses to upgrade.

## How to evaluate before tagging

### G2: reuse the harvest

1. Fix the arm-B path (above). Run `generate_corpus.py` on the current deployment-target models, all 31 briefs, 3 samples, with three arm-B variants, backstop region empty as the protocol requires: **B3** (v3 core from `g2-v3.0.0`), **B4** (this draft), and **B4+ex** (this draft with v3's quoted phrases and example pair put back). Reuse the 2026-07 arm A if the models match; otherwise rerun A.
2. `run_judge.py prepare / dispatch / tally` each arm against the same exemplars, with the same judge model across arms, and `family_rollup.py` for the deterministic recount.
3. Read three comparisons. **B4 vs B3**: total judge-flagged habits (2026-07: Opus 441, Sonnet 437 under B3-equivalent), and per family: headers, bold lead-ins, bullets, em-dash, plus the two displacement families (parentheticals, aphoristic closings). **B4 vs B4+ex**: the priming question, directly. Do the quoted phrases and openings appear more often when quoted in the core? Grep the outputs for the literal strings too, including "6 weeks to 10 days." **Gate effectiveness A→B4 vs A→B3.**
4. Adopt B4 if it's no worse than B3 on any family beyond sample noise and no worse on displacement. If B4+ex beats B4, the priming premise is wrong for the core and the examples come back, which would also inform the backstop.

### G1: a small adherence battery (nothing measures this yet)

Build `g1-eval/` beside `harvest/`: about 20 cases, each a short fixture (documents or a prior turn) and a prompt designed to arm one gate, plus negative controls designed *not* to arm any:

- **Gate 1:** a request for a figure that isn't in the provided document.
- **Gate 2:** a synthesis mixing sourced facts with needed inference.
- **Gate 3:** a problem with two plausible framings.
- **Gate 4:** a recommendation with a hidden cost.
- **Gate 5:** "turn this one case into a reusable method."
- **Gate 6:** the context already states the insight the task invites.
- **HIGH-STAKES:** contract terms or a policy detail.
- **Error correction:** an error seeded in a prior turn.
- **Professional challenge:** a request that contradicts a stated strategy.
- **Example anchoring:** an instruction carrying a sample output.
- **Negative controls:** a reformat, a lookup, and a rename, which test overtriggering.

Run each case in three arms (no G1, v3, v4), at least 5 samples, on the current models. Use two surfaces. The **API**, with G1 as the system prompt, is the library-agent analog. **Headless `claude -p`**, with each G1 version in place of the deployed import, is the Claude Code analog; how to swap the import without touching `~/.claude` is still to be worked out, possibly a scratch config directory. Score with a blind judge on a per-case rubric (one pass/fail criterion per gate, written before the runs) plus a deterministic ceremony check: gate names, "Second-order check:"-style headers, and ritual parallels on the negative controls. Accept v4 if it's within noise of v3 on every gate and no worse on ceremony. The no-G1 arm shows which gates the models now satisfy unaided. Under your own test, those are candidates to cut entirely in a later version.

A field signal costs nothing extra: the dream review's digest already records your corrections. Tagging the ones that map to a G1 gate ("that isn't in the source," "say which part is yours," "you said you read it") gives a before-and-after rate once v4 is deployed.

## Questions for Chris

1. **One G1 for both surfaces?** I wrote one text for both Claude Code sessions and library agents. Would you rather Claude Code get a slimmer core (Gates 1, 2 and 6, error correction, challenge) and leave Gates 3–5 and HIGH-STAKES to library agents and analysis skills? Your dream test points that way for coding and site sessions. I didn't draft it because it would split the single source.
2. **G2 in Claude Code:** do you want it deployed as a skill for external-facing writing? If yes, what should it be called? I haven't named it.
3. **Quoted examples:** accept their removal from G2's core on the repo's priming principle now, or hold the change until the B4 vs B4+ex run shows the effect?
4. **Prose-shaped G2:** are you comfortable testing a G2 without numbered steps and bolded lead-ins, given the docs recommend headers and bullets for instruction files? G1 v4 follows the docs; G2 v4 deliberately departs from them inside each gate.
5. **Cross-domain narrowing:** is it acceptable that structural parallels are sought only when Gate 3 arms, rather than whenever analyzing?
6. **Deployed frontmatter:** should `claude-config/deploy.sh` strip G1's YAML frontmatter from the copy in `~/.claude`?
7. **HIGH-STAKES scope:** v3 and v4 limit it to "organizational specifics." In Claude Code, the irreversible-harm cases are often operational (database writes, deletes), and your CLAUDE.md covers those separately. Should HIGH-STAKES stay organizational, or widen? I kept v3's definition rather than guess.
8. **Duplication with `~/.claude/CLAUDE.md`:** several of its Operational Constraints overlap G1. "Mark the move"-style attribution appears in "Do the thinking, not the transcribing," and Gate 1's sourcing in "Never recreate from memory" and "Mark unknowns as TODO." Under your test one side should go. That belongs to a dream review of `claude-config`, not this branch. Do you want it flagged there?
9. **Version numbers:** I've treated both modules as major, G1 for the trigger narrowing and G2 because the model-visible text changes in ways whose effect isn't yet measured. Agree, or should G2 be a minor until the evaluation says otherwise?
