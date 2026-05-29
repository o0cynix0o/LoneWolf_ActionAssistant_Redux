# LW Book 3 Route Audit

Date: 2026-05-28

GitHub issue: #42

Scope: first Book 3 route helper pass.

## Route Baseline

- Local Project Aon source sections: 350 / 350.
- Local source route links: 603.
- All sections are reachable from section 1.
- The Project Aon SVGZ route graph matches local source routes exactly.

## Implemented Route Helpers

- Source routes are available for every section through `data/book3-section-flows.json`.
- Section 139 has a Red Laumspur route check that distinguishes Red Laumspur from normal Laumspur.
- Section 303 removes the Ornate Silver Key when the key route is selected.

## Remaining Route Work

- Add checked labels and helpers for the remaining Discipline checks.
- Add item/history route checks for Blue Stone items, Baknar Oil, Silver Helm, and other durable items.
- Add random route helpers.
- Keep ordinary book routes out of the Choices panel unless they are true assistant choices/checks.

## Tests

- `testing\lwbook3_section_flow_audit.py --check`
- `testing\lwbook3_playable_pipeline_smoke.py`
