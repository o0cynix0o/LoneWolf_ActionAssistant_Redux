# Agent Handoff: Lone Wolf Action Assistant Redux

This project is a one-time bootstrap from the Grey Star Action Assistant workflow into a new Lone Wolf AA2 repo.

## Start Here

The first playable target is **Book 1: Flight from the Dark**. Book 1 is published as prerelease `v0.1.0-rc1`.

Local source:

```text
C:\Scripts\LoneWolf_ActionAssistant_Redux\books\lw\01fftd
```

Book 2 source is also installed locally:

```text
C:\Scripts\LoneWolf_ActionAssistant_Redux\books\lw\02fotw
```

Do not use Grey Star rules as the source of truth. Grey Star supplied the workflow, cards, receipts, layout system, and testing discipline. Lone Wolf rules must come from the local Project Aon Lone Wolf book files and the original Lone Wolf project.

## What Was Bootstrapped

- Web assistant shell from Grey Star.
- Launcher and local server skeleton.
- Release packaging script.
- Combat Results Table and Kai reference data from the old Lone Wolf project.
- Audit workflow from Grey Star.
- Book 1 audit data placeholders, now with the section-flow and simple automation baselines filled in.
- Wiki/docs skeleton.

## Known Scaffold Debt

The first issue pass replaced the visible Book 1 character creation and sheet model. The second issue pass generated the Book 1 section-flow baseline from the local Project Aon `sect*.htm` files and wired route buttons to that checked-in graph. The third issue pass added the first conservative Book 1 simple automations. The fourth issue pass added the first Book 1 combat preset baseline. The fifth issue pass added the first Book 1 route-check and random outcome baseline. The sixth issue pass added the first repeatable end-to-end Book 1 playtest route to section 350. The seventh issue pass added branch playtests for early combat, death recovery, and inventory/stat consequences. The eighth issue pass added same-section random side effects and corrected Laumspur recovery behavior. The ninth issue pass added explicit Kai Healing and player-choice loss helpers. The tenth issue pass added the section 21 staged marsh roll helper. The eleventh issue pass added the section 307 weapon exchange helper. The twelfth issue pass completed the section-by-section automation-language scan. The thirteenth issue pass added an exhaustive checked-preset combat edge playtest. The fourteenth issue pass added a broader Book 1 route gauntlet. The fifteenth issue pass backfilled the reusable book pipeline, Book 1 automation ledger, achievement candidates, and player-facing Book 1 strategy guide. The sixteenth issue pass implemented the approved Book 1 achievement batch with automatic sync/backfill. The seventeenth issue pass scaffolded the Lone Wolf GitHub wiki and docs mirror using the Grey Star wiki structure. The eighteenth issue pass removed safe leftover scaffold references from runtime code and recorded the reference audit. The nineteenth issue pass brought project-wrapper parity closer to Grey Star by adding a Lone Wolf source map, expanding README/install/release docs, adding a Book 1 aggregate playtest wrapper, and adding audit/campaign/achievement rollup placeholders. The twentieth through twenty-fifth issue passes polished the browser play experience: receipts moved out of Choices, ordinary book routes stopped duplicating as choice buttons, the map image scales to the screen, death screens gained themed copy, Repeat Book 1 resets the run while keeping durable history, and Hunting Meal exemptions now clearly report unchanged Meals. Issue #26 published the first Book 1 release candidate. Issue #27 opened the Book 2 pipeline with a source/rules/handoff scan and rulings queue. The following debt remains for later passes:

- Book 2 rulings in `testing\logs\LWBOOK2_RULINGS_QUEUE.md`.
- Book 2 setup/start-state implementation.
- Book 2 section-flow, automation, combat/random, achievements, guide docs, tests, and playtesting ladder.
- Book 3 and later transition rules.
- Legacy compatibility code for older scaffold-derived save fields.
- Any remaining route aftermaths where the book asks the player to choose which item or weapon is lost or exchanged.
- Any remaining staged random edge cases found during broader route playtesting.

