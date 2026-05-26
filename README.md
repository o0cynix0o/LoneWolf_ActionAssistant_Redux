# Lone Wolf Action Assistant Redux

Lone Wolf Action Assistant Redux is the clean AA2 rebuild of the Lone Wolf play assistant. This repository starts from the proven Grey Star Action Assistant workflow and rebuilds the rules, audit data, testing, docs, packaging, issues, and release process around *Flight from the Dark*.

Current status: **pre-alpha Book 1 simple automation baseline**

The modern web dashboard, card layout, receipt drawer, launcher shape, release tooling, and workflow docs are in place. The first Book 1 pass creates a legal *Flight from the Dark* character and shows the Lone Wolf action-chart fields for Kai Disciplines, Weapons, Backpack, Special Items, Meals, and Gold Crowns. Later passes add a generated Book 1 source-link graph and the first conservative section-effect automations. Combat exceptions and route math are still incomplete, so this is not a public playable release yet.

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

- Grey Star AA card-dashboard web shell adapted for Lone Wolf Redux.
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
- Book 1 simple automation baseline:
  - 47 confirmed section-effect entries
  - required Meal handling with Hunting exemption
  - direct END/Gold/gear/completion/death effects
  - optional loot buttons for 18 sections
- Agent handoff docs for continuing the rebuild in a fresh chat.
- Grey Star-style audit, playtest, docs, release, wiki, issue, and packaging workflow.

## What Still Needs Rebuilt

- Healing and Kai Discipline effects.
- Full Lone Wolf combat audit for all Book 1 special cases.
- Deeper Book 1 route checks and random/stat branch automation.
- Achievements, combat playtests, and strategy guide.
- Public release notes and package once Book 1 support is real.

## Start Locally

```powershell
.\Launch-LoneWolfRedux.ps1
```

Then open:

```text
http://localhost:8797/assistant.html
```

The next work should begin with [AGENT.md](AGENT.md) and the Book 1 audit logs under `testing\logs`.
