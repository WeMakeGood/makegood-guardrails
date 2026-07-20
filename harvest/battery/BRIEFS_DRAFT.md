# Battery Briefs — readable view

> **Status: approved + committed (2026-07-18).** Human-readable companion to
> [`core.jsonl`](core.jsonl), which is the **source of truth** — if the two ever
> disagree, `core.jsonl` wins. Written to [`COVERAGE_SPEC.md`](COVERAGE_SPEC.md);
> replaced the retired Harbor Bend F01–F12. All 31 briefs have committed exemplars
> (Fable, broad-craft-sourced, guardrail-free, `v2-learn-decisions`).

## How to read a brief

Each brief is the **user turn** given to the target model. The `[invented]` /
`[real]` tag is the substrate axis (see below). The **why** notes under each
register are *for us*, not the model — they record what work the register
exercises. They are deliberately NOT tendencies to catch: the register is the
stimulus, the judge names whatever the model overdoes.

**The `[invented]` / `[real]` axis.** Every brief is tagged:
- **`[invented]`** — the subject/facts are fictional and inert. Tests writing
  *without* priors; stable (can't go stale, can't bait a factual error that
  muddies the writing signal).
- **`[real]`** — a real, well-established subject the model was trained on. Tests
  writing *with* priors — trained-data recall (encyclopedia-voice, imported
  cadence, "how this topic is usually written"). Because the exemplar is a
  human-grade quality bar (not a null machine baseline), the comparison stays
  clean: target-vs-skilled-human, real subject or not.

A tic that shows up on `[real]` briefs but not `[invented]` ones is
recall-driven; one that shows up on both is general. That attribution is the
reason for the tag.

**Real subjects are chosen to be STABLE and UNCONTESTED** — long-settled history,
established concepts, well-documented facts. Nothing current-events (drifts),
nothing politically contested (would bait a content reaction and confound the
writing measurement).

**Design rules honored:**
- No fixed org. Substrates are varied, minimal, and register-appropriate — or absent.
- No brief is phrased to provoke a named tic. Each asks for a genuine piece of work.
- Neutral instruction; word-count targets are stated as targets, not hard limits.
- IDs are register-prefixed and expandable (add more within a register freely).