Do not paper over this by renaming labels only. Replace the underlying state and rules.

## First Validation Target

A successful first milestone is:

1. Start the local server.
2. Open `http://localhost:8797/assistant.html`.
3. Book 1 loads from `books\lw\01fftd`.
4. New character creation follows *Flight from the Dark* rules.
5. The sheet has correct Lone Wolf fields.
6. No Magicks/Willpower/Herb Pouch controls are visible.
7. `python -m py_compile app_server.py lonewolf_redux.py launch_lonewolf_redux.py ws_server.py` passes.

Current Book 1 aggregate validation:

```powershell
python .\testing\playtest_book1.py
```

Issue #1 changed the default character model to Book 1 Kai rules:

- Combat Skill and Endurance use the Book 1 random digit formulas.
- New characters choose exactly five Kai Disciplines.
- Weaponskill rolls against the Book 1 weapon table.
- Starting gear is Axe, one Meal, Map of Sommerlund, Gold Crowns, plus the monastery-find roll.
- The web sheet now exposes Gold Crowns, Meals, Kai Disciplines, Weapons, Backpack Items, and Special Items.

Issue #2 changed the route baseline:

- `testing\lwbook1_section_flow_audit.py` crawls `books\lw\01fftd\sect*.htm`.
- `data\book1-section-flows.json` contains 350 Book 1 section entries and 555 source route links.
- The graph check found zero missing sections, zero invalid section links, and all 350 sections reachable from section 1.
- The assistant uses checked-in `sourceRoutes` for legal route buttons and refuses illegal route-button jumps while keeping manual Set Position available for recovery/testing.
- `testing\logs\LWBOOK1_SECTION_FLOW_BASELINE.md` records the route graph summary and heuristic classification counts.

Issue #3 changed the simple automation baseline:

- `data\book1-simple-automations.json` has 48 confirmed Book 1 section-effect entries.
- Required Meal sections use the Book 1 Hunting exemption.
- Direct END loss/gain, Gold Crowns, Vordak Gem effects, permanent CS loss from section 236, deterministic gear loss, terminal death/failure, and section 350 completion are represented.
- `data\book1-section-flows.json` includes optional loot buttons for 24 confirmed sections.
- `testing\lwbook1_simple_automation_smoke.py` verifies representative effects.
- `testing\logs\LWBOOK1_SIMPLE_AUTOMATION_BASELINE.md` records coverage and remaining risk.

Issue #4 changed the combat preset baseline:

- `data\book1-section-flows.json` includes 29 confirmed Book 1 combat presets.
- The combat engine supports conditional preset modifiers, including no Mindshield and no Torch checks.
- Timed combat modifiers now honor conditions, used by the section 283 Vordak fight.
- Mindblast immunity, forced unarmed combat, multi-enemy queues, evasion routes, round-limit outcomes, and section 227 flawless/wounded victory routes are represented where confirmed.
- `testing\lwbook1_combat_smoke.py` verifies representative combat presets and exceptions.
- `testing\logs\LWBOOK1_COMBAT_AND_RANDOM_AUDIT.md` records coverage and remaining combat/random risk.

Issue #5 changed the initial route/random baseline:

- `data\book1-section-flows.json` initially included 17 confirmed roll helpers and 11 confirmed route checks.
- The first route checks cover representative Kai Discipline, item, Gold Crown, and END branches.
- Roll helpers initially covered straightforward one-roll route outcomes; later passes added same-section side effects and the section 21 staged roll helper.
- `testing\lwbook1_route_random_smoke.py` verifies representative route and random helpers.
- `testing\logs\LWBOOK1_ROUTE_RANDOM_AUDIT.md` records coverage and remaining route/random risk.

Issue #6 changed the playtest baseline:

- `testing\lwbook1_end_to_end_playtest.py` follows a deterministic legal route from section 1 to section 350:
  `1 -> 141 -> 56 -> 222 -> 252 -> 70 -> 157 -> 30 -> 261 -> 264 -> 6 -> 200 -> 168 -> 64 -> 16 -> 192 -> 171 -> 303 -> 237 -> 265 -> 142 -> 135 -> 223 -> 75 -> 163 -> 321 -> 273 -> 51 -> 288 -> 129 -> 3 -> 196 -> 332 -> 350`.
