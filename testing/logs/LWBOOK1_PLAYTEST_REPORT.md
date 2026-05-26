# Book 1 Playtest Report

Date: 2026-05-26

Scope: issues #1-#6, covering the Book 1 character/sheet rebuild, section-flow baseline, simple automation, combat presets, route/random helpers, and the first repeatable end-to-end playtest route.

## Checks

- Python compile: `app_server.py`, `lonewolf_redux.py`, `launch_lonewolf_redux.py`, and `ws_server.py`.
- Deterministic character creation through `create_book1_character_state`.
- Combat smoke for a Book 1 character with Kai Disciplines.
- Section-flow baseline check with `testing\lwbook1_section_flow_audit.py --check`.
- Simple automation smoke with `testing\lwbook1_simple_automation_smoke.py`.
- Combat preset smoke with `testing\lwbook1_combat_smoke.py`.
- Route/random helper smoke with `testing\lwbook1_route_random_smoke.py`.
- End-to-end route playtest with `testing\lwbook1_end_to_end_playtest.py`.
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
- Combat smoke covered representative Book 1 enemies, Mindblast immunity, conditional CS modifiers, timed modifiers, forced unarmed combat, evasion, round limits, and section 227 victory routing.
- Route/random smoke covered representative Kai Discipline, item, Gold Crown, END, and one-roll random route helpers.
- End-to-end playtest reached section 350 through this legal route:
  `1 -> 141 -> 56 -> 222 -> 252 -> 70 -> 157 -> 30 -> 261 -> 264 -> 6 -> 200 -> 168 -> 64 -> 16 -> 192 -> 171 -> 303 -> 237 -> 265 -> 142 -> 135 -> 223 -> 75 -> 163 -> 321 -> 273 -> 51 -> 288 -> 129 -> 3 -> 196 -> 332 -> 350`.
- The end-to-end route verified the section 303 Camouflage route check, section 237 random route helper with roll 3, Hunting preserving the Meal at section 168, mid-route save/load at section 168, and Book 1 completion payload activation at section 350.
- Death checkpoint smoke verified an entry-stage terminal section can rewind to the previous ready section checkpoint.

## Remaining Risk

- This is a playable baseline route, not exhaustive route coverage.
- Multi-roll sections and random outcomes with immediate same-section side effects remain manual.
- Some player-choice inventory losses, Healing timing, Laumspur special behavior, and remaining combat exceptions still need later audit passes.
- Packaging/release is still blocked until broader manual playtesting confirms the app feels playable outside the checked baseline path.
