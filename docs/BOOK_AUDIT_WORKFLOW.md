# Lone Wolf Full Book Audit Workflow

> AA2 note: this workflow is now aimed at Lone Wolf Book 1 first. Use Book 1's Kai Disciplines, Gold Crowns, Meals, Backpack, Weapons, Special Items, Endurance, Combat Skill, and random-number rules as the vocabulary for new audit work.

This is the Lone Wolf AA2 version of the full book audit standard.

Use this when the task is to:

- read a Lone Wolf book from the local corpus
- map routes and endings
- find missing item, Kai Discipline, combat, and random-number rules
- create structured automation ledgers
- propose route, exploration, story, and item achievements
- leave repeatable local reports for later implementation work

## Standard Request Phrases

- `Run the Full Book Audit for Lone Wolf Book X`
- `Run the Full Book Audit + Build for Lone Wolf Book X`

The first means analysis and reports only.

The second means:

- analysis
- reports
- proposal
- implementation of approved findings
- player-facing strategy guide draft or update, when route/support changes enough to matter
- main repo push and GitHub Wiki publish for public wiki pages
- validation

## Source Material

Use the local book corpus first:

- `books/lw/`

For Lone Wolf book audits, the preferred source order is:

1. local corpus under `books/lw/<book-code>/`
2. local supporting pages in the same folder:
   - `gamerulz.htm`
   - `discplnz.htm`
   - `footnotz.htm`
   - `equipmnt.htm`
   - `action.htm`
   - `cmbtrulz.htm`
   - `crsumary.htm`
   - `crtable.htm`
   - `random.htm`
   - `errata.htm`
   - `sage.htm`
3. Project Aon text and errata only as fallback, cross-check, or gap filler

The local corpus is the primary offline audit baseline because it gives section files, rules pages, footnotes, images, and errata locally.

Do not copy large passages of book text into committed docs. Reference files and sections instead.

See also:

- `docs/BOOK_SOURCE_MAP.md`

## Expected Local Report Outputs

For each book, the audit should usually produce:

- `LWBOOKX_AUTOMATION_LEDGER.md`
- `LWBOOKX_ENDINGS_AND_ROUTE_FAMILIES.md`
- `LWBOOKX_ROUTE_AUDIT.md`
- `LWBOOKX_RULES_AND_ITEMS_AUDIT.md`
- `LWBOOKX_COMBAT_AND_RANDOM_AUDIT.md`
- `LWBOOKX_ACHIEVEMENT_CANDIDATES.md`

These are local working reports and normally stay in `testing/logs/`.

`LWBOOKX_AUTOMATION_LEDGER.md` is the build handoff. It should be structured enough that implementation can work from it without rereading the whole book.

Generated sweep artifacts belong in `testing/tmp/`.

Player-facing wiki pages live under `docs/wiki/` and are a separate output from the technical reports. Strategy guides should usually update:

- `docs/wiki/Book-X-Strategy-Guide.md`
- `docs/wiki/Strategy-Guide.md`, when the guide index or style description changes

After changing files in `docs/wiki/`, publish those same changed pages to the separate GitHub Wiki repository:

- `https://github.com/o0cynix0o/LoneWolfRedux_ActionAssistant.wiki.git`

Pushing the main repository alone does not update the live GitHub Wiki.

## Audit Steps

### 1. Read The Book Text

Start in the local corpus:

- confirm the book with `title.htm`
- read `gamerulz.htm`, `equipmnt.htm`, `action.htm`, `cmbtrulz.htm`, `crtable.htm`, `footnotz.htm`, and `errata.htm`
- read `discplnz.htm`, `sage.htm`, and `crsumary.htm` when present
- trace the adventure from `sect1.htm`

Review the book with an eye toward:

- branch points
- Kai Discipline checks
- item pickups
- forced item loss or inventory constraints
- Endurance, Combat Skill, Gold Crown, and inventory changes
- special combat rules
- random-number rolls
- permanent penalties or bonuses
- unique endings
- route-check math that decides a legal destination, such as current END, current CS, a current-stat threshold, or a random roll plus current stats

### 2. Map Endings And Route Families

Identify:

- the success ending
- hard failure endings
- major winning route families
- important item or Kai Discipline dependencies

The goal is to understand the meaningful route families first, then fill in the smaller branches.

### 3. Run The Route Audit

