# LW Book 4 Playable Pipeline

Scope: first playable helper slice for Book 4, *The Chasm of Doom*.

This is an onboarding helper build, not a release candidate. It is meant to let the player start Book 4, continue from Book 3, and shake out rough edges through real play.

## Implemented

- Book 4 metadata is wired into the app, landing page, reader toolbar, install page, and library.
- Standalone Book 4 character creation is available.
- Book 3 completion can continue into Book 4.
- Book 4 setup adds one new Kai Discipline, rolls starting Gold, enforces the 50-Crown cap, adds Map of the Southlands and Badge of Rank, and offers six equipment choices.
- Backpack Items carry forward by standing user ruling.
- Padded Leather Waistcoat and Chainmail Waistcoat can stack; duplicate chainmail does not stack.
- `data\book4-section-flows.json` records the checked source-link route graph and first helper data.
- `data\book4-simple-automations.json` records confirmed simple effects, Meal handling, Backpack loss/replacement, terminal deaths, and completion.
- Regional Meal handling supports normal Hunting, Wildlands Hunting suppression, and Maaken Mines Hunting suppression.
- Section 22 uses a choice-based item-loss helper instead of deleting arbitrary gear.
- Underwater combat supports the random oxygen-round roll and Mind Over Matter bonus.
- Section 333 supports the one-round comparison routing.
- Section 350 completes Book 4 and records the Dagger of Vashna.

## Validation

- `python testing\lwbook4_section_flow_audit.py --check`
- `python testing\lwbook4_automation_language_audit.py --check`
- `python testing\lwbook4_setup_smoke.py`
- `python testing\lwbook4_playable_pipeline_smoke.py`
- `python testing\playtest_book4.py`
- Book 2 and Book 3 setup/playable smokes were rerun as regression checks.
- Landing/settings static browser smokes were rerun.

## Remaining Work

- Human route playtesting.
- Book 4 achievement planning and implementation.
- Strategy-guide updates once playtesting produces useful route advice.
- Any UI label polish for helper buttons that feel too clinical during play.
- Optional Shield-use toggle if automatic Shield handling proves too broad.