- The route uses a Book 1 character with Camouflage, Sixth Sense, Tracking, Hunting, and Healing.
- The test verifies the section 303 Camouflage route check, the section 237 roll helper, Hunting preserving the Meal at section 168, mid-route save/load, Book 1 completion at section 350, and death checkpoint rewind behavior.
- `testing\logs\LWBOOK1_PLAYTEST_REPORT.md` records the checked route and remaining playtest risk.

Issue #7 changed the branch playtest baseline:

- `testing\lwbook1_branch_playtest.py` adds short legal-route playtests outside the issue #6 success path.
- The early combat branch follows `1 -> 85 -> 229`, verifies illegal route blocking from section 85, loads the section 229 Kraan preset, resolves victory, and confirms the assistant waits for the player to choose section 267 or 125.
- The death branch follows `1 -> 275 -> 74 -> 281 -> 311 -> 47 -> 322 -> 17 -> 53`, verifies the section 17 roll helper, triggers terminal death, and rewinds to section 17.
- Inventory/stat branches cover legal-route Meal consumption without Hunting at section 130, Gold Crown gain at section 33, and weapon loss at section 274.
- `testing\logs\LWBOOK1_PLAYTEST_REPORT.md` records the branch routes and remaining playtest risk.

Issue #8 changed the random/recovery baseline:

- `data\book1-section-flows.json` now includes 20 confirmed roll helpers.
- Roll-outcome actions are supported for confirmed same-section random effects, with once-per-visit protection so repeated Roll clicks do not double-apply effects.
- Sections 36, 158, and 188 apply their confirmed random END or Backpack consequences when the roll outcome is recorded.
- Plain Book 1 Laumspur restores 3 END, and required Meal automation can consume Laumspur when no normal Meal is available.
- `testing\lwbook1_random_recovery_smoke.py` verifies those roll side effects and Laumspur behavior.
- `testing\logs\LWBOOK1_RANDOM_RECOVERY_AUDIT.md` records the issue #8 coverage and remaining risk.

Issue #9 changed the Healing/loss-choice baseline:

- The issue #9 pass introduced 2 confirmed explicit loss-choice helpers, section 144 and section 277.
- The web and CLI assistants expose a Kai Healing helper for characters with Healing; it restores 1 END, caps at maximum END, and can apply once per section visit.
- Healing is blocked in sections with audited combat presets to avoid applying it during combat timing.
- Section 144 lets the player choose the stolen Backpack Item, falling back to a chosen Weapon if no Backpack Item is available.
- Section 277 lets the player choose the broken Weapon.
- `testing\lwbook1_healing_loss_smoke.py` verifies Healing readiness, duplicate protection, combat/no-discipline blocks, and both loss-choice helpers.
- `testing\logs\LWBOOK1_HEALING_LOSS_AUDIT.md` records the issue #9 coverage and remaining risk.

Issue #10 changed the staged roll baseline:

- `data\book1-section-flows.json` includes 1 confirmed staged roll helper, currently section 21.
- Section 21 tracks the marsh check across first, second, and final rolls for the current section visit.
- Section 21 routes first-roll success and second-roll recovery to 189, final-roll success to 312, and final-roll failure to terminal death.
- Repeated Roll clicks after the staged helper completes return the stored result instead of changing the stage or reapplying death effects.
- `testing\lwbook1_section21_staged_smoke.py` verifies first-roll success, second-roll recovery, final-roll success, and final-roll death.
- `testing\logs\LWBOOK1_ROUTE_RANDOM_AUDIT.md` and `testing\logs\LWBOOK1_PLAYTEST_REPORT.md` record the issue #10 coverage.

Issue #11 changed the player-choice aftermath baseline:

