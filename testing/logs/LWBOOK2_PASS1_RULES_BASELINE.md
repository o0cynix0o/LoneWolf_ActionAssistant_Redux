# LW Book 2 Pass 1 Rules Baseline

Date: 2026-05-27

GitHub issue: #27

Scope: first pipeline slice for Book 2, *Fire on the Water*. This pass verifies the local source folder, scans rules/support pages, records start-state handoff requirements, and captures implementation rulings needed before Book 2 state changes are built.

This report records mechanics, file references, and section numbers only. Do not copy Book 2 prose into committed audit artifacts.

## Source Verification

- Local source folder: `books/lw/02fotw`
- Title page: `title.htm`
- Expected section files: 350
- Found section files: 350
- Missing section files: none
- Invalid section links in numbered sections: none
- Reachable from section 1: 350 / 350
- Source route links: 576
- Branch sections: 176
- Terminal sections by source-link scan: 19
- Section 1 source routes: 273, 160
- Section 350 is the Book 2 success ending and points forward to Book 3.

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

## Compared To Book 1

Book 2 keeps the familiar Book 1 rules shape:

- Combat Skill and Endurance use the same base random-number formulas for a standalone character.
- The same ten basic Kai Disciplines are listed.
- Combat uses the same Combat Results Table flow.
- Weapons, Backpack Items, Special Items, Meals, Gold Crowns, and the two-Weapon/eight-Backpack-Item limits remain core Action Chart fields.
- Hunting still exempts ordinary Meal requirements unless a section or annotation says otherwise.
- Healing Potion remains a Backpack Item and cannot be used immediately before combat.

Book 2 adds campaign handoff behavior:

- A character who completed Book 1 carries Combat Skill, Endurance, and existing Kai Disciplines into Book 2.
- That character chooses one additional Kai Discipline for Book 2.
- Weapons and Special Items from Book 1 may carry forward.
- Gold from Book 1 may carry forward and is added to the Book 2 starting gold roll.
- Book 2 gives a new mandatory Special Item: Seal of Hammerdal.
- Book 2 still expects the Map of Sommerlund to be recorded as a Special Item.
- Book 2 start equipment is a player choice rather than Book 1's monastery-find random roll.

## Book 2 Start-State Handoff

Clear start-state requirements:

- If continuing from Book 1, keep the character's base Combat Skill, maximum/current Endurance, five Book 1 Kai Disciplines, Weaponskill weapon, Weapons, Special Items, and Gold Crowns.
- Add exactly one new Kai Discipline that is not already known.
- Roll starting Gold as random digit + 10.
- If continuing from Book 1, add the Book 2 Gold roll to carried Gold Crowns.
- Add the Seal of Hammerdal as a Special Item.
- Ensure the Map of Sommerlund is recorded as a Special Item.
- Let the player choose any two items from the Book 2 armoury list:
  - Sword: Weapon
  - Short Sword: Weapon
  - Two Meals: two Backpack Meal entries
  - Chainmail Waistcoat: Special Item, +4 maximum/current Endurance effect
  - Mace: Weapon
  - Healing Potion: Backpack Item, restores 4 Endurance after combat
  - Quarterstaff: Weapon
  - Spear: Weapon
  - Shield: Special Item, +2 Combat Skill when used in combat
  - Broadsword: Weapon
- If the character already has Weapons from Book 1, allow one or both carried Weapons to be exchanged during the Book 2 armoury choice.

Standalone Book 2 remains possible from the rules text:

- Roll Combat Skill as random digit + 10.
- Roll Endurance as random digit + 20.
- Choose five Kai Disciplines.
- If Weaponskill is chosen, roll/record the Weaponskill weapon.
- Then apply the same Book 2 Gold, Seal of Hammerdal, Map, and armoury choices.

## New Rule/Model Needs

Book 2 needs these app changes before it is playable:

- Campaign transition flow from Book 1 completion into Book 2 setup.
- Book-specific setup wizard that can add one Kai Discipline without rebuilding the whole character.
- Armoury chooser that handles two Book 2 picks, including multi-item pick `Two Meals`.
- Weapon exchange support during setup.
- Book 2 starting Gold roll and Gold carry-over addition.
- Book 2 Special Item auto-adds for Seal of Hammerdal and Map of Sommerlund.
- Support for standalone Book 2 creation, if approved.
- Carry-over handling for Backpack availability and Backpack Items from Book 1, per ruling B2-R1.
- Hard Gold cap behavior at 50 Crowns, per ruling B2-R3.
- Special Item duplicate handling for items such as Chainmail Waistcoat and Map, pending implementation detail.

