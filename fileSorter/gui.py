"""CustomTkinter GUI for the file sorter.

This module owns everything visual. All file-moving work is delegated to
``fileSorter.sorter.sort_files`` so the UI stays thin and the logic stays
testable.
"""

import logging
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from fileSorter.sorter import sort_files


logging.basicConfig(
    filename="file_sorter.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Colors pulled from the theme so the folder buttons match the entry box.
ENTRY_FG = ["#F9F9FA", "#1F1D26"]
ENTRY_HOVER = ["#ECECF0", "#2A2833"]
ENTRY_TEXT = ["gray14", "#F3F2F7"]
ENTRY_BORDER = ["#979DA2", "#3A3747"]


class FileSorter:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("fileSorter/custom.json")
        self.app = ctk.CTk()
        self.app.bind("<Button-1>", lambda event: event.widget.focus_set())
        self.app.title("File Organizer")
        self.app.geometry("480x620")

        self.startFile_Path = None
        self.destFile_Path = None

        # Compact heading.
        self.title_label = ctk.CTkLabel(
            self.app,
            text="File Organizer",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.title_label.pack(padx=20, pady=(20, 12))

        self.entry = ctk.CTkEntry(
            self.app,
            placeholder_text="Format: YYYY",
            width=260,
            height=50,
            font=ctk.CTkFont(size=15),
        )
        self.entry.pack(padx=20, pady=(10, 0))

        self.entry_label = ctk.CTkLabel(
            self.app,
            text="Enter Cutoff Date Above.",
            font=ctk.CTkFont(size=18),
        )
        self.entry_label.pack(padx=20, pady=(6, 15))

        self.button1 = ctk.CTkButton(
            self.app,
            text="Select File Starting Point",
            width=260,
            height=50,
            font=ctk.CTkFont(size=18),
            fg_color=ENTRY_FG,
            hover_color=ENTRY_HOVER,
            text_color=ENTRY_TEXT,
            border_width=2,
            border_color=ENTRY_BORDER,
            command=self.button_eventStart,
        )
        self.button1.pack(padx=20, pady=15)

        self.button2 = ctk.CTkButton(
            self.app,
            text="Select File Destination Point",
            width=260,
            height=50,
            font=ctk.CTkFont(size=18),
            fg_color=ENTRY_FG,
            hover_color=ENTRY_HOVER,
            text_color=ENTRY_TEXT,
            border_width=2,
            border_color=ENTRY_BORDER,
            command=self.button_eventDest,
        )
        self.button2.pack(padx=20, pady=15)

        self.button3 = ctk.CTkButton(
            self.app,
            text="Start Program",
            width=260,
            height=50,
            font=ctk.CTkFont(size=18),
            command=self.start_program,
        )
        self.button3.pack(padx=20, pady=15)

        self.status_label = ctk.CTkLabel(self.app, text="")
        self.status_label.pack(padx=20, pady=10)

        self.progressbar = ctk.CTkProgressBar(self.app)
        self.progressbar.set(0)
        self.progressbar.pack(padx=20, pady=10)

        self.percent_label = ctk.CTkLabel(self.app, text="0%", text_color="#2DD4BF")
        self.percent_label.pack(padx=20, pady=(0, 10))

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

    def _run_sort(self, cutoff_year):
        try:
            moved = sort_files(
                self.startFile_Path, self.destFile_Path, cutoff_year,
                progress_callback=self._on_progress,
            )
        except Exception as exc:
            logging.exception("Run failed")
            self.app.after(0, lambda: messagebox.showerror("Error", str(exc)))
            self.app.after(0, lambda: self.button3.configure(state="normal"))
            return
        self.app.after(0, lambda: self.status_label.configure(text=f"Done. Moved {moved} file(s)."))
        self.app.after(0, lambda: self.button3.configure(state="normal"))
        self.app.after(0, lambda: messagebox.showinfo("Complete", f"Moved {moved} file(s)."))

    def _on_progress(self, done, total):
        fraction = done / total 
        percent = int(fraction * 100)
        self.app.after(0, lambda: self.progressbar.set(fraction))
        self.app.after(0, lambda: self.percent_label.configure(text=f"{percent}%"))

    def start_program(self):
        # Validate the cutoff year.
        raw = self.entry.get().strip()
        try:
            cutoff_year = int(raw)
        except ValueError:
            messagebox.showerror("Invalid input", "Cut off date must be a year, e.g. 2020.")
            return

        # Validate folder selections.
        if self.startFile_Path is None or self.destFile_Path is None:
            messagebox.showerror("Missing folders", "Please select both a start and destination folder.")
            return

        self.progressbar.set(0)
        self.percent_label.configure(text="0%")
        self.button3.configure(state="disabled")

        threading.Thread(target=self._run_sort, args=(cutoff_year,), daemon=True).start()

    def run(self):
        self.app.mainloop()
