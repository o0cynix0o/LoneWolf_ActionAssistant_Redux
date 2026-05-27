# LW Book 1 Achievement Candidates

Date: 2026-05-27

Status: approved and implemented in issue #16, except the meta route-gauntlet candidate, which remains deferred.

These candidates use durable state where possible: completed book flags, section history, combat history, item history, inventory state, death/failure history, and route helper outcomes.

| Stable ID | Display name | Category | Trigger source | Implemented trigger | Backfill | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `lw1_complete` | Flight from the Dark | Story | Completed books | Book 1 completed | Yes | Implemented; keeps the existing starter ID instead of `lw1_first_clear`. |
| `lw1_reach_holmgard` | To The King's Citadel | Story | Section history | Section 350 reached or Book 1 completed | Yes | Implemented. |
| `lw1_clean_story_route` | Messenger To The King | Route | Section history | All sections in the checked end-to-end story route visited | Yes | Implemented from the issue #6 success route. |
| `lw1_first_blood` | First Blood | Combat | Combat history / summary | First recorded Book 1 combat victory | Yes | Existing starter achievement retained. |
| `lw1_gourgaz_victory` | Gourgaz Slayer | Combat | Combat history | Victory in section 255 combat | Yes | Implemented. |
| `lw1_princes_sword` | Prince's Sword | Item | Item history, inventory, or book summary | Take the section 255 weapon | Yes going forward | Implemented with durable item history for future loot pickups. |
| `lw1_vordak_gem_backlash` | Dark Gem Burn | Danger | Section history | Section 236 reached | Yes | Implemented. |
| `lw1_vordak_gem_failure` | Too Late To Turn Back | Failure | Death/failure history or section history | Section 292 failure recorded or reached | Yes | Implemented. |
| `lw1_capture_escape` | Captive No More | Route | Section history | Sections 162 and 258 reached | Yes | Implemented. |
| `lw1_capture_death` | No Way Out | Failure | Death history or section history | Section 127 death recorded or reached | Yes | Implemented. |
| `lw1_paid_ferry` | Paid Passage | Resource | Route journal or section history | Section 46 paid route to 246 used, with section-history fallback | Partial | Implemented; old saves without route journal can still backfill from visited sections. |
| `lw1_caravan_fare` | Caravan Fare | Resource | Route journal or section history | Section 12 paid route to 262 used, with section-history fallback | Partial | Implemented; old saves without route journal can still backfill from visited sections. |
| `lw1_backpack_lost` | Travel Light | Inventory | Section history | Gear-loss section reached: 174, 258, or 294 | Yes | Implemented. |
| `lw1_marsh_escape` | Out Of The Morass | Random | Section history | Section 21 plus section 189 or 312 reached | Partial | Implemented with section-history fallback rather than exact roll history. |
| `lw1_crystal_star_pendant` | Crystal Star Pendant | Item | Item history, inventory, or book summary | Take section 349 Special Item | Yes going forward | Implemented with durable item history for future loot pickups. |
| `lw1_long_road` | Long Road to Holmgard | Exploration | Section history / summary | Visit 75 or more unique Book 1 sections | Yes | Existing starter achievement retained. |
| `lw1_route_gauntlet` | Hard Road To Holmgard | Route | Section history | Hit one route-gauntlet family from issue #14 | Partial | Deferred; kept as internal playtest proof unless a meta achievement is wanted later. |

## Approval Notes

- The implemented batch is replay-focused without requiring completionist routes.
- Item achievements now record durable item history when an `add_item` automation succeeds.
- No manual rebuild button was added; automatic sync/backfill remains the standard.
- `testing\lwbook1_achievement_smoke.py` covers definitions, route/story unlocks, item history, paid routes, failure branches, and summary backfill.
