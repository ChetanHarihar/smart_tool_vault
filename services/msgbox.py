import tkinter as tk
from tkinter import messagebox

def on_exit(root):
    if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()

    root.protocol("WM_DELETE_WINDOW", lambda:on_exit(root))

    root.mainloop()