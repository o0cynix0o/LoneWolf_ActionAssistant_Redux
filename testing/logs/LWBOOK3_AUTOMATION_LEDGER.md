# LW Book 3 Automation Ledger

Date: 2026-05-28

GitHub issue: #42

Scope: current Book 3 automation build ledger. This is the build handoff for the next Book 3 route-helper slice.

## Implemented Rows

| Section | Trigger timing | Rule type | Preconditions | State change | Player-facing label | Receipt location | Test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | Manual helper | Loot | Player chooses item | Add Bone Sword as Special Item | Take Bone Sword | Status/loot receipt | `lwbook3_playable_pipeline_smoke.py` |
| 4 | Manual helper | Loot | Player chooses item | Add Blue Stone Disc as Special Item | Take Blue Stone Disc | Status/loot receipt | `lwbook3_playable_pipeline_smoke.py` |
| 8 | Manual helper | Loot/use item | Player chooses item, then uses it | Add Baknar Oil Backpack item; use sets `baknarOilApplied` | Take Baknar Oil | Status/loot/use receipt | `lwbook3_playable_pipeline_smoke.py` |
| 61 | On entry | Failure ending | None | Register recoverable mission failure without killing Lone Wolf | Mission failed | Death/failure screen | `lwbook3_playable_pipeline_smoke.py` |
| 84 | Manual helper | Loot | Player chooses item | Add Blue Stone Triangle as durable Special Item | Take Blue Stone Triangle | Status/loot receipt | pending route play |
| 91 | Manual helper | Loot/use item | Player chooses item, then uses it | Add Baknar Oil Backpack item; use sets `baknarOilApplied` | Take Baknar Oil | Status/loot/use receipt | covered by item-use smoke |
| 132 | On entry | Meal | Backpack Meal available or not | Remove one Meal, otherwise lose 3 END | Use a Backpack Meal or lose END | Status section | `lwbook3_playable_pipeline_smoke.py` |
| 139 | Route check | Item check | Red Laumspur distinct from normal Laumspur | Route to Red Laumspur result or no-potion result | Red Laumspur check | Choices route-check area | `lwbook3_playable_pipeline_smoke.py` |
| 144 | On entry | Death ending | None | Register terminal death | Terminal death | Death screen | pending direct smoke in later gauntlet |
| 194 | Manual helper | Loot | Player chooses item | Add Silver Helm | Take Silver Helm | Status/loot receipt | pending route play |
| 303 | After route button | Item use/loss | Player routes through Ornate Silver Key branch | Remove Ornate Silver Key | Use Ornate Silver Key | Status route receipt | pending route play |
| 308 | Manual helper | Loot | Player chooses item | Add Silver Helm | Take Silver Helm | Status/loot receipt | pending route play |
| 321 | Manual helper | Loot | Player chooses item | Add Blue Stone Triangle as durable Special Item | Take Blue Stone Triangle | Status/loot receipt | pending route play |
| 350 | On entry | Completion | None | Mark Book 3 complete | Complete Book 3 | Completion screen | `lwbook3_playable_pipeline_smoke.py` |

## Combat Rows

First combat presets are implemented for sections 14, 32, 68, 78, 83, 88, 89, 99, 103, 106, 108, 123, 137, 138, 147, 158, 161, 164, 180, 200, 208, 241, 259, 260, 263, 265, 270, 296, 304, and 343.

Combat preset coverage includes:

- multi-enemy queues
- Helghast Mindblast immunity
- no-Mindshield per-round END loss
- partial Mindblast resistance
- Sommerswerd doubled damage against undead where confirmed
- evasion routes where confirmed
- flawless/wounded victory routes for Kalkoth venom sections
- timed victory routing for Akraa'Neonor sections

## Needs Ledger Review

The automation-language scan still lists many Book 3 candidate sections. The next pass should convert the remaining signal sections into:

- implemented automation
- manual helper
- reviewed no automation
- queued ambiguity

Priority areas:

- random helpers
- remaining END loss/gain sections
- remaining Meal sections
- remaining item pickup/loss sections
- all Discipline and item route checks
- Gold gains/costs
- achievement candidates
