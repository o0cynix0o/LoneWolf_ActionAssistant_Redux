# Lone Wolf Action Assistant Redux

Lone Wolf Action Assistant Redux is the clean AA2 rebuild of the Lone Wolf play assistant. This repository starts from the proven Grey Star Action Assistant workflow and rebuilds the rules, audit data, testing, docs, packaging, issues, and release process around *Flight from the Dark*.

Current status: **pre-alpha Book 1 character rebuild**

The modern web dashboard, card layout, receipt drawer, launcher shape, release tooling, and workflow docs are in place. The first Book 1 pass now creates a legal *Flight from the Dark* character and shows the Lone Wolf action-chart fields for Kai Disciplines, Weapons, Backpack, Special Items, Meals, and Gold Crowns. Section audit data is still placeholder-level, so this is not a public playable release yet.

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
- Book 1 placeholder audit data files.
- Agent handoff docs for continuing the rebuild in a fresh chat.
- Grey Star-style audit, playtest, docs, release, wiki, issue, and packaging workflow.

## What Still Needs Rebuilt

- Healing and Kai Discipline effects.
- Full Lone Wolf combat audit for all Book 1 special cases.
- Book 1 section audit and automation data.
- Achievements, route audits, playtests, and strategy guide.
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
