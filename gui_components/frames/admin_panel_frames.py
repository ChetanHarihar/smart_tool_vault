import tkinter as tk
from tkinter import ttk
import os

class UserManagement(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="#E8E9EB", width=824, height=526)
        self.pack_propagate(False)
        self.init_ui()

    def init_ui(self):
        # Create a label frame
        add_user_label_frame = tk.LabelFrame(self, text="Add User", width=814, height=160)
        add_user_label_frame.pack_propagate(False)
        add_user_label_frame.pack()

        # Container to hold the widgets
        add_user_widget_container = tk.Frame(add_user_label_frame)
        add_user_widget_container.pack(pady=(15, 0))

        # Labels
        tk.Label(add_user_widget_container, text="Name:").grid(row=0, column=0, sticky="w")
        tk.Label(add_user_widget_container, text="UID:").grid(row=1, column=0, sticky="w")

        # Entry Boxes
        self.name_entry = tk.Entry(add_user_widget_container, width=25)
        self.name_entry.grid(row=0, column=1)
        self.uid_entry = tk.Entry(add_user_widget_container, width=25)
        self.uid_entry.grid(row=1, column=1)

        # Radio Button
        self.role_var = tk.IntVar()
        self.admin_btn = tk.Radiobutton(add_user_widget_container, text="Admin", variable=self.role_var, value=1)
        self.admin_btn.grid(row=2, column=0, sticky="w")
        self.employee_btn = tk.Radiobutton(add_user_widget_container, text="Employee", variable=self.role_var, value=2)
        self.employee_btn.grid(row=2, column=1, sticky="w")
        self.role_var.set(1)

        # Buttons
        self.clear_btn = tk.Button(add_user_widget_container, text="Clear", command=self.clear_user_fields)
        self.clear_btn.grid(row=3, column=0, padx=5, pady=5)
        self.add_btn = tk.Button(add_user_widget_container, text="Add", command=None, state="disabled")
        self.add_btn.grid(row=3, column=1, padx=5, pady=5)

        # Bind events to Entry fields
        self.name_entry.bind("<KeyRelease>", self.validate_user_data)
        self.uid_entry.bind("<KeyRelease>", self.validate_user_data)

    def validate_user_data(self, event=None):
        name = self.name_entry.get()
        uid = self.uid_entry.get()
        
        if name and uid:
            self.add_btn.config(state="normal")
        else:
            self.add_btn.config(state="disabled")

    def clear_user_fields(self):
        self.name_entry.delete(0, tk.END)
        self.uid_entry.delete(0, tk.END)
        self.add_btn.config(state="disabled")


