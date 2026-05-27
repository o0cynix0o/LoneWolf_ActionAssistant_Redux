# Lone Wolf Book Source Map

This doc is the quick map for the local Lone Wolf book corpus used by audits, route work, automation planning, and release checks.

The Project Aon book files are not part of the public repository or release ZIP. Each developer/player must download the standard HTML editions directly from Project Aon for personal use. See `docs/INSTALL_PROJECT_AON_BOOKS.md`.

## Source Priority

Preferred source order:

1. locally installed corpus under `books/lw/`
2. local rules and support pages in the same book folder
3. original Lone Wolf reference project for prior app behavior only
4. Project Aon plus errata as fallback or cross-check

The local corpus is the audit baseline for development and testing. Do not copy large book passages into audit reports.

## Local Corpus Layout

Main local corpus root:

- `books/lw/`

Typical book folder contents:

- `title.htm`
- `sect1.htm` through the book's last section file
- `gamerulz.htm`
- `equipmnt.htm`
- `action.htm`
- `cmbtrulz.htm`
- `crsumary.htm`
- `crtable.htm`
- `random.htm`
- `errata.htm`
- map, illustration, and art assets

Most useful files during audits:

- `sect*.htm`
  section text and route tracing
- `gamerulz.htm`
  book-specific rules context
- `equipmnt.htm`
  starting gear, equipment choices, carry-over rules, and inventory context
- `action.htm`
  Action Chart and tracked fields
- `cmbtrulz.htm`
  combat rules
- `crsumary.htm`
  combat sequence checklist
- `crtable.htm`
  combat result table reference
- `random.htm`
  random-number table guidance
- `errata.htm`
  Project Aon errata notes and known corrections, when present

Some Project Aon book folders include extra notes, footnotes, or support pages. The book pipeline must scan those pages too, because later books often introduce rule tweaks, annotations, and start-of-adventure handoff changes outside the numbered sections.

## Lone Wolf Book Folder Map

Current implemented/audited folder:

- `01fftd`
  `Flight from the Dark`

Known future pipeline targets:

- `02fotw`
  `Fire on the Water`
- `03tcok`
  `The Caverns of Kalte`
- `04tcod`
  `The Chasm of Doom`
- `05sots`
  `Shadow on the Sand`

Do not treat a future folder as supported just because it exists locally. Each book must pass the full workflow in `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md`.

## Recommended Audit Start Pattern

For a new Lone Wolf book audit:

1. open `books/lw/<code>/title.htm` and confirm the title
2. inspect supporting pages such as `gamerulz.htm`, `equipmnt.htm`, `action.htm`, `cmbtrulz.htm`, `crsumary.htm`, `crtable.htm`, `random.htm`, `errata.htm`, and any annotation/footnote pages present
3. scan the start-of-book handoff for new Disciplines, new gear, carried equipment, inventory resets, and special rules
4. trace sections from `sect1.htm`
5. run a mechanical sweep across `sect*.htm`
6. write report files under `testing/logs/`
7. write generated sweep artifacts under `testing/tmp/`
8. stop and ask for rulings when a rule, item container, optional payment, meal timing, or carry-over effect is ambiguous

## Current Book 1 Baseline

Book 1 folder:

- `books/lw/01fftd`

Expected section range:

- `sect1.htm` through `sect350.htm`

Checked-in data artifacts:

- `data/book1-section-flows.json`
- `data/book1-simple-automations.json`
- `data/book-route-checks.json`

Primary technical audit logs:

- `testing/logs/LWBOOK1_PASS1_RULES_BASELINE.md`
- `testing/logs/LWBOOK1_SECTION_FLOW_BASELINE.md`
- `testing/logs/LWBOOK1_AUTOMATION_LANGUAGE_AUDIT.md`
- `testing/logs/LWBOOK1_AUTOMATION_LEDGER.md`
- `testing/logs/LWBOOK1_COMBAT_AND_RANDOM_AUDIT.md`
- `testing/logs/LWBOOK1_PLAYTEST_REPORT.md`
- `testing/logs/LWBOOK1_AUDIT_INDEX.md`

## Repo Hygiene

- `books/lw/` is local reference material, ignored by git, and not packaged for release
- audit docs should reference source files and sections instead of copying text
- workflow docs belong in `docs/`
- local reports belong in `testing/logs/`
- generated sweep artifacts belong in `testing/tmp/`
- public strategy pages belong in `docs/wiki/` and can be mirrored to the GitHub wiki when approved
