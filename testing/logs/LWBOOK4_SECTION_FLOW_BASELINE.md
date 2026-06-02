# LW Book 4 Section Flow Baseline

Scope: source-link graph for local Project Aon Book 4 section files.

This report records section numbers, graph counts, and audit classifications only. Do not copy Book 4 prose into committed audit artifacts.

## Summary

- Sections found: 350 / 350
- Source route links: 568
- Branch sections: 183
- Terminal sections: 15
- Reachable from section 1: 350 / 350
- Missing section files: 0
- Invalid section links: 0
- Project Aon SVG route graph available: yes
- Confirmed optional loot/helper sections: 23
- Confirmed combat preset sections: 45
- Confirmed route-check sections: 39
- Confirmed random-roll helper sections: 34
- Confirmed loss-choice sections: 2

## Baseline Checks

- Section 1 routes: 160, 273
- Section 350 classifications: inventory, terminal_success
- Missing sections: none
- Invalid links: none
- Unreachable sections from section 1: none

## Classification Counts

- combat: 54
- combat_skill_modifier: 10
- endurance_gain: 12
- endurance_loss: 48
- gold: 11
- inventory: 93
- kai_discipline_check: 48
- meal: 41
- random: 34
- route_choice: 183
- single_route: 152
- terminal_death: 14
- terminal_success: 1

## Data Artifact

- `data/book4-section-flows.json` contains one source-link baseline entry for every discovered section.
- `sourceRoutes` is the compact legal-link baseline used for later helper implementation.
- `classification` is heuristic and remains useful for review slices.
- Book 4 now carries confirmed helpers for setup-sensitive routes, random rolls, combat presets, optional loot, and the section 22 item-loss picker.

## Remaining Risk

- This pass still keeps the local Project Aon HTML as the source of truth.
- Combat and loot helper coverage is intentionally practical rather than final; playtesting can add polish where Book 4 wording needs a friendlier helper button.
- Achievements and full lore-guide coverage are separate passes after the first playable Book 4 run.
