import tkinter as tk
from PIL import Image, ImageTk
import os

class LoginSuccess(tk.Toplevel):
    def __init__(self, username, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="white")
        self.title("Login successful")
        self.geometry("300x120")
        self.root = master

        # Center the window above the main window
        self.center_window()

        # Add success image
        correct_image = Image.open(os.path.join(os.getcwd(), "assets", "correct.png"))  
        correct_image = correct_image.resize((50, 50), Image.Resampling.LANCZOS)  
        self.correct_image = ImageTk.PhotoImage(correct_image)

        # Container frame
        frame = tk.Frame(self, bg="white")
        frame.pack()
        
        self.img_label = tk.Label(frame, image=self.correct_image, bg="white")
        self.img_label.pack(padx=5, pady=10, side=tk.LEFT)
        
        # Add a text label
        label = tk.Label(frame, text=f"Logged in as {username}", bg="white")
        label.pack(padx=5, pady=5, side=tk.LEFT)

        self.proceed_button = tk.Button(self, text="Proceed", command=self.destroy)
        self.proceed_button.pack(pady=10, side=tk.BOTTOM)

    def center_window(self):
        # Get the dimensions of the screen
        screen_width = self.root.winfo_width()

        # Calculate the position for the Toplevel window
        x = self.root.winfo_x() + (screen_width // 2) - (300 // 2)  # Center horizontally
        y = self.root.winfo_y() + 200  # Position above the main window

        self.geometry(f"+{x}+{y}")


class LoginFailed(tk.Toplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="white")
        self.title("Login failed")
        self.geometry("300x120")
        self.root = master

        # Center the window above the main window
        self.center_window()

        # Add failure image (use a different image if desired)
        failed_image = Image.open(os.path.join(os.getcwd(), "assets", "incorrect.png")) 
        failed_image = failed_image.resize((50, 50), Image.Resampling.LANCZOS)  
        self.failed_image = ImageTk.PhotoImage(failed_image)

        # Container frame
        frame = tk.Frame(self, bg="white")
        frame.pack()
        
        self.img_label = tk.Label(frame, image=self.failed_image, bg="white")
        self.img_label.pack(padx=5, pady=10, side=tk.LEFT)
        
        # Add a text label
        label = tk.Label(frame, text="Retry again...", bg="white")
        label.pack(padx=5, pady=5, side=tk.LEFT)

        self.retry_button = tk.Button(self, text="Retry", command=self.destroy)
        self.retry_button.pack(pady=10, side=tk.BOTTOM)

    def center_window(self):
        # Get the dimensions of the screen
        screen_width = self.root.winfo_width()

        # Calculate the position for the Toplevel window
        x = self.root.winfo_x() + (screen_width // 2) - (300 // 2)  # Center horizontally
        y = self.root.winfo_y() + 200  # Position above the main window

        self.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x200")
    root.title("Login")

    # Button to activate LoginSuccess dialog
    success_button = tk.Button(root, text="Login Success", command=lambda: LoginSuccess("User123", master=root))
    success_button.pack(pady=10)

    # Button to activate LoginFailed dialog
    failed_button = tk.Button(root, text="Login Failure", command=lambda: LoginFailed(master=root))
    failed_button.pack(pady=10)

    root.mainloop()