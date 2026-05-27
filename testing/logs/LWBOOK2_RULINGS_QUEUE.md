# LW Book 2 Rulings Queue

Date: 2026-05-27

GitHub issue: #27

Scope: rulings needed before Book 2 start-state and section automation implementation.

## Applied Setup Rulings

| ID | Topic | User ruling | Implementation direction |
| --- | --- | --- | --- |
| B2-R1 | Book 1 Backpack Items | Backpack Items should carry over from Book 1 because some Book 1 items matter later in the series. | Carry Backpack availability and Backpack Items into Book 2 when transitioning from a completed Book 1 save, still enforcing the eight-item Backpack limit. |
| B2-R2 | Standalone Book 2 start | Standalone Book 2 is allowed only when Book 2 is the first book the player has read; if coming from Book 1, no new character is needed. | Support two setup paths: campaign transition from Book 1 and clearly labeled fresh standalone Book 2 creation. |
| B2-R3 | Gold cap during transition | Gold caps hard at 50; if the cap is reached, no additional Gold is picked up. | Clamp Gold Crowns to 50 whenever Book 2 starting/carry-over Gold is applied and show a receipt when Gold is lost to the cap. |
| B2-R4 | Collector's Edition Special Item loss option | Follow Project Aon main text only for now, until section 194 is reached in play and reviewed. | Implement main-text behavior only; keep the CE note documented as a future/manual consideration. |
| B2-R5 | Access papers | Track as a story flag and an inventory item that can be removed, until the section is play-reviewed. | Add an item/flag pattern when section automation reaches access papers: inventory can show/remove the papers, while story flag can support route logic. |

## Original Setup Questions

| ID | Topic | Source | Question | Default Recommendation |
| --- | --- | --- | --- | --- |
| B2-R1 | Book 1 Backpack Items | `gamerulz.htm`, `equipmnt.htm` | Should Book 1 Backpack Items carry into Book 2, or should the transition carry only Weapons, Special Items, Gold, stats, and Disciplines as the Book 2 rules explicitly list? | Follow Book 2 text strictly: do not carry Book 1 Backpack Items into Book 2 unless a later rule gives them back. |
| B2-R2 | Standalone Book 2 start | `gamerulz.htm`, `discplnz.htm`, `equipmnt.htm` | Should the app allow starting Book 2 directly with fresh rolls and five Disciplines, or require a completed Book 1 save for the campaign path? | Support both, but label standalone Book 2 clearly as a fresh Book 2 character. |
| B2-R3 | Gold cap during transition | `equipmnt.htm` | If carried Book 1 Gold plus Book 2 starting Gold exceeds 50 Crowns, should the app cap at 50 automatically or prompt the player to discard excess? | Cap at 50 and show a status receipt explaining the Belt Pouch limit. |
| B2-R4 | Collector's Edition Special Item loss option | `footnotz.htm` section 194 | Should the app offer the Collector's Edition alternative Special Item loss rule, or follow the local Project Aon main section text only? | Follow Project Aon main text by default; record the CE note as manual/optional unless you want edition-toggle support. |
| B2-R5 | Access papers | `footnotz.htm` section 327 | Should access papers be tracked as an inventory item, a route-history/story flag, or not tracked at all? | Do not add them to inventory; use route history/story flag if later route logic needs proof. |

## Later Section-Audit Rulings To Watch

| ID | Topic | Source | Question | Default Recommendation |
| --- | --- | --- | --- | --- |
| B2-R6 | Sommerswerd combat model | `footnotz.htm` sections 79 and 242 | Should Sommerswerd be selectable as the active combat weapon even though it is a Special Item? | Yes. Treat it as a weapon-like Special Item with its own combat modifiers. |
| B2-R7 | Magic Spear combat model | `errata.htm` section 106 | Should Magic Spear be selectable as the active combat weapon while stored as a Special Item? | Yes. Treat it as a weapon-like Special Item, with Spear Weaponskill support. |
| B2-R8 | Crystal Star Pendant history | `errata.htm` section 328 | Should Crystal Star Pendant route checks use current inventory or durable item history? | Use durable item history, matching the wording that the item was ever received. |
| B2-R9 | Hunting disabled in Wildlands | `errata.htm` sections 150 and 346 | Should Meal automation support section/region-specific Hunting suppression? | Yes. Add a Book 2 meal context flag for Wildlands sections and restore Hunting availability after the relevant route. |

## Status

Setup rulings B2-R1 through B2-R5 are answered and ready for implementation. Later section-audit rulings B2-R6 through B2-R9 remain watch-items for the combat, item, and Meal automation passes.