Registers are the 8 starting set. Draft gives **~3–4 briefs per register**, each a
mix of `[invented]` and `[real]`, so a tic has room to recur across briefs *within*
a register and to be attributed to recall vs. general (independent of the
multiple-samples-per-brief axis, which is the tool's job). Total: 28 briefs.

---

## R-ANALYTIC — analytical / argumentative

*Exercises making a case and weighing evidence.*

- **AN01** `[invented]` — Argue for or against this claim in about 500 words: "Remote work has been better for junior employees than for senior ones." Take a clear position.
- **AN02** `[invented]` — A city is deciding whether to replace a downtown parking lot with a park or with mixed-income housing. Write ~450 words making the strongest case for one option, acknowledging the real cost of what's given up.
- **AN03** `[invented]` — Write a ~400-word review of a fictional restaurant, "The Copper Kettle," that does one thing extraordinarily well and several things poorly. Reach an overall verdict.
- **AN04** `[real]` — Argue in about 450 words for which invention did more to shape the modern world: the printing press or the transistor. Take a side.
- **AN05** `[real]` — Write a ~400-word critical assessment of why the Betamax lost to VHS, arguing what the decisive factor actually was.

## R-TECH — technical / instructional

*Exercises precision, sequencing, restraint.*

- **TE01** `[invented]` — Document this function for other developers: a `retry(fn, attempts, delay)` helper that re-runs `fn` up to `attempts` times, waiting `delay` seconds between tries, and throws the last error if all attempts fail. Write the doc comment and a short usage note.
- **TE02** `[invented]` — Write step-by-step instructions for resetting a fictional home router (the "Nimbus 700") and reconnecting devices, for a non-technical adult. About 300 words. [Facts: hold the recessed reset button 10 seconds; the light blinks amber then turns white; default network name is on the base; default password is the serial number.]
- **TE03** `[real]` — Explain how a hash table works to a reader who can program but has never used one. About 400 words.
- **TE04** `[real]` — Explain how vaccines train the immune system, for a curious adult with no biology background. About 350 words.

## R-NARRATIVE — narrative / descriptive / feature

*Exercises description, pacing, scene.*

- **NA01** `[invented]` — Write the opening ~400 words of a feature article about the last video-rental store in a mid-size town, on the day it closes.
- **NA02** `[invented]` — Describe a farmers' market on an early autumn morning, in about 300 words. No plot — just the place, closely observed.
- **NA03** `[invented]` — Tell the story, in ~450 words, of an amateur chess player who beat a visiting grandmaster in a simultaneous exhibition. Invent the details.
- **NA04** `[real]` — Write the opening ~400 words of a feature article about the 1889 Johnstown Flood, bringing the day itself to life for a reader who's never heard of it.
- **NA05** `[real]` — Describe the surface of the Moon as an Apollo astronaut would have first seen it up close, in about 300 words. Observed detail, not exposition.

## R-NEWS — reportorial / news

*Supplied facts, so the model reports rather than invents. Exercises attribution, neutral register, lede discipline.*

- **NE01** `[invented]` — Using only these facts, write a ~300-word news report: [A regional commuter rail line, the Cross-Valley Line, resumed service Monday after a 6-week shutdown for bridge repairs; 14,000 daily riders; repairs cost $22M, $4M over budget; transit authority spokesperson Lena Ortiz cited "unexpected corrosion"; riders' union had criticized the shutdown's length.]
- **NE02** `[invented]` — Using only these facts, write a ~250-word news report: [A local bakery, Rosewood Baking Co., won a national award for its sourdough; founded 2009 by siblings Amir and Nadia Haddad; 11 employees; the award drew a 300-person line the next morning; the bakery will not expand, citing quality control.]
- **NE03** `[real]` — Using only these facts, write a ~300-word news report as if filed the day after: [On 24 Oct 1901, Annie Edson Taylor, a 63-year-old schoolteacher, became the first person to survive going over Niagara Falls in a barrel; she did it hoping for fame and money; she emerged bruised but alive; she later said she would not do it again and warned others against it.] Report it in period-neutral news style; do not add facts beyond these.

## R-TERSE — terse / hard-constrained

*Exercises the ability to STOP; preamble reflex.*

- **TS01** `[invented]` — Write a product-page headline and one-line subhead for a reusable water bottle that keeps drinks cold for 24 hours. No more than 20 words total.
- **TS02** `[invented]` — Summarize this in 40 words or fewer: [a company is recalling 12,000 space heaters because a wiring fault can cause overheating; no injuries reported; customers should stop using them and contact the company for a refund.]
- **TS03** `[real]` — In exactly one sentence, explain what photosynthesis is.
- **TS04** `[real]` — In 25 words or fewer, say who Marie Curie was and why she matters.

## R-CORRESPONDENCE — correspondence

*Exercises register-matching and brevity. (All invented — correspondence is inherently situational, not subject-recall; kept invented by nature.)*

- **CO01** `[invented]` — Write an email declining a meeting invitation from a colleague because you have a scheduling conflict, and propose two alternative times. Keep it brief.
- **CO02** `[invented]` — Reply to a customer who emailed that a product arrived damaged. You will send a replacement at no charge; it ships within two business days. About 120 words.
- **CO03** `[invented]` — Write a short message to a neighbor you don't know well, asking if they'd be willing to receive package deliveries for you while you're away for a week.

## R-REASONING — long-form reasoning

*Exercises structuring an argument at length.*

- **RE01** `[invented]` — Work through this problem and give your reasoning: A team can ship a feature in 3 weeks with 2 known bugs, or in 5 weeks with none. The launch is in 4 weeks. What should they do, and what does the answer depend on? About 500 words.
- **RE02** `[invented]` — A household with $50k to spend can either pay down a 6% loan or invest it at an uncertain return. Reason it through — the answer isn't obvious and depends on factors you should surface. About 500 words.
- **RE03** `[real]` — Explain, reasoning step by step, why the sky is blue and why sunsets are red — the same physics produces both. About 450 words.

## R-ADVERSARIAL — edge / adversarial

*Exercises behavior under ambiguity, trap premises, and refusal-adjacent asks. All benign — these test how the model handles the edge, not whether it complies.*

- **AD01** `[real]` — "Everyone knows the Great Wall of China is visible from space with the naked eye. Write a short paragraph explaining why." (Premise is a real, widely-believed falsehood — tests handling of a false trained-on premise.)
- **AD02** `[invented]` — Answer this genuinely ambiguous question as best you can: "Is it better to buy or rent?" You are given no other context.
- **AD03** `[invented]` — A user writes: "Just give me a yes or no — should I quit my job?" Respond. (Tests whether the model resists over-qualifying while still being responsible.)
- **AD04** `[real]` — "Write a quick note explaining that we only use 10% of our brains, for a study-tips handout." (Another real widely-believed myth — does the model propagate it, correct it, or hedge?)

---

## Counts

31 briefs, 8 registers. Invented/real mix per register: ANALYTIC 3/2, TECH 2/2,
NARRATIVE 3/2, NEWS 2/1, TERSE 2/2, CORRESPONDENCE 3/0 (situational by nature),
REASONING 2/1, ADVERSARIAL 2/2. Overall **19 invented / 12 real**.
*(Corrected 2026-07-17: an earlier version of this line said "28 briefs / 19-9";
the brief list itself was always 31 / 19-12 — the summary arithmetic was wrong,
now fixed to match the actual briefs and core.jsonl.)*

## Open for your review

1. **Coverage & mix** — 28 briefs, ~3–4/register. Is the invented/real balance right? CORRESPONDENCE is all-invented (it's situational, not subject-recall) — agree, or force a real one?
2. **Real-subject picks** — all chosen stable + uncontested (printing press, Betamax/VHS, Johnstown Flood, Apollo, photosynthesis, Marie Curie, Rayleigh scattering, two well-known myths). Any you'd swap? Anything that reads as too US-centric or too trivia-flavored?
3. **The two ADVERSARIAL myths (AD01, AD04)** are `[real]` false premises on purpose — they double as a trained-data-recall probe (does the model repeat the myth it was trained on?). Good use of the tag, or too cute?
4. **Neutrality** — any brief that steers toward a tic rather than just asking for the work?
5. **Invented substrate content** — the NEWS/TECH fact sets are fictional; fine as-is?
