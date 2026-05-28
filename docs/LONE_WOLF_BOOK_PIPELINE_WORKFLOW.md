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
- `testing/logs/LWBOOKN_RULINGS_QUEUE.md`
- `testing/logs/LWBOOKN_SECTION_FLOW_BASELINE.md`
- `testing/logs/LWBOOKN_SECTION_AUDIT.md`
- `testing/logs/LWBOOKN_AUTOMATION_LANGUAGE_AUDIT.md`
- `testing/logs/LWBOOKN_AUTOMATION_LEDGER.md`
- `testing/logs/LWBOOKN_COMBAT_AND_RANDOM_AUDIT.md`
- `testing/logs/LWBOOKN_ROUTE_AUDIT.md`
- `testing/logs/LWBOOKN_ROUTE_GRAPH_CHECK.md` when a Project Aon SVG route graph is available
- `testing/logs/LWBOOKN_PLAYABLE_PIPELINE.md`
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
- Detect new or changed rules:
  - Combat Skill and Endurance
  - Disciplines, new powers, rank changes, or power upgrades
  - Healing, recovery, poison, fatigue, and history-based recovery
  - Meals and Hunting-style exemptions or suppressions
  - Backpack, Weapons, Special Items, item limits, and item containers
  - Gold gains, costs, caps, and carry-over
  - Combat rules, enemy immunities, weapon restrictions, timed effects, evasion, survival, fixed-CS fights, and per-round damage
  - Carry-over rules from the previous book and into the next book
  - Special Items that behave as weapons, passes, keys, flags, currencies, or removable story objects
  - Durable item history checks where current inventory is not enough
- Record all rule deltas and implementation needs in the rules baseline.

## 3. Book Handoff / Start-State Scan

- Find the setup for starting the book.
- Detect what the player keeps, loses, receives, chooses, rolls, exchanges, or caps:
  - New Discipline/power
  - New gear
  - Weapons and weapon exchanges
  - Backpack availability and Backpack Items
  - Special Items
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
- Generate or update `data/bookN-section-flows.json`.
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
  - Random numbers
  - Discipline checks
  - Item checks
  - Combat
  - Death/failure/completion
  - Book transition
  - Route effects
  - History-based effects
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
- Story flags for passes, papers, disguises, and similar objects.
- Book-specific recovery math based on combat history or route history.
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
- Automation-language smoke test.
- UI label/static browser smoke test.
- Choices-panel filter smoke test.
- Live-save restart/API smoke test.
- End-to-end playtest.
- Branch playtest.
- Route gauntlet playtest.

Tests should use copied or in-memory saves unless the user explicitly asks to modify the live campaign save.

## 14. Run Validation

- Python compile.
- Regenerate/check data artifacts.
- Run all smoke tests and playtests.
- Run `git diff --check`.
- Confirm `books/` is not staged/tracked.
- Start or refresh local server.
- HTTP smoke test `/assistant.html` and `/api/state`.
- If a book was completed or repeated, verify the live API state matches the expected lifecycle state.

## 15. Run The Playtesting Ladder

The playtesting ladder turns the audit into repeatable confidence. It should run against copied or in-memory saves and must not change the live campaign save unless explicitly requested.

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
  - Every book completion, carry-forward transition, and repeat-book reset.
  - Every approved achievement trigger category.

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
