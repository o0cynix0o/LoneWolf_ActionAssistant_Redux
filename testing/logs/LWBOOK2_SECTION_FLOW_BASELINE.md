# LW Book 2 Section Flow Baseline

Scope: source-link graph for local Project Aon Book 2 section files.

This report records section numbers, graph counts, and audit classifications only. Do not copy Book 2 prose into committed audit artifacts.

## Summary

- Sections found: 350 / 350
- Source route links: 576
- Branch sections: 176
- Terminal sections: 19
- Reachable from section 1: 350 / 350
- Missing section files: 0
- Invalid section links: 0

## Baseline Checks

- Section 1 routes: 273, 160
- Section 350 classifications: terminal_success
- Missing sections: none
- Invalid links: none
- Unreachable sections from section 1: none

## Classification Counts

- combat: 33
- combat_skill_modifier: 10
- endurance_gain: 12
- endurance_loss: 40
- gold: 43
- inventory: 72
- kai_discipline_check: 67
- meal: 33
- random: 27
- route_choice: 176
- single_route: 155
- terminal_death: 18
- terminal_success: 1

## Data Artifact

- `data/book2-section-flows.json` now contains one entry for every discovered section.
- `sourceRoutes` is the compact legal-link baseline used by the assistant.
- `classification` is heuristic and remains useful for future review slices.
- 23 sections include confirmed optional loot buttons.
- 31 sections include confirmed combat presets.
- 25 sections include confirmed roll helpers.
- 48 sections include confirmed route checks.

## Remaining Risk

- The automation-language audit currently reports zero uncovered signal categories.
- Broader real-route play may still find helper wording or timing that deserves polish.
- Section 238 Cartwheel has a mini-game helper; other arbitrary-stake gambling remains manual until reviewed.
