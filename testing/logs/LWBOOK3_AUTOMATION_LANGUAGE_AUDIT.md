# LW Book 3 Automation Language Audit

Scope: Book 3 section-by-section scan for automation-likely language.

This report records signal labels and section numbers only. It intentionally does not copy Book 3 prose.

## Summary

- Sections scanned: 350
- Sections with at least one automation signal: 202

## Signal Categories

- combat: 37 sections
- combat_skill_modifier: 1 sections
- endurance_gain: 4 sections
- endurance_loss: 48 sections
- gold: 6 sections
- inventory_gain: 30 sections
- inventory_loss: 8 sections
- meal: 42 sections
- random: 33 sections
- route_check: 95 sections
- terminal: 1 sections

## Sections By Category

- combat: 14, 32, 52, 68, 78, 83, 88, 89, 99, 103, 106, 108, 123, 137, 138, 142, 147, 158, 161, 164, 180, 200, 202, 207, 208, 214, 241, 258, 259, 260, 263, 265, 270, 296, 304, 343, 350
- combat_skill_modifier: 137
- endurance_gain: 79, 157, 233, 340
- endurance_loss: 18, 21, 27, 32, 33, 43, 55, 62, 77, 83, 88, 94, 99, 121, 123, 129, 132, 138, 140, 147, 150, 155, 158, 170, 180, 193, 196, 206, 209, 211, 214, 217, 226, 237, 241, 251, 258, 259, 260, 263, 280, 284, 294, 299, 304, 326, 328, 331
- gold: 49, 97, 152, 181, 218, 319
- inventory_gain: 4, 12, 18, 25, 26, 45, 50, 59, 84, 102, 119, 156, 177, 194, 210, 218, 223, 231, 233, 280, 282, 295, 298, 308, 309, 311, 316, 321, 334, 349
- inventory_loss: 16, 18, 41, 79, 157, 188, 196, 303
- meal: 1, 5, 8, 12, 21, 23, 43, 61, 76, 101, 112, 114, 117, 119, 121, 149, 155, 157, 160, 167, 183, 212, 223, 226, 232, 237, 258, 273, 275, 276, 281, 283, 284, 301, 305, 309, 318, 323, 331, 332, 346, 347
- random: 29, 54, 73, 74, 80, 86, 88, 94, 96, 134, 142, 146, 149, 152, 155, 167, 179, 183, 185, 211, 232, 258, 262, 272, 283, 284, 291, 302, 322, 323, 327, 331, 346
- route_check: 15, 26, 29, 32, 33, 36, 40, 44, 45, 49, 50, 54, 57, 67, 69, 70, 75, 76, 82, 83, 85, 86, 90, 92, 97, 99, 104, 105, 107, 114, 122, 124, 125, 128, 129, 132, 137, 139, 146, 149, 150, 151, 160, 169, 170, 171, 173, 182, 183, 185, 187, 190, 192, 194, 206, 210, 227, 229, 236, 242, 244, 247, 250, 255, 258, 262, 268, 272, 273, 274, 275, 276, 277, 283, 284, 289, 290, 299, 301, 302, 303, 304, 318, 323, 326, 328, 329, 330, 331, 332, 342, 344, 346, 348, 349
- terminal: 144

## Review Status

- All Book 3 signals are marked `needs-ledger-review` until rulings are answered and implementation begins.
- The next pass should convert each signal into implemented automation, manual helper, reviewed no automation, or queued ambiguity.

## Data Artifact

- Source route shape is in `data/book3-section-flows.json`.
- This audit is a planning report only; it does not define playable section behavior.
