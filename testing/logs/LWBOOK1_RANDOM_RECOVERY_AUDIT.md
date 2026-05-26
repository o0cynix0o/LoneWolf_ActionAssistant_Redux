# LW Book 1 Random And Recovery Audit

Date: 2026-05-26

Scope: issue #8 random side-effect and recovery item behavior pass.

## Confirmed Changes

- Added a roll-outcome action model for same-section random effects.
- Added once-per-visit protection so repeated Roll clicks do not double-apply outcome damage or item loss.
- Added checked roll effects for sections 36, 158, and 188.
- Corrected plain Book 1 Laumspur to restore 3 END.
- Required Meal automation can consume Laumspur when no normal Meal is available, restoring 3 END as it fulfills the Meal requirement.
- Roll receipts and section cards now surface any applied roll-effect messages.

## Verification

- `testing\lwbook1_random_recovery_smoke.py` covers:
  - section 36 ladder fall damage and duplicate-roll protection
  - section 158 second lightning-bolt damage
  - section 188 Backpack loss and alternate END-loss outcome
  - Laumspur as a 3 END consumable
  - Laumspur as a required Meal substitute

## Remaining Risk

- Section 21 remains manual because it is a staged multi-roll section with possible death and recovery branches.
- Player-choice losses, such as choosing which weapon breaks after section 277, remain manual.
- Broad Kai Healing timing still needs a dedicated pass; this issue only corrected item-based recovery behavior.
