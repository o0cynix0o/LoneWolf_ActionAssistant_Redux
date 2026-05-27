# LW Book 1 Automation Ledger

Date: 2026-05-27

Scope: backfilled build ledger for implemented Book 1 assistant support.

This ledger was created after the first fourteen Book 1 milestones were already implemented. For future books, build this ledger before implementation. For Book 1, the checked-in data files remain the exact source of truth.

## Data Sources

- `data/book1-simple-automations.json`
- `data/book1-section-flows.json`
- `testing/lwbook1_section_flow_audit.py`
- `testing/lwbook1_automation_language_audit.py`

## Implemented Support Summary

| Rule type | Trigger timing | Sections | App support | Acceptance coverage | Status |
| --- | --- | --- | --- | --- | --- |
| Character creation | Book start | Book 1 start | Book 1 CS, END, Kai Disciplines, Weaponskill, starting gear, Gold, and monastery find | Character creation tests and playtests | Implemented |
| Required Meals | On entry | 37, 130, 147, 168, 184, 235, 300 | Meal consumption with Hunting exemption and Laumspur fallback | Simple automation, branch, and route gauntlet smokes | Implemented |
| Direct END loss/gain | On entry or roll outcome | 36, 76, 119, 144, 146, 147, 158, 166, 188, 203, 212, 276, 304, 308, 313, 343 | Stat automation and route checks where needed | Simple, random/recovery, route gauntlet | Implemented |
| Gold changes and paid routes | Loot, entry, or route choice | 12, 33, 46, 62, 76, 94, 124, 184, 197, 242, 263, 269, 291, 304, 315, 319 | Gold gain/loss plus route-cost actions | Automation-language and route gauntlet smokes | Implemented |
| Loot buttons | After player chooses to take item | 15, 20, 62, 113, 124, 148, 164, 184, 193, 197, 199, 243, 255, 263, 267, 290, 291, 305, 307, 315, 319, 346, 347, 349 | Loot controls with Backpack, Weapon, and Special Item routing | Simple, automation-language, and route gauntlet smokes | Implemented |
| Gear loss | On entry or roll outcome | 162, 174, 188, 205, 258, 274, 294 | Backpack/Weapon discard and Backpack availability handling | Simple, random/recovery, branch, and route gauntlet smokes | Implemented |
| Player-choice loss/exchange | Prompt choice | 144, 277, 307 | Loss-choice and weapon-exchange helpers | Healing/loss and player-choice aftermath smokes | Implemented |
| Route checks | Route-check calculation | 1, 4, 9, 12, 18, 19, 23, 37, 46, 52, 70, 71, 83, 88, 91, 105, 125, 128, 151, 162, 167, 172, 173, 175, 200, 203, 211, 222, 235, 242, 272, 303, 308, 311, 334, 341 | Kai Discipline, item, Gold, and END checks | Route/random, automation-language, end-to-end, and route gauntlet smokes | Implemented |
| Random roll helpers | After random digit | 2, 7, 17, 22, 36, 44, 49, 89, 158, 160, 188, 205, 226, 237, 275, 279, 294, 302, 314, 337 | Roll result display, routing, and same-section side effects | Route/random and random/recovery smokes | Implemented |
| Staged roll helper | Multi-stage random flow | 21 | Section-visit staged roll state and death handling | Section 21 staged smoke | Implemented |
| Combat presets | Combat start/round/victory | 17, 29, 34, 43, 55, 63, 72, 112, 133, 136, 138, 169, 170, 180, 191, 208, 220, 227, 229, 231, 246, 253, 255, 260, 283, 336, 339, 340, 342 | Presets, modifiers, immunity, evasion, round limits, victory routing, multi-enemy queues | Combat smoke and combat edge playtest | Implemented |
| Death/failure/success endings | On entry or staged roll outcome | 21, 53, 54, 60, 108, 127, 154, 185, 219, 234, 259, 271, 286, 292, 306, 309, 327, 350 | Death/failure state, checkpoint recovery, Book 1 completion | Simple, branch, end-to-end, and route gauntlet smokes | Implemented |
| Kai Healing helper | Per eligible section visit | Non-combat sections for characters with Healing | One END per eligible section visit, blocked in combat | Healing/loss smoke | Implemented |

## Manual Or Deferred

- Achievement definitions are candidates only until approved.
- Browser ergonomics still require a manual pass before packaging.
- Future route playtests may identify isolated manual helpers, but the automation-language scan currently has no uncovered categories.
