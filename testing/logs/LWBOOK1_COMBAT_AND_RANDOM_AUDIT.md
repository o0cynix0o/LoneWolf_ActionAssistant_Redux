# LW Book 1 Combat And Random Audit

Date: 2026-05-26

Scope: first combat preset baseline for local Project Aon Book 1 section files.

This log records confirmed mechanics by section number only. Do not copy Book 1 prose into committed audit artifacts.

## Summary

- Confirmed combat presets added for 29 Book 1 combat sections.
- Section 236 remains a simple automation entry, not a combat preset.
- Multi-enemy queues are used where the section fights enemies one at a time.
- Single combined enemies are used where the section says to fight a group or rider/mount pair as one enemy.
- Victory routes, evasion routes, and victory choices are included only where the section gives them directly.

## Automated Combat Exceptions

- Temporary CS modifiers: 17, 55, 136, 229.
- Mindshield conditional penalties: 29, 34, 342.
- Timed combat modifiers: 283.
- Torch conditional penalty: 170.
- Mindblast immunity: 133, 170, 255, 342.
- Forced unarmed combat: 260.
- Combat evasion after/within a fight: 43, 169, 191, 220, 231, 339.
- Round-limit outcomes: 231, 339.
- END-loss-dependent victory route: 227.
- Post-victory route choices rather than forced routing: 17, 112, 208, 229.

## Data Artifacts

- `data/book1-section-flows.json` now carries the combat presets.
- `testing/lwbook1_section_flow_audit.py` regenerates the checked-in flow data from local book files plus the manual combat audit.
- `testing/lwbook1_combat_smoke.py` verifies representative presets and exception handling.

## Remaining Work

- Route-check math for random, stat, item, and Kai Discipline branches is still separate work.
- Non-combat random outcomes are not automated by this combat pass.
- More end-to-end playtesting is needed before packaging or release.
