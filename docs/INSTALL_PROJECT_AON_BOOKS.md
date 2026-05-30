# Install The Project Aon Book Files

Lone Wolf Action Assistant Redux does not include Project Aon book HTML files in the repository or release ZIP.

Project Aon provides the Internet Editions from its own site. Their license lets you download the books for personal use, but it does not let this project redistribute the book files. Download the books directly from Project Aon, then place them in the local folder layout below.

Read the license here:

- https://www.projectaon.org/en/Main/License

## Use The Standard HTML Editions

Download the **standard** edition for each supported Lone Wolf book. This is the full-featured, multi-page HTML edition that matches the assistant's reader paths.

Current supported books:

| Book | Status | Project Aon page | Standard ZIP |
| --- | --- | --- | --- |
| 1. Flight from the Dark | Playable release candidate | https://www.projectaon.org/en/Main/FlightFromTheDark | https://www.projectaon.org/en/xhtml/lw/01fftd/01fftd.zip |
| 2. Fire on the Water | Playable helper build | https://www.projectaon.org/en/Main/FireOnTheWater | https://www.projectaon.org/en/xhtml/lw/02fotw/02fotw.zip |
| 3. The Caverns of Kalte | Onboarding helper build | https://www.projectaon.org/en/Main/TheCavernsOfKalte | https://www.projectaon.org/en/xhtml/lw/03tcok/03tcok.zip |
| 4. The Chasm of Doom | Onboarding helper build | https://www.projectaon.org/en/Main/TheChasmOfDoom | https://www.projectaon.org/en/xhtml/lw/04tcod/04tcod.zip |
| 5. Shadow on the Sand | Onboarding helper build | https://www.projectaon.org/en/Main/ShadowOnTheSand | https://www.projectaon.org/en/xhtml/lw/05sots/05sots.zip |

Future books must be installed locally before they can be audited through `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md`.

Common Project Aon Lone Wolf folder codes:

| Book | Folder code | Status in this app |
| --- | --- | --- |
| 1. Flight from the Dark | `01fftd` | Supported |
| 2. Fire on the Water | `02fotw` | Supported; needs more real-route time |
| 3. The Caverns of Kalte | `03tcok` | Onboarding helper build |
| 4. The Chasm of Doom | `04tcod` | Onboarding helper build |
| 5. Shadow on the Sand | `05sots` | Onboarding helper build |

Project Aon also has an all-books download page:

- https://www.projectaon.org/en/Main/AllOfTheBooks

For this assistant, individual standard ZIPs are the simplest path because each book is audited, implemented, and tested one at a time.

## Expected Folder Layout

After extraction, your project should look like this:

```text
LoneWolf_ActionAssistant_Redux/
  books/
    README.md
    lw/
      01fftd/
        title.htm
        sect1.htm
        ...
      02fotw/
        title.htm
        sect1.htm
        ...
      03tcok/
        title.htm
        sect1.htm
        ...
      04tcod/
        title.htm
        sect1.htm
        ...
      05sots/
        title.htm
        sect1.htm
        ...
```

The app currently expects these folder names:

- `01fftd`
- `02fotw`
- `03tcok`
- `04tcod`
- `05sots`

## Manual Install

1. Download the standard ZIPs for the books you want to play from Project Aon.
2. Open your Lone Wolf Action Assistant Redux folder.
3. Create this folder if it does not exist:

   ```text
   books\lw
   ```

4. Extract the ZIP into `books\lw`.
5. Confirm these files exist:

   ```text
   books\lw\01fftd\title.htm
   books\lw\01fftd\sect1.htm
   books\lw\02fotw\title.htm
   books\lw\02fotw\sect1.htm
   books\lw\03tcok\title.htm
   books\lw\03tcok\sect1.htm
   books\lw\04tcod\title.htm
   books\lw\04tcod\sect1.htm
   books\lw\05sots\title.htm
   books\lw\05sots\sect1.htm
   ```

If you see an extra nested folder after extraction, move the book folder so the path matches the examples above.

## PowerShell Example

From the project folder:

```powershell
New-Item -ItemType Directory -Force .\books\lw

Expand-Archive "$env:USERPROFILE\Downloads\01fftd.zip" -DestinationPath .\books\lw -Force
Expand-Archive "$env:USERPROFILE\Downloads\02fotw.zip" -DestinationPath .\books\lw -Force
Expand-Archive "$env:USERPROFILE\Downloads\03tcok.zip" -DestinationPath .\books\lw -Force
Expand-Archive "$env:USERPROFILE\Downloads\04tcod.zip" -DestinationPath .\books\lw -Force
Expand-Archive "$env:USERPROFILE\Downloads\05sots.zip" -DestinationPath .\books\lw -Force

Test-Path .\books\lw\01fftd\title.htm
Test-Path .\books\lw\01fftd\sect1.htm
Test-Path .\books\lw\02fotw\title.htm
Test-Path .\books\lw\02fotw\sect1.htm
Test-Path .\books\lw\03tcok\title.htm
Test-Path .\books\lw\03tcok\sect1.htm
Test-Path .\books\lw\04tcod\title.htm
Test-Path .\books\lw\04tcod\sect1.htm
Test-Path .\books\lw\05sots\title.htm
Test-Path .\books\lw\05sots\sect1.htm
```

Each `Test-Path` command should return `True`.

## After Installing

Start the assistant:

```powershell
.\Launch-LoneWolfRedux.ps1
```

Then open:

```text
http://127.0.0.1:8797/assistant.html
```

The book pane should load the Project Aon HTML files from your local `books\lw` folder.

## Developer Notes

- Keep `books\lw` local.
- Do not commit Project Aon book files.
- Do not package Project Aon book files.
- Use `docs/BOOK_SOURCE_MAP.md` and `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md` before onboarding another book.
