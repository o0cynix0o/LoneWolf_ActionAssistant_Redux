# LW Book 3 Pass 1 Rules Baseline

Date: 2026-05-28

GitHub issue: #42

Scope: first pipeline slice for Book 3, *The Caverns of Kalte*. This pass verifies the local source folder, scans rules/support pages, records start-state handoff requirements, cross-checks the Project Aon route graph, and captures rulings needed before Book 3 behavior is built.

This report records mechanics, file references, and section numbers only. Do not copy Book 3 prose into committed audit artifacts.

## Source Verification

- Local source folder: `books/lw/03tcok`
- Title page: `title.htm`
- Expected section files: 350
- Found section files: 350
- Missing section files: none
- Invalid section links in numbered sections: none
- Reachable from section 1: 350 / 350
- Source route links: 603
- Branch sections: 209
- Terminal sections by source-link scan: 21
- Section 1 source routes: 160, 273
- Section 350 is the Book 3 success ending and points forward to Book 4.
- Project Aon route graph: `https://www.projectaon.org/en/svg/lw/03tcok.svgz`
- SVG route graph status: available, 350 nodes, 603 edges, no differences against the local source-link graph.

Support pages present:

- `gamerulz.htm`
- `discplnz.htm`
- `equipmnt.htm`
- `action.htm`
- `cmbtrulz.htm`
- `crsumary.htm`
- `crtable.htm`
- `random.htm`
- `levels.htm`
- `kaiwisdm.htm`
- `errata.htm`
- `footnotz.htm`
- `tssf.htm`

## Compared To Book 2

Book 3 keeps the familiar Kai-series rules shape:

- Combat Skill and Endurance use the same base random-number formulas for a standalone character.
- The same ten basic Kai Disciplines are listed.
- Combat uses the same Combat Results Table flow.
- Weapons, Backpack Items, Special Items, Meals, Gold Crowns, and the two-Weapon/eight-Backpack-Item limits remain core Action Chart fields.
- Only one Weapon may be used at a time in combat.
- Laumspur still restores 4 Endurance after combat and cannot be used immediately before combat.

Book 3 changes the campaign and environment model:

- A continuing character carries Combat Skill, Endurance, current Kai Disciplines, Weapons, and Special Items into Book 3.
- Backpack Items carry forward by user ruling, even where Book 3 setup text names Weapons and Special Items explicitly.
- A continuing character should add one new Kai Discipline beyond the current campaign set.
- Gold from previous books can be added to the Book 3 starting gold roll, still capped at 50.
- Book 3 gives winter expedition gear, a Map of Kalte, and access to an equipment list with two picks.
- Hunting is not a reliable Meal exemption in Kalte because the book identifies Kalte as an icy desert.
- Meal handling defaults to Backpack Meals or Endurance loss by user ruling; only explicit section text should use the ice-sledge food supply instead.

## Book 3 Start-State Handoff

Clear start-state requirements:

- If continuing from Book 2, keep the character's base Combat Skill, maximum/current Endurance, known Kai Disciplines, Weaponskill weapon, Weapons, Special Items, Gold Crowns, history flags, achievements, and relevant combat log.
- Add exactly one new Kai Discipline that is not already known for the Book 3 campaign path.
- Roll Book 3 starting Gold as random digit + 10.
- Add the Book 3 Gold roll to carried Gold Crowns, then enforce the hard 50-Crown cap.
- Add the Map of Kalte.
- Note winter expedition gear: winter boots, tunic, fur-lined cloak, and mittens.
- Let the player choose any two items from the Book 3 equipment list:
  - Sword: Weapon
  - Short Sword: Weapon
  - Padded Leather Waistcoat: Special Item, +2 Endurance
  - Spear: Weapon
  - Mace: Weapon
  - Warhammer: Weapon
  - Axe: Weapon
  - Potion of Laumspur: Backpack Item, restores 4 Endurance after combat
  - Quarterstaff: Weapon
  - Special Rations: one Meal
  - Broadsword: Weapon
- Enforce the two-Weapon limit and eight-Backpack-Item limit during setup.

Standalone Book 3 remains possible from the rules text:

- Roll Combat Skill as random digit + 10.
- Roll Endurance as random digit + 20.
- Choose five Kai Disciplines.
- If Weaponskill is chosen, roll/record the Weaponskill weapon.
- Then apply the same Book 3 Gold, Map, winter gear, and two equipment choices.

## New Rule/Model Needs

Book 3 needs these app changes before it is playable:

