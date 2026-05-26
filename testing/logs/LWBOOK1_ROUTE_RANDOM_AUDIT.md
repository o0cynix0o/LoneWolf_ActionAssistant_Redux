# LW Book 1 Route And Random Audit

Date: 2026-05-26

Scope: first route-check and random outcome baseline for local Project Aon Book 1 section files.

This log records confirmed mechanics by section number only. Do not copy Book 1 prose into committed audit artifacts.

## Summary

- Confirmed roll helpers added for 17 Book 1 sections.
- Confirmed route checks added for 11 Book 1 sections.
- The pass uses existing assistant cards: Section Roll for random digits and Route Check for sheet-dependent branches.
- Roll helpers only resolve the route/result label; they do not apply route-specific stat or item side effects.

## Roll Helpers

- Two-way random routes: 2, 7, 22, 44, 49, 160, 205, 226, 237, 275, 279, 302, 314, 337.
- Three-way random routes: 17, 89, 294.

## Route Checks

- Kai Discipline checks: 52, 88, 105, 128, 162, 242, 303.
- Item checks: 9, 173.
- Stat checks: 12, 203.
- Section 162 and section 203 checks are tied to sections with automatic entry effects; the smoke test verifies those entry effects are applied before checking the route.

## Data Artifacts

- `data/book1-section-flows.json` now carries the first route/random baseline.
- `testing/lwbook1_section_flow_audit.py` regenerates the checked-in flow data from local book files plus manual route/random audit entries.
- `testing/lwbook1_route_random_smoke.py` verifies representative roll, Kai, item, Gold, and END branches.

## Remaining Work

- Multi-roll sections remain manual, especially section 21.
- Random outcomes with immediate side effects in the same section need a later roll-outcome action model before they can be safely automated.
- Optional Kai choices with several non-Kai alternatives need more nuanced availability display before broad automation.
