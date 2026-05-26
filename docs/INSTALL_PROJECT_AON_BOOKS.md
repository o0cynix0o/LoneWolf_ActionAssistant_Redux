# Installing Project Aon Books

Lone Wolf Action Assistant Redux does not include Project Aon book files.

For the first AA2 build pass, install **Flight from the Dark** locally:

- Project Aon page: https://www.projectaon.org/en/Main/FlightFromTheDark
- Standard HTML ZIP: https://www.projectaon.org/en/xhtml/lw/01fftd/01fftd.zip
- License: https://www.projectaon.org/en/Main/License

Extract the ZIP into:

```text
books\lw
```

The app expects:

```text
books\lw\01fftd\title.htm
books\lw\01fftd\sect1.htm
```

PowerShell example:

```powershell
New-Item -ItemType Directory -Force .\books\lw
Expand-Archive "$env:USERPROFILE\Downloads\01fftd.zip" -DestinationPath .\books\lw -Force
```

The local developer copy already has `books\lw\01fftd` populated. Keep it local. Do not commit it.
