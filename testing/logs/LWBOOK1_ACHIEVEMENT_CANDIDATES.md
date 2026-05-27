# LW Book 1 Achievement Candidates

Date: 2026-05-27

Status: candidate list only. Do not implement until approved.

These candidates use durable state where possible: completed book flags, section history, combat history, inventory state, death/failure history, and route helper outcomes.

| Stable ID | Display name | Category | Trigger source | Candidate trigger | Backfill | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `lw1_first_clear` | Flight From The Dark | Story | Completed books | Book 1 completed | Yes | Core completion achievement. |
| `lw1_reach_holmgard` | To The King's Citadel | Story | Section history | Section 350 reached | Yes | Same event as completion, but can be a route milestone if desired. |
| `lw1_clean_story_route` | Messenger To The King | Route | Section history | Complete the checked story route used by the end-to-end playtest | Partial | Requires exact route-family definition before implementation. |
| `lw1_gourgaz_victory` | Gourgaz Slayer | Combat | Combat history | Victory in section 255 combat | Yes | Strong combat milestone. |
| `lw1_princes_sword` | Prince's Sword | Item | Inventory or loot history | Take the section 255 weapon | Partial | Inventory can change later; durable loot history would be better. |
| `lw1_vordak_gem_backlash` | Dark Gem Burn | Danger | Section history / automation | Section 236 reached | Yes | Route gauntlet covers this outcome. |
| `lw1_vordak_gem_failure` | Too Late To Turn Back | Failure | Death/failure history | Section 292 failure recorded | Yes | Candidate failure/recovery achievement. |
| `lw1_capture_escape` | Captive No More | Route | Section history | Sections 162 and 258 reached | Yes | Mind Over Matter escape path. |
| `lw1_capture_death` | No Way Out | Failure | Death history | Section 127 death recorded | Yes | Candidate death-archive achievement. |
| `lw1_paid_ferry` | Paid Passage | Resource | Section history / route action | Section 46 paid route to 246 used | Partial | Route-action history would make this cleaner. |
| `lw1_caravan_fare` | Caravan Fare | Resource | Section history / route action | Section 12 paid route to 262 used | Partial | Route-action history would make this cleaner. |
| `lw1_backpack_lost` | Travel Light | Inventory | Inventory state / section history | Gear-loss section reached: 174, 258, or 294 | Yes | Needs care because later gear recovery may alter current inventory. |
| `lw1_marsh_escape` | Out Of The Morass | Random | Staged roll history | Survive section 21 staged roll | Partial | Requires durable roll history for exact backfill. |
| `lw1_crystal_star_pendant` | Crystal Star Pendant | Item | Inventory or loot history | Take section 349 Special Item | Partial | Inventory can change later; durable loot history would be better. |
| `lw1_route_gauntlet` | Hard Road To Holmgard | Route | Section history | Hit one route-gauntlet family from issue #14 | Partial | Better as internal playtest proof unless user wants meta achievements. |

## Approval Notes

- This list is intentionally conservative.
- Before implementation, decide whether Book 1 achievements should be story-only, replay-focused, or full completionist.
- Several item achievements need durable loot history if they should remain unlocked after later item loss.
- Do not add a manual rebuild button; automatic sync/backfill should be the standard.
