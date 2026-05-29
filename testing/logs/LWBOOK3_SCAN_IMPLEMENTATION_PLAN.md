# LW Book 3 Scan Implementation Plan

Date: 2026-05-28

GitHub issue: #42

Scope: build plan for Book 3 after the rulings queue is answered.

## Inputs Ready

- `testing/logs/LWBOOK3_PASS1_RULES_BASELINE.md`
- `testing/logs/LWBOOK3_RULINGS_QUEUE.md`
- `testing/logs/LWBOOK3_SECTION_FLOW_BASELINE.md`
- `testing/logs/LWBOOK3_ROUTE_GRAPH_CHECK.md`
- `testing/logs/LWBOOK3_AUTOMATION_LANGUAGE_AUDIT.md`
- `data/book3-section-flows.json`

## Build Slice 1: Book Metadata And Setup

- Add Book 3 metadata to app book lists, landing page, library/current links, and supported-book state.
- Add campaign transition from completed Book 2 into Book 3.
- Add standalone Book 3 setup if the player starts here fresh.
- Add one new Kai Discipline during Book 3 setup.
- Add Book 3 starting Gold roll, carry-over addition, and hard 50-Crown cap.
- Add Map of Kalte, winter gear handling, and two equipment choices.
- Enforce Weapon, Backpack, body armor, and helmet limits according to rulings.
- Create Book 3 start checkpoint for repeat-book replay.

## Build Slice 2: Rule Helpers

- Add Book 3 Hunting suppression for Meal requirements in Kalte.
- Add ice-sledge food/provisions state and receipt text.
- Add Red Laumspur as a distinct item.
- Add Baknar oil as a Book 3-only story flag.
- Add Blue Stone Triangle and Silver Helm item models.
- Add mission-failure ending support for section 61.

## Build Slice 3: Section Automation Ledger

- Convert all automation-language signals into `LWBOOK3_AUTOMATION_LEDGER.md`.
- Mark each signal as implemented automation, manual helper, reviewed no automation, or queued ambiguity.
- Add player-facing labels for route/check buttons before wiring them into Choices.
- Keep automation receipts in the status area, not in the Choices panel.

## Build Slice 4: Combat, Random, And Routes

- Add combat presets for all Book 3 fights, including immunity, forced weapon, evasion, carry-forward damage, and per-round damage notes.
- Add random roll helpers and staged rolls.
- Add Discipline and item route checks with friendly labels.
- Add inventory gain/loss choices and destructive-choice prompts.
- Add history-based route support where current inventory is not enough.

## Build Slice 5: Completion, Achievements, And Docs

- Add section 350 completion behavior.
- Add unsupported Book 4 messaging until Book 4 is onboarded.
- Run achievement-candidate scan and queue approvals.
- Add or update Book 3 strategy/wiki docs in the friendly public tone used by the rest of the project.

## Verification

- Run Python compile checks for new scripts.
- Run section-flow, route graph, and automation-language check modes.
- Run existing app smoke tests.
- Add Book 3 setup and transition tests.
- Run a Book 3 automated route gauntlet covering setup, early branches, combat, death/failure, and completion.
- Restart the local server only after implementation, then hand the app to user playtesting.