- Campaign transition flow from Book 2 completion into Book 3 setup.
- Book-specific setup wizard that adds one Kai Discipline without rebuilding the whole character.
- Book 3 equipment chooser with two picks and weapon-limit handling.
- Gold carry-over plus Book 3 starting Gold roll with the hard 50-Crown cap.
- Book 3 Special Item/flag handling for Map of Kalte and winter expedition gear.
- Book 3 Meal context where Hunting is suppressed in Kalte.
- Ice-sledge food/provisions handling only where section text explicitly says the sledge food is used.
- Section-flow data from `data/book3-section-flows.json`.
- Route graph check from `testing/logs/LWBOOK3_ROUTE_GRAPH_CHECK.md`.
- Automation ledger, combat/random audit, route audit, achievements scan, UI-readiness scan, and playtest gauntlet after rulings.

## Annotation And Errata Findings

The Book 3 support pages contain gameplay-relevant annotations that must be included in later section audits:

- `footnotz.htm` section 4: Bone Sword is normally a Weapon; the Collector's Edition gives a Kalte-only +1 Combat Skill note for one specific Bone Sword.
- `footnotz.htm` section 61: mission-failure ending where Lone Wolf survives but has not completed the adventure and cannot continue to future adventures.
- `footnotz.htm` section 132: Collector's Edition allows consuming enough food for 1 Meal to avoid the Endurance loss.
- `footnotz.htm` section 139: Red Laumspur is a distinct concentrated potion; regular Laumspur does not qualify.
- `footnotz.htm` section 350: identifies the portal as a Shadow Gate.
- `errata.htm` equipment: only one Weapon at a time in combat; Laumspur cannot be used immediately before combat.
- `errata.htm` sections 8 and 91: Baknar oil is noted on the Action Chart, uses no space, and applies only in this adventure.
- `errata.htm` section 10: each liquid may be examined only once.
- `errata.htm` section 16: player chooses which Backpack Items are destroyed; if only one exists, that single item is destroyed.
- `errata.htm` section 18: erase one Weapon or weapon-like Special Item.
- `errata.htm` section 26: Dagger and Mace may be kept as Weapons.
- `errata.htm` section 32: carry forward prior Kalkoth damage into a later Kalkoth fight.
- `errata.htm` section 41: Blue Stone Triangle may still be kept.
- `errata.htm` section 55: the listed loss is a Combat Skill loss.
- `errata.htm` section 64: north tunnel route was corrected to section 321.
- `errata.htm` sections 79 and 157: erase the used potion from the Action Chart.
- `errata.htm` section 84: Blue Stone Triangle is a Special Item worn around the neck.
- `errata.htm` section 88: only picking 9 for the extra random pick causes death.
- `errata.htm` sections 132, 176, 212, 226, and 331: some lowercase meal references are not Action Chart Meals.
- `errata.htm` sections 138 and 263: effects apply even when attempting to evade.
- `errata.htm` section 150: Firesphere choice order was adjusted.
- `errata.htm` sections 194, 303, and 326: Silver Helm, Sixth Sense, and Ornate Silver Key behavior need route/item handling; section 303 erases the Ornate Silver Key.
- `errata.htm` section 252: bridge state can depend on earlier route history.
- `errata.htm` section 308: if wearing another helmet, discard it to keep the Silver Helm.

## Early Section-Scan Signal Counts

These are heuristic source-scan counts for planning only; they are not implemented automation coverage.

- combat: 41
- combat skill modifier: 6
- endurance gain: 7
- endurance loss: 51
- gold: 6
- inventory: 80
- kai discipline check: 62
- meal: 43
- random: 33
- route choice: 209
- single route: 120
- terminal death: 1
- terminal success: 1
- terminal unclassified: 19

The separate automation-language audit found 202 sections with at least one automation signal.

## Next Implementation Slice

Recommended next issue slice after rulings:

1. Build Book 3 metadata, setup state, campaign transition, and standalone setup.
2. Add Book 3 carry-forward, new Discipline, Gold cap, Map, winter gear, sledge-food, and equipment choice tests.
3. Convert the section-flow baseline into playable route helpers.
4. Build the Book 3 automation ledger from the language audit.
5. Implement clear combat presets, random helpers, inventory effects, route checks, and completion/failure behavior.
6. Run an automated route gauntlet before handing the book to user playtesting.

## Remaining Risk

- This pass did not implement Book 3 behavior.
- Book 3 carry-forward has open rulings around Backpack Items, winter gear tracking, food supply, armor stacking, and Collector's Edition notes.
- Setup and rules rulings are answered; later section-by-section playtesting may still reveal smaller route-specific questions.
- Section automations, combat presets, route checks, random helpers, achievements, strategy docs, and UI polish remain future work.
