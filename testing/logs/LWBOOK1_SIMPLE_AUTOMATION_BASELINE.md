# LW Book 1 Simple Automation Baseline

Date: 2026-05-26

Scope: issue #3 conservative section-effect pass for *Flight from the Dark*.

## Coverage

- `data/book1-simple-automations.json` now has 48 confirmed Book 1 section entries.
- 16 terminal death/failure endings are marked.
- Section 350 marks Book 1 success/completion.
- 7 required Meal sections are automated with a Hunting exemption.
- Confirmed direct END changes, Gold Crown gains, Vordak Gem effects, permanent CS loss from the Vordak Gem backlash, and deterministic gear loss are automated.
- `data/book1-section-flows.json` now includes optional loot buttons for 21 sections:
  15, 20, 62, 113, 124, 148, 164, 184, 197, 199, 243, 263, 290, 291, 305, 307, 315, 319, 346, 347, and 349.

## Verification

- `python testing\lwbook1_simple_automation_smoke.py`
- `python testing\lwbook1_section_flow_audit.py --check`
- `python -m py_compile app_server.py lonewolf_redux.py launch_lonewolf_redux.py ws_server.py testing\lwbook1_section_flow_audit.py testing\lwbook1_simple_automation_smoke.py`

Representative smoke coverage:

- Section 119 applies END loss.
- Section 130 consumes a Meal, and Hunting avoids the Meal requirement.
- Section 212 restores END to maximum.
- Section 33 applies Gold Crowns.
- Section 76 applies END loss and adds a Vordak Gem.
- Section 20 loot restores Backpack availability and adds supplies.
- Section 162 discards Backpack and Weapons.
- Section 258 discards Backpack and Weapons.
- Section 236 applies END loss, permanent CS loss, and removes a Vordak Gem.
- Laumspur can be used as a Backpack consumable for 3 END and can fulfill a required Meal if no normal Meal is available.
- Section 350 completes Book 1.
- Section 53 marks terminal death.

## Remaining Risk

- Combat presets and combat exceptions are still unaudited.
- Random-number branches and stat-based route checks remain manual unless already represented as source links.
- Some inventory losses that require player choice remain manual.
- Healing timing across ordinary non-combat sections remains manual.
