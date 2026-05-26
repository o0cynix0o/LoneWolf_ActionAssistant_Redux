# LW Book 1 Section 21 Staged Roll Audit

Date: 2026-05-26

Scope: issue #10 staged random helper for Book 1 section 21.

## Confirmed Changes

- Added a `stagedRoll` model to the Book 1 section-flow data.
- Section 21 now tracks first, second, and final marsh rolls per section visit.
- First-roll success routes to section 189.
- First-roll failure advances to the second roll.
- Second-roll success routes to section 189.
- Second-roll failure advances to the final roll.
- Final-roll success routes to section 312.
- Final-roll failure marks the terminal death state and preserves normal death recovery controls.
- Repeated Roll clicks after completion return the stored staged result instead of changing the outcome.

## Verification

- `testing\lwbook1_section21_staged_smoke.py` covers:
  - first-roll success
  - second-roll recovery
  - final-roll success
  - final-roll death and rewind availability

## Remaining Risk

- The staged-roll model is currently confirmed only for section 21.
- Broader route playtesting may identify additional staged random sections or player-choice aftermaths that need the same treatment.
