import tkinter as tk
from tkinter import ttk
from settings.config import *
from gui_components.widgets import msgbox
from login_panel import LoginPanel
import os

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(SCREEN_SIZE)
    root.title("Smart Tool Vault")
    style = ttk.Style(root)

    # build the path to the theme file
    theme_path = os.path.join(THEME_PATH, "theme", "forest-light.tcl")

    root.tk.call("source", theme_path)
    style.theme_use("forest-light")

    # Bind the on_closing function to the window close event
    root.protocol("WM_DELETE_WINDOW", lambda:msgbox.on_exit(root))

    # Create an instance of LoginPanel and pack it into the root window
    app = LoginPanel(root)
    app.pack()
    
    root.mainloop()