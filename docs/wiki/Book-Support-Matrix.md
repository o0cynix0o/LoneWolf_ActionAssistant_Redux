# Book Support Matrix

This matrix describes assistant support, not whether the book text exists locally.

|Book|Title|Reader Assets|Assistant Support|Achievements|Status|
|----|-----|-------------|-----------------|------------|------|
|1|Flight from the Dark|User-installed Project Aon HTML|Character creation, routes, automation, combat, rolls, loot, death recovery, saves|Implemented|Playable release candidate|
|2|Fire on the Water|User-installed Project Aon HTML|Setup/start-state only|Not started|Pipeline in progress; not playable yet|
|3|The Caverns of Kalte|Not wired yet|Not started|Not started|Future pipeline target|
|4|The Chasm of Doom|Not wired yet|Not started|Not started|Future pipeline target|
|5|Shadow on the Sand|Not wired yet|Not started|Not started|Future pipeline target|

## Book 1

Book 1 is the supported starting point:

- 350 section files expected in `books\lw\01fftd`
- Book 1 character creation
- Kai Disciplines and Weaponskill support
- source-link section routes
- route checks for Kai Discipline, item, Gold, and Endurance branches
- simple section automation
- required Meal handling with Hunting exemptions
- combat presets
- random helpers and staged roll support
- loot buttons and loss-choice helpers
- death and failure recovery
- Book 1 completion flow
- Book 1 achievements
- Book 1 strategy guide

## Book 2

Book 2 setup work has started. The app can prepare a fresh Book 2 character or continue a completed Book 1 save into Book 2, including the extra Kai Discipline, starting Gold, Seal of Hammerdal, carry-over inventory, and Royal Armoury choices.

Book 2 is not fully playable yet. Section automation, combat presets, route checks, achievements, and the strategy guide still need the rest of the pipeline.

## Book 3 And Later

Do not claim support for a later book until the book pipeline has been run.

Each later book needs:

- rules scan
- book handoff scan
- new-power and new-gear setup
- section-flow audit
- automation-language pass
- combat and random helper pass
- achievement planning and implementation
- strategy guide update
- smoke and route validation
