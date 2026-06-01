# Lone Wolf Book Pipeline Workflow

This workflow is the reusable command contract for onboarding any Lone Wolf book into Action Assistant Redux.

## Operator Command

When the user says:

```text
Onboard book N
```

the assistant should treat it as:

```powershell
python tools/lw_book_pipeline.py --book N --source books/lw/NNslug --workflow full --ask-when-ambiguous
```

If the pipeline script is not complete enough to perform a step, the assistant should perform the step directly, update the workflow notes, and keep moving.

The command means:

- Verify the local book source.
- Run the rules, handoff, annotation, section-flow, route, combat, random, automation-language, achievement-candidate, and UI-readiness scans.
- Build every clear mechanic, helper, data artifact, test, and browser-facing affordance that can be implemented safely.
- Prove combat, random, and route helpers against the source text with semantic app tests before handing the book to the user for playtesting.
- Stop only for true rulings, approvals, edition differences, or risky player-choice behavior.
- Record every stop in a rulings queue so one approval session can unblock the next build session.
- Do not package, release, or commit source book files.

## Ask-Less Rule

Default posture: automate clear mechanical findings and continue.

Stop and ask only when:

- The source text is ambiguous.
- Multiple editions disagree and the local source does not settle it.
- A mechanic depends on player intent that cannot be inferred.
- A wager, donation, item sacrifice, or exchange amount is arbitrary.
- The change would alter campaign carry-forward rules.
- Achievement implementation needs approval.
- Packaging or release is being considered.

Do not stop to ask whether to run tests, update docs, restart the local server, open a GitHub issue, or commit normal onboarding work. Do those things as part of the workflow.

## Required Outputs

Each book pass should produce or update:

- `testing/logs/LWBOOKN_PASS1_RULES_BASELINE.md`
- `testing/logs/LWBOOKN_RULESET_CHANGE_AUDIT.md`
- `testing/logs/LWBOOKN_RULINGS_QUEUE.md`
- `testing/logs/LWBOOKN_SECTION_FLOW_BASELINE.md`
- `testing/logs/LWBOOKN_SECTION_AUDIT.md`
- `testing/logs/LWBOOKN_AUTOMATION_LANGUAGE_AUDIT.md`
- `testing/logs/LWBOOKN_AUTOMATION_LEDGER.md`
- `testing/logs/LWBOOKN_COMBAT_AND_RANDOM_AUDIT.md`
- `testing/logs/LWBOOKN_ROUTE_AUDIT.md`
- `testing/logs/LWBOOKN_ROUTE_GRAPH_CHECK.md` when a Project Aon SVG route graph is available
- `testing/logs/LWBOOKN_COMBAT_SEMANTIC_PLAYTEST.md`
- `testing/logs/LWBOOKN_PLAYABLE_PIPELINE.md`
- `testing/logs/LWBOOKN_SEMANTIC_APP_PLAYTEST.md`
- `testing/logs/LWBOOKN_ROUTE_GAUNTLET_PLAYTEST.md`
- `testing/logs/LWBOOKN_PLAYTEST_REPORT.md`
- `testing/logs/LWBOOKN_ACHIEVEMENT_CANDIDATES.md`
- `docs/wiki/Book-N-Strategy-Guide.md` when strategy guidance is useful

Reports must record mechanics, section numbers, file references, decisions, and test coverage. Do not copy long book prose into committed artifacts.

## 1. Verify Source

- Confirm the local book folder exists under `books/lw/`.
- Confirm `books/` is ignored and not tracked by git.
- Detect book number, title, slug/folder, section count, section files, support pages, map/images, rules pages, errata, and footnotes.
- Confirm every expected `sect*.htm` exists.
- Confirm every linked section target exists.
- Confirm source route reachability from section 1.
- Probe the optional Project Aon route graph at `https://www.projectaon.org/en/svg/lw/NNslug.svgz`.
- If the route graph exists, record its status, title links, section nodes, and edge count as an external cross-check only.
- Record missing pages, invalid links, unreachable sections, and source irregularities.
- Refuse to package or commit source book files.

