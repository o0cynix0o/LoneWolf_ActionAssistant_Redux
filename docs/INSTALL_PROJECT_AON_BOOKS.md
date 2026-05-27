# Install The Project Aon Book Files

Lone Wolf Action Assistant Redux does not include Project Aon book HTML files in the repository or release ZIP.

Project Aon provides the Internet Editions from its own site. Their license lets you download the books for personal use, but it does not let this project redistribute the book files. Download the books directly from Project Aon, then place them in the local folder layout below.

Read the license here:

- https://www.projectaon.org/en/Main/License

## Use The Standard HTML Editions

Download the **standard** edition for each supported Lone Wolf book. This is the full-featured, multi-page HTML edition that matches the assistant's reader paths.

Current supported book:

| Book | Status | Project Aon page | Standard ZIP |
| --- | --- | --- | --- |
| 1. Flight from the Dark | Playable release candidate | https://www.projectaon.org/en/Main/FlightFromTheDark | https://www.projectaon.org/en/xhtml/lw/01fftd/01fftd.zip |

Future books must be installed locally before they can be audited through `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md`.

Common Project Aon Lone Wolf folder codes:

| Book | Folder code | Status in this app |
| --- | --- | --- |
| 1. Flight from the Dark | `01fftd` | Supported |
| 2. Fire on the Water | `02fotw` | Future pipeline target |
| 3. The Caverns of Kalte | `03tcok` | Future pipeline target |
| 4. The Chasm of Doom | `04tcod` | Future pipeline target |
| 5. Shadow on the Sand | `05sots` | Future pipeline target |

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
```

The app currently expects this folder name for Book 1:

- `01fftd`

## Manual Install

1. Download the Book 1 standard ZIP from Project Aon.
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
   ```

If you see an extra nested folder after extraction, move the book folder so the path matches the examples above.

## PowerShell Example

From the project folder:

```powershell
New-Item -ItemType Directory -Force .\books\lw

Expand-Archive "$env:USERPROFILE\Downloads\01fftd.zip" -DestinationPath .\books\lw -Force

Test-Path .\books\lw\01fftd\title.htm
Test-Path .\books\lw\01fftd\sect1.htm
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
