# LW Book 4 Rulings Queue

Scope: Book 4 onboarding rulings for *The Chasm of Doom*.

This file records mechanical decisions only. It does not copy book prose.

## Answered Rulings

| ID | Topic | Ruling | Implementation note |
| --- | --- | --- | --- |
| B4-R1 | Backpack carry-over | Backpack Items always carry forward. | Campaign continuation preserves carried Backpack Items, then enforces the eight-item Backpack cap when Book 4 gear is chosen. |
| B4-R2 | Badge of Rank | Track as a Special Item and story flag. | Book 4 setup adds `Badge of Rank` and sets `book4BadgeOfRank`. |
| B4-R3 | Book 4 starting gear | Choose exactly six items. | Standalone and campaign setup require six distinct Book 4 equipment picks. |
| B4-R4 | Armour stacking | Padded Leather Waistcoat and Chainmail Waistcoat can stack. | Chainmail adds its END bonus once; duplicate chainmail does not stack. |
| B4-R5 | Shield | Treat as ordinary supported gear for now. | Current combat helper keeps the existing automatic Shield bonus behavior; a manual/toggle version can be added if playtesting wants it. |
| B4-R6 | Torches and Tinderbox | Lit torch is not recorded; extra Torch/Tinderbox can be taken. | Torch/Tinderbox sections expose ordinary item helper buttons where relevant. |
| B4-R7 | Random item loss | Let the player pick the item. | Section 22 uses a loss-choice helper, preferring Backpack Items and falling back to Weapons. |
| B4-R8 | Backpack lost in water | Lose the Backpack and contents until replaced. | Waterfall/river sections mark Backpack unavailable and clear contents; section 167 can restore a replacement Backpack with food. |
| B4-R9 | Mission-failure endings | Treat as death-style terminal failure when Lone Wolf lives. | The first Book 4 terminal sections found in the source are implemented as terminal death endings; special alive-failure wording should be added if playtesting reaches one. |

## Follow-Up Watch List

- Add a Shield toggle if real play makes automatic Shield use feel too aggressive.
- Promote useful Book 4 route discoveries into achievements after the first human playtest pass.
- Update public strategy pages after route testing gives enough practical advice to be helpful.