## 2. Rules Scan

- Read action chart, rules, combat, equipment, random-number, levels/ranks, errata, footnotes, and annotations.
- Compare against the previous implemented book.
- Identify the ruleset family before reading sections:
  - Kai books
  - Magnakai books
  - Grand Master books
  - any later-series rule family the source introduces
- If the book crosses a ruleset boundary, create `LWBOOKN_RULESET_CHANGE_AUDIT.md` before implementation. Record what changes in character creation, action chart fields, rank/power structure, combat rules, inventory containers, carry-forward, healing, meals, currency, and book completion.
- Treat ruleset changes as engine-work candidates, not just data changes. If a new rule family needs new state fields, UI panels, validation, or save migration, implement that support before section automation.
- Detect new or changed rules:
  - Combat Skill and Endurance
  - Disciplines, new powers, rank changes, or power upgrades
  - Healing, recovery, poison, fatigue, and history-based recovery
  - Meals and Hunting-style exemptions or suppressions
  - Backpack, Weapons, Special Items, item limits, and item containers
  - Safekeeping, temporary confiscation, or any other unavailable-but-not-lost gear state
  - Gold gains, costs, caps, and carry-over
  - Combat rules, enemy immunities, weapon restrictions, timed effects, evasion, survival, fixed-CS fights, and per-round damage
  - Carry-over rules from the previous book and into the next book
  - Special Items that behave as weapons, passes, keys, flags, currencies, or removable story objects
  - Durable item history checks where current inventory is not enough
- Record all rule deltas and implementation needs in the rules baseline.
- Do not start final implementation from section text until rules, annotations, and handoff pages have been scanned. Section automation built on an outdated rules model must be considered incomplete.

## 3. Book Handoff / Start-State Scan

- Find the setup for starting the book.
- Detect what the player keeps, loses, receives, chooses, rolls, exchanges, or caps:
  - New Discipline/power
  - New gear
  - Weapons and weapon exchanges
  - Backpack availability and Backpack Items
  - Special Items
  - Safekeeping choices and protected stored items
  - Meals
  - Gold
  - Item limits and duplicate handling
  - Stat restoration or carry-forward
- Create both campaign-continuation and standalone-start plans if the source supports both.
- Define the book-start checkpoint shape that will support repeat-book replay.
- Stop only if carry-forward or start-state logic is genuinely unclear.

## 4. Build Section Graph

- Crawl all `sect*.htm`.
- Extract legal source route links.
- If the Project Aon SVG/SVGZ route graph exists, parse its Graphviz SVG nodes/edges and compare it with the local source-link graph.
- Classify route shape:
  - single route
  - player choice
  - item check
  - Discipline check
  - random route
  - combat route
  - no-route terminal
- Classify terminal shape separately:
  - death
  - mission failure without death
  - successful completion
  - unclassified no-route ending
- Generate or update `data/bookN-section-flows.json`.
- Run a route-target certification pass:
  - Every generated combat route target must appear in that section's source links unless the route is explicitly a terminal state implemented outside the source page.
  - Every generated random-roll route target must appear in that section's source links unless it is a documented death/failure helper.
  - Every generated route-check target must appear in that section's source links.
  - Every route action that spends, removes, grants, or flags something must be tied to a source route or a documented manual helper.
- Run a terminal-ending certification pass:
  - Every no-route death section must have death/recovery automation.
  - Every no-route mission-failure section must have failure/recovery automation and must not be recorded as a Lone Wolf death unless the text says he dies.
  - Every completion section must have completion automation.
  - No `terminal_unclassified` section may remain unless it is explicitly documented as source-only text with no app action.
- Any generated route target that is not present in the source text is a blocker until corrected or documented with a clear reason.
- Write the section-flow baseline log.
- Write `LWBOOKN_ROUTE_GRAPH_CHECK.md` if an online route graph was available.

