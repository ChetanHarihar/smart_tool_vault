import tkinter as tk
import time

class TopBar(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="white", width=1024, height=50, borderwidth=2, relief="groove")
        self.pack_propagate(False)
        self.init_ui()
    
    def init_ui(self):
        # place user label
        self.user_info_label = tk.Label(self, text="User: ", font=('times new roman', 12, 'bold'), bg="white")
        self.user_info_label.place(relx=0.05, rely=0.5, anchor="center")

        # place machine label
        self.machine_info_label = tk.Label(self, text="Machine: ", font=('times new roman', 12, 'bold'), bg="white")
        self.machine_info_label.place(relx=0.5, rely=0.5, anchor="center")

        # date_time frame
        self.date_time_frame = tk.Frame(self, bg="white")
        self.date_time_frame.pack(side=tk.RIGHT, padx=(0, 10))

        # date label
        self.date_label = tk.Label(self.date_time_frame, font=('Arial', 10), bg="white")
        self.date_label.pack(side=tk.TOP)

        # time label
        self.time_label = tk.Label(self.date_time_frame, font=('Arial', 10), bg="white")
        self.time_label.pack(side=tk.BOTTOM)

    def update_datetime(self):
        time_string = time.strftime("%I:%M:%S %p")
        self.time_label.config(text=time_string)

        date_string = time.strftime("%B %d, %Y")
        self.date_label.config(text=date_string)

        self.date_time_frame.after(1000, self.update_datetime)


if __name__ == "__main__":
    root = tk.Tk()

    nav_bar = TopBar(root)
    nav_bar.pack()

    nav_bar.update_datetime()
    root.mainloop()