# LW Book 4 Automation Language Audit

Scope: Book 4 section-by-section scan for automation-likely language.

This report records signal labels and section numbers only. It intentionally does not copy Book 4 prose.

## Summary

- Sections scanned: 350
- Sections with at least one automation signal: 209

## Signal Categories

- book_transition: 1 sections
- combat: 77 sections
- combat_skill_modifier: 3 sections
- endurance_gain: 7 sections
- endurance_loss: 37 sections
- gold: 11 sections
- inventory_gain: 23 sections
- inventory_loss: 5 sections
- meal: 41 sections
- random: 34 sections
- route_check: 66 sections
- terminal: 14 sections

## Sections By Category

- book_transition: 350
- combat: 2, 3, 5, 7, 12, 14, 20, 26, 36, 38, 43, 46, 47, 53, 56, 59, 62, 65, 66, 71, 72, 77, 86, 88, 89, 90, 93, 108, 111, 114, 121, 122, 123, 124, 125, 133, 137, 138, 143, 147, 153, 169, 174, 175, 176, 184, 186, 193, 194, 196, 198, 202, 203, 208, 211, 233, 234, 243, 255, 260, 267, 277, 284, 285, 287, 289, 295, 299, 302, 307, 308, 310, 312, 316, 323, 325, 333
- combat_skill_modifier: 62, 153, 316
- endurance_gain: 12, 74, 137, 157, 268, 302, 322
- endurance_loss: 3, 19, 52, 67, 75, 77, 78, 103, 112, 122, 126, 129, 133, 139, 141, 158, 165, 176, 185, 188, 194, 204, 234, 236, 247, 263, 269, 275, 283, 284, 303, 324, 333, 339, 340, 341, 343
- gold: 2, 44, 102, 109, 152, 230, 231, 261, 268, 272, 280
- inventory_gain: 2, 10, 44, 67, 70, 78, 79, 84, 118, 123, 152, 168, 213, 222, 230, 246, 258, 268, 274, 296, 302, 322, 350
- inventory_loss: 29, 165, 218, 327, 336
- meal: 1, 2, 12, 19, 25, 33, 35, 43, 44, 67, 78, 80, 92, 102, 116, 120, 126, 128, 129, 139, 141, 152, 165, 167, 171, 182, 185, 188, 200, 204, 230, 231, 247, 261, 268, 269, 271, 280, 319, 324, 339
- random: 11, 13, 31, 35, 43, 50, 59, 63, 67, 75, 96, 112, 117, 126, 128, 154, 173, 183, 189, 194, 207, 211, 225, 234, 240, 247, 249, 271, 304, 309, 312, 319, 343, 345
- route_check: 15, 21, 23, 24, 25, 29, 35, 40, 43, 44, 51, 54, 57, 67, 70, 73, 75, 77, 87, 92, 102, 113, 117, 118, 120, 122, 128, 129, 136, 168, 171, 173, 182, 183, 185, 193, 194, 200, 207, 209, 212, 224, 234, 244, 249, 253, 254, 258, 260, 269, 270, 271, 272, 274, 279, 289, 291, 293, 296, 301, 309, 315, 318, 331, 335, 344
- terminal: 17, 42, 85, 99, 144, 177, 181, 192, 242, 262, 267, 329, 334, 347

## Review Status

- The first Book 4 implementation slice has converted the confirmed setup rules, route checks, random helpers, loss-choice helpers, simple effects, loot buttons, and combat presets into app data.
- Remaining signals should be reviewed during real-route play and converted into implemented automation, manual helper, reviewed no automation, or queued ambiguity.

## Data Artifact

- Source route shape is in `data/book4-section-flows.json`.
- This audit is a planning report only; it does not define playable section behavior.