class InventoryManagement(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="#E8E9EB", width=824, height=526)
        self.pack_propagate(False)
        self.init_ui()

    def init_ui(self):
        # Create a Notebook widget
        self.notebook = ttk.Notebook(self)

        # Create and add tabs
        self.add = ttk.Frame(self.notebook)
        self.manage = ttk.Frame(self.notebook)
        self.stock_management = ttk.Frame(self.notebook)

        self.notebook.add(self.add, text="Add")
        self.notebook.add(self.manage, text="Manage")
        self.notebook.add(self.stock_management, text="Stock Management")

        # Pack the Notebook widget 
        self.notebook.pack(fill="both", expand=True)

        # create label frames for adding category, item and machine
        self.category_label_frame = tk.LabelFrame(self.add, text="Add Category", width=824, height=130)
        self.category_label_frame.pack_propagate(False)
        self.category_label_frame.pack(pady=(15,0))

        self.add_category_widget_frame = tk.Frame(self.category_label_frame)
        self.add_category_widget_frame.pack(side="left", padx=(5,5))

        tk.Label(self.add_category_widget_frame, text="Category Name:").grid(row=0,column=0,sticky='w')

        self.cat_entry = tk.Entry(self.add_category_widget_frame, width=30)
        self.cat_entry.grid(row=0,column=1, pady=(5))

        tk.Label(self.add_category_widget_frame, text="Minimum stock:").grid(row=1,column=0,sticky='w')

        self.min_stock_entry = tk.Entry(self.add_category_widget_frame, width=30)
        self.min_stock_entry.grid(row=1,column=1)

        self.cat_add_btn = tk.Button(self.category_label_frame, text="Add", command=None)
        self.cat_add_btn.pack(side="left", padx=(5,5))

        self.item_label_frame = tk.LabelFrame(self.add, text="Add Item", width=824, height=130)
        self.item_label_frame.pack_propagate(False)
        self.item_label_frame.pack(pady=(15,0))

        add_item_widget_frame = tk.Frame(self.item_label_frame)
        add_item_widget_frame.pack(side="left", padx=(5,5))

        tk.Label(add_item_widget_frame, text="Category Name:").grid(row=0,column=0,sticky='w')

        self.cat_item_entry = tk.Entry(add_item_widget_frame, width=30)
        self.cat_item_entry.grid(row=0,column=1, pady=(5))

        tk.Label(add_item_widget_frame, text="Item Name:").grid(row=1,column=0,sticky='w')

        self.item_entry = tk.Entry(add_item_widget_frame, width=30)
        self.item_entry.grid(row=1,column=1)

        self.item_add_btn = tk.Button(self.item_label_frame, text="Add", command=None)
        self.item_add_btn.pack(side="left", padx=(5,5))

        self.machine_label_frame = tk.LabelFrame(self.add, text="Add Machine", width=824, height=130)
        self.machine_label_frame.pack_propagate(False)
        self.machine_label_frame.pack(pady=(15,0))

        add_mac_widget_frame = tk.Frame(self.machine_label_frame)
        add_mac_widget_frame.pack(side="left", padx=(5,5))

        tk.Label(add_mac_widget_frame, text="Machine Name:").grid(row=0,column=0,sticky='w')

        self.mac_name_entry = tk.Entry(add_mac_widget_frame, width=30)
        self.mac_name_entry.grid(row=0,column=1, pady=(5))

        tk.Label(add_mac_widget_frame, text="Machine Code:").grid(row=1,column=0,sticky='w')

        self.mac_code_entry = tk.Entry(add_mac_widget_frame, width=30)
        self.mac_code_entry.grid(row=1,column=1)

        self.mac_add_btn = tk.Button(self.machine_label_frame, text="Add", command=None)
        self.mac_add_btn.pack(side="left", padx=(5,5))

        self.manage_main_frame = tk.Frame(self.manage)
        self.manage_main_frame.pack_propagate(False)
        self.manage_main_frame.pack(fill="both", expand=True)

        manage_btns_frame = tk.Frame(self.manage_main_frame)
        manage_btns_frame.pack(pady=(10, 5))

        self.cat_view_btn = tk.Button(manage_btns_frame, text="View Categories", command=lambda: self.switch_view(self.cat_view_frame))
        self.cat_view_btn.pack(side='left', padx=(2.5, 2.5))

        self.item_view_btn = tk.Button(manage_btns_frame, text="View Items", command=lambda: self.switch_view(self.item_view_frame))
        self.item_view_btn.pack(side='left', padx=(2.5, 2.5))

        self.mac_view_btn = tk.Button(manage_btns_frame, text="View Machines", command=lambda: self.switch_view(self.mac_view_frame))
        self.mac_view_btn.pack(side='left', padx=(2.5, 2.5))

        self.manage_view_frame = tk.Frame(self.manage_main_frame)
        self.manage_view_frame.pack(pady=(10,10))

        self.cat_view_frame = tk.Frame(self.manage_view_frame)
        self.cat_view_frame.pack()

        self.item_view_frame = tk.Frame(self.manage_view_frame)

        self.mac_view_frame = tk.Frame(self.manage_view_frame)

        self.stock_main_frame = tk.Frame(self.stock_management)
        self.stock_main_frame.pack()

        # create label frames to restock items
        self.restock_label_frame = tk.LabelFrame(self.stock_main_frame, text="Restock", width=814, height=90)
        self.restock_label_frame.pack_propagate(False)
        self.restock_label_frame.pack(side=tk.BOTTOM, pady=(10,0))

        self.restock_item_label = tk.Label(self.restock_label_frame, text="Item Name:")
        self.restock_item_label.pack(side="left", padx=(40,5))

        self.restock_item_name = tk.Label(self.restock_label_frame, text="", width=45, anchor='w')
        self.restock_item_name.pack(side="left", padx=(5,5))

        self.restock_quantity_label = tk.Label(self.restock_label_frame, text="Quantity")
        self.restock_quantity_label.pack(side="left", padx=(5,5))

        self.restock_quantity_entry = tk.Entry(self.restock_label_frame, width=10)
        self.restock_quantity_entry.pack(side="left", padx=(5,5))

        self.restock_btn = tk.Button(self.restock_label_frame, text="Restock", command=None)
        self.restock_btn.pack(side="left", padx=(20,5))

    def switch_view(self, view):
        for widget in self.manage_view_frame.winfo_children():
            widget.forget()
        view.pack()