## 5. Automation-Language Scan

- Scan every section for automation-likely language:
  - END loss/gain
  - CS changes
  - Meals and Hunting exceptions
  - Gold gain/loss/cost/cap
  - inventory gain/loss/use
  - Weapons
  - Backpack Items
  - Special Items
  - Safekeeping or temporary storage language
  - Random numbers
  - Discipline checks
  - Item checks
  - Combat
  - Death/failure/completion
  - Book transition
  - Route effects
  - History-based effects
  - Special combat routing such as one-round fights, compare-loss fights, fixed-round survival, forced victory/failure checks, or routes based on combat result details rather than simple victory
- Flag combat wording that changes ordinary fight behavior:
  - ignore Lone Wolf END loss
  - ignore enemy END loss
  - only apply losses after a certain round
  - fight only one round
  - fight for X rounds or fewer
  - stop if the fight reaches a later round
  - route based on who lost more ENDURANCE
  - route based on equal ENDURANCE loss
  - route based on a combat-round random number
  - route based on weapon used
  - route based on enemy immunity or susceptibility
  - route based on previous enemy or section history
- Write findings by signal/category without copying long prose.
- Every signal must become one of:
  - implemented automation
  - manual helper
  - reviewed no automation
  - ambiguous and queued

## 6. Review Queue / Rulings

- Create or update `testing/logs/LWBOOKN_RULINGS_QUEUE.md`.
- Categorize findings:
  - Already covered
  - Clear automation
  - Player choice/manual helper
  - No sheet change
  - Ambiguous
  - Edition difference
  - Needs playtest ruling
- For each queued ruling, record:
  - stable ID
  - section/support page reference
  - question
  - recommended default
  - impact if wrong
  - current status
- Ask the user a concise batch of questions only after the scan has gone as far as it can.

## 7. Build The Automation Ledger

- Create `testing/logs/LWBOOKN_AUTOMATION_LEDGER.md`.
- Record one row per candidate automation section.
- Recommended columns:
  - Section
  - Trigger timing
  - Rule type
  - Preconditions
  - State change
  - Prompt needed
  - Legal prompt values or choices
  - Web-safe payload needed
  - Player-facing label
  - Status/receipt location
  - Current app support
  - Acceptance test needed
  - Status
- Use consistent trigger timing labels:
  - On entry before text
  - On entry after text
  - Before combat
  - During combat round
  - After combat
  - After random roll
  - After route-check calculation
  - After route button
  - After prompt choice
  - After inventory choice
  - After book transition
  - After completion/repeat
  - Manual only
- The ledger is the build handoff. It should be complete enough that implementation can continue without rereading the whole book.

## 8. Implement Data And App Support

Generate or update:

- Book metadata and app-shell book list.
- Standalone and campaign start-state logic.
- Book-start checkpoints for repeat/replay.
- Simple automation entries.
- Loot buttons.
- Shop buttons and paid route actions.
- Item/Discipline checks.
- Route checks.
- Random roll helpers.
- Staged roll helpers.
- Combat presets.
- Loss/exchange choice helpers.
- Death/failure/completion effects.
- Book transition and repeat-book effects.
- Achievement definitions only after approval.
- Strategy/wiki docs when useful.

Also implement app support when data alone is not enough:

- Special Item combat weapon handling.
- Required/forced weapon handling.
- Active-combat preset sync for stale saves.
- Preferred combat weapon defaults.
- Item history flags for durable route checks.
- Enemy/combat history flags for "if you fought this before" rules.
- Story flags for passes, papers, disguises, and similar objects.
- Book-specific recovery math based on combat history or route history.
- Combat route support for:
  - ignored player loss rounds
  - ignored enemy loss rounds
  - round-limit exits before victory
  - victory-within or too-late exits
  - combat-roll route exits
  - victory choice lists where the book offers a post-combat player choice
  - required weapon or special weapon restrictions
