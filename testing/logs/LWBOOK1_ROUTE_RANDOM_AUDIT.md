# LW Book 1 Route And Random Audit

Date: 2026-05-26

Scope: first route-check and random outcome baseline for local Project Aon Book 1 section files.

This log records confirmed mechanics by section number only. Do not copy Book 1 prose into committed audit artifacts.

## Summary

- Confirmed roll helpers added for 20 Book 1 sections.
- Confirmed route checks added for 11 Book 1 sections.
- The pass uses existing assistant cards: Section Roll for random digits and Route Check for sheet-dependent branches.
- Roll helpers resolve the route/result label.
- Confirmed same-section roll effects are applied for sections 36, 158, and 188 with once-per-visit protection.

## Roll Helpers

- Two-way random routes: 2, 7, 22, 36, 44, 49, 160, 205, 226, 237, 275, 279, 302, 314, 337.
- Three-way random routes: 17, 89, 294.
- Single-route random effects: 158, 188.

## Roll Outcome Effects

- Section 36: roll 0-4 routes to 140 and applies the 2 END loss; roll 5-9 routes to 323.
- Section 158: the entry automation applies the first 6 END loss; roll 6-9 applies the further 4 END loss before routing to 106.
- Section 188: roll 0-6 discards the Backpack and Backpack Items before routing to 303; roll 7-9 applies the 3 END loss before routing to 303.
- Roll outcome effects are guarded by the section visit key so pressing Roll again in the same visit does not double-apply the damage or item loss.

## Route Checks

- Kai Discipline checks: 52, 88, 105, 128, 162, 242, 303.
- Item checks: 9, 173.
- Stat checks: 12, 203.
- Section 162 and section 203 checks are tied to sections with automatic entry effects; the smoke test verifies those entry effects are applied before checking the route.

## Data Artifacts

- `data/book1-section-flows.json` now carries the first route/random baseline.
- `testing/lwbook1_section_flow_audit.py` regenerates the checked-in flow data from local book files plus manual route/random audit entries.
- `testing/lwbook1_route_random_smoke.py` verifies representative roll, Kai, item, Gold, and END branches.
- `testing/lwbook1_random_recovery_smoke.py` verifies representative same-section roll side effects and Laumspur behavior.

## Remaining Work

- Multi-roll sections remain manual, especially section 21.
- Player-choice random aftermaths remain manual where the book asks the player to pick an item or weapon to lose.
- Optional Kai choices with several non-Kai alternatives need more nuanced availability display before broad automation.
