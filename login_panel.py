from settings.config import *
from gui_components.widgets.login_message import *
from services import database
from employee_panel import EmployeePanel
from admin_panel import AdminPanel

class LoginPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="white")
        self.root = master
        self.role = None
        self.login_failed_window = None
        self.scan = True
        self.user_data = None
        self.employee_panel = EmployeePanel(self.root)
        self.admin_panel = AdminPanel(self.root)
        self.pack_propagate(False)
        self.init_ui()
    
    def init_ui(self):
        # Create label and pack
        self.login_label = tk.Label(self, text='Login As?', font=('times new roman', 30, 'bold'), bg="white")
        self.login_label.pack(pady=(120, 50))

        # Load and resize images for admin and employee roles
        emp_image_path = os.path.join(BASE_DIR, "assets", "employee.png")
        admin_image_path = os.path.join(BASE_DIR, "assets", "admin.png")
        
        emp = Image.open(emp_image_path).resize((120, 120))
        admin = Image.open(admin_image_path).resize((120, 120))

        # Convert images to PhotoImage and store them as attributes
        self.emp_image = ImageTk.PhotoImage(emp)
        self.admin_image = ImageTk.PhotoImage(admin)

        # Create and pack button container
        btn_container = tk.Frame(self, bg="white")
        btn_container.pack()

        self.employee_btn = tk.Button(btn_container, image=self.emp_image, borderwidth=0, background="white", activebackground="white", command=lambda:self.run_scan("employee"))
        self.employee_btn.pack(padx=(50), side=tk.LEFT)

        self.admin_btn = tk.Button(btn_container, image=self.admin_image, borderwidth=0, background="white", activebackground="white", command=lambda:self.run_scan("admin"))
        self.admin_btn.pack(padx=(50), side=tk.RIGHT)

    def run_scan(self, role):
        self.role = 1 if role == "admin" else 2
        print(self.role)
        # load the scan frame
        self.pack_forget()
        self.load_scan_frame()

    def load_scan_frame(self):
        self.scan_frame = tk.Frame(self.root, bg="white")
        self.scan_frame.pack_propagate(False)

        # add rfid scan image
        scan_img = Image.open(os.path.join(BASE_DIR, "assets", "rfid_logo.png")).resize((200, 200))
        self.scan_img = ImageTk.PhotoImage(scan_img)
        
        # Create label with the image and pack
        self.scan_img_label = tk.Label(self.scan_frame, image=self.scan_img)
        self.scan_img_label.pack(pady=(120, 10))

        # Create label and pack
        self.scan_label = tk.Label(self.scan_frame, text="Place your card on the Scanner", font=("times new roman", 16, 'bold'), background='white')
        self.scan_label.pack(pady=(10, 5))

        # Create an entry to store the id of the card 
        self.card_id = tk.Entry(self.scan_frame, font=("times new roman", 14), relief='flat', fg="white")
        self.card_id.config(insertontime=0)
        self.card_id.pack()
        self.card_id.focus_set()

        self.check_scan()

        self.scan_frame.pack(fill="both", expand=True)

    def check_scan(self):
        if self.scan:
            print("Scanning...")
            scanned_ID = self.card_id.get()
            if scanned_ID:
                # check the role and validate the scan
                scan_result = database.check_scan_result(uid=scanned_ID, role=self.role, db_path=DATABASE_PATH)
                # if scan_result:
                if scan_result:
                    self.user_id = scan_result[0]
                    self.username = scan_result[1]
                    if self.login_failed_window and self.login_failed_window.winfo_exists():
                        self.login_failed_window.destroy()
                    self.login_success_window = LoginSuccess(master=self.root, username=self.username)
                    print("Valid card")
                    self.scan = False
                    if self.role == 1:
                        # load admin panel
                        pass
                    else:
                        # load employee panel
                        pass
                else:
                    if self.login_failed_window is None or not self.login_failed_window.winfo_exists():
                        self.login_failed_window = LoginFailed(self.root)
                    print("Invalid card")
                    self.card_id.delete(0, tk.END)
                    self.scan_frame.pack_forget()
                    self.pack(fill="both", expand=True)

        self.root.after(3000, self.check_scan)  # Schedule the function to run again after 3000 ms (3 seconds)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{SCREEN_SIZE[0]}x{SCREEN_SIZE[1]}")
    
    # Create the login panel and pack it into the root window
    frame = LoginPanel(root)
    frame.pack(fill="both", expand=True)

    # Start the main loop
    root.mainloop()