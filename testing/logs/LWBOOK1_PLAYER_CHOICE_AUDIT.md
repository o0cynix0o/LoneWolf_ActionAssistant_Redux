# LW Book 1 Player Choice Audit

Date: 2026-05-26

Scope: issue #11 player-choice aftermath helper pass.

## Confirmed Changes

- Extended explicit loss-choice helpers so a selected carried item can be exchanged for a replacement item.
- Section 307 now exposes the Warhammer as a Weapon exchange instead of ordinary loot.
- The player chooses which carried Weapon to trade away.
- The section 307 Meal remains an ordinary loot helper.
- Exchange helpers use the same once-per-visit protection as loss helpers.

## Verification

- `testing\lwbook1_player_choice_aftermath_smoke.py` covers:
  - section 307 exchange helper payload
  - selected Weapon removal
  - Warhammer replacement
  - duplicate exchange protection
  - no-Weapon block

## Remaining Risk

- The exchange model is currently confirmed only for section 307.
- Additional player-choice aftermaths may surface during broader route playtesting.