- UI label shaping for player-facing buttons.
- Choices-panel filtering so only real choices appear there.
- Status/receipt output for automation effects.
- Landing page, library, current-section links, and book selector visibility.

## 9. Playable App Lifecycle Pass

This pass is mandatory. Book onboarding is not complete until the app lifecycle works, not just the raw mechanics.

Verify:

- Standalone new character for this book if supported.
- Campaign continuation from the previous book.
- New book setup choices.
- Book-start checkpoint creation.
- First section loaded correctly.
- Completion screen activation.
- Continue-to-next-book state if next book is supported.
- Unsupported-next-book messaging if not supported.
- Repeat this book from completion.
- Death/failure recovery and rewind.
- Save/load after book start.
- Save/load after completion.
- Server restart with current save.
- `/api/state` after restart.
- Browser action buttons for continue/repeat/complete.

## 10. Combat Hardening Pass

For every combat preset, verify:

- Enemy name, CS, END.
- Active weapon selected correctly.
- Required/forced weapon behavior.
- No-weapon penalty.
- Weaponskill.
- Mindblast and enemy immunity.
- Mindshield or equivalent protection.
- Shield or defensive item bonuses.
- Special Item weapons.
- Timed modifiers.
- Fixed-CS fights.
- Per-round effects.
- Double damage or special damage rules.
- Evade availability and route.
- Victory route.
- Defeat route.
- Survival, timeout, or round-limit route.
- Combat history archive.
- Active-combat stale-save repair.

Before this pass can be marked complete, run an automated combat route-target check for the book. It must fail if any preset references a section that is not one of the source links for that section, including:

- `victoryRoute`
- `defeatRoute`
- `evadeRoute`
- `flawlessVictoryRoute`
- `woundedVictoryRoute`
- `playerLossRoute`
- `oneRoundComparisonRoutes`
- `winWithinRoute`
- `tooLateRoute`
- `survivalRoute`
- `roundExceededRoute`
- `victoryChoices`
- `combatRollRoutes`

Special combat wording is not allowed to pass on structural checks alone. For every book, any section that says or implies `one round`, `fight for X rounds`, `compare ENDURANCE loss`, `if you lose more`, `if the enemy loses more`, `if losses are equal`, `survive`, `after X rounds`, `cannot harm`, `only harmed by`, `immune to`, or similar special handling must get a semantic app test that starts the fight through the app and asserts the exact resulting section or state.

A generated combat preset is only complete when the test proves the player-facing behavior matches the section text. "The fight starts" is not enough.

Write `testing/logs/LWBOOKN_COMBAT_SEMANTIC_PLAYTEST.md` with:

- Combat preset count.
- Route-target mismatch count.
- Every corrected or intentionally manual special-combat section.
- Tests that prove app behavior, not just data shape.
- Remaining combat risk, if any.

## 11. UI Meaning And Choices Pass

Every visible control must read like something a player understands.

- Route action labels should be action-first, such as `Purchase White Pass`, not raw audit text.
- Choices card must contain actual player choices only.
- Automation receipts, route effects, applied effects, and audit notes belong in status/receipt areas.
- Route buttons already present in the source text do not need duplicate ordinary-choice cards unless they perform an app action.
- Loot, shop, loss, exchange, combat, roll, continue, and repeat buttons need clear labels.
- The browser should show new books in landing, library, current section, title links, and book navigation.
- Map and image panels must scale to the viewport without cutting off the useful image.

## 12. Achievement And Strategy Planning

- Draft achievement candidates after the route and rules audit are stable.
- Record candidates in `testing/logs/LWBOOKN_ACHIEVEMENT_CANDIDATES.md`.
- For each candidate, record:
  - Stable ID
  - Display name
  - Book number
  - Category
  - Player-facing description
  - Unlock trigger
  - Trigger source
  - Whether it can backfill from existing saves
  - Acceptance test needed
