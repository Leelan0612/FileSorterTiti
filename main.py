from pathlib import Path 
import shutil 
import logging 
import customtkinter as ctk
from tkinter import Tk, filedialog
from fileSorter.fileSorterClass import FileSorter


def main():
    app = FileSorter()
    app.run()

if __name__ == "__main__":
    main()
