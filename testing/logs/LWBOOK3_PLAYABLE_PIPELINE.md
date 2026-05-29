# LW Book 3 Playable Pipeline

Date: 2026-05-28

GitHub issue: #42

Scope: first playable helper slice for Book 3, *The Caverns of Kalte*.

This is an onboarding helper build, not a release candidate. It is meant to let the player begin Book 3, continue from Book 2, and use the first confirmed helpers while the rest of the section automation is filled in through playtesting.

## Implemented

- Book 3 metadata is wired into the app, landing page, reader toolbar, and library.
- Standalone Book 3 character creation is available.
- Book 2 completion can continue into Book 3.
- Book 3 setup adds one new Kai Discipline, rolls starting Gold, enforces the 50-Crown cap, adds Map of Kalte, sets winter-gear story flags, and offers two equipment choices.
- Backpack Items carry forward into Book 3 by ruling.
- Padded Leather Waistcoat can stack with prior armour bonuses by ruling.
- Repeat Book 3 restores the Book 3 start checkpoint while preserving durable history.
- Section 61 is a recoverable mission failure: Lone Wolf is alive, but the run cannot continue forward.
- Section 132 consumes a Backpack Meal or applies the END loss.
- Section 144 records terminal death.
- Section 350 completes Book 3.
- Baknar Oil is a usable Backpack item that sets a Book 3 flag.
- Red Laumspur is distinct from normal Laumspur for section checks.
- Bone Sword is a special weapon with the Kalte bonus.
- Blue Stone Triangle is tracked as a durable Special Item.

## First Helper Coverage

- `data/book3-section-flows.json` contains source routes for all 350 sections.
- The Project Aon SVGZ route graph matches the local source graph exactly: 350 nodes and 603 edges.
- First loot/helper sections are recorded for Bone Sword, Blue Stone Disc, Baknar Oil, Blue Stone Triangle, Silver Helm, and Ornate Silver Key use.
- First combat presets cover the main scanned Book 3 fight stat blocks, including Helghast Mindblast immunity, Sommerswerd doubled damage against undead, partial Mindblast resistance, multi-enemy queues, evasion where recorded, and timed Akraa'Neonor fights.

## Tests

- `testing\lwbook3_setup_smoke.py`
- `testing\lwbook3_playable_pipeline_smoke.py`
- Existing Book 2 setup and playable pipeline smoke tests still pass.

## Remaining Work

- Full section-by-section automation ledger conversion.
- More route checks for all Discipline/item/history branches.
- Random helpers and staged random outcomes.
- More loot/shop/loss-choice helpers.
- Achievement candidate review and implementation.
- Book 3 strategy guide.
- Automated route gauntlet and human playtesting.
