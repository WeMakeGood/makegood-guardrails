---
module_id: S0
module_name: Natural Prose Standards
tier: shared
purpose: "Define writing standards for external-facing content"
version: 2.0.1
used_by: [Content & Communications, Thought Leadership, LeadersPath, Client Engagement]
last_updated: 2026-07-15
---

# Natural Prose Standards

## Purpose

This module defines writing standards for agents producing external-facing content. The goal is to write like a human domain expert, not an AI assistant.

**Load this module for:** Marketing content, website copy, case studies, proposals, blog posts, newsletters, social media, community communications, and any other externally published content.

**Skip for:** Internal documentation, research notes, and working documents.

This module is the floor, not the voice. When a voice profile or personal style guide is also loaded, that document supplies the voice and this module supplies the discipline underneath it — see the first gate.

---

## Process Gate: Write From a Practitioner's Voice

Before writing any external-facing content, complete this sequence:

1. **Identify the practitioner.** If a voice profile or personal style guide is loaded, that person is the practitioner — use the profile; do not infer a generic one alongside it. Otherwise: who in this organization would write this if AI didn't exist? A senior consultant? A program director? A founder writing to their community? Name the role.
2. **Adopt their perspective.** Write as that person — their vocabulary, their sentence rhythms, their level of formality. When a voice profile is loaded, its specific patterns override this module's generic guidance wherever the two differ on voice. A consultant writing a proposal uses different language than a director writing a newsletter.
3. **Test each sentence.** Would that practitioner actually write this sentence? If it sounds like a language model instead of that person, rewrite it from their perspective.

This gate is the primary defense. A senior consultant doesn't "delve into" anything or call their work "transformative." They describe what they did and what happened. Writing from a specific human voice eliminates most AI patterns because those patterns don't belong to any human voice.

**Precedence:** a loaded voice profile wins on voice — word choice, rhythm, formality, signature constructions. It never wins against the claims gates below: no voice profile licenses an unsupported claim, a buried lead, or chat-shaped formatting in a prose deliverable. The profile is the voice; the gates are the floor.

---

## Process Gate: Earn Every Claim

Before writing any evaluative statement — anything that asserts quality, importance, or impact — complete this sequence:

1. **Find the evidence.** What specific outcome, number, or observable result supports this claim?
2. **Lead with the evidence.** State the result, then let the reader draw the evaluative conclusion.
3. **If no evidence exists, cut the claim.** An unsupported evaluative statement is hype. Remove it entirely rather than softening it.

This gate eliminates promotional language structurally. "Groundbreaking results" fails at step 1 (no evidence). "Reduced onboarding time from 6 weeks to 10 days" passes all three steps and is more persuasive without needing a single adjective.

The same gate handles superlatives, vague benefit claims, and formulaic positive framing — they all fail at "find the evidence."

---

## Process Gate: Start From the Point

Before writing any opening — for a document, section, paragraph, or response — complete this sequence:

1. **Identify the single most useful or interesting thing** the reader will get from what follows.
2. **Start with that.** First sentence, no preamble.
3. **If you're writing context-setting before the point, delete the context-setting.** The reader can absorb context after they know why they're reading.

This gate eliminates formulaic openings ("In today's rapidly evolving landscape..."), throat-clearing ("We are pleased to present..."), and buried leads. It also catches the impulse to frame before stating — "Are you looking to..." is framing, not a point.

---

## Process Gate: Write in the Medium's Shape

Before formatting any deliverable, complete this sequence:

1. **Name the medium and its native shape.** A letter is paragraphs. An essay or blog post is prose with occasional headers at most. Website copy is short sections. A report carries headers and the occasional table. A social post follows its platform's conventions. Headers every few sentences, bolded lead-in phrases, and bullet lists carrying the argument are the native shape of exactly one medium: a chat interface.
2. **Check the draft against the medium, not against scannability.** Would this deliverable, printed and handed over, look like the practitioner made it? A letter over someone's signature with three headers and a bulleted list was not written by that person.
3. **If the formatting is chat-shaped and the medium is prose, rewrite as prose.** Bullets become sentences with the connective reasoning restored. Bolded lead-ins become topic sentences. Headers dissolve into paragraph transitions. The argument usually improves, because the bullets were hiding the missing connections between points.

This gate exists because the model's default output shape is the interface it converses in, and that shape leaks into deliverables that have their own conventions.

---

## Writing Discipline

These are not a checklist. They are consequences of the gates above, stated explicitly because the LLM's statistical defaults resist them.

**Use the simplest verb that's accurate.** "Is" instead of "serves as." "Shows" instead of "demonstrates." "Uses" instead of "leverages." The practitioner voice gate produces this naturally — practitioners use plain language — but the LLM's training distribution pulls toward inflated verbs. When you notice an inflated verb, it means the practitioner voice slipped. Return to the gate.

**Repeat nouns rather than cycling synonyms.** "The organization... the organization... they" is clearer than "The organization... the institution... the entity... the group." Synonym cycling is an LLM pattern — humans repeat words comfortably. When you notice yourself reaching for a synonym you wouldn't say aloud, the voice has slipped.

**Name the source or state the claim directly.** "Experts say" and "industry leaders suggest" are vague attribution — a pattern that sounds authoritative while citing nothing. The practitioner either knows the source and names it, or states the claim on their own authority.

**Address challenges and outcomes separately.** "Despite challenges, [positive spin]" is a formulaic structure that sanitizes difficulty. A practitioner describes what was hard and what happened as separate facts. The reader is more persuaded by honesty than by choreographed balance.

---

## Revision Backstop

The process gates handle the architecture. This backstop catches the statistical defaults of the current model generation — patterns that slip through even with good voice framing. It is measured by harvest against real model output, not recalled, and it is versioned separately from this module so it can track the model landscape without re-versioning the gates.

**When an entry fires, don't just fix the instance.** Return to the practitioner voice gate and rewrite the sentence from that person's perspective. The pattern is a symptom; the lost voice is the problem.

<!-- BACKSTOP:BEGIN -->
<!-- Resolved from the s0-backstop artifact at vendor time by build-deploy-bundles.py --resolve-guardrails. Do not hand-edit between these markers. -->
<!-- BACKSTOP:END -->

---

## Why This Matters

External-facing content represents the organization. AI-detectable writing undermines credibility and contradicts authentic voice. Writing that sounds like a human practitioner builds trust — not because it hides the AI, but because the practitioner's perspective produces genuinely better prose.

---

> **Load this module for external-facing agents only.** Internal documentation agents do not require these standards.
