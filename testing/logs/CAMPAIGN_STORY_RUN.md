# Campaign Story Run

Scope: campaign-level parity placeholder for Lone Wolf Action Assistant Redux.

Current supported campaign span: **Books 1-5, with Book 1 as the release candidate and Books 2-5 as helper builds**.

Grey Star has a full multi-book campaign run because Books 1-4 are mature there. Lone Wolf Redux now has Book 1 release-candidate support plus Books 2-5 helper builds, but should not claim full campaign parity until those helper builds have had enough real-route playtesting.

## Current Route Coverage

Book 1 route and completion coverage currently lives in:

- `testing/lwbook1_end_to_end_playtest.py`
- `testing/lwbook1_branch_playtest.py`
- `testing/lwbook1_route_gauntlet_playtest.py`
- `testing/logs/LWBOOK1_PLAYTEST_REPORT.md`
- `testing/logs/LWBOOK1_ROUTE_GAUNTLET_PLAYTEST.md`

Book 2 through Book 5 helper coverage currently lives in:

- `testing/playtest_book2.py`
- `testing/playtest_book3.py`
- `testing/playtest_book4.py`
- `testing/playtest_book5.py`

## Future Expansion

As Books 2-5 mature, this log should record:

- multi-book route playthroughs
- new Discipline/power selection
- start gear and carry-over handling
- campaign save compatibility
- book transition receipts
- successful story routes across supported books

Do not package campaign claims until the corresponding books are actually playable.
