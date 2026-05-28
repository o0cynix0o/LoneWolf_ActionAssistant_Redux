# LW Book 2 Achievement Pass

Date: 2026-05-27

Scope: Book 2 achievement definitions, triggers, and backfill.

## Implemented Achievements

|Achievement|Trigger summary|
|-----------|---------------|
|Fire on the Water|Complete Book 2.|
|The Hammerdal Road|Reach the Hammerdal story stretch.|
|The Sun-Sword Returns|Claim the Sommerswerd.|
|Borrowed Thunder|Take the Magic Spear.|
|Helghast Breaker|Win a recorded Book 2 Helghast combat.|
|Table Manners|Win the tavern arm-wrestling purse.|
|Shipwrecked But Moving|Survive a Green Sceptre disaster route.|
|Red Pass, Green Light|Secure harbour access in Port Bax.|
|Paper Trail|Record the forged access-papers death.|
|Across The Lastlands|Visit 90 or more unique Book 2 sections.|

## Validation

- `python .\testing\lwbook1_achievement_smoke.py`

The existing achievement smoke now verifies both Book 1 and Book 2 definitions and representative Book 2 unlock/backfill triggers.
