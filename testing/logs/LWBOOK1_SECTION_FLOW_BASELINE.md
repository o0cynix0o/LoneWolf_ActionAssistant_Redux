# LW Book 1 Section Flow Baseline

Scope: source-link graph for local Project Aon Book 1 section files.

This report records section numbers, graph counts, and audit classifications only. Do not copy Book 1 prose into committed audit artifacts.

## Summary

- Sections found: 350 / 350
- Source route links: 555
- Branch sections: 176
- Terminal sections: 17
- Reachable from section 1: 350 / 350
- Missing section files: 0
- Invalid section links: 0

## Baseline Checks

- Section 1 routes: 141, 85, 275
- Section 350 classifications: terminal_success
- Missing sections: none
- Invalid links: none
- Unreachable sections from section 1: none

## Classification Counts

- combat: 30
- combat_skill_modifier: 12
- endurance_gain: 2
- endurance_loss: 27
- gold: 15
- inventory: 65
- kai_discipline_check: 57
- meal: 16
- random: 21
- route_choice: 176
- single_route: 157
- terminal_death: 1
- terminal_success: 1
- terminal_unclassified: 15

## Data Artifact

- `data/book1-section-flows.json` now contains one entry for every discovered section.
- `sourceRoutes` is the compact legal-link baseline used by the assistant.
- `classification` is heuristic and marks candidates for the later human section automation audit.
- 18 sections include confirmed optional loot buttons.
- 29 sections include confirmed combat presets.

## Remaining Work

- Confirm route checks that depend on Kai Disciplines, items, END, Gold Crowns, or random digits.
- Expand simple automations only after each additional section effect is confirmed by the audit.
- Continue combat/random audit for route checks and non-combat random outcomes.
