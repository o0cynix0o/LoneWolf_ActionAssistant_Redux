# LW Book 5 Combat Semantic Playtest

Scope: follow-up check for the same combat-routing issue found during Book 3 playtesting.

## Fixed

- Corrected wrong combat exits for sections 119, 159, 280, 357, and 393.
- Removed the false combat preset from section 264 and made it a Sommerswerd route check with the Mindshield END loss.
- Added first-round enemy-loss suppression for section 4.
- Added combat-roll routing for section 357, where rolling 1 during combat sends Lone Wolf to section 293.
- Added round-limit routing for timed fights such as sections 20, 330, and 361.
- Added missing evasion data for sections 123, 273, 334, 387, and 393.
- Added the previous-Elix combat-history modifier for section 57.
- Added missing combat modifiers for sections 12, 64, 91, 110, 190, 316, 355, and 357.

## Result

- Book 5 now has 38 combat presets.
- Combat preset route targets match the Project Aon source links.
- The playable smoke now checks both route-target safety and named semantic expectations for the corrected sections.

## Validation

```powershell
python .\testing\lwbook5_section_flow_audit.py --check
python .\testing\lwbook5_playable_pipeline_smoke.py
python .\testing\playtest_book5.py
```

Current result: passed.
