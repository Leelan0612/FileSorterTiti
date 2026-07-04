"""CustomTkinter GUI for the file sorter.

This module owns everything visual. All file-moving work is delegated to
``fileSorter.sorter.sort_files`` so the UI stays thin and the logic stays
testable.
"""

import logging
import os
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .sorter import sort_files

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path


def resource_path(relative: str) -> str:
    """Return an absolute path to a bundled resource.

    Works both when running from source and when frozen by PyInstaller. When
    frozen, PyInstaller unpacks bundled data to ``sys._MEIPASS``; otherwise the
    resource sits next to this module in the ``fileSorter`` package folder.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        base = Path(__file__).resolve().parent
    return str(Path(base) / relative)


def _log_file() -> Path:
    """A user-writable log location that survives the .exe temp directory."""
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    folder = Path(base) / "FileOrganizer"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "file_sorter.log"

def format_time(seconds):
    seconds = int(seconds)

    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


LOG_FILE = _log_file()

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


PAGE_BG = "#FFFFFF"
CARD_BG = "#F2F5F8"
CARD_BORDER = "#E1E8EC"
BLUE = "#2C5F8A"
BLUE_HOVER = "#21496B"
GREEN = "#2E8B57"
GREEN_HOVER = "#246B45"
TEXT = "#2D3436"
HINT = "#636E72"
INPUT_BG = "#FFFFFF"
INPUT_BORDER = "#DFE6E9"
PROGRESS_BG = "#DFE6E9"
WHITE = "#FFFFFF"
SECONDARY_HOVER = "#E8EEF3"


class FileSorter:
    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme(str(resource_path("fileSorter/custom.json")))
        self.app = ctk.CTk()
        icon_path = resource_path("app.ico")

        try:
            self.app.iconbitmap(str(icon_path))
        except Exception:
            pass
        self.app.configure(fg_color=PAGE_BG)
        self.app.bind("<Button-1>", lambda event: event.widget.focus_set())
        self.app.title("File Organizer")
        self.app.geometry("560x820")
        self.app.minsize(520, 780)

        self.startFile_Path = None
        self.destFile_Path = None

        card1 = self._make_card()
        self._step_header(card1, "1", "Step 1: Set Cut-off Year")

        ctk.CTkLabel(
            card1, text="Cut-off Year", text_color=TEXT,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(4, 4))

        self.entry = ctk.CTkEntry(
            card1,
            placeholder_text="e.g., 2023",
            placeholder_text_color=HINT,
            height=48,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            border_width=2,
            text_color=TEXT,
            font=ctk.CTkFont(size=16),
        )
        self.entry.pack(fill="x", padx=20)

        ctk.CTkLabel(
            card1, text="Format: YYYY (4 digits)", text_color=HINT,
            font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=20, pady=(4, 18))

        card2 = self._make_card()
        self._step_header(card2, "2", "Step 2: Select Folders")

        self.button1 = ctk.CTkButton(
            card2, text="Choose where files are now",
            height=56, font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=BLUE, hover_color=BLUE_HOVER, text_color=WHITE,
            command=self.button_eventStart,
        )
        self.button1.pack(fill="x", padx=20, pady=(4, 8))

        self.button2 = ctk.CTkButton(
            card2, text="Choose where to move them",
            height=56, font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=BLUE, hover_color=BLUE_HOVER, text_color=WHITE,
            command=self.button_eventDest,
        )
        self.button2.pack(fill="x", padx=20, pady=(0, 18))

        card3 = self._make_card()
        self._step_header(card3, "3", "Step 3: Start Organization")

        self.button3 = ctk.CTkButton(
            card3, text="Start",
            height=52, font=ctk.CTkFont(size=20, weight="bold"),
            fg_color=GREEN, hover_color=GREEN_HOVER, text_color=WHITE,
            command=self.start_program,
        )
        self.button3.pack(fill="x", padx=20, pady=(4, 12))

        self.progressbar = ctk.CTkProgressBar(
            card3, height=20, corner_radius=10,
            fg_color=PROGRESS_BG, progress_color=BLUE,
        )
        self.progressbar.set(0)
        self.progressbar.pack(fill="x", padx=20)

        self.percent_label = ctk.CTkLabel(
            card3, text="0%", text_color=BLUE,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.percent_label.pack(pady=(8, 4))

        self.status_label = ctk.CTkLabel(
            card3, text="", text_color=HINT, font=ctk.CTkFont(size=14),
        )
        self.status_label.pack(pady=(0, 12))

        shortcut_row = ctk.CTkFrame(card3, fg_color="transparent")
        shortcut_row.pack(fill="x", padx=20, pady=(0, 18))

        self.open_log_button = ctk.CTkButton(
            shortcut_row, text="Open Log", height=38,
            font=ctk.CTkFont(size=13),
            fg_color=WHITE, hover_color=SECONDARY_HOVER, text_color=BLUE,
            border_width=1, border_color=CARD_BORDER,
            command=self.open_log,
        )
        self.open_log_button.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.open_dest_button = ctk.CTkButton(
            shortcut_row, text="Open Destination", height=38,
            font=ctk.CTkFont(size=13),
            fg_color=WHITE, hover_color=SECONDARY_HOVER, text_color=BLUE,
            border_width=1, border_color=CARD_BORDER,
            command=self.open_destination,
        )
        self.open_dest_button.pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _make_card(self):
        card = ctk.CTkFrame(
            self.app, fg_color=CARD_BG, corner_radius=12,
            border_width=1, border_color=CARD_BORDER,
        )
        card.pack(fill="x", padx=24, pady=12)
        return card

    def _step_header(self, parent, number, title):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(18, 10))
        badge = ctk.CTkLabel(
            row, text=number, width=36, height=36, corner_radius=18,
            fg_color=BLUE, text_color=WHITE,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        badge.pack(side="left")
        ctk.CTkLabel(
            row, text=title, text_color=TEXT,
            font=ctk.CTkFont(size=19, weight="bold"),
        ).pack(side="left", padx=12)

    def button_eventStart(self):
        chosen = filedialog.askdirectory()
        if chosen:
            self.startFile_Path = Path(chosen)
            print("Start folder:", self.startFile_Path)

    def button_eventDest(self):
        chosen = filedialog.askdirectory()
        if chosen:
            self.destFile_Path = Path(chosen)
            print("Destination folder:", self.destFile_Path)

    def open_log(self):
        if not LOG_FILE.exists():
            messagebox.showinfo("No log yet", "The log file is created after your first run.")
            return
        try:
            os.startfile(str(LOG_FILE))
        except OSError as exc:
            messagebox.showerror("Could not open log", str(exc))

    def open_destination(self):
        if self.destFile_Path is None:
            messagebox.showinfo("No folder selected", "Choose a destination folder first.")
            return
        try:
            os.startfile(str(self.destFile_Path))
        except OSError as exc:
            messagebox.showerror("Could not open folder", str(exc))

    def _run_sort(self, cutoff_year):
        try:
            moved = sort_files(
                self.startFile_Path, self.destFile_Path, cutoff_year,
                progress_callback=self._on_progress,
            )
        except Exception as exc:
            logging.exception("Run failed")
            self.app.after(0, lambda: messagebox.showerror("Error", str(exc)))
            self.app.after(0, lambda: self.status_label.configure(text="Error."))
            self.app.after(0, lambda: self.button3.configure(state="normal"))
            return
        self.app.after(0, lambda: self.status_label.configure(text=f"Done. Moved {moved} file(s)."))
        self.app.after(0, lambda: self.button3.configure(state="normal"))
        self.app.after(0, lambda: messagebox.showinfo("Complete", f"Moved {moved} file(s)."))

    def _on_progress(self, done, total, remaining):
        fraction = done / total
        percent = int(fraction * 100)

        self.app.after(0, lambda: self.progressbar.set(fraction))
        self.app.after(0, lambda: self.percent_label.configure(text=f"{percent}%"))

        self.app.after(
            0,
            lambda: self.status_label.configure(
                text=f"Moving folders... Time left: {format_time(remaining)}"
            ),
        )

    def start_program(self):
        raw = self.entry.get().strip()
        try:
            cutoff_year = int(raw)
        except ValueError:
            messagebox.showerror("Invalid input", "Cut-off year must be a number, e.g. 2020.")
            return

        if self.startFile_Path is None or self.destFile_Path is None:
            messagebox.showerror("Missing folders", "Please select both a start and destination folder.")
            return

        self.progressbar.set(0)
        self.percent_label.configure(text="0%")
        self.status_label.configure(text="Moving files...")
        self.button3.configure(state="disabled")

        threading.Thread(target=self._run_sort, args=(cutoff_year,), daemon=True).start()

    def run(self):
        self.app.mainloop()