- Do not implement achievement batches until approved.
- Prefer durable triggers:
  - Completed book number
  - Section history
  - Combat history
  - Inventory state
  - Item history
  - Story flags
  - Recorded death/recovery state
  - Book-completion summary
- Avoid triggers that require copied story text, exact prose matching, or a manual rebuild button.
- Draft or update player-facing strategy guides only after route/support knowledge changes enough to help players.
- Strategy guides should be warm, practical, spoiler-conscious when possible, and not written like technical audit reports.

## 13. Generate Tests

Generate or update:

- Section-flow check.
- Rules/start-state smoke test.
- Standalone creation smoke test.
- Campaign continuation smoke test.
- Book lifecycle/repeat smoke test.
- Simple automation smoke test.
- Route/random smoke test.
- Combat smoke test.
- Combat hardening edge test.
- Combat route-target certification test for every onboarded book.
- Terminal-ending recovery test for every death/failure/completion section.
- Automation-language smoke test.
- UI label/static browser smoke test.
- Choices-panel filter smoke test.
- Live-save restart/API smoke test.
- End-to-end playtest.
- Branch playtest.
- Route gauntlet playtest.
- Semantic app playtest for every non-trivial mechanic recorded in the ledger.

Tests should use copied or in-memory saves unless the user explicitly asks to modify the live campaign save.

Semantic app tests must drive the same app behavior a player would use. Depending on the feature, use the browser UI, web API, or assistant method through the same state paths used by the UI. They must assert concrete outcomes:

- Current book and section.
- END, CS, Gold, Meals, and inventory changes.
- Story flags and item history.
- Combat round logs and combat archive.
- Completion, death, repeat, and transition state.
- Player-facing status/receipt text when it matters.

Do not count a data-generation check as a playtest. Data checks prove the helper exists; semantic app tests prove it behaves correctly.

For ruleset changes, tests must also prove:

- Existing saves migrate or normalize correctly.
- New action chart fields appear in the web app.
- New powers/ranks are selectable only at valid book-start or transition points.
- Old-book behavior still passes its regression tests.
- Carry-forward into and out of the new ruleset preserves allowed inventory and history.

## 14. Run Validation

- Python compile.
- Regenerate/check data artifacts.
- Run all smoke tests and playtests.
- Run all route-target certification tests.
- Run all terminal-ending certification and recovery tests.
- Run all semantic app playtests for special combat, random, and route-check sections.
- Run `git diff --check`.
- Confirm `books/` is not staged/tracked.
- Start or refresh local server.
- HTTP smoke test `/assistant.html` and `/api/state`.
- If a book was completed or repeated, verify the live API state matches the expected lifecycle state.

## 15. Run The Playtesting Ladder

The playtesting ladder turns the audit into repeatable confidence. It applies to every onboarded book, not just the current trouble spot, and should run against copied or in-memory saves. It must not change the live campaign save unless explicitly requested.

For every book, "test play" means app-level behavior tests plus representative route playthroughs. A structural smoke test is useful, but it does not qualify a book as human playtest ready by itself.

### Level 1: Basic Validation

- Confirm every expected `sect*.htm` file exists.
- Confirm every source section link points to an existing section.
- Confirm rules/support pages exist or are documented as missing.
- Confirm the optional Project Aon SVG/SVGZ route graph is reachable or documented as unavailable.
- Confirm JSON data files load.
- Confirm Python files compile.
- Confirm the web API starts and returns state.
- Confirm the live save pointer is protected before dry-run work.

### Level 2: Audit Coverage

- Confirm every section has been classified.
- Confirm every mechanical effect is recorded in the section audit or automation ledger.
- Confirm every ambiguity is resolved, marked manual, or listed as waiting for a user ruling.
- Confirm every combat and random-number section appears in the combat/random audit.
- Confirm every annotation and errata note was reviewed.
- Confirm every ruleset change is recorded in `LWBOOKN_RULESET_CHANGE_AUDIT.md` and has either engine support, a manual helper, or a queued ruling.

