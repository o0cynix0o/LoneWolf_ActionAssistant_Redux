# Lone Wolf Action Assistant Redux

Lone Wolf Action Assistant Redux is the clean AA2 rebuild of the Lone Wolf play assistant. This repository starts from the proven Grey Star Action Assistant workflow and rebuilds the rules, audit data, testing, docs, packaging, issues, and release process around *Flight from the Dark*.

Current status: **pre-alpha scaffold**

The modern web dashboard, card layout, receipt drawer, launcher shape, release tooling, and workflow docs are in place. The remaining Grey Star rule assumptions in the Python and web assistant are intentional scaffolding markers for the next build pass. They must be replaced with Lone Wolf rules before this becomes a playable release.

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

## What This Scaffold Contains

- Grey Star AA card-dashboard web shell adapted for Lone Wolf Redux.
- Local Python web server and launcher skeleton.
- CLI bridge skeleton.
- Old Lone Wolf data references copied into `data/`:
  - combat results table
  - Kai Disciplines
  - Magnakai references
  - Weaponskill map
- Book 1 placeholder audit data files.
- Agent handoff docs for continuing the rebuild in a fresh chat.
- Grey Star-style audit, playtest, docs, release, wiki, issue, and packaging workflow.

## What Still Needs Rebuilt

- Character creation for *Flight from the Dark*.
- Kai Discipline picker and rules.
- Combat Skill / Endurance rolls and equipment rules.
- Weapons, Backpack Items, Special Items, Meals, Gold Crowns.
- Healing and Kai Discipline effects.
- Lone Wolf combat rules and CRT integration.
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

This is a scaffold. The next work should begin with [AGENT.md](AGENT.md).
