# Lone Wolf AA2 Workflow

This is the Grey Star workflow translated into a Lone Wolf rebuild plan.

## 1. Rules Baseline

Read the Book 1 rules pages before touching automation:

- `books\lw\01fftd\action.htm`
- `books\lw\01fftd\cmbtrulz.htm`
- `books\lw\01fftd\crtable.htm`
- equipment pages
- discipline pages
- errata and footnotes

Record findings in `testing\logs\LWBOOK1_PASS1_RULES_BASELINE.md`.

## 2. Section Audit

Audit section by section, starting at section 1.

For each section record:

- section type
- outgoing links
- stat changes
- meals/provisions
- item gains/losses
- combat
- random number checks
- Kai Discipline checks
- death/failure endings
- completion endings
- ambiguity/questions

Store the table in `testing\logs\LWBOOK1_SECTION_AUDIT.md`.

## 3. Automation Audit

Convert safe, mechanical section results into data only after the section audit supports them.

Targets:

- `data\book1-simple-automations.json`
- `data\book1-section-flows.json`
- later route-check files if needed

Do not automate choices that belong to the player.

## 4. Combat And Random Audit

Build a separate pass for:

- combat presets
- special combat rules
- no-weapon penalties
- evasion
- random number table routing
- discipline modifiers

Store in `testing\logs\LWBOOK1_COMBAT_AND_RANDOM_AUDIT.md`.

## 5. Route Audit

Build a graph from the local section files and collapse it into player-facing route families.

Store:

- raw route graph under `testing\tmp`
- readable route audit in `testing\logs\LWBOOK1_ROUTE_AUDIT.md`

## 6. Achievements

Achievements should come from the route audit, not vibes.

Create:

- journey achievements
- route achievements
- combat achievements
- item/discovery achievements
- replay targets

Store candidates in `testing\logs\LWBOOK1_ACHIEVEMENT_CANDIDATES.md`.

## 7. Playtesting

Use both targeted dry tests and route tests.

Minimum:

- new character creation
- save/load
- section movement
- section automation
- combat
- death repeat/rewind
- book completion
- story route
- achievement route

Write results to `testing\logs\LWBOOK1_PLAYTEST_REPORT.md`.

## 8. Strategy Guide

Public guides should feel like a BradyGames-style player guide:

- warm
- practical
- spoiler-conscious when possible
- direct about useful choices
- not clinical unless it is an audit log

Technical audit documents can stay terse.

## 9. GitHub And Release Loop

For behavior work:

1. Open issue.
2. Implement.
3. Test.
4. Update docs.
5. Commit and push.
6. Package only when release-worthy.
7. Publish release only when playable.
8. Close/verify issue.

Never include Project Aon book files in git or release ZIPs.