### Level 3: Automation Coverage

For every recorded mechanic, confirm one of these is true:

- App automation exists.
- A manual UI control/helper exists.
- The reason it remains manual is documented.

Include:

- END, CS, Gold, and book-specific stat changes.
- Meal rules.
- Item gain/loss/use.
- Backpack, Weapons, and Special Items handling.
- Safekeeping, confiscation, storage, and restoration paths.
- Status flags.
- Discipline or item gates.
- Random roll helpers.
- Combat presets.
- Death/recovery.
- Book completion, transition, and repeat.
- Achievement definitions and automatic sync/backfill when approved.

### Level 4: Branch Coverage

- Test every outgoing route at least once where practical.
- Confirm all target sections exist.
- Confirm every reachable branch from section 1 is represented in route data or source-link checks.
- Exercise each major route family at least once in dry-run state.
- Document unreachable, errata-corrected, or source-irregular branches.

### Level 5: Mechanic Outcome Coverage

- Test every non-trivial mechanic outcome:
  - Every random roll result band.
  - Every loot picker option.
  - Every route-check outcome.
  - Every death/failure ending style.
  - Every gear loss and gear restore path.
  - Every combat preset start.
  - Combat victory, defeat, evade, survival, timeout, round-limit, timed-modifier, fixed-CS, and per-round-effect cases where applicable.
  - Special combat routing based on one-round results, fixed-round results, compared ENDURANCE losses, required weapons, immunities, or any route that is not plain victory/defeat.
  - Every book completion, carry-forward transition, and repeat-book reset.
  - Every approved achievement trigger category.

Route-target certification is required before Level 5 can pass. A section with a route mismatch is not human-playtest ready, even if ordinary app smoke tests pass.

For special combat sections, each named outcome in the source text needs its own assertion. Example pattern:

- Player loses more ENDURANCE -> expected target section.
- Enemy loses more ENDURANCE -> expected target section.
- Equal loss -> expected target section.

If a section has three possible outcomes, one passing outcome does not cover the section.

### Level 6: Full-Path Smoke Tests

Run a small set of realistic route dry runs:

- One successful route to book completion.
- One route that exercises death/recovery.
- One route that exercises gear loss/restoration.
- One route that exercises an important item/Discipline-gated path.
- One low-Endurance route.
- One resource-pressure route.
- One route gauntlet for book-specific edge cases.
- One book transition or repeat-book cleanup run when supported.

The target is not every possible playthrough. The target is complete route, branch, and mechanic confidence plus representative full paths.

## 16. Update Docs

- Update agent handoff.
- Update rules audit log.
- Update section-flow baseline.
- Update section audit.
- Update automation-language audit.
- Update automation ledger.
- Update combat/random audit.
- Update route audit.
- Update playtest report.
- Update remaining-risk/release-blocker list.
- Update achievement candidates when achievements are in scope.
- Update public strategy guide notes when route/support knowledge changed enough to matter.

Public-facing docs should sound friendly and team-written. Technical logs can be direct and precise.

## 17. GitHub Workflow

- Open or track a GitHub issue for the book/milestone.
- Use sub-issues only when useful for follow-up fixes discovered by playtesting.
- Commit with `Refs #` while partial, or `Fixes #` when complete.
- Push.
- Verify issue state with GitHub CLI.
- Do not package or release unless the app is actually playable and release-approved.

## 18. Final Output

- Report what was implemented.
- Report what was tested.
- Report what was intentionally left manual.
- Report any ambiguous rulings still needed.
- Report remaining blockers.
- Give the local app URL.

For `Onboard book N`, final output should clearly say whether the book is:

- scan-only complete
- waiting on rulings
- mechanically implemented
- playable by smoke tests
- human playtest ready
- release ready
