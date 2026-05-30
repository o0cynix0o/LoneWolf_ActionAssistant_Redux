# LW Book 5 Section Flow Baseline

Scope: source-link graph for local Project Aon Book 5 section files.

This report records section numbers, graph counts, and helper classifications only. It does not reproduce book prose.

## Summary

- Sections found: 400 / 400
- Source route links: 683
- Branch sections: 231
- Terminal sections: 13
- Reachable from section 1: 400 / 400
- Missing section files: 0
- Invalid section links: 0
- Project Aon SVG route graph available: yes
- Confirmed optional loot/helper sections: 7
- Confirmed combat preset sections: 18
- Confirmed route-check sections: 7
- Confirmed random-roll helper sections: 6
- Confirmed loss-choice sections: 3

## Baseline Checks

- Section 1 routes: 36, 176, 104
- Section 400 classifications: terminal_success
- Missing sections: none
- Invalid links: none
- Unreachable sections from section 1: none

## Classification Counts

- combat: 42
- combat_skill_modifier: 23
- endurance_gain: 14
- endurance_loss: 61
- gold: 23
- inventory: 95
- kai_discipline_check: 73
- meal: 25
- random: 34
- route_choice: 230
- single_route: 156
- terminal_death: 8
- terminal_success: 1
- terminal_unclassified: 5

## Data Artifact

- `data/book5-section-flows.json` contains one source-link baseline entry for every discovered section.
- The first helper slice includes safekeeping-aware setup, palace confiscation/restoration, key loot, route checks, random helpers, loss choices, and combat presets.

## Remaining Risk

- The local Project Aon HTML remains the source of truth.
- Book 5 is an onboarding helper build until real-route playtesting shakes out button labels, achievements, and optional side-route polish.
