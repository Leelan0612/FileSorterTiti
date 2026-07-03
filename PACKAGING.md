# Packaging FileOrganizer into a Windows .exe

This turns the app into a single `FileOrganizer.exe` that a client can run
without installing Python or any dependencies.

## Build it

From the project root, on Windows:

```
build.bat
```

That installs PyInstaller, installs the runtime dependencies, and produces:

```
dist\FileOrganizer.exe
```

Ship that single file. Nothing else is required on the client's machine.

## What the build handles

- **CustomTkinter assets** — `--collect-all customtkinter` bundles its themes
  and fonts, which PyInstaller otherwise misses (the app would crash on launch
  without this).
- **The purple/blue theme** — `custom.json` is bundled and located at runtime
  via `resource_path()` in `gui.py`, which checks the PyInstaller bundle folder
  when frozen and the source folder otherwise.
- **The log file** — writes to `%LOCALAPPDATA%\FileOrganizer\file_sorter.log`,
  a per-user writable location that persists after the app closes. The
  "Open Log" button opens that same file.

## Before shipping

- **Icon (optional):** add an `app.ico` to the project root and append
  `--icon app.ico` to the PyInstaller command in `build.bat`.
- **Test the .exe on a clean machine** (or one without Python) to confirm it
  launches, the theme loads, folders can be picked, a sort runs, the progress
  bar and percentage update, and the log/destination buttons work.
- **SmartScreen:** unsigned executables trigger a Windows SmartScreen warning
  the first time. For a polished client deliverable, consider code-signing the
  `.exe`; otherwise document that they click "More info -> Run anyway."

## Version

Current: 1.0. Bump this and note changes here as you release updates.
