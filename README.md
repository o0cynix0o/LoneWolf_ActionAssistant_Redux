# Lone Wolf Action Assistant Redux

Lone Wolf Action Assistant Redux is the clean AA2 rebuild of the Lone Wolf play assistant. This repository starts from the proven Grey Star Action Assistant workflow and rebuilds the rules, audit data, testing, docs, packaging, issues, and release process around *Flight from the Dark*.

Current status: **Book 1 playable local pre-alpha**

The modern web dashboard, card layout, receipt drawer, launcher, release tooling, and workflow docs are in place. Book 1 now supports valid *Flight from the Dark* character creation, Lone Wolf Action Chart fields, source-link routes, section automation, route checks, random helpers, combat presets, loot/loss helpers, death recovery, achievements, playtest coverage, and wiki pages.

This is still not a public packaged release. The next non-book milestone is the manual browser ergonomics and release-readiness pass.

## Book Files Are Not Included

This project does **not** redistribute Project Aon book HTML files. Users must download the books from Project Aon for personal use and place them locally under:

```text
books\lw
```

The first audit target is already expected at:

```text
books\lw\01fftd
```

Project Aon links:

- License: https://www.projectaon.org/en/Main/License
- Flight from the Dark: https://www.projectaon.org/en/Main/FlightFromTheDark
- Standard HTML ZIP: https://www.projectaon.org/en/xhtml/lw/01fftd/01fftd.zip

## What This Rebuild Contains

- Card-dashboard web shell adapted for Lone Wolf Redux.
- Local Python web server and launcher skeleton.
- CLI bridge skeleton.
- Old Lone Wolf data references copied into `data/`:
  - combat results table
  - Kai Disciplines
  - Magnakai references
  - Weaponskill map
- Book 1 character creation from *Flight from the Dark* rules:
  - Combat Skill = random digit + 10
  - Endurance = random digit + 20
  - exactly five Kai Disciplines
  - Weaponskill random weapon mapping
  - Axe, Backpack with one Meal, Map of Sommerlund, Gold Crown roll, and monastery-find roll
- Book 1 section-flow baseline generated from the local `sect*.htm` files:
  - 350 sections found
  - 555 source route links
  - zero invalid section links
  - section 1 legal routes exposed from checked-in data
- Book 1 automation baseline:
  - checked section-effect entries
  - required Meal handling with Hunting exemption
  - direct END/Gold/gear/completion/death effects
  - optional loot buttons and loss-choice helpers
- Book 1 combat presets, random helpers, route checks, death recovery, and achievements.
- Local docs mirror and GitHub wiki scaffold for player-facing pages.
- Agent handoff docs for continuing the rebuild in a fresh chat.
- Grey Star-style audit, playtest, docs, release, wiki, issue, and packaging workflow.

## What Still Needs Rebuilt

- Manual browser ergonomics and release-readiness review.
- Any Book 1 polish found during ordinary play.
- Public release package after the release-readiness pass.
- Book 2 and later support through the Lone Wolf book pipeline.

## Start Locally

```powershell
.\Launch-LoneWolfRedux.ps1
```

Then open:

```text
http://localhost:8797/assistant.html
```

The next work should begin with [AGENT.md](AGENT.md) and the Book 1 audit logs under `testing\logs`.
