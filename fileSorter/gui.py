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


class FileSorter:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("File Organizer")
        self.app.geometry("1000x1000")

        self.startFile_Path = None
        self.destFile_Path = None

        self.entry = ctk.CTkEntry(
            self.app,
            placeholder_text="Enter Cut Off Date",
        )
        self.entry.pack(padx=20, pady=20)

        self.button1 = ctk.CTkButton(
            self.app,
            text="Select File Starting Point",
            border_color="blue",
            border_width=2,
            command=self.button_eventStart,
        )
        self.button1.pack(padx=20, pady=20)

        self.button2 = ctk.CTkButton(
            self.app,
            text="Select File Destination Point",
            border_color="blue",
            border_width=2,
            command=self.button_eventDest,
        )
        self.button2.pack(padx=20, pady=20)

        self.button3 = ctk.CTkButton(
            self.app,
            text="Start Program",
            border_color="green",
            border_width=2,
            command=self.start_program,
        )
        self.button3.pack(padx=20, pady=20)

        self.status_label = ctk.CTkLabel(self.app, text="")
        self.status_label.pack(padx=20, pady=20)

        self.progressbar = ctk.CTkProgressBar(self.app)
        self.progressbar.set(0)
        self.progressbar.pack(padx=20, pady=20)

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
        self.app.after(0, lambda: self.progressbar.set(done / total))

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
        self.button3.configure(state="disabled")

        threading.Thread(target=self._run_sort, args=(cutoff_year,), daemon=True).start()

    def run(self):
        self.app.mainloop()