Create `LWBOOKX_ROUTE_AUDIT.md` as a required report, separate from the shorter endings summary.

The route audit should record:

- every section file in the expected range
- every source link and any invalid target
- every section reachable from section 1
- sections with no incoming source link
- terminal/no-out-link endpoints, classified as success, death/failure, or needs human classification
- every branch point with two or more outgoing section links
- every branch point that can still reach the success ending
- shortest known source-link path to the success ending
- opening route branches and their reachable endpoints
- route-family starter groups for later human classification

Do not confuse this with testing every possible playthrough. The route audit is graph coverage and route-family classification. The playtest ladder later turns the route audit into dry-run coverage.

The route audit is allowed to sound technical. It is a working report. Do not copy that voice straight into the public strategy guide.

### 4. Run A Mechanical Text Sweep

Run a machine-assisted sweep over every `sect*.htm` for automation language.

Useful Lone Wolf search terms include:

- `lose`
- `gain`
- `restore`
- `deduct`
- `add`
- `erase`
- `discard`
- `Meal`
- `ENDURANCE`
- `COMBAT SKILL`
- `Gold Crowns`
- `Meal`
- `Kai Discipline`
- `Weaponskill`
- `Random Number Table`
- `if you possess`
- `if you have`
- `if you lack`
- `if you know`
- `turn to`

Treat the sweep as a candidate generator, not as truth. The human audit must confirm context, timing, and whether the text describes an actual state change.

Before leaving each section, run the route-check pass:

- Does the section ask the player to calculate a total, final score, or current-stat threshold before choosing a route?
- Does the section ask for a random number and then add current END, CS, Gold Crowns, item bonuses, or Kai Discipline bonuses?
- Does a same-section entry effect happen before the route check? If so, mark the route check as needing the entry effect applied first.
- Can the result be represented in `data/book-route-checks.json` as a Choices-card route check, or is it already covered as a Section Roll helper?
- Record the route-check formula, thresholds, legal destinations, timing, and app support status in the section audit or automation ledger.

### 5. Build The Section Automation Ledger

Create one row per candidate automation section.

Recommended columns:

- section
- trigger timing
- rule type
- preconditions
- state change
- prompt needed
- legal prompt values or choices
- web-safe payload needed
- current app support
- acceptance test needed
- status

Use consistent trigger timing labels:

- on entry before text
- on entry after text
- after combat
- after random roll
- after route-check calculation
- after prompt choice
- after inventory choice
- after book transition
- manual only

### 6. Audit Missing Rules And Items

Scan for high-value automation candidates:

- Kai Discipline-gated branches
- Gold Crown, Meal, and inventory spending
- item bonuses or special item behavior
- section entry damage or healing
- forced gains and losses
- route-check calculations and current-stat thresholds
- combat exceptions
- permanent stat changes
- book-specific restrictions

Mark each candidate as:

- already supported
- partly supported
- missing
- better left manual for now

### 7. Audit Combat Exceptions

Create a combat exception table for every combat found in the book.

Recommended columns:

- section
- enemy name
- enemy Combat Skill
- enemy Endurance
- Kai Discipline modifiers
- weapon restrictions
- evade rules
- auto-win or auto-loss conditions
- post-combat state changes
- current app support
- acceptance test needed

### 8. Audit Random Number And Prompt Flows

Create a table for every roll or structured choice that should be supported by automation or the web UI.

Recommended columns:

- section
- prompt label
- visible option text
- legal values
- random number modifier
- zero-counts-as-ten behavior
- result mapping
- state changes
- web context text needed
- current app support
- acceptance test needed

### 9. Compare Against The App

Check the current script and web UI so the audit distinguishes:

- what the book contains
- what the app already supports
- what still needs implementation

For this project, start with:

- `lonewolf_redux.py`
- `app_server.py`
- `assistant.html`
- `data/crt.json`

### 10. Draft Achievement Candidates

Propose a first batch of:

- route achievements
- exploration achievements
- story achievements
- item or discovery achievements
- survival and resource achievements

Good achievement candidates are memorable, triggerable from reliable state, and do not depend on copied book text.

For each proposed achievement, record:

- stable ID
- display name
- book number
- category
- player-facing description
- unlock trigger
- trigger source: section history, book summary, combat history, inventory, status flag, or completed-book state
- whether it can be backfilled from existing saves
- dry-run acceptance check

Prefer durable triggers over fragile one-off UI events. Good triggers include:

- completed book number
- specific section or section-combination visits
- combat history entries and combat summary counts
- final book summary stats
- inventory items present in current state or book-completion summary
- recorded death/recovery counts

Avoid achievement triggers that require copied story text, exact prose matching, or a manual button press just to rebuild history.

The achievement workflow for each book is:

1. Draft the candidate list during the audit.
2. Show the list to the user for approval before implementation.
3. Implement approved definitions and trigger checks.
4. Sync achievements automatically from save history whenever state is loaded or served.
5. Preserve unlocked achievements permanently within the save/profile state.
6. Add or update the Achievements tab so the player can inspect unlocked, locked, and recent achievements.
7. Add backfill tests using dry-run saves so finished books can populate achievements without replaying.

Do not add a manual "rebuild achievements" button unless the user specifically asks for one. Automatic sync/backfill is the standard.

### 11. Write The Reports

Summarize:

- endings and route families
- route audit graph coverage and route-family starters
- the automation ledger
- missing rules and items
- combat and random-number exceptions
- top implementation candidates
- achievement candidates

The reports should let a later chat continue without rereading the conversation.

Reports are allowed to use audit language such as graph coverage, source links, trigger basis, branch points, and route-family classification. Keep that language in the reports unless the player-facing guide truly needs a small piece of it.

### 12. Propose Top Build Candidates

Before implementation, summarize:

- the best missing rules to automate first
- the best achievement batch to add
- which achievements should backfill from existing save data
- which achievements require a future replay
- assumptions and ambiguities
- acceptance checks for each proposed automation

### 13. Implement Approved Findings

If the user approves build-out:

- add rule and item support
- add achievement definitions and trigger checks
- add automatic achievement sync/backfill during load and state serving
- expose achievement payloads to the web app
- add or update the Achievements tab
- keep route-only choices on the book page unless the assistant needs a mechanical prompt
- keep unlocked achievements when death recovery, rewind, repeat-book, or next-book transitions occur
- add or update the book-complete repeat option when replay cleanup is useful
- update player-facing strategy guides when route, achievement, or support behavior changes
- validate in both CLI and web paths when possible

The repeat-book option should:

- keep the same character
- keep the same inventory unless the book rules or user ask otherwise
- keep completed-book records and unlocked achievements
- reset current section to section 1 of the completed book
- reset Endurance to current maximum
- reset book-start resources such as Gold Crowns only when the book rules require it
- reset current combat, death state, section checkpoints, and current-book stats for the new pass
- preserve the ability to continue to the next book from the completed-book screen before repeating

### 14. Run The Playtesting Ladder

After implementation, run validation in six levels. The goal is complete route, branch, and mechanic coverage, plus a few full-path smoke tests. Do not try to enumerate infinite full playthroughs when loops or repeated state changes make that impractical.

#### 1. Basic Validation

Confirm the book and app data are structurally sound:

- every `sect*.htm` file exists for the expected section range
- every source section link points to an existing section
- rules/supporting pages needed by the audit exist or are documented as missing
- JSON data files load without syntax errors
- Python files compile
- the web API starts and returns state
- the live save pointer is protected before any dry-run work

#### 2. Audit Coverage

Confirm every section has been accounted for:

- every section is classified by type: story, route choice, loot, combat, stat change, meal, random roll, Kai Discipline check, gear loss/restore, death/failure, book completion, or special case
- every mechanical effect is recorded in the section audit or automation ledger
- every ambiguity is either resolved with a user ruling or marked as manual/undecided
- every combat and random-number section appears in the combat/random audit

#### 3. Automation Coverage

For every recorded mechanic, confirm it has one of three outcomes:

- app automation exists
- a manual UI control exists
- the reason it remains manual is documented

This includes:

- END, CS, Gold Crown changes
- Meal rules
- item gain/loss/use
- Backpack handling
- status flags
- Kai Discipline gates and costs
- random roll helpers
- combat presets
- death/recovery
- book completion and transition
- achievement definitions and automatic sync/backfill
- repeat-book restart behavior

#### 4. Branch Coverage

Test every outgoing route at least once:

- crawl all book-page links from every section
- confirm all target sections exist
- confirm every reachable branch from section 1 is represented in route data or source-link checks
- exercise each branch family at least once in dry-run state
- document unreachable or errata-corrected branches

