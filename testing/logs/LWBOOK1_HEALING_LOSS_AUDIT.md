# LW Book 1 Healing And Loss Choice Audit

Date: 2026-05-26

Scope: issue #9 Kai Healing and explicit player-choice loss helper pass.

## Confirmed Changes

- Added a Kai Healing helper for Book 1 characters with the Healing Discipline.
- Healing restores 1 END, caps at maximum END, and is protected from duplicate application per section visit.
- Healing is blocked in sections with audited combat presets so the player does not accidentally heal during a combat section.
- Added explicit loss-choice helpers for section 144 and section 277.
- Section 144 prefers a chosen Backpack Item; if no Backpack Item is available, it falls back to a chosen Weapon.
- Section 277 removes the chosen broken Weapon.
- Loss-choice helpers are explicit buttons; the assistant does not choose the lost item for the player.

## Verification

- `testing\lwbook1_healing_loss_smoke.py` covers:
  - Healing readiness in a non-combat section after END loss
  - duplicate Healing protection
  - no-Healing and combat-section blocks
  - section 144 Backpack Item loss
  - section 144 fallback Weapon loss
  - section 277 selected Weapon loss

## Remaining Risk

- Section 21 staged random handling is now covered by the dedicated section 21 smoke test.
- Additional player-choice aftermaths may surface during broader route playtesting.
- The Healing helper is explicit rather than automatic; fully automatic timing remains intentionally avoided.