- `data\book1-section-flows.json` includes 3 confirmed explicit loss/exchange helpers, currently section 144, section 277, and section 307.
- Loss-choice helpers can now carry a replacement item, letting one button remove the selected carried item and add the replacement with once-per-visit protection.
- Section 307 no longer treats the Warhammer as ordinary loot; the player chooses which carried Weapon to exchange for it.
- The section 307 Meal remains a separate ordinary loot button.
- `testing\lwbook1_player_choice_aftermath_smoke.py` verifies the section 307 weapon exchange, duplicate protection, and no-Weapon block.
- `testing\logs\LWBOOK1_PLAYER_CHOICE_AUDIT.md` records the issue #11 coverage.

Issue #12 completed the automation-language audit:

- `testing\lwbook1_automation_language_audit.py` scans all 350 local Book 1 section files for automation-likely language and writes section-number/category findings without copying book prose.
- The first clear slice added optional loot helpers for section 15 Sword, section 346 Spear, and section 349 Crystal Star Pendant.
- User rulings added section 193 Scroll as a Backpack Item, section 267 Message as a Special Item, section 267 Dagger as a Weapon, and section 255 Prince's Sword as a Weapon.
- Section 258 now applies the repeated Backpack/Weapons loss when reached directly.
- Section 46 now exposes a Sixth Sense route warning without forcing either non-Sixth-Sense route choice.
- Route-cost actions now deduct 10 Gold Crowns for section 12 -> 262 and 2 Gold Crowns for section 46 -> 246.
- Sections 115, 132, and 150 are recorded as no sheet change for Meal language.
- The final route-check pass added the clear remaining optional Kai Discipline and item route displays from the scanner.
- Reviewed false positives and already-covered combat-condition branches are recorded in `testing\logs\LWBOOK1_AUTOMATION_LANGUAGE_AUDIT.md`.
- The automation-language report now shows zero uncovered signal categories.
- `testing\lwbook1_automation_language_smoke.py` verifies the clear helpers and representative reviewed route checks.

Issue #13 changed the combat hardening baseline:

- `testing\lwbook1_combat_edge_playtest.py` loads and resolves every checked-in Book 1 combat preset.
- The playtest confirms section 236 remains the only combat-class section without a combat preset, because it is handled as simple automation.
- The playtest verifies preset route linkage, multi-enemy queues, victory-choice combats, evasion gates, round-limit timeout routes, and combat archive creation.
- `testing\logs\LWBOOK1_COMBAT_EDGE_PLAYTEST.md` records the pass.

Issue #14 changed the route playtesting baseline:

- `testing\lwbook1_route_gauntlet_playtest.py` follows risky legal routes covering paid routes, combat-adjacent choices, item-gated outcomes, death/failure states, END-threshold routing, gear loss, and side-route loot.
- The gauntlet covers section 255 through section 46/246/197, section 12 through section 191/234, section 242/9 Vordak Gem outcomes, section 162 capture outcomes, section 203 END routing, section 174 gear loss, and section 349 loot.
- `testing\logs\LWBOOK1_ROUTE_GAUNTLET_PLAYTEST.md` records the pass.
- Manual browser playtesting has confirmed ordinary Book 1 play feels good enough for the first release-candidate packaging pass.

Issue #15 changed the workflow and guide baseline:

- `docs\LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md` records the reusable per-book onboarding pipeline.
- `testing\logs\LWBOOK1_PIPELINE_BACKFILL.md` maps Book 1's completed work to that pipeline.
- `testing\logs\LWBOOK1_AUTOMATION_LEDGER.md` backfills the Book 1 automation ledger from the checked-in data.
- `testing\logs\LWBOOK1_ACHIEVEMENT_CANDIDATES.md` records the approved Book 1 achievement list and issue #16 implementation status.
- `docs\wiki\Book-1-Strategy-Guide.md` adds the player-facing guide in the Grey Star guide tone: practical, warm, route-aware, and not written like an audit log.

Issue #16 changed the achievement baseline:

