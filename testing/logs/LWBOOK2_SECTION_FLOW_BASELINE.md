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
- terminal_death: 1
- terminal_success: 1
- terminal_unclassified: 17

## Data Artifact

- `data/book2-section-flows.json` now contains one entry for every discovered section.
- `sourceRoutes` is the compact legal-link baseline used by the assistant.
- `classification` is heuristic and marks candidates for the later human section automation audit.
- No Book 2 section effects, route checks, combats, random helpers, achievements, or strategy routes are implemented by this slice.

## Remaining Work

- Run the full Book 2 automation-language audit section by section.
- Add route checks, section effects, loot/loss helpers, random helpers, and combat presets only after each candidate is confirmed against the book text.
- Add Book 2 achievements and strategy docs after the automation/combat pass is stable.
