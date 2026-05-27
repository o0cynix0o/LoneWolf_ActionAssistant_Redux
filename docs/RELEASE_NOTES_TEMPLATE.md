# Release Notes Template

Use this template when preparing a tagged release. Keep Project Aon book files out of the repository and release ZIP.

## Version

`vX.Y.Z`

## Release Status

- Supported books:
- Release type:
- Packaging approval:

## Highlights

- 

## Player-Facing Changes

- 

## Automation And Rules Changes

- 

## Docs And Wiki Changes

- 

## Testing

Commands:

```powershell
python -m py_compile app_server.py lonewolf_redux.py launch_lonewolf_redux.py ws_server.py
python .\testing\playtest_book1.py
```

Manual browser pass:

- 

## Known Limitations

- 

## Packaging Notes

- Release ZIP created with `.\tools\Make-Release.ps1`
- Confirmed `git ls-files books/lw` returned no output
- Confirmed runtime saves, UI preferences, local wiki checkout, and dist artifacts were excluded
