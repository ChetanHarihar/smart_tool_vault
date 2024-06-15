import tkinter as tk
from PIL import Image, ImageTk

class ScanFrame(tk.Frame):
    # load and resize the rfid scan image
    scan_img = Image.open("/home/pi/Python/SMART_VAULT/assets/rfid_logo.png").resize((200, 200))

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="white", width=1024, height=576)
        self.pack_propagate(False)
        self.init_ui()
    
    def init_ui(self):
        # convert it to tk image object
        self.scan_img_tk = ImageTk.PhotoImage(ScanFrame.scan_img)
        
        # Create label with the image and pack
        self.scan_img_label = tk.Label(self, image=self.scan_img_tk)
        self.scan_img_label.pack(pady=(120, 10))

        # Create label and pack
        self.scan_label = tk.Label(self, text="Place your card on the Scanner", font=("times new roman", 16, 'bold'), background='white')
        self.scan_label.pack(pady=(10, 5))


class ResultFrame(tk.Frame):
    # load and resize the rfid scan image
    correct_img = Image.open("/home/pi/Python/SMART_VAULT/assets/correct.png").resize((100, 100))
    incorrect_img = Image.open("/home/pi/Python/SMART_VAULT/assets/incorrect.png").resize((100, 100))

    def __init__(self, master=None, result=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="white", width=1024, height=576)
        self.result = result
        self.pack_propagate(False)
        self.init_ui()
    
    def init_ui(self):
        # convert it to tk image object
        self.correct_img_tk = ImageTk.PhotoImage(ResultFrame.correct_img)
        self.incorrect_img_tk = ImageTk.PhotoImage(ResultFrame.incorrect_img)
        
        # Create label with the image and pack
        if self.result == 1:
            self.result_img_label = tk.Label(self, image=self.correct_img_tk, borderwidth=0, bg="white")
            self.result_img_label.pack(pady=(150, 10))
            # Create label and pack
            self.result_label = tk.Label(self, text="Access Granted", font=("times new roman", 16, 'bold'), background='white')
            self.result_label.pack(pady=(10, 5))

        elif self.result == 0:
            self.result_img_label = tk.Label(self, image=self.incorrect_img_tk, borderwidth=0, bg="white")
            self.result_img_label.pack(pady=(150, 10))
            # Create label and pack
            self.result_label = tk.Label(self, text="Scan Failed. Trying again...", font=("times new roman", 16, 'bold'), background='white')
            self.result_label.pack(pady=(10, 5))


if __name__ == "__main__":
    root = tk.Tk()

    # frame = ScanFrame()
    frame = ResultFrame(root, result=1)

    frame.pack()

    root.mainloop()