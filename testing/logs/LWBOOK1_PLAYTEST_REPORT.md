# Book 1 Playtest Report

Date: 2026-05-26

Scope: issue #1 character/sheet rebuild, issue #2 section-flow baseline, and issue #3 simple automation smoke tests.

## Checks

- Python compile: `app_server.py`, `lonewolf_redux.py`, `launch_lonewolf_redux.py`, and `ws_server.py`.
- Deterministic character creation through `create_book1_character_state`.
- Combat smoke for a Book 1 character with Kai Disciplines.
- Section-flow baseline check with `testing\lwbook1_section_flow_audit.py --check`.
- Simple automation smoke with `testing\lwbook1_simple_automation_smoke.py`.
- Local HTTP smoke on `http://127.0.0.1:8797`.

## Results

- Deterministic creation with CS roll 4 produced Combat Skill 14.
- Endurance roll 6 plus Chainmail Waistcoat roll 4 produced Endurance 30/30.
- Kai Discipline selection stored five disciplines.
- Weaponskill roll 6 mapped to Axe.
- Starting inventory stored Axe, one Meal, Map of Sommerlund, Chainmail Waistcoat, and 3 Gold Crowns.
- New character state did not include `WillpowerCurrent`.
- Combat smoke against a Giak used Lone Wolf weapon/Kai modifiers instead of Staff/Willpower math.
- `assistant.html` returned HTTP 200.
- `/api/book-files` reported Book 1 installed from `books\lw\01fftd`.
- `/books/lw/01fftd/sect1.htm` returned HTTP 200.
- `/api/state` no longer exposes Magicks, Willpower, Herb Pouch, Nobles, or Staff combat fields to the web dashboard.
- Section-flow baseline found 350 section files, 555 source route links, zero invalid section links, and 350 sections reachable from section 1.
- Section 1 route buttons are sourced from the checked-in graph: 141, 85, and 275.
- Route action smoke accepted legal route 1 -> 141 and refused illegal route 1 -> 2.
- Simple automation smoke covered END loss, required Meals, Hunting meal exemption, END restoration, Gold Crowns, Vordak Gem handling, gear loss, optional section 20 supplies, Book 1 completion, and terminal death.
- Simple automation data now covers 47 confirmed section-effect entries and optional loot buttons for 18 sections.

## Remaining Risk

- Route math, random-branch automation, and some player-choice inventory losses remain manual.
- Healing, Laumspur special behavior, and all section-specific combat exceptions need later audit passes.
