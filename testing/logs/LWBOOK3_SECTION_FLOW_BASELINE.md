# LW Book 3 Section Flow Baseline

Scope: source-link graph for local Project Aon Book 3 section files.

This report records section numbers, graph counts, and audit classifications only. Do not copy Book 3 prose into committed audit artifacts.

## Summary

- Sections found: 350 / 350
- Source route links: 603
- Branch sections: 209
- Terminal sections: 21
- Reachable from section 1: 350 / 350
- Missing section files: 0
- Invalid section links: 0
- Project Aon SVG route graph available: yes
- Confirmed optional loot/helper sections: 28
- Confirmed combat preset sections: 30
- Confirmed route-check sections: 1

## Baseline Checks

- Section 1 routes: 160, 273
- Section 350 classifications: terminal_success
- Missing sections: none
- Invalid links: none
- Unreachable sections from section 1: none

## Classification Counts

- combat: 41
- combat_skill_modifier: 6
- endurance_gain: 7
- endurance_loss: 51
- gold: 6
- inventory: 80
- kai_discipline_check: 62
- meal: 43
- random: 33
- route_choice: 209
- single_route: 120
- terminal_death: 19
- terminal_failure: 1
- terminal_success: 1

## Data Artifact

- `data/book3-section-flows.json` contains one source-link baseline entry for every discovered section.
- `sourceRoutes` is the compact legal-link baseline used for later helper implementation.
- `classification` is heuristic and remains useful for review slices.

## Remaining Risk

- This pass is source-link and heuristic classification only.
- Some combat presets and loot helpers are now recorded; random helpers, full route checks, achievements, and lifecycle support are covered by later implementation/testing passes.
- Combat/loot helper coverage is partial and should grow during Book 3 playtesting.