- `lonewolf_redux.py` now exposes the approved Book 1 achievement definitions and trigger checks through the existing achievement sync/payload path.
- `Automation.ItemHistory` records successful `add_item` automation pickups so item achievements can survive later inventory changes.
- Route-resource achievements use the route journal when available and section-history fallback for older saves.
- `testing\lwbook1_achievement_smoke.py` covers definitions, story route completion, combat/item achievements, paid routes, failure branches, exploration, and summary backfill.
- `testing\logs\LWBOOK1_ACHIEVEMENT_IMPLEMENTATION.md` records the implementation pass; `lw1_route_gauntlet` remains deferred as internal playtest proof.

Issue #17 changed the wiki baseline:

- `docs\wiki\AGENT.md` records the Lone Wolf wiki authoring rules adapted from the Grey Star wiki guide.
- `docs\wiki\_Sidebar.md` and the player-facing page set now mirror the Grey Star wiki shape: getting started, install guide, commands, modes, combat, inventory, stats/achievements, saves, release guide, support matrix, strategy index, story route, achievement guide, FAQ, and Book 1 guide.
- The live GitHub wiki checkout exists at ignored path `wiki\`; keep it mirrored with `docs\wiki\` before pushing wiki changes.
- The current wiki is honest about release state: Book 1 is the playable release candidate, and later books remain pipeline targets.

Issue #18 changed the scaffold-reference baseline:

- Removed the unused legacy achievement catalogue and trigger block from `lonewolf_redux.py`.
- Removed direct legacy combat-loss field references from the browser UI and normalized them inside save migration instead.
- Replaced the leftover Moonstone landing-page subtitle with Book 1 Lone Wolf wording.
- `testing\logs\LW_SCAFFOLD_REFERENCE_AUDIT.md` records intentional references, cleaned leftovers, and later-book rule debt.

Issue #19 changed the project parity baseline:

- `docs\BOOK_SOURCE_MAP.md` now maps the local Lone Wolf corpus, source priority, current Book 1 artifacts, and future book onboarding pattern.
- `README.md`, `docs\INSTALL_PROJECT_AON_BOOKS.md`, and `docs\PUBLIC_RELEASE_CHECKLIST.md` now match the Grey Star project-guide shape more closely while staying honest about Book 1 release-candidate status.
- `testing\playtest_book1.py` provides the aggregate Book 1 validation entry point used by release checks.
- `testing\logs\LWBOOK1_AUDIT_INDEX.md` maps focused Lone Wolf audit logs back to Grey Star-style canonical buckets.
- `testing\logs\CAMPAIGN_STORY_RUN.md` and `testing\logs\ACHIEVEMENT_100_PERCENT_RUN.md` exist as Book 1-only parity placeholders until later books are implemented.
- `docs\RELEASE_NOTES_TEMPLATE.md` seeds future release-note creation.

Issue #27 started the Book 2 pipeline:

- `testing\logs\LWBOOK2_PASS1_RULES_BASELINE.md` records the Book 2 source verification, rules comparison, start-state handoff findings, annotation/errata findings, and early section-scan signal counts.
- `testing\logs\LWBOOK2_RULINGS_QUEUE.md` lists required rulings before Book 2 setup and automation implementation.
- Local `books\lw\02fotw` has 350 section files, 576 source route links, zero missing section files, zero invalid section links, and all 350 sections reachable from section 1.
- Major Book 2 model needs include one new Kai Discipline, Book 2 armoury choices, Weapon exchange during setup, Seal of Hammerdal, Sommerswerd/Magic Spear weapon-like Special Item behavior, and Book-specific Meal/Hunting edge cases.

## GitHub Workflow

Use the repo:

```text
https://github.com/o0cynix0o/LoneWolf_ActionAssistant_Redux
```

For every bug or task that changes behavior:

1. Open a GitHub issue.
2. Implement the fix.
3. Update docs/tests.
4. Commit with `Fixes #<issue>` when appropriate.
5. Push.
6. Package and publish a release only when the app is release-worthy.
7. Verify the issue and release state.

This bootstrap commit is not a public playable release.
