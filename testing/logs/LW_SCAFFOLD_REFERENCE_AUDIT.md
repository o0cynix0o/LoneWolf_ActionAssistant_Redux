# Lone Wolf Scaffold Reference Audit

Date: 2026-05-27

Issue: #18

## Scope

Searched the project for direct Grey/Gray Star references and nearby scaffold identifiers:

- `grey star`, `gray star`, `greystar`, `graystar`
- legacy achievement IDs such as `gs1_`
- nearby old-rule terms such as `Moonstone`, `Willpower`, `Magicks`, `StaffWillpower`, and `Nobles`

The search excluded local Project Aon book files, generated caches, temp test folders, release artifacts, and `.git` internals.

## Cleaned

- Removed the unused legacy `gs1_` through `gs4_` achievement catalogue from `lonewolf_redux.py`.
- Removed the unused legacy achievement trigger block from `achievement_satisfied`.
- Updated the runtime module header so it no longer describes Book 1 as an unfinished scaffold.
- Renamed the save-brand migration helper to a neutral legacy-branding name.
- Removed direct legacy combat-loss field references from `assistant.html` and the CLI history view.
- Kept old combat-loss save migration working through a neutral legacy key list.
- Replaced the landing page's Moonstone subtitle with Book 1 Lone Wolf wording.
- Updated `AGENT.md`, `README.md`, and `docs/AGENT_HANDOFF.md` where their status language was stale.

## Intentional References Retained

These are not runtime leftovers:

- `AGENT.md`, `README.md`, and handoff docs still say the project used the Grey Star workflow as its template.
- `docs/wiki/AGENT.md` intentionally names Grey Star as the wiki tone/style reference.
- `testing/logs/BOOTSTRAP_HANDOFF.md` is a historical bootstrap log.
- `testing/logs/LWBOOK1_PIPELINE_BACKFILL.md` records the earlier comparison against the Grey Star guide style.
- `docs/RELEASE_NOTES_PREALPHA.md` records the original scaffold source in release-note form.

## Later-Book Rule Debt

The broader scan still finds old-rule terms in inactive or not-yet-supported later-book transition code, especially Willpower, Magicks, Staff handling, and Moonstone references.

Those are not Book 1 browser-facing Grey/Gray Star mentions, but they are real later-book scaffold debt. They should be replaced by the Book 2+ rules scan and book handoff pipeline instead of being renamed blindly.

## Verification

- Direct `gs1_` through `gs4_` runtime achievement definitions/triggers removed.
- Browser/CLI direct `GrayStarLoss` display fallback removed.
- Runtime grep is clean for direct Grey/Gray Star names.
- Project compile, Book 1 smoke/playtest ladder, achievement smoke, automation-language audit JSON, and HTTP smoke passed after cleanup.
