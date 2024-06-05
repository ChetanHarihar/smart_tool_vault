import tkinter as tk
from PIL import Image, ImageTk

class RoleButton(tk.Button):
    # Load and resize images for admin and employee roles
    emp = Image.open('/home/das01/Python/smart_tool_vault/assets/employee.png').resize((120, 120))
    admin = Image.open('/home/das01/Python/smart_tool_vault/assets/admin.png').resize((120, 120))

    def __init__(self, master=None, role=None, command=None, **kwargs):
        super().__init__(master, **kwargs)

        # Convert images to PhotoImage and store them as attributes
        self.emp_image = ImageTk.PhotoImage(RoleButton.emp)
        self.admin_image = ImageTk.PhotoImage(RoleButton.admin)

        if role == 'admin':
            self.config(image=self.admin_image, borderwidth=0, background="white", activebackground="white",command=command)
        elif role == 'employee':
            self.config(image=self.emp_image, borderwidth=0, bg="white", activebackground="white", command=command)


if __name__ == "__main__":

    root = tk.Tk()

    # Create a RoleButton 
    admin_btn = RoleButton(root, role='admin')
    admin_btn.pack()

    # Create a RoleButton 
    emp_btn = RoleButton(root, role='employee')
    emp_btn.pack()


    root.mainloop()