# LW Book 5 Playable Pipeline

Scope: first onboarding helper build for Book 5, *Shadow on the Sand*.

## Implemented

- Book metadata for `05sots`, with 400 numbered sections.
- Fresh Book 5 character setup.
- Book 4 -> Book 5 campaign handoff with one new Kai Discipline, Book 5 Gold, Book 5 equipment choices, carry-forward inventory, and mandatory Book 5 setup items.
- Place-aware Special Item safekeeping for Book 5 and later campaign use.
- Source-link route data generated from local Project Aon HTML.
- Project Aon SVGZ route graph comparison.
- First simple section automation data.
- First route checks, roll helpers, loot helpers, loss-choice helpers, and combat presets.
- Palace confiscation/restoration that handles Weapons, Backpack Items, Special Items, and Gold Crowns without disturbing safekeeping.
- Limbdeath poisoning as a continuing section-entry effect until cured.
- Sommerswerd loss/recovery and Book 5 finale helper.
- Aggregate validation wrapper that runs Book 5 checks plus Book 2-4 regressions.

## Validation

Current aggregate command:

```powershell
python .\testing\playtest_book5.py
```

Current result:

- Book 5 setup smoke passed.
- Book 5 section-flow baseline check passed.
- Book 5 automation-language audit check passed.
- Book 5 playable pipeline smoke passed.
- Book 4 aggregate playtest passed, including Book 2 and Book 3 regression smokes.

## Remaining Risk

- This is an onboarding helper build, not a release candidate.
- Real-route playtesting should be used to tune labels, missing edge helpers, achievements, and the strategy guide.
- The book text remains the source of truth whenever the helper and the page disagree.
