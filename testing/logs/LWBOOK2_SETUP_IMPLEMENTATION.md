# LW Book 2 Setup Implementation

Date: 2026-05-27

GitHub issue: #28

Scope: Book 2 setup/start-state implementation for *Fire on the Water*. This is the first code slice after the Book 2 rules and handoff scan. It does not implement Book 2 section automation, combat presets, route checks, achievements, or strategy-guide material.

## Implemented

- Added Book 2 metadata: `Fire on the Water`, folder `02fotw`, 350 sections.
- Added Book 2 Royal Armoury option data:
  - Sword
  - Short Sword
  - Two Meals
  - Chainmail Waistcoat
  - Mace
  - Healing Potion
  - Quarterstaff
  - Spear
  - Shield
  - Broadsword
- Added standalone Book 2 creation for a fresh Book 2 start.
- Added Book 1 completion -> Book 2 campaign continuation.
- Campaign continuation preserves:
  - Combat Skill
  - Endurance
  - Kai Disciplines
  - Weaponskill weapon
  - Weapons
  - Backpack availability
  - Backpack Items
  - Special Items
  - Gold Crowns
- Campaign continuation adds one new Kai Discipline.
- Book 2 setup adds the Seal of Hammerdal and ensures the Map of Sommerlund is recorded.
- Book 2 setup rolls starting Gold as random digit + 10 and hard-caps total Gold Crowns at 50.
- Book 2 setup applies two Royal Armoury choices.
- Weapon choices support setup-time Weapon exchange when the two-Weapon limit is already full.
- Chainmail Waistcoat adds +4 maximum/current Endurance only when it is newly added.
- The web completion screen now collects the Book 2 setup choices.
- The new-character screen can create a clearly labeled fresh Book 2 character.

## Rulings Applied

- Book 1 Backpack Items carry into Book 2.
- Standalone Book 2 is allowed as a fresh-start path only; campaign continuation does not create a new character.
- Gold caps hard at 50.
- Section 194 uses Project Aon main text only for now.
- Access papers will later be modeled as both an inventory item and story flag.

## Tests

Added:

```powershell
python .\testing\lwbook2_setup_smoke.py
```

Covered:

- Book 1 completion -> Book 2 transition.
- Backpack Item carry-over from Book 1.
- Book 2 Gold roll and 50-Crown cap.
- New Kai Discipline addition.
- Mandatory Seal of Hammerdal and Map of Sommerlund.
- Two Royal Armoury choices.
- Weapon exchange during setup.
- Standalone Book 2 creation.

## Remaining Work

- Run the full automation-language scan across all Book 2 sections.
- Implement Book 2 section effects, route checks, random helpers, combat presets, loss/exchange helpers, death/failure/completion, achievements, and strategy docs.
- Handle later watch-items for Sommerswerd, Magic Spear, Crystal Star Pendant durable history, and Wildlands Hunting suppression.
