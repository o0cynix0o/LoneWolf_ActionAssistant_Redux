# Book 1 Achievement Implementation

Date: 2026-05-27

Issue: #16

## Implemented

- Book 1 achievement definitions now use Lone Wolf IDs and display text.
- Existing starter IDs are preserved for saves that already unlocked `lw1_complete`, `lw1_first_blood`, or `lw1_long_road`.
- `lw1_complete` now carries the approved "Flight from the Dark" completion display.
- Item achievements now use durable `Automation.ItemHistory` entries recorded when an `add_item` automation succeeds.
- Route-resource achievements use route journal entries when available and section-history fallback for older saves.
- Automatic achievement sync/backfill remains the only rebuild path; no manual rebuild button was added.

## Trigger Coverage

- Story: Book 1 completion, section 350 reached, and the checked end-to-end story route.
- Combat: first Book 1 victory and the section 255 Gourgaz victory.
- Items: Prince's Sword and Crystal Star Pendant from item history, current inventory, or completed-book summaries.
- Danger/failure: Vordak Gem backlash, Vordak Gem failure, captive-death outcome.
- Route/resource: capture escape, paid ferry, caravan fare.
- Inventory/random/exploration: gear-loss sections, marsh escape section pattern, 75 unique Book 1 sections.

## Deferred

- `lw1_route_gauntlet` remains deferred because it is better suited as internal playtest proof unless the app later wants meta achievements tied to test-route families.

## Validation

- `python -m py_compile lonewolf_redux.py testing\lwbook1_achievement_smoke.py`
- `python testing\lwbook1_achievement_smoke.py`
