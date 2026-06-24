import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
import shutil
import logging

logging.basicConfig(
    filename="file_sorter.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
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
            placeholder_text="Enter Cut Off Date"
        )
        self.entry.pack(padx=20, pady=20)

        self.button1 = ctk.CTkButton(
            self.app,
            text="Select File Starting Point",
            border_color="blue",
            border_width=2,
            command=self.button_eventStart
        )
        self.button1.pack(padx=20, pady=20)

        self.button2 = ctk.CTkButton(
            self.app,
            text="Select File Destination Point",
            border_color="blue",
            border_width=2,
            command=self.button_eventDest
        )
        self.button2.pack(padx=20, pady=20)

        self.button3 = ctk.CTkButton(
            self.app,
            text="Start Program",
            border_color="green",
            border_width=2,
            command=self.start_program
        )
        self.button3.pack(padx=20, pady=20)

    def button_eventStart(self):
        self.startFile_Path = Path(filedialog.askdirectory())
        print("Start folder:", self.startFile_Path)

    def button_eventDest(self):
        self.destFile_Path = Path(filedialog.askdirectory())
        print("Destination folder:", self.destFile_Path)

    def start_program(self):
        moved = 0
        cutoff_date = self.entry.get()
        intcutoff_date = int(cutoff_date)
        

        print("Starting program...")
        print("Start folder:", self.startFile_Path)
        print("Destination folder:", self.destFile_Path)
        print("Cutoff date:", cutoff_date)

        logging.info("Program started")
        logging.info(f"Source: {self.startFile_Path}")
        logging.info(f"Destination: {self.destFile_Path}")
        logging.info(f"Cutoff: {intcutoff_date}")

        for item in self.startFile_Path.iterdir():
            if item.is_dir():
                (self.destFile_Path / item.name).mkdir(exist_ok=True)
                
        
                for file in item.iterdir():
                    if file.is_file():
                        try: 
                            fileYear = int(file.stem)
                        except ValueError:
                            print("Skipping:", file.name)
                            logging.info(f"Skipped non-year file: {file.name}")
                            continue
                        if fileYear < intcutoff_date:
                            shutil.move(file, Path(self.destFile_Path) / item.name)
                            logging.info(f"Moved {file.name} to {self.destFile_Path / item.name}")
                            moved += 1
        logging.info(f"Run complete. Moved {moved} files.")
                            

                    
        


    def run(self):
        self.app.mainloop()



