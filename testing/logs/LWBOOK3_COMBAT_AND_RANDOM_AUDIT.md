# LW Book 3 Combat And Random Audit

Date: 2026-05-28

GitHub issue: #42

Scope: first Book 3 combat/random helper pass.

## Combat Implemented

The first combat pass covers the clear stat-block fights found during the scan:

- 30 combat preset sections are represented in `data/book3-section-flows.json`.
- Multi-enemy queues are used where the book lists enemies fought one at a time.
- Helghast fights are immune to Mindblast and apply the no-Mindshield per-round END loss.
- Undead fights that call out Sommerswerd vulnerability double enemy END loss when Sommerswerd is used.
- Section 137 reduces Mindblast to a net +1 CS through a conditional modifier.
- Kalkoth venom fights can route to the wounded result or flawless result.
- Sections 164 and 200 use timed victory routing.
- Bone Sword is available as a special combat weapon and gets its Kalte +1 CS bonus.

## Random Status

Random helpers are implemented for the 33 random-signal sections recorded in the Book 3 flow data. The semantic repair pass now checks every raw digit 0-9 for every Book 3 roll helper and fails if the app produces a route that is not present in the source section links.

## Tests

- `testing\lwbook3_playable_pipeline_smoke.py` covers Helghast immunity/per-round damage, partial Mindblast resistance, Akraa'Neonor timed routing, Bone Sword weapon support, and Book 3 simple ending behavior.

## Remaining Risk

- Some combat sections may need route-specific tuning once they are reached in normal play.
- Random helper routes are app-safety tested, but the report can still improve by listing every roll band in a human-readable table.

## 2026-06-01 Semantic Repair Pass

Live playtesting found that several Book 3 combat helpers were structurally present but semantically wrong. The repair pass corrected route targets and special combat behavior for the affected sections, then added app-level semantic assertions so these helpers are tested by outcome, not just by existence.

Updated coverage includes:

- Corrected victory routes for sections 14, 68, 78, 83, 88, 89, 103, 106, 108, 123, 161, 180, 208, 241, 259, 260, 270, and 296.
- Immediate END-loss routing for Kalkoth/Javek-style special fights where the section changes route as soon as Lone Wolf loses END.
- Section 88 Javek venom handling: ignored END loss, venom roll, safe continuation, or death.
- Section 180 Fenor aid: additional enemy END loss each round.
- Timed and fixed-round combat routing for sections 164, 200, 208, and 296.

Detailed app-level results are recorded in `testing/logs/LWBOOK3_SEMANTIC_APP_PLAYTEST.md`.
