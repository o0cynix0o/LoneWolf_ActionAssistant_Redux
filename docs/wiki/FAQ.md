# FAQ

## Is This Playable Yet?

Yes. Book 1 is playable locally as the first release candidate.

You can create a Book 1 character, use the Book 1 Action Chart, follow section routes, apply audited section effects, resolve supported combats and rolls, recover from death, save/load, and unlock achievements.

The next books are not supported yet; we will onboard them one at a time so rule changes, new powers, and new gear choices are not rushed.

## Which Book Is Supported First?

Start with **Book 1: Flight from the Dark**:

```text
books\lw\01fftd
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

For Book 2 and later, start with the rules scan and book handoff scan. Later Lone Wolf books can add rule tweaks, new-power choices, new starting gear choices, and carry-over checks.

Use [Book Support Matrix](Book-Support-Matrix) to see what is supported now.
