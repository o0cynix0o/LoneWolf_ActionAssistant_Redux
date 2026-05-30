# FAQ

## Is This Playable Yet?

Yes. Book 1 is playable locally as the first release candidate.

You can create a Book 1 character, use the Book 1 Action Chart, follow section routes, apply audited section effects, resolve supported combats and rolls, recover from death, save/load, and unlock achievements.

Book 2 is also playable as a helper build. You can prepare a fresh Book 2 character or continue a completed Book 1 run into the Book 2 starting state, then use checked routes, section helpers, combat presets, death recovery, completion, and achievements. It still needs more real-route time before we package it as a public release candidate.

Books 3, 4, and 5 are playable onboarding helper builds. They support campaign handoff, fresh starts, source routes, first section helpers, combat presets, death/failure recovery, completion, and repeat-book replay. They are ready to try, but we still expect playtesting to find polish work.

## Which Book Is Supported First?

Start with **Book 1: Flight from the Dark**:

```text
books\lw\01fftd
```

Book 2 uses:

```text
books\lw\02fotw
```

Books 3 through 5 use:

```text
books\lw\03tcok
books\lw\04tcod
books\lw\05sots
```

## Are The Books In The Repo?

No. The local `books\lw` folder is ignored by git and must not be included in releases.

## How Do I Start The App?

From the project folder:

```powershell
.\Launch-LoneWolfRedux.ps1
```

Then open:

```text
http://127.0.0.1:8797/assistant.html
```

## Can I Open assistant.html Directly?

Use the local server URL instead. Opening the file directly can leave the assistant disconnected from the local API.

## Does The App Replace The Book?

No. It is a companion for your own local Project Aon book files. Read the book text and let the assistant handle the Action Chart bookkeeping.

## What Should The Next Book Pipeline Do First?

For Books 2 through 5, the next work is polish from real routes. For Book 6 and later, start with the rules scan and book handoff scan. Later Lone Wolf books can add rule tweaks, new-power choices, new starting gear choices, safekeeping calls, and carry-over checks.

Use [Book Support Matrix](Book-Support-Matrix) to see what is supported now.
