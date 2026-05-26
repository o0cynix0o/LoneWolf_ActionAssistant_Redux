# Book 1 Playtest Report

Date: 2026-05-26

Scope: issue #1 character and sheet rebuild smoke tests.

## Checks

- Python compile: `app_server.py`, `lonewolf_redux.py`, `launch_lonewolf_redux.py`, and `ws_server.py`.
- Deterministic character creation through `create_book1_character_state`.
- Combat smoke for a Book 1 character with Kai Disciplines.
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

## Remaining Risk

- Section movement is still source-link only; Book 1 automation data remains empty.
- Healing, Hunting meal exceptions, and all section-specific combat exceptions need the next audit pass.