Route choices can remain on the book page links when the assistant panel would only duplicate navigation. Mechanical branches still need assistant support or documentation.

#### 5. Mechanic Outcome Coverage

Test every non-trivial mechanic outcome:

- every random roll result band
- every loot picker option
- every status toggle
- every book-approved payment, loss, or substitution mode
- every death/failure ending style
- every gear loss and gear restore path
- every combat preset start
- combat victory, defeat, evade, survival, timeout, round-limit, timed-modifier, fixed-CS, and per-round-effect cases where applicable
- every book completion and carry-forward transition
- every achievement trigger category
- expected unlocked/missing achievement counts for at least one representative save
- repeat-book reset while preserving achievements

These tests should run against copied or in-memory saves. They must not change the live campaign save unless the user explicitly asks.

#### 6. Full-Path Smoke Tests

Run a small set of realistic full-route dry runs:

- one successful route to the book completion section
- one route that exercises death/recovery
- one route that exercises gear loss/restoration
- one route that earns a story or discovery achievement
- one low-Endurance route
- one important item/Kai Discipline-gated route
- one repeat-book cleanup run from a completed-book state
- book-specific edge-case routes found during the audit

The success target is not "every infinite playthrough." The success target is 100% route/branch/mechanic coverage plus representative complete paths.

### 15. Update Public Strategy Guides

After the audit/build/playtest work, update the public strategy guide when the book now has better route knowledge, new achievements, new assistant support, or changed advice.

The strategy guide is not a technical manual. It should read like a friendly BradyGames-style player guide:

- conversational, warm, and useful while someone is playing
- focused on what kind of run to make, what to chase, and what to avoid
- spoiler-friendly, but not a dump of copied book text
- section numbers used as helpful landmarks, not as the whole explanation
- route advice written as paths, threads, or replay goals rather than audit classifications
- clear first-clear advice and clear replay/achievement cleanup advice

Use a public guide structure like:

1. Quick start or quick answer
2. What the book is really testing
3. Best first playthrough
4. Paths worth knowing
5. Items worth chasing or respecting
6. Combat, Kai Discipline, and inventory tips
7. Common mistakes
8. Achievement cleanup
9. Final recommendation

Keep story summaries and tone, but keep them short enough to help the player understand the run. The guide should feel like someone sitting beside the player saying, "Here is the play," not like an audit report.

Before publishing a strategy guide, run a voice sweep and remove or rewrite report-style language such as:

- `route audit`
- `route graph`
- `success-capable`
- `source-link`
- `test harness`
- `support data`
- `mechanical-effect`
- `trigger basis`
- `classification`

It is fine for the app to be mentioned when the advice is practical, for example "use the Combat tab" or "let the assistant store your gear." Avoid talking about internals unless the page is explicitly a developer report.

When the guide is ready:

1. Commit and push the `docs/wiki/` changes to the main repository.
2. Clone or update `https://github.com/o0cynix0o/LoneWolfRedux_ActionAssistant.wiki.git`.
3. Copy only the changed public wiki pages into the wiki repo.
4. Run `git diff --check` in the wiki repo.
5. Commit and push the wiki repo.
6. Verify the wiki remote points at the new commit.

## What Usually Stays Manual

Leave rules manual when they are too ambiguous, too isolated, or easy for the player to perform once without bookkeeping pain.

Document them anyway so they are not lost.

## What Usually Gets Automated First

Highest-value automation candidates are usually:

- Endurance, Combat Skill, Gold Crown, and inventory changes
- item gains and forced losses
- Kai Discipline-gated prompts
- special combat setup rules
- reliable story achievement triggers
- achievement auto-backfill from durable save data
- completion and repeat-book replay support

## Naming Conventions

Reports:

- `LWBOOK1_*`
- `LWBOOK2_*`
- `LWBOOK3_*`
- `LWBOOK4_*`

Temporary sweep artifacts:

- `lwbook1_source_sweep.json`
- `lwbook1_source_inventory.json`

## Success Condition

The audit is successful when another chat can pick up the book with:

- route picture
- missing rule list
- item list
- combat and random-flow list
- achievement plan
- implemented/backfillable achievement status
- local report files
- validation notes
- updated public strategy guide, when route/support knowledge changed
- live GitHub Wiki publish status for changed public wiki pages
- a completed six-level playtesting ladder, or clear notes on which levels still need data/user rulings

without needing the original conversation.
