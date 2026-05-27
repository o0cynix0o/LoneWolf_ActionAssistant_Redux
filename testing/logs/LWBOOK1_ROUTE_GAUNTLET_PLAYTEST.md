# LW Book 1 Route Gauntlet Playtest

Date: 2026-05-27

Scope: issue #14 broader Book 1 self-play coverage beyond the main success route and branch smoke tests.

This log records section numbers and mechanical outcomes only. Do not copy Book 1 prose into committed audit artifacts.

## Summary

- Added a repeatable route gauntlet that follows legal route links through risky Book 1 paths.
- The gauntlet focuses on resource pressure, paid routes, combat-adjacent choices, item-gated outcomes, death/failure recovery states, Backpack loss, and side-route loot.
- No app-code fix was required by this pass.

## Covered Paths

- Section 255 Gourgaz branch through section 46 paid ferry route, section 246 Drakkar combat, and section 197 loot.
- Section 12 caravan fare route through section 191 Bodyguard evasion to section 234 death.
- Section 242 and section 9 Vordak Gem checks, covering both section 292 failure and section 236 backlash.
- Section 162 capture route with and without Mind Over Matter, covering section 258 escape and section 127 death.
- Section 203 END threshold routing to sections 80 and 344.
- Section 174 Backpack/Weapon loss reached through legal route links.
- Section 349 Crystal Star Pendant side-route loot.

## Result

- `python testing\lwbook1_route_gauntlet_playtest.py` passed.
- The section 197 Short Sword is blocked when the player already carries two Weapons, while the Gold Crown gain still applies. The gauntlet records that as expected inventory pressure rather than a bug.

## Remaining Risk

- The gauntlet broadens coverage, but it is still not every possible route through Book 1.
- Browser ergonomics should still get a manual player-facing pass before packaging.
- Packaging/release remains blocked until the app feels playable through ordinary use, not just scripted route checks.
