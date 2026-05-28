# LW Book 2 Playable Pipeline

Date: 2026-05-27

Scope: Book 2 automation, combat, death, completion, and player-helper pass.

This report records implementation coverage and tests only. It does not copy Book 2 prose.

## Implemented

- Added `data/book2-simple-automations.json` for confirmed Book 2 section effects.
- Expanded `data/book2-section-flows.json` with audited Book 2 loot, shops, route checks, roll helpers, route actions, and combat presets.
- Added terminal death/failure handling for checked no-route death sections and completion handling for section 350.
- Added Book 2-specific combat support for the Sommerswerd, Magic Spear, Shield, undead double-loss rules, doubled nonlethal enemy loss, timed modifiers, no-weapon penalties, and arm-wrestling END restoration.
- Added route/item helpers for Red Pass, White Pass, Access Papers, Ticket to Port Bax, Sommerswerd, Magic Spear, Chainmail Waistcoat loss, required Meals, Gold Crown gains/losses, and Green Sceptre aftermaths.
- Tightened section 240 recovery so Healing restores END to maximum, while non-Healing recovery restores half of tracked Book 2 combat END loss only.
- Kept route-effect helpers out of the browser Choices card; route effects still apply through route buttons and report through receipts/status output.
- Corrected section 106 so the Magic Spear is available before the Helghast combat, selected as the active weapon, and required to wound the enemy.
- Updated the landing page and simple library so Book 2 appears beside Book 1.
- Improved checked-route choice labels so player-facing route actions, such as Purchase White Pass, are shown before audit-condition text.
- Corrected section 299 so giving the Magic Spear to Rhygar removes it, while the no-spear route remains harmless.
- Hardened section 30 Zombie Crew combat so Mindblast immunity is restored onto matching active fights before combat ratio is shown or resolved.
- Left arbitrary-stake gambling and arbitrary donations as reviewed manual cases.

## Validation

- `python .\testing\lwbook2_section_flow_audit.py --check`
- `python .\testing\lwbook2_automation_language_audit.py --write`
- `python .\testing\lwbook2_setup_smoke.py`
- `python .\testing\lwbook2_playable_pipeline_smoke.py`
- `python .\testing\browser_choices_static_smoke.py`
- `python .\testing\browser_landing_static_smoke.py`

## Current Risk

- Book 2 is now playable by helper coverage, but still needs broader human route playtesting.
- Section 238 Cartwheel and section 308 Portholes remain manual because the player chooses stakes and numbers.
- Shop buttons trust the player to choose purchases they can afford, matching the existing helper style.
