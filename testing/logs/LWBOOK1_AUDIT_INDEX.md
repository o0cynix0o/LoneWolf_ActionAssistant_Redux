# LW Book 1 Audit Index

Scope: parity index for Book 1 audit artifacts. This maps the Grey Star-style canonical audit buckets to the current Lone Wolf reports without duplicating source prose or existing findings.

## Canonical Coverage

| Canonical bucket | Lone Wolf artifact | Status |
| --- | --- | --- |
| Rules baseline | `testing/logs/LWBOOK1_PASS1_RULES_BASELINE.md` | Present |
| Rules and items audit | `testing/logs/LWBOOK1_PASS1_RULES_BASELINE.md`, `testing/logs/LWBOOK1_HEALING_LOSS_AUDIT.md`, `testing/logs/LWBOOK1_PLAYER_CHOICE_AUDIT.md`, `testing/logs/LWBOOK1_SIMPLE_AUTOMATION_BASELINE.md` | Split across focused reports |
| Section audit | `testing/logs/LWBOOK1_SECTION_FLOW_BASELINE.md`, `testing/logs/LWBOOK1_AUTOMATION_LANGUAGE_AUDIT.md`, `testing/logs/LWBOOK1_AUTOMATION_LEDGER.md` | Present as flow plus automation audit |
| Route audit | `testing/logs/LWBOOK1_ROUTE_RANDOM_AUDIT.md`, `testing/logs/LWBOOK1_ROUTE_GAUNTLET_PLAYTEST.md` | Present as route/random plus gauntlet |
| Endings and route families | `testing/logs/LWBOOK1_PLAYTEST_REPORT.md`, `testing/logs/LWBOOK1_ROUTE_GAUNTLET_PLAYTEST.md`, `testing/logs/CAMPAIGN_STORY_RUN.md` | Book 1 coverage only |
| Combat and random audit | `testing/logs/LWBOOK1_COMBAT_AND_RANDOM_AUDIT.md`, `testing/logs/LWBOOK1_COMBAT_EDGE_PLAYTEST.md`, `testing/logs/LWBOOK1_RANDOM_RECOVERY_AUDIT.md` | Present |
| Automation ledger | `testing/logs/LWBOOK1_AUTOMATION_LEDGER.md` | Present |
| Achievement candidates | `testing/logs/LWBOOK1_ACHIEVEMENT_CANDIDATES.md`, `testing/logs/LWBOOK1_ACHIEVEMENT_IMPLEMENTATION.md` | Present |
| Playtest report | `testing/logs/LWBOOK1_PLAYTEST_REPORT.md` | Present |

## Validation Entry Point

Use the aggregate Book 1 playtest wrapper:

```powershell
python .\testing\playtest_book1.py
```

The wrapper runs compile checks and the current granular Book 1 validation ladder.

## Notes For Future Books

- Prefer the expected report names in `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md` for Book 2 onward.
- Focused extra logs are fine when they make a ruling easier to track, but each book should have a single index or rollup that maps those focused logs back to the canonical buckets.
- Do not copy long book text into logs. Record section numbers, rule categories, app behavior, and acceptance checks.