## Annotation And Errata Findings

The Book 2 support pages contain several gameplay-relevant annotations that must be included in later section audits:

- `footnotz.htm` section 31: if Lone Wolf has no Backpack, Rhygar can be treated as outfitting him with one.
- `footnotz.htm` sections 79 and 242: Sommerswerd is a weapon-like Special Item, grants its own Combat Skill bonus, can benefit from Weaponskill with Short Sword/Sword/Broadsword, and interacts with undead damage as directed by text/notes.
- `footnotz.htm` section 103: one Laumspur Meal can satisfy a required Meal and restore Endurance, or be used as ordinary Laumspur outside Meal timing.
- `footnotz.htm` section 113: Crystal Star Pendant appears to require both prior Banedon information and Sixth Sense.
- `footnotz.htm` section 181: confirms one Backpack worn and eight Backpack Items maximum.
- `footnotz.htm` section 194: Collector's Edition offers an alternative Special Item loss rule.
- `footnotz.htm` section 262: no Backpack means the Meal and Orange Potion cannot be carried.
- `footnotz.htm` section 289: loss of the Seal of Hammerdal changes the route for continuity.
- `footnotz.htm` section 290: poisoned food still requires another Meal or Endurance loss.
- `footnotz.htm` section 327: access papers do not need to be tracked as an Action Chart item and can be sold for all available Crowns if fewer than six are held.
- `errata.htm` section 91: merchant cargo requires a Backpack for Backpack Items; each Meal counts as one item.
- `errata.htm` section 103: if no Backpack, the item must be consumed immediately or abandoned.
- `errata.htm` section 106: Magic Spear is a weapon-like Special Item; Spear Weaponskill matters in the Helghast fight.
- `errata.htm` section 142: White Pass is a Special Item.
- `errata.htm` section 150: Hunting becomes available again after leaving the Wildlands.
- `errata.htm` section 196: Seal of Hammerdal is erased from the Action Chart.
- `errata.htm` section 238: free silver token is once-only and Cartwheel has a specific 0 placement rule.
- `errata.htm` section 263: Red Pass is a Special Item.
- `errata.htm` section 299: Project Aon selected a mixed route version for the Magic Spear/Rhygar choice; the local text should be treated as source of truth unless the user requests edition variants.
- `errata.htm` sections 313 and 338: Magic Spear is erased from the Action Chart.
- `errata.htm` section 314: Meal handling was clarified around offered food.
- `errata.htm` section 328: Crystal Star Pendant route should use durable item history, not only current inventory.
- `errata.htm` section 337: later gear recovery includes Weapons and Backpack Items.
- `errata.htm` section 346: Hunting cannot be used for Meal instructions while travelling through the Wildlands.

## Early Section-Scan Signal Counts

These are heuristic source-scan counts for planning only; they are not implemented automation coverage.

- combat: 33
- combat skill modifier: 10
- endurance gain: 12
- endurance loss: 40
- gold: 43
- inventory: 105
- kai discipline check: 67
- meal: 33
- random: 27
- route choice: 176
- single route: 155
- terminal death: 1
- terminal success: 1
- terminal unclassified: 17

## Next Implementation Slice

Recommended next issue after rulings:

1. Build Book 2 start-state data and setup UI.
2. Add tests for Book 1 completion -> Book 2 setup and standalone Book 2 setup if approved.
3. Generate `data/book2-section-flows.json` from source links.
4. Write `LWBOOK2_SECTION_FLOW_BASELINE.md`.
5. Begin the Book 2 automation-language scan from the signal categories above.

## Applied Rulings

- Book 1 Backpack Items carry over into Book 2.
- Standalone Book 2 creation is allowed only as a clearly labeled fresh start, not when continuing from Book 1.
- Gold Crowns cap hard at 50; excess Gold is not picked up.
- Section 194 follows Project Aon main text only for now.
- Access papers should become both an inventory item that can be removed and a story flag that can support route logic.

## Remaining Risk

- This pass did not implement Book 2 behavior.
- Section automations, combat presets, route checks, random helpers, achievements, and strategy docs remain future work.
- Later section-audit watch-items remain for Sommerswerd, Magic Spear, Crystal Star Pendant history, and Wildlands Hunting suppression.
