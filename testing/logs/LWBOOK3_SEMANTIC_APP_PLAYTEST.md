# LW Book 3 Semantic App Playtest

Date: 2026-06-01

Scope: repair pass for Book 3, *The Caverns of Kalte*, after live playtesting exposed that structural smoke tests were not enough.

This report records mechanics, section numbers, and app behavior only. It does not copy long book prose.

## Why This Pass Happened

Section 158 exposed a gap in the onboarding workflow: the combat preset existed and the app could start the fight, but the preset did not match the section's special one-round routing. This pass raises Book 3 to the new workflow standard by checking semantic behavior through the app layer.

## Fixes Made

| Area | Sections | Result |
| --- | --- | --- |
| Wrong combat victory routes | 14, 68, 78, 83, 88, 89, 103, 106, 108, 123, 161, 180, 208, 241, 259, 260, 270, 296 | Corrected combat route data to match the local Book 3 source links and section instructions. |
| Immediate END-loss combat routing | 32, 123, 138, 147, 180, 259, 263 | Added or corrected `playerLossRoute` behavior so the app routes immediately when the section says any Lone Wolf END loss changes the outcome. |
| One-round comparison combat | 158 | Confirmed all three outcomes: player loses more, enemy loses more, equal loss. |
| Timed or survival combat | 164, 200, 208, 296 | Confirmed fast/slow victory and fixed-round survival routing. |
| Early-round ignored damage | 241, 260 | Added first-two-round ignored Lone Wolf END loss handling. |
| Mindblast immunity | 83, 88, 106, 161, 260, 265, 304 | Added or verified enemy immunity flags so Mindblast is not applied. |
| Section 83 Mindforce | 83 | Added conditional END loss when Lone Wolf lacks Mindshield. |
| Section 88 Javek venom | 88 | Added special combat handling: Lone Wolf END loss is ignored, a venom roll is made, 0-8 continues combat, 9 records death. |
| Section 180 Fenor aid | 180 | Added per-round enemy END loss from Fenor's attack and corrected the no-loss/loss routes. |

## Tests Added

`testing/lwbook3_playable_pipeline_smoke.py` now includes semantic checks for:

- Every Book 3 combat preset's route targets being present in the section source links.
- Every Book 3 combat preset's key route semantics.
- Section 83 Mindshield/no-Mindshield outcomes.
- Section 88 safe and fatal venom checks.
- Section 158 all three one-round comparison outcomes.
- Section 180 Fenor damage plus immediate wound routing.
- Section 208 fast and slow victory routes.
- Section 241 ignored first-round damage.
- Section 296 three-round survival routing.
- Every Book 3 roll helper accepts every raw digit 0-9 without producing a non-source route.

## Validation Run

- `python -m py_compile lonewolf_redux.py testing\lwbook3_section_flow_audit.py testing\lwbook3_playable_pipeline_smoke.py`
- `python testing\lwbook3_section_flow_audit.py --write`
- `python testing\lwbook3_automation_language_audit.py --write`
- `python testing\lwbook3_section_flow_audit.py --check`
- `python testing\lwbook3_automation_language_audit.py --check`
- `python testing\lwbook3_playable_pipeline_smoke.py`
- `python testing\browser_choices_static_smoke.py`
- `python testing\browser_landing_static_smoke.py`
- `python testing\playtest_book3.py`

All listed checks passed after the repair.

## Remaining Risk

- This pass focused on the Book 3 combat and direct mechanic misses that can break a route during live play.
- Random helpers are now app-safety tested across every raw digit. Future work can still improve the reports by adding a human-readable roll-outcome table for every random section.
- Human playtesting should now be a feel-check and route-shakeout, not the first line of defense for special combat routing.
