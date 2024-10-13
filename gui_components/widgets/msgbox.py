import tkinter as tk
from tkinter import messagebox

def on_exit(root):
    if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
        root.destroy()

def confirm_pickup():
    result = messagebox.askyesno("Confirm Pickup", "Are you sure you want to confirm the pickup?")
    # returns true if user presses Yes
    return result

def confirm_remove_user():
    result = messagebox.askokcancel("Confirmation", "Are you sure you want to remove the User?")
    # returns true if user presses OK
    return result

def confirm_remove_category():
    result = messagebox.askokcancel("Confirmation", "Are you sure you want to remove the Category?")
    # returns true if user presses OK
    return result

def confirm_remove_item():
    result = messagebox.askokcancel("Confirmation", "Are you sure you want to remove the Item?")
    # returns true if user presses OK
    return result

def confirm_item_restock():
    result = messagebox.askokcancel("Confirmation", "Are the Items added, confirm restock?")
    # returns true if user presses OK
    return result

def confirm_remove_rack():
    result = messagebox.askokcancel("Confirmation", "Are you sure you want to remove the Rack?")
    # returns true if user presses OK
    return result

def confirm_remove_ip():
    result = messagebox.askokcancel("Confirmation", "Are you sure you want to remove the placed Item?")
    # returns true if user presses OK
    return result

def confirm_remove_machine():
    result = messagebox.askokcancel("Confirmation", "Are you sure you want to remove the Machine")
    # returns true if user presses OK
    return result

def show_error_message_box(title, message):
    messagebox.showerror(title, message)

def show_success_message_box(message):
    messagebox.showinfo("Success", message)

if __name__ == "__main__":
    root = tk.Tk()

    root.protocol("WM_DELETE_WINDOW", lambda:on_exit(root))

    root.mainloop()