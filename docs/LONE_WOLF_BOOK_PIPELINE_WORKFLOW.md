# Lone Wolf Book Pipeline Workflow

This workflow captures the repeatable process for onboarding any Lone Wolf book into the Action Assistant Redux app.

Example command shape:

```powershell
python tools/lw_book_pipeline.py --book 2 --source books/lw/02fotw --workflow full --ask-when-ambiguous
```

Core rule:

The pipeline may automate clear, mechanical findings. If something is ambiguous, it must stop, write the question to a rulings file, and ask before continuing.

## 1. Verify Source

- Confirm the local book folder exists.
- Confirm `books/` is not tracked by git.
- Detect book number, title, section count, section files, rules pages, and support pages.
- Refuse to package or commit source book files.

## 2. Rules Scan

- Read the book's action, rules, combat, and equipment pages.
- Compare against the previous implemented book.
- Detect new or changed rules:
  - Combat Skill / Endurance
  - Disciplines or new powers
  - Healing/recovery
  - Meals and Hunting-style exemptions
  - Backpack, Weapons, Special Items
  - Gold
  - Combat rules
  - Carry-over rules
- Scan page annotations, footnotes, errata, and special notes.
- Write a rules audit log.

## 3. Book Handoff / Start-State Scan

- Find the setup for starting the next adventure.
- Detect what the player receives or chooses:
  - New Discipline/power
  - New gear
  - Meals
  - Gold
  - Special Items
  - Carry-over equipment
  - Item limits or resets
- Produce a start-state implementation plan.
- Stop and ask if starting gear or carry-over logic is unclear.

## 4. Build Section Graph

- Crawl all `sect*.htm`.
- Extract legal route links.
- Check missing sections, invalid links, and unreachable sections.
- Generate `data/bookN-section-flows.json`.
- Write a section-flow baseline log.

## 5. Automation-Language Scan

- Scan every section for automation-likely language:
  - END loss/gain
  - CS changes
  - Meals
  - Gold gain/loss/cost
  - Inventory gain/loss
  - Weapons
  - Backpack Items
  - Special Items
  - Random numbers
  - Discipline checks
  - Item checks
  - Combat
  - Death/failure/completion
- Write signal/category findings without copying long book prose.

## 6. Review Queue / Rulings

- Categorize findings:
  - Already covered
  - Clear automation
  - Player choice/manual helper
  - No sheet change
  - Ambiguous
- If `--ask-when-ambiguous` is enabled:
  - Stop at ambiguous findings.
  - Ask concise questions.
  - Write answers to a rulings file.
  - Resume only after rulings are recorded.

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
  - Current app support
  - Acceptance test needed
  - Status
- Use consistent trigger timing labels:
  - On entry before text
  - On entry after text
  - After combat
  - After random roll
  - After route-check calculation
  - After prompt choice
  - After inventory choice
  - After book transition
  - Manual only
- The ledger is the build handoff. It should be complete enough that implementation can continue without rereading the whole book.

## 8. Implement Data

- Generate or update:
  - Simple automation entries
  - Loot buttons
  - Route checks
  - Paid route actions
  - Item/Discipline checks
  - Random roll helpers
  - Staged roll helpers
  - Combat presets
  - Loss/exchange choice helpers
  - Death/failure/completion effects
  - Book-start handoff/start-state logic

## 9. Achievement And Strategy Planning

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
  - Recorded death/recovery state
  - Book-completion summary
- Avoid triggers that require copied story text, exact prose matching, or a manual rebuild button.
- Draft or update player-facing strategy guides only after route/support knowledge changes enough to help players.
- Strategy guides should be warm, practical, spoiler-conscious when possible, and not written like technical audit reports.
- Public guide work can be deferred until core playability is stable, but the pipeline should still record when guide updates are needed.

## 10. Generate Tests

- Section-flow check.
- Rules/start-state smoke test.
- Simple automation smoke test.
- Route/random smoke test.
- Combat smoke test.
- Automation-language smoke test.
- End-to-end playtest.
- Branch playtest.
- Route gauntlet playtest.

## 11. Run Validation

- Python compile.
- Regenerate/check data artifacts.
- Run all smoke tests and playtests.
- Run `git diff --check`.
- Confirm `books/` is not staged/tracked.
- Start or refresh local server.
- HTTP smoke test `/assistant.html` and `/api/state`.

