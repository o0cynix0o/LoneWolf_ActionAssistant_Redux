# Lone Wolf Full Section Automation Audit

Generated: 2026-06-02

Scope: Books 1-5, one section at a time. This report records section numbers, signal categories, coverage, and behavior-test status only.

## Summary

- Blockers: 0
- Review items: 0
- Detail JSON: `testing/tmp/lw_full_section_audit.json`

## Book 1: Flight from the Dark

- Sections scanned: 350
- Behavior failures: 0
- Signal coverage review items: 0
- Signal counts: combat=11, combat_skill_modifier=12, endurance_gain=2, endurance_loss=27, gold=15, gold_cost=6, inventory_gain=12, inventory_loss=6, meal=8, random=21, route_check=60, terminal_death=17, terminal_success=1
- Coverage counts: combat=29, ending:death=16, ending:success=1, loot=25, lossChoice=3, roll=20, routeAction=2, routeAction:stat=2, routeCheck=36, simple=48, simple:add_item=3, simple:discard_backpack_items=1, simple:discard_gear=4, simple:discard_weapons=2, simple:ending=17, simple:meal=7, simple:remove_item=1, simple:stat=17, sourceRoutes=333, stagedRoll=1

## Book 2: Fire on the Water

- Sections scanned: 350
- Behavior failures: 0
- Signal coverage review items: 0
- Signal counts: combat=8, combat_skill_modifier=8, endurance_gain=12, endurance_loss=40, gold=43, gold_cost=19, inventory_gain=12, inventory_loss=10, meal=10, random=27, route_check=75, safekeeping=1, terminal_death=18, terminal_success=1
- Coverage counts: cartwheel=1, combat=31, ending:death=18, ending:success=1, loot=23, portholes=1, roll=25, routeAction=25, routeAction:add_item=2, routeAction:meal=6, routeAction:meal_or_gold=1, routeAction:remove_item=3, routeAction:stat=15, routeAction:weapons=1, routeCheck=48, simple=54, simple:add_item=9, simple:discard_backpack_items=1, simple:discard_gear=1, simple:discard_special_items=1, simple:discard_weapons=1, simple:ending=19, simple:meal=2, simple:remove_chainmail=2, simple:remove_item=3, simple:stat=25, simple:weapons=1, sourceRoutes=331

## Book 3: The Caverns of Kalte

- Sections scanned: 350
- Behavior failures: 0
- Signal coverage review items: 0
- Signal counts: combat=37, combat_skill_modifier=1, endurance_gain=4, endurance_loss=48, gold=6, inventory_gain=31, inventory_loss=10, meal=42, random=33, route_check=106, terminal=1, terminal_death=19, terminal_failure=1, terminal_success=1
- Coverage counts: combat=30, ending:death=19, ending:failure=1, ending:success=1, goldDistraction=1, loot=29, lossChoice=2, roll=32, routeCheck=1, simple=58, simple:backpack_stash=2, simple:discard_weapons=1, simple:ending=21, simple:meal=3, simple:remove_item=5, simple:stat=29, sourceRoutes=329

## Book 4: The Chasm of Doom

- Sections scanned: 350
- Behavior failures: 0
- Signal coverage review items: 0
- Signal counts: book_transition=1, combat=77, combat_skill_modifier=3, endurance_gain=9, endurance_loss=39, gold=11, inventory_gain=23, inventory_loss=8, meal=41, random=34, route_check=68, terminal=14, terminal_death=14, terminal_success=1
- Coverage counts: combat=45, ending:death=14, ending:success=1, loot=23, lossChoice=2, roll=34, routeAction=1, routeAction:meal=1, routeCheck=39, simple=59, simple:add_item=2, simple:backpack=4, simple:ending=15, simple:flag=4, simple:meal=13, simple:remove_item=1, simple:stat=23, sourceRoutes=335

## Book 5: Shadow on the Sand

- Sections scanned: 400
- Behavior failures: 0
- Signal coverage review items: 0
- Signal counts: book_transition=6, combat=57, combat_skill_modifier=19, endurance_gain=13, endurance_loss=46, gold=25, gold_cost=4, inventory_gain=35, inventory_loss=9, meal=29, random=34, route_check=119, safekeeping=3, terminal=8, terminal_death=12, terminal_success=1
- Coverage counts: combat=39, combatRollRoutes=1, ending:death=12, ending:success=1, loot=22, lossChoice=3, roll=33, routeAction=5, routeAction:flag=1, routeAction:stat=4, routeCheck=13, simple=65, simple:add_item=1, simple:book5_kai_master=1, simple:book5_limbdeath=1, simple:ending=13, simple:flag=4, simple:gear=4, simple:meal=2, simple:remove_item=1, simple:restore_sommerswerd_if_lost=1, simple:stat=44, sourceRoutes=387, stagedRoll=1

## Blockers

- none

## Review Items

- none

## Audit Contract

- `signals` means source language likely implies automation, a helper, or a no-automation ruling.
- `coverage` means an app data hook exists: simple automation, roll helper, staged roll, mini-game, combat, route check, loot, loss choice, route action, or source route.
- `behaviorPassed` means the helper was exercised in an isolated assistant state without touching the live save.
- `behaviorFailed` is a blocker.
- `missingSignalCoverage` is a review item unless a human ruling says source text only.
