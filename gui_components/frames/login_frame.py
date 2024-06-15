import tkinter as tk

class LoginPage(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="white", width=1024, height=576)
        self.pack_propagate(False)
        self.init_ui()
    
    def init_ui(self):
        # Create label and pack
        self.login_label = tk.Label(self, text='Login As?', font=('times new roman', 30, 'bold'), bg="white")
        self.login_label.pack(pady=(120, 50))

if __name__ == "__main__":
    root = tk.Tk()

    frame = LoginPage(root)
    frame.pack()

    root.mainloop()