class ItemPlacementManagement(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="#E8E9EB", width=824, height=526)
        self.pack_propagate(False)
        self.init_ui()

    def init_ui(self):
        # Create a Notebook widget
        self.notebook = ttk.Notebook(self)

        # Create and add tabs
        self.add = ttk.Frame(self.notebook)
        self.manage = ttk.Frame(self.notebook)

        self.notebook.add(self.add, text="Add")
        self.notebook.add(self.manage, text="Manage")

        # Pack the Notebook widget 
        self.notebook.pack(fill="both", expand=True)

        # create label frames for adding racks and item placement details
        self.rack_label_frame = tk.LabelFrame(self.add, text="Add Rack", width=814, height=100)
        self.rack_label_frame.pack_propagate(False)
        self.rack_label_frame.pack(pady=(15,0))

        tk.Label(self.rack_label_frame, text="Rack Name:").pack(side="left", padx=(5,5))

        self.rack_entry = tk.Entry(self.rack_label_frame, width=25)
        self.rack_entry.pack(side="left", padx=(5,5))

        self.rack_add_btn = tk.Button(self.rack_label_frame, text="Add", command=None)
        self.rack_add_btn.pack(side="left", padx=(5,5))

        self.ip_label_frame = tk.LabelFrame(self.add, text="Item Placement", width=814, height=340)
        self.ip_label_frame.pack_propagate(False)
        self.ip_label_frame.pack(pady=(10,0))

        self.manage_main_frame = tk.Frame(self.manage)
        self.manage_main_frame.pack_propagate(False)
        self.manage_main_frame.pack(fill="both", expand=True)

        manage_btns_frame = tk.Frame(self.manage_main_frame)
        manage_btns_frame.pack()

        self.rack_view_btn = tk.Button(manage_btns_frame, text="View Racks", command=lambda: self.switch_view(self.rack_view_frame))
        self.rack_view_btn.pack(side='left', padx=(2.5, 2.5))

        self.placement_view_btn = tk.Button(manage_btns_frame, text="View Placement", command=lambda: self.switch_view(self.placement_view_frame))
        self.placement_view_btn.pack(side='left', padx=(2.5, 2.5))

        self.manage_view_frame = tk.Frame(self.manage_main_frame)
        self.manage_view_frame.pack(pady=(10,10))

        self.rack_view_frame = tk.Frame(self.manage_view_frame)
        self.rack_view_frame.pack()

        self.placement_view_frame = tk.Frame(self.manage_view_frame)

    def switch_view(self, view):
        for widget in self.manage_view_frame.winfo_children():
            widget.forget()
        view.pack()


class TroubleShooting(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="#E8E9EB", width=824, height=526)
        self.pack_propagate(False)
        self.init_ui()

    def init_ui(self):
        # Create a Notebook widget
        self.notebook = ttk.Notebook(self)

        # Create and add tabs
        self.read_card = ttk.Frame(self.notebook)
        self.actuate = ttk.Frame(self.notebook)

        self.notebook.add(self.read_card, text="Read Card")
        self.notebook.add(self.actuate, text="Actuate")

        # Pack the Notebook widget 
        self.notebook.pack(fill="both", expand=True)

# If this file is run directly for testing purposes
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)

    # build the path to the theme file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    theme_path = os.path.join(base_dir, "theme", "forest-light.tcl")

    root.tk.call("source", theme_path)
    style.theme_use("forest-light")
    
    frame = UserManagement(root)
    frame.pack()
    
    root.mainloop()