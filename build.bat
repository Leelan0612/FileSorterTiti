@echo off
REM ============================================================
REM  Build FileOrganizer.exe (standalone Windows executable)
REM
REM  Run this from the project root in a terminal:
REM      build.bat
REM
REM  Output: dist\FileOrganizer.exe  (a single self-contained file)
REM ============================================================

REM Install build + runtime dependencies (safe to re-run).
python -m pip install --upgrade pyinstaller
python -m pip install -r requirements.txt

REM Build. Flags explained:
REM   --onefile           bundle everything into one .exe
REM   --windowed          no console window pops up behind the GUI
REM   --name FileOrganizer  the .exe name
REM   --collect-all customtkinter   bundle CustomTkinter's themes/fonts (required)
REM   --collect-submodules send2trash  ensure send2trash ships fully
REM   --add-data "...custom.json;."   bundle our theme next to the app
REM   (add --icon app.ico once you have an icon file)
python -m PyInstaller --noconfirm --onefile --windowed --name FileOrganizer ^
  --collect-all customtkinter ^
  --collect-submodules send2trash ^
  --add-data "fileSorter/custom.json;." ^
  main.py

echo.
echo Done. The executable is at: dist\FileOrganizer.exe
pause
