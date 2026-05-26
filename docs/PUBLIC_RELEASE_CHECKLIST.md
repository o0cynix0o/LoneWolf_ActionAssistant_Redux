# Public Release Checklist

Use this before tagging or uploading a public build.

## Clean Start

1. Clone or unzip the project into a fresh folder.
2. Install dependencies:

   ```powershell
   python -m pip install -r .\requirements.txt
   ```

3. Start the app:

   ```powershell
   .\Launch-LoneWolfRedux.ps1
   ```

4. Install the Project Aon book files by following `docs/INSTALL_PROJECT_AON_BOOKS.md`.
5. Open `http://localhost:8797/assistant.html`.

## Smoke Test

1. Create a new Book 1 character.
2. Confirm the book pane and assistant pane both load.
3. Change one card size, close the server, restart it, and confirm the card size sticks.
4. Add and drop a test item.
5. Use Save Now.
6. Export the current save.
7. Backup all saves.
8. Import the exported save and confirm it loads.

## Automated Checks

Run:

```powershell
python -m py_compile app_server.py lonewolf_redux.py launch_lonewolf_redux.py ws_server.py
python .\testing\playtest_book1.py
python .\testing\playtest_book2.py
python .\testing\playtest_book3.py
python .\testing\playtest_book4.py
python .\testing\playtest_campaign.py
```

Expected result: all book playtests and campaign checks report zero failures.

## Package

Create the release ZIP:

```powershell
.\tools\Make-Release.ps1
```

The package is written to `dist/`. Runtime files such as saves, current position, UI preferences, and the local wiki checkout are not included.

Confirm the package does not include Project Aon book files:

```powershell
git ls-files books/lw
```

Expected result: no output.
