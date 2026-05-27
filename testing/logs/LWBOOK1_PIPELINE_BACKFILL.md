# LW Book 1 Pipeline Backfill

Date: 2026-05-27

Scope: issue #15 pass applying `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md` to Book 1 after the Book 1 implementation was already mostly complete.

This log records what was skipped because it already exists, what was backfilled, and what remains blocked before release.

## Completed Before This Pass

- Source verification: local Book 1 files are installed under `books/lw/01fftd`, and `books/` is not tracked.
- Rules scan: `LWBOOK1_PASS1_RULES_BASELINE.md`.
- Section graph: `LWBOOK1_SECTION_FLOW_BASELINE.md` and `data/book1-section-flows.json`.
- Simple automation baseline: `LWBOOK1_SIMPLE_AUTOMATION_BASELINE.md` and `data/book1-simple-automations.json`.
- Combat/random support: `LWBOOK1_COMBAT_AND_RANDOM_AUDIT.md`, `LWBOOK1_ROUTE_RANDOM_AUDIT.md`, and related smoke tests.
- Automation-language scan: `LWBOOK1_AUTOMATION_LANGUAGE_AUDIT.md`, currently reporting zero uncovered signal categories.
- Playtesting ladder coverage: end-to-end route, branch playtest, combat edge playtest, and route gauntlet playtest.

## Backfilled In This Pass

- Reusable book pipeline workflow: `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md`.
- Automation ledger: `LWBOOK1_AUTOMATION_LEDGER.md`.
- Achievement candidate list: `LWBOOK1_ACHIEVEMENT_CANDIDATES.md`.
- Player-facing Book 1 strategy guide: `docs/wiki/Book-1-Strategy-Guide.md`.
- Strategy guide index updated to the Grey Star guide tone and perspective.

## Grey Star Tone Reference

The Grey Star strategy guides use a player-first voice:

- They explain what the book is testing, not just what the audit found.
- They give a clear first-clear recommendation.
- They keep route numbers as practical landmarks.
- They call out items and mistakes in ordinary player language.
- They reserve technical audit terms for `testing/logs`.

The Lone Wolf Book 1 guide follows that same perspective while avoiding copied book prose.

## Remaining Release Blockers

- Manual browser ergonomics pass.
- Final release checklist pass.
- Packaging/release approval.
