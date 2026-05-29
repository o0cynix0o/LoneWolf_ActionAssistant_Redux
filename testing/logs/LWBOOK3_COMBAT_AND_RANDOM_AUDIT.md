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

Random helpers are not broadly implemented yet for Book 3. The source scan found 33 random-signal sections. These should be the next helper slice after setup/combat smoke is stable.

## Tests

- `testing\lwbook3_playable_pipeline_smoke.py` covers Helghast immunity/per-round damage, partial Mindblast resistance, Akraa'Neonor timed routing, Bone Sword weapon support, and Book 3 simple ending behavior.

## Remaining Risk

- Some combat sections may need route-specific tuning once they are reached in normal play.
- Random sections still need helper implementation.
