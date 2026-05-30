# LW Book 5 Automation Language Audit

Scope: Book 5 section-by-section scan for automation-likely language.

This report records signal labels and section numbers only. It intentionally does not copy Book 5 prose.

## Summary

- Sections scanned: 400
- Sections with at least one automation signal: 225

## Signal Categories

- book_transition: 6 sections
- combat: 57 sections
- combat_skill_modifier: 19 sections
- endurance_gain: 12 sections
- endurance_loss: 46 sections
- gold: 25 sections
- gold_cost: 4 sections
- inventory_gain: 35 sections
- inventory_loss: 7 sections
- meal: 29 sections
- random: 34 sections
- route_check: 112 sections
- terminal: 8 sections

## Sections By Category

- book_transition: 200, 320, 331, 339, 352, 400
- combat: 4, 12, 20, 46, 57, 64, 72, 91, 106, 110, 111, 119, 123, 135, 149, 154, 159, 161, 162, 168, 178, 180, 190, 194, 200, 204, 223, 226, 228, 231, 238, 240, 244, 247, 253, 268, 273, 280, 299, 316, 323, 324, 329, 330, 334, 341, 352, 353, 355, 357, 361, 370, 375, 378, 387, 389, 393
- combat_skill_modifier: 12, 57, 64, 91, 106, 110, 135, 159, 166, 190, 194, 253, 280, 299, 316, 353, 355, 357, 393
- endurance_gain: 2, 63, 93, 130, 131, 135, 154, 161, 211, 237, 302, 359
- endurance_loss: 8, 22, 23, 34, 38, 40, 50, 51, 63, 72, 86, 108, 119, 127, 137, 159, 162, 164, 183, 192, 238, 240, 244, 251, 254, 264, 273, 278, 280, 284, 285, 287, 297, 320, 350, 354, 368, 369, 370, 371, 372, 379, 380, 385, 392, 393
- gold: 3, 10, 14, 27, 35, 40, 52, 69, 101, 102, 111, 154, 169, 176, 207, 211, 248, 256, 265, 276, 307, 318, 362, 388, 395
- gold_cost: 211, 248, 265, 276
- inventory_gain: 2, 3, 35, 40, 52, 56, 67, 71, 100, 101, 102, 111, 122, 130, 131, 169, 207, 212, 221, 224, 253, 255, 264, 270, 281, 288, 289, 290, 300, 310, 319, 333, 341, 380, 382
- inventory_loss: 19, 40, 69, 270, 276, 350, 380
- meal: 11, 23, 49, 56, 79, 118, 125, 126, 128, 131, 137, 146, 149, 152, 169, 172, 180, 196, 198, 218, 239, 282, 301, 302, 312, 320, 331, 360, 381
- random: 11, 15, 23, 48, 49, 56, 118, 125, 127, 146, 152, 162, 180, 198, 205, 222, 224, 229, 239, 242, 247, 275, 282, 301, 305, 312, 323, 325, 336, 357, 360, 372, 381, 392
- route_check: 1, 11, 13, 15, 17, 22, 23, 24, 26, 30, 31, 48, 49, 51, 56, 57, 64, 79, 87, 90, 95, 110, 111, 112, 113, 118, 122, 125, 126, 128, 130, 134, 136, 137, 142, 146, 152, 153, 156, 162, 163, 167, 180, 187, 188, 194, 195, 198, 199, 200, 208, 210, 212, 215, 219, 221, 224, 229, 234, 235, 239, 240, 241, 242, 246, 248, 250, 253, 256, 264, 268, 273, 276, 278, 282, 285, 286, 287, 288, 289, 299, 300, 301, 312, 313, 314, 325, 329, 333, 335, 337, 344, 350, 353, 354, 355, 360, 363, 370, 371, 372, 380, 381, 382, 386, 391, 392, 393, 395, 396, 397, 400
- terminal: 5, 230, 257, 259, 261, 293, 304, 366

## Review Status

- The first Book 5 implementation slice has converted the confirmed setup rules, safekeeping, route checks, random helpers, loss-choice helpers, simple effects, loot buttons, and combat presets into app data.
- Remaining signals should be reviewed during real-route play and converted into implemented automation, manual helper, reviewed no automation, or queued ambiguity.

## Data Artifact

- Source route shape is in `data/book5-section-flows.json`.
- This audit is a planning report only; it does not define playable section behavior.
