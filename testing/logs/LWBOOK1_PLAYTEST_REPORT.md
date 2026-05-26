# Book 1 Playtest Report

Date: 2026-05-26

Scope: issues #1-#12, covering the Book 1 character/sheet rebuild, section-flow baseline, simple automation, combat presets, route/random helpers, the first repeatable end-to-end playtest route, early branch playtests, random/recovery side effects, Healing, explicit loss-choice helpers, the section 21 staged roll helper, the section 307 weapon exchange helper, and the first section-by-section automation-language slice.

## Checks

- Python compile: `app_server.py`, `lonewolf_redux.py`, `launch_lonewolf_redux.py`, and `ws_server.py`.
- Deterministic character creation through `create_book1_character_state`.
- Combat smoke for a Book 1 character with Kai Disciplines.
- Section-flow baseline check with `testing\lwbook1_section_flow_audit.py --check`.
- Simple automation smoke with `testing\lwbook1_simple_automation_smoke.py`.
- Combat preset smoke with `testing\lwbook1_combat_smoke.py`.
- Route/random helper smoke with `testing\lwbook1_route_random_smoke.py`.
- Random/recovery smoke with `testing\lwbook1_random_recovery_smoke.py`.
- Healing/loss smoke with `testing\lwbook1_healing_loss_smoke.py`.
- Section 21 staged roll smoke with `testing\lwbook1_section21_staged_smoke.py`.
- Player-choice aftermath smoke with `testing\lwbook1_player_choice_aftermath_smoke.py`.
- Automation-language smoke with `testing\lwbook1_automation_language_smoke.py`.
- End-to-end route playtest with `testing\lwbook1_end_to_end_playtest.py`.
- Branch playtest with `testing\lwbook1_branch_playtest.py`.
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
- Simple automation data now covers 48 confirmed section-effect entries and optional loot buttons for 21 sections.
- Combat smoke covered representative Book 1 enemies, Mindblast immunity, conditional CS modifiers, timed modifiers, forced unarmed combat, evasion, round limits, and section 227 victory routing.
- Route/random smoke covered representative Kai Discipline, item, Gold Crown, END, and one-roll random route helpers.
- End-to-end playtest reached section 350 through this legal route:
  `1 -> 141 -> 56 -> 222 -> 252 -> 70 -> 157 -> 30 -> 261 -> 264 -> 6 -> 200 -> 168 -> 64 -> 16 -> 192 -> 171 -> 303 -> 237 -> 265 -> 142 -> 135 -> 223 -> 75 -> 163 -> 321 -> 273 -> 51 -> 288 -> 129 -> 3 -> 196 -> 332 -> 350`.
- The end-to-end route verified the section 303 Camouflage route check, section 237 random route helper with roll 3, Hunting preserving the Meal at section 168, mid-route save/load at section 168, and Book 1 completion payload activation at section 350.
- Death checkpoint smoke verified an entry-stage terminal section can rewind to the previous ready section checkpoint.
- Branch playtest covered early combat through `1 -> 85 -> 229`, verified illegal route blocking from section 85, loaded the section 229 Kraan combat preset, resolved a victory that correctly waits for player choice, and followed the legal victory branch to section 267.
- Branch playtest covered death/recovery through `1 -> 275 -> 74 -> 281 -> 311 -> 47 -> 322 -> 17 -> 53`, verified the section 17 roll helper with roll 0, triggered terminal death at section 53, and rewound to section 17.
- Branch playtest covered inventory/stat consequences through legal routes to section 130 Meal consumption without Hunting, section 33 Gold Crowns, and section 274 weapon loss from the section 17 roll helper.
- Random/recovery smoke covered same-section roll effects for sections 36, 158, and 188, including duplicate-roll protection.
- Laumspur now restores 3 END and can fulfill a required Meal when no normal Meal is available.
- Healing/loss smoke covered Kai Healing readiness, duplicate protection, no-Healing/combat blocks, section 144 selected loss, section 144 fallback loss, and section 277 selected Weapon loss.
- Section 21 staged roll smoke covered first-roll success, second-roll recovery, final-roll success, and final-roll death with rewind.
- Player-choice aftermath smoke covered section 307's explicit Weapon-for-Warhammer exchange and duplicate protection.
- Automation-language smoke covered the clear issue #12 slice: section 15 Sword, section 346 Spear, section 349 Crystal Star Pendant, section 258 gear loss, and section 46 Sixth Sense warning.
- Section-flow data now includes 21 optional loot helpers, 3 explicit loss/exchange-choice helpers, and 1 staged roll helper.

## Remaining Risk

- The checked routes are playable baselines, not exhaustive route coverage.
- Additional player-choice aftermaths may still surface during broader route playtesting.
- Issue #12 still has ambiguous automation-language candidates awaiting ruling before implementation.
- Remaining combat exceptions still need later audit passes.
- Packaging/release is still blocked until broader manual playtesting confirms the app feels playable outside the checked baseline path.
