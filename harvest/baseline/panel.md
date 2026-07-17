# Identification Panel — Index

Human-readable index over `panel.jsonl`, which is the source of truth
(one measured text per line: provenance + length-normalized metrics, produced
by `measure_density.py`). **No source text is stored** — only citation,
publication metadata, the prose-boundary note, and the numbers.

**Role (working design):** the panel is **not** the baseline. It is (1) the
craft-study input the exemplar generator reads to write craft-strong exemplars,
and (2) the real-writing reference a discovered candidate is grounding-checked
against. The synthetic exemplar reference lives in `exemplars/` (being rebuilt
against the new battery — see `../battery/COVERAGE_SPEC.md`). Regenerate this
index from the JSONL; don't hand-edit rows here.

**Pass version:** `2026-07` (in progress). Measured with `measure_density.py` v0.1.0.

## Screening recap (all required per text)

Contamination guard (pre-2023 **or** documented stronger authorship guarantee — `README.md §1`) · human-authorship confidence · genre fit · editorial excellence. **Diversity cap: ~2 texts per idiolect-source per genre** — the named writer, or the org/agency when unsigned or agency-driven. Org alone is not capped.

## Counts by genre (14 texts total; target 15–25/genre)

| Genre | Texts | Distinct idiolects | Toward target |
|---|---|---|---|
| appeal | 1 | 1 | ●○○○○○○○○○○○○○○ |
| editorial | 3 | 3 | ●●●○○○○○○○○○○○○ |
| feature | 10 | 8 | ●●●●●●●●●●○○○○○ |

> ✅ No idiolect-cap breach: no single writer/voice exceeds ~2 texts in any genre. (Note the earlier org-level Fast Company concentration is *not* a breach under the writer-keyed cap — those 8 texts are 6 distinct writers.)

## Index

| ID | Citation | Author | Date | Genre | Words | Date basis |
|---|---|---|---|---|---|---|
| APP-01 | SOFII: Camp Oochigeas mid-value direct mail appeal | John Lepp/Agents of Good;  | 2018 | appeal | 597 | pre-2023 ✓ |
| ED-01 | The Atlantic, "The See-No-Evil Supreme Court" | Adam Serwer | 2026-07-14 | editorial | 1471 | authorship ⚑ |
| ED-02 | The Atlantic, "Generative AI Is an Engineering Disas | Alex Reisner | 2026-07-14 | editorial | 1693 | authorship ⚑ |
| ED-03 | The New York Times, "Weaponizing the First Amendment | Adam Liptak | 2018-06-30 | editorial | 2200 | pre-2023 ✓ |
| FE-01 | The Atlantic, "How the Elite See Rome" | Cullen Murphy | 2026-08 | feature | 4312 | authorship ⚑ |
| FE-02 | Fast Company, "Is Kyrie Irving's rant about his Nike | Jeff Beer | 2021-07-30 | feature | 674 | pre-2023 ✓ |
| FE-03 | Fast Company, "The cardboard real estate boom is her | Nate Berg | 2021-07-30 | feature | 729 | pre-2023 ✓ |
| FE-04 | Fast Company, "The hidden way the Tokyo Olympics cou | Nate Berg | 2021-07-29 | feature | 988 | pre-2023 ✓ |
| FE-05 | Fast Company, "Why Nike infused its Olympic designs  | Mark Wilson | 2021-07-28 | feature | 979 | pre-2023 ✓ |
| FE-06 | Fast Company, "Why U.K. bus stops suddenly smell lik | Jeff Beer | 2021-07-29 | feature | 274 | pre-2023 ✓ |
| FE-07 | Fast Company, "Management changed productivity measu | Lydia Dishman | 2021-09-30 | feature | 1232 | pre-2023 ✓ |
| FE-08 | Fast Company, "Soman Chainani is revolutionizing YA  | KC Ifeanyi | 2021-09-30 | feature | 1131 | pre-2023 ✓ |
| FE-09 | Fast Company, "Will mental health resources evaporat | Jared Lindzon | 2021-09-30 | feature | 1173 | pre-2023 ✓ |
| FE-10 | Pitchfork, "Káryyn's Curiously Powerful Experimental | Jazz Monroe | 2017-09-07 | feature | 2004 | pre-2023 ✓ |

⚑ = post-2023, admitted on an authorship guarantee; see the row's `date_basis` in `panel.jsonl` (ED-02's is an explicitly-labeled inference).

<!-- Next: grow editorial and the untouched genres; seed `news` (extractor needs archive.ph + NYT-interactive paths). Envelope math waits for ~15-25/genre, idiolect-cap respected. -->
