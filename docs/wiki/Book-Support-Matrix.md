# Book Support Matrix

This matrix describes assistant support, not whether the book text exists locally.

|Book|Title|Reader Assets|Assistant Support|Achievements|Status|
|----|-----|-------------|-----------------|------------|------|
|1|Flight from the Dark|User-installed Project Aon HTML|Character creation, routes, automation, combat, rolls, loot, death recovery, saves|Implemented|Playable release candidate|
|2|Fire on the Water|User-installed Project Aon HTML|Setup, routes, automation, combat, rolls, loot, death recovery, completion, saves|Implemented|Playable helper build; needs more real-route time|
|3|The Caverns of Kalte|User-installed Project Aon HTML|Setup, source routes, partial section helpers, partial combat, death/failure recovery, completion, saves|Not started|Onboarding helper build; needs more route work|
|4|The Chasm of Doom|User-installed Project Aon HTML|Setup, source routes, first section helpers, combat presets, item-loss helpers, death recovery, completion, saves|Not started|Onboarding helper build; needs real-route testing|
|5|Shadow on the Sand|User-installed Project Aon HTML|Setup, source routes, first section helpers, combat presets, item-loss helpers, safekeeping, death/failure recovery, completion, saves|Not started|Onboarding helper build; needs real-route testing|

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

Book 2 has the playable helper pipeline in place:

- 350 section files expected in `books\lw\02fotw`
- fresh Book 2 creation or completed Book 1 campaign handoff
- extra Kai Discipline, starting Gold, Seal of Hammerdal, carry-over inventory, and Royal Armoury choices
- source-link section routes
- route checks for Kai Discipline, item, pass, Gold, and Endurance branches
- simple section automation
- required Meal handling, including places where Hunting does not help
- combat presets for checked Book 2 combats
- random helpers for straightforward rolls
- loot and shop buttons
- death recovery
- Book 2 completion flow
- Book 2 achievements
- Book 2 strategy guide

The next useful step is more real-route time. The helper coverage is there; now we want ordinary play to shake out anything that feels clumsy.

## Book 3

Book 3 has the first onboarding helper build in place:

- 350 section files expected in `books\lw\03tcok`
- fresh Book 3 creation or completed Book 2 campaign handoff
- extra Kai Discipline, starting Gold, Map of Kalte, winter-gear story flags, carry-over Backpack Items, and two equipment choices
- source-link section routes checked against the Project Aon SVG route graph
- section 61 mission-failure recovery, section 132 Meal handling, and section 350 completion
- first loot helpers for Bone Sword, Blue Stone Disc, Baknar Oil, Blue Stone Triangle, Silver Helm, and related special items
- first combat presets for the main scanned Book 3 fights
- Red Laumspur is treated separately from regular Laumspur
- Baknar Oil is a usable Backpack item that sets a Book 3 flag

This is an onboarding helper build, not a release candidate. The next useful step is more route work: random helpers, wider route checks, remaining section automations, achievements, and real playtesting.

## Book 4

Book 4 has the first onboarding helper build in place:

- 350 section files expected in `books\lw\04tcod`
- fresh Book 4 creation or completed Book 3 campaign handoff
- extra Kai Discipline, starting Gold, Map of the Southlands, Badge of Rank, carry-over Backpack Items, and six equipment choices
- Padded Leather Waistcoat and Chainmail Waistcoat can stack; duplicate chainmail does not stack
- source-link section routes checked against the Project Aon SVG route graph
- first route checks, random helpers, optional loot buttons, and section 22 item-loss picker
- first combat presets for the scanned Book 4 fights, including underwater oxygen timing and one-round comparison routing
- regional Meal handling where Hunting helps normally, but not in the Wildlands or Maaken Mines
- section 350 completion and Dagger of Vashna carry-forward

This is ready for playtesting, not release packaging. The next useful step is a human route pass that turns clumsy labels, missing edge helpers, and achievement candidates into the next implementation slice.

## Book 5

Book 5 has the first onboarding helper build in place:

- 400 section files expected in `books\lw\05sots`
- fresh Book 5 creation or completed Book 4 campaign handoff
- extra Kai Discipline, starting Gold, Map of Vassagonia, carry-over Backpack Items, and up to four equipment choices
- Special Item safekeeping for items left at the monastery before the adventure begins
- source-link section routes checked against the Project Aon SVG route graph
- first route checks, random helpers, optional loot buttons, and item-loss pickers
- first combat presets for the scanned Book 5 fights, including timed rules, half-recovery fights, and Sommerswerd-specific exceptions
- Book 5-specific Blood poisoning, Sommerswerd loss/recovery, and final Kai Master completion helpers
- section 400 completion and Book of the Magnakai carry-forward

This is ready for playtesting, not release packaging. The next useful step is a human route pass that turns clumsy labels, missing edge helpers, and achievement candidates into the next implementation slice.

## Book 6 And Later

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