## 12. Run The Playtesting Ladder

The playtesting ladder turns the audit into repeatable confidence. It should run against copied or in-memory saves and must not change the live campaign save unless explicitly requested.

### Level 1: Basic Validation

- Confirm every expected `sect*.htm` file exists.
- Confirm every source section link points to an existing section.
- Confirm rules/support pages exist or are documented as missing.
- Confirm JSON data files load.
- Confirm Python files compile.
- Confirm the web API starts and returns state.
- Confirm the live save pointer is protected before dry-run work.

### Level 2: Audit Coverage

- Confirm every section has been classified.
- Confirm every mechanical effect is recorded in the section audit or automation ledger.
- Confirm every ambiguity is resolved, marked manual, or listed as waiting for a user ruling.
- Confirm every combat and random-number section appears in the combat/random audit.

### Level 3: Automation Coverage

- For every recorded mechanic, confirm one of these is true:
  - App automation exists.
  - A manual UI control/helper exists.
  - The reason it remains manual is documented.
- Include:
  - END, CS, Gold, and book-specific stat changes
  - Meal rules
  - Item gain/loss/use
  - Backpack, Weapons, and Special Items handling
  - Status flags
  - Discipline or item gates
  - Random roll helpers
  - Combat presets
  - Death/recovery
  - Book completion and transition
  - Achievement definitions and automatic sync/backfill when approved

### Level 4: Branch Coverage

- Test every outgoing route at least once where practical.
- Confirm all target sections exist.
- Confirm every reachable branch from section 1 is represented in route data or source-link checks.
- Exercise each major route family at least once in dry-run state.
- Document unreachable, errata-corrected, or source-irregular branches.

### Level 5: Mechanic Outcome Coverage

- Test every non-trivial mechanic outcome:
  - Every random roll result band
  - Every loot picker option
  - Every route-check outcome
  - Every death/failure ending style
  - Every gear loss and gear restore path
  - Every combat preset start
  - Combat victory, defeat, evade, survival, timeout, round-limit, timed-modifier, fixed-CS, and per-round-effect cases where applicable
  - Every book completion and carry-forward transition
  - Every approved achievement trigger category

### Level 6: Full-Path Smoke Tests

- Run a small set of realistic route dry runs:
  - One successful route to book completion
  - One route that exercises death/recovery
  - One route that exercises gear loss/restoration
  - One route that exercises an important item/Discipline-gated path
  - One low-Endurance route
  - One resource-pressure route
  - One route gauntlet for book-specific edge cases
  - One book transition or repeat-book cleanup run when supported
- The target is not every possible playthrough. The target is complete route, branch, and mechanic confidence plus representative full paths.

## 13. Update Docs

- Update agent handoff.
- Update rules audit log.
- Update section-flow baseline.
- Update automation-language audit.
- Update combat/random audit.
- Update playtest report.
- Update remaining-risk/release-blocker list.
- Update `LWBOOKN_AUTOMATION_LEDGER.md`.
- Update `LWBOOKN_ACHIEVEMENT_CANDIDATES.md` when achievements are in scope.
- Update public strategy guide notes when route/support knowledge changed enough to matter.

Expected technical report names:

- `LWBOOKN_PASS1_RULES_BASELINE.md`
- `LWBOOKN_SECTION_FLOW_BASELINE.md`
- `LWBOOKN_SECTION_AUDIT.md`
- `LWBOOKN_AUTOMATION_LANGUAGE_AUDIT.md`
- `LWBOOKN_AUTOMATION_LEDGER.md`
- `LWBOOKN_COMBAT_AND_RANDOM_AUDIT.md`
- `LWBOOKN_ROUTE_AUDIT.md`
- `LWBOOKN_ROUTE_GAUNTLET_PLAYTEST.md`
- `LWBOOKN_PLAYTEST_REPORT.md`
- `LWBOOKN_ACHIEVEMENT_CANDIDATES.md`

## 14. GitHub Workflow

- Open or track a GitHub issue for the book/milestone.
- Commit with `Refs #` while partial, or `Fixes #` when complete.
- Push.
- Verify issue state with GitHub CLI.
- Do not package or release unless the app is actually playable and release-approved.

## 15. Final Output

- Report what was implemented.
- Report what was tested.
- Report any ambiguous rulings still needed.
- Report remaining blockers.
- Give the local app URL.
