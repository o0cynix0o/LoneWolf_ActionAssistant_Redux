# LW Book 3 Rulings Queue

Date: 2026-05-28

GitHub issue: #42

Scope: rulings needed before Book 3 start-state and section automation implementation.

## Applied Setup And Rules Rulings

| ID | Topic | User ruling | Implementation direction |
| --- | --- | --- | --- |
| B3-R1 | Backpack Item carry-over | Backpack Items always carry forward. | Carry Backpack availability and Backpack Items into Book 3, still enforcing the eight-item Backpack limit. |
| B3-R2 | Winter gear tracking | Story flags for now. | Track winter boots, tunic, fur-lined cloak, and mittens as Book 3 setup/story flags, not visible inventory. |
| B3-R3 | Map of Kalte | Special Item. | Add Map of Kalte as a Special Item during Book 3 setup. |
| B3-R4 | Ice-sledge food | Unless the text says yes, Meal instructions eat from the Backpack. | Default Meal automation consumes Backpack Meals or applies END loss; use sledge food only for explicitly supported text. |
| B3-R5 | Hunting in Kalte | Yes, Hunting is disabled for Meal automation in Kalte. | Suppress Hunting Meal exemption in Book 3 unless a later section explicitly restores it. |
| B3-R6 | Padded Leather Waistcoat stacking | Stacking rules later allow this. | Allow Padded Leather Waistcoat END bonus to stack with prior armour bonuses. |
| B3-R7 | Bone Sword Collector's Edition bonus | This is a special weapon. | Treat the section 4 Bone Sword as a special weapon with its Kalte-specific +1 CS behavior. |
| B3-R8 | Section 132 CE Meal option | Take a Meal from the Backpack or take END loss if there is no Meal. | Implement the CE-style section 132 Meal choice as Backpack Meal-or-END-loss behavior. |
| B3-R9 | Section 61 failure ending | Treat as a death in all ways except the death log should record that Lone Wolf did not die, he failed the mission. | Register a recoverable failure/death-state ending with failure copy and no future-book continuation. |
| B3-R10 | Red Laumspur | Treat as different from regular Laumspur. | Track Red Laumspur as a distinct item/flag; regular Laumspur does not qualify. |
| B3-R11 | Baknar oil | Use like Grey Star bug juice: takes a slot and has a use button that sets a flag. | Track Baknar oil as a usable Backpack item that sets a Book 3 flag when consumed. |
| B3-R12 | Helmet slot | Yes. | Treat helmets as a single worn slot; Silver Helm replaces/discards another helmet if required. |
| B3-R13 | Blue Stone Triangle | Durable item; it comes back up in later stories. | Track as a durable Special Item and preserve item history for later route checks. |

## Original Setup And Rules Questions

| ID | Topic | Source | Question | Default recommendation | Impact if wrong | Status |
| --- | --- | --- | --- | --- | --- | --- |
| B3-R1 | Backpack Item carry-over | `gamerulz.htm`, `equipmnt.htm` | Should Book 2 Backpack Items carry into Book 3? | No by strict Book 3 text, because it explicitly carries Weapons and Special Items but does not explicitly carry Backpack Items. | Inventory may either preserve useful series items or incorrectly bring supplies/items the book did not intend. | Answered |
| B3-R2 | Winter gear tracking | `equipmnt.htm` | Should winter boots, tunic, fur-lined cloak, and mittens appear as inventory/Special Items or be tracked as story setup only? | Story setup flag only unless a section checks/removes them. | Inventory can get noisy, but missing a later check would break automation. | Answered |
| B3-R3 | Map of Kalte | `equipmnt.htm` | Should Map of Kalte be a Special Item or a story flag? | Special Item, matching the way maps have been handled in the app. | Route checks or carry-forward may miss it if only stored as an invisible flag. | Answered |
| B3-R4 | Ice-sledge food | `equipmnt.htm` | Should Book 3 Meal automation spend sledge provisions before Backpack Meals while the sledge food is available? | Yes. Add a Book 3 story food supply/availability flag; consume Backpack Meals only when the sledge supply is unavailable or a section specifically calls for carried food. | Meal automation could wrongly remove Backpack Meals or wrongly avoid the -3 Endurance penalty. | Answered |
| B3-R5 | Hunting in Kalte | `discplnz.htm`, `equipmnt.htm` | Should Hunting suppress required Meals anywhere in Book 3? | No by default; globally suppress Hunting Meal exemption in Kalte unless a section explicitly says otherwise. | Hunting could accidentally cancel real Meal penalties in the icy desert. | Answered |
| B3-R6 | Padded Leather Waistcoat stacking | `equipmnt.htm` | If the player already has Chainmail Waistcoat or another worn armor item, can Padded Leather Waistcoat stack? | Do not stack body armor; choosing Padded Leather should replace or decline the current body armor. | Endurance maximum could inflate beyond intended gear rules. | Answered |
| B3-R7 | Bone Sword Collector's Edition bonus | `footnotz.htm` section 4 | Should the app support the CE +1 Combat Skill note for the specific Bone Sword, or main text only? | Main text only for now; record it as a normal Weapon until playtesting reaches it. | Combat may differ from Collector's Edition handling. | Answered |
| B3-R8 | Section 132 CE Meal option | `footnotz.htm` section 132 | Should the app offer the CE food-for-Endurance-loss option? | Main text only unless approved. | The player may miss an edition-variant survival option. | Answered |
| B3-R9 | Section 61 failure ending | `footnotz.htm` section 61 | Should section 61 be treated as a special mission-failure ending instead of death or success? | Yes. Mark as terminal failure: alive, no future-book continuation, repeat/rewind available. | The app might incorrectly unlock Book 4 or log it as death. | Answered |
| B3-R10 | Red Laumspur | `footnotz.htm` section 139 | Should Red Laumspur be tracked separately from regular Laumspur? | Yes. Use a distinct item/flag; regular Laumspur should not satisfy this check. | A regular potion could incorrectly unlock a route/effect. | Answered |
| B3-R11 | Baknar oil | `errata.htm` sections 8 and 91 | Should Baknar oil use inventory space? | No. Track as a Book 3-only story flag/status note with no Backpack or Special Item slot. | Inventory limits could be applied incorrectly. | Answered |
| B3-R12 | Helmet slot | `errata.htm` section 308 | Should Silver Helm force discarding another worn helmet? | Yes. Treat helmets as a single worn slot; taking Silver Helm discards another helmet if present. | Helmet bonuses/items could stack incorrectly. | Answered |
| B3-R13 | Blue Stone Triangle | `errata.htm` sections 64 and 84 | Should Blue Stone Triangle be a durable Special Item worn around the neck? | Yes. Track as a Special Item and preserve item history for route checks. | Later checks may fail if the item/history is missing. | Answered |

## Clear Defaults Unless Overridden

| Topic | Direction |
| --- | --- |
| New Discipline | Continuing from Book 2 adds one new Kai Discipline beyond the current campaign set. |
| Gold cap | Gold remains hard-capped at 50. Excess Gold is not picked up. |
| Special Rations | Record as one Meal and one Backpack slot. |
| Laumspur setup pick | Record as a Backpack Item with one 4-Endurance dose after combat only. |
| Weapon limit | Enforce two carried Weapons during setup and later item pickup. |
| Unsupported Book 4 | Until Book 4 is onboarded, Book 3 completion should show unsupported-next-book messaging rather than attempting a Book 4 transition. |

## Status

Book 3 source, route graph, section-flow, and automation-language scans are complete. Setup and rules rulings are answered, so implementation can begin.
