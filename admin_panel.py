import tkinter as tk
from tkinter import ttk
import os
from gui_components.widgets import msgbox
from gui_components.widgets.treeview import TreeView
from gui_components.widgets.topbar import TopBar
from gui_components.frames.admin_panel_frames import *
from services.mqtt_functions import connect_mqtt, handle_publish
from services.rfid_module import scan_rfid
from services import database
from settings.config import *
import queue
import threading
card_data = queue.Queue()


class AdminPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(width=1024, height=576)
        self.root = master
        self.user_id = None
        self.user_name = None
        self.category_data = database.fetch_categories()
        self.item_data = database.fetch_all_items(self.category_data)
        self.rack_details = database.get_all_racks()
        self.racks = [name for id, name in database.get_all_racks()]
        self.rows = ['A', 'B', 'C', 'D', 'E']
        self.cols = ['1', '2', '3', '4', '5', '6']
        # Connect ot MQTT Server
        self.mqtt_client = connect_mqtt(mqtt_server=MQTT_SERVER, mqtt_port=MQTT_PORT)
        self.init_ui()

    def init_ui(self):
        # create and pack nav_bar frame
        self.top_bar = TopBar(self)
        self.top_bar.pack(padx=(2.5, 2.5), pady=(5, 2.5))

        # user info label
        self.user_label = tk.Label(self.top_bar, text=f"Logged in as: ", font=('times new roman', 12, 'bold'), bg="white")
        self.user_label.pack(side=tk.LEFT, padx=(20, 0))

        # Create and pack frame container
        self.main_container = tk.Frame(self, width=1024, height=526)
        self.main_container.pack_propagate(False)
        self.main_container.pack(padx=(2.5, 2.5), pady=(2.5,5))

        self.side_menu = tk.Frame(self.main_container, width=200, height=526, bg="#00563B")
        self.side_menu.pack_propagate(False)
        self.side_menu.grid(row=0, column=0)

        self.btns_container = tk.Frame(self.side_menu, bg="#00563B")
        self.btns_container.pack(pady=(180, 0))

        self.emp_man_btn = tk.Button(self.btns_container, text="User Management", bg="#00563B", fg="white", relief='flat', highlightbackground="#00563B", width=200, command=lambda: self.switch_frame(self.emp_man_frame))
        self.emp_man_btn.pack()

        self.inv_man_btn = tk.Button(self.btns_container, text="Inventory Management", bg="#00563B", fg="white", relief='flat', highlightbackground="#00563B", width=200, command=lambda: self.switch_frame(self.inv_man_frame))
        self.inv_man_btn.pack()

        self.ip_man_btn = tk.Button(self.btns_container, text="Item Placement Management", bg="#00563B", fg="white", relief='flat', highlightbackground="#00563B", width=200, command=lambda: self.switch_frame(self.ip_man_frame))
        self.ip_man_btn.pack()

        self.ts_btn = tk.Button(self.btns_container, text="Trouble Shooting", bg="#00563B", fg="white", relief='flat', highlightbackground="#00563B", width=200, command=lambda: self.switch_frame(self.ts_frame))
        self.ts_btn.pack()

        self.frame_container = tk.Frame(self.main_container, bg="#E8E9EB", width=824, height=526)
        self.frame_container.pack_propagate(False)
        self.frame_container.grid(row=0, column=1)

        self.emp_man_frame = EmployeeManagement(self.frame_container)
        self.emp_man_frame.add_btn.config(command=self.add_user)
        self.emp_man_frame.pack()

        self.view_user_labelframe = tk.LabelFrame(self.emp_man_frame, text="View Users")
        self.view_user_labelframe.pack(pady=(5, 0))

        # create tree view to display the list of users
        # Create a frame to pack the cart treeview
        self.user_treeview_frame = tk.Frame(self.view_user_labelframe, width=814, height=270)
        self.user_treeview_frame.pack_propagate(False)
        self.user_treeview_frame.pack()

        self.user_treeview = TreeView(self.user_treeview_frame, height=7)

        # Create columns
        self.user_treeview["columns"] = ("ID", "User Name", "UID", "Role")
        self.user_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the cart_tree column
        self.user_treeview.column("ID", width=40, anchor=tk.CENTER)
        self.user_treeview.column("User Name", width=200, anchor=tk.W)
        self.user_treeview.column("UID", width=150, anchor=tk.W)
        self.user_treeview.column("Role", width=70, anchor=tk.CENTER)

        # Create headings
        self.user_treeview.heading("ID", text="ID")
        self.user_treeview.heading("User Name", text="User Name", anchor=tk.W)
        self.user_treeview.heading("UID", text="UID", anchor=tk.W)
        self.user_treeview.heading("Role", text="Role", anchor=tk.CENTER)

        self.show_user_info()

        # remove button
        self.remove_btn = tk.Button(self.emp_man_frame, text="Remove", command=self.remove_user)
        self.remove_btn.pack(pady=(10, 0))

        self.inv_man_frame = InventoryManagement(self.frame_container)
        self.inv_man_frame.cat_add_btn.config(command=self.add_cat)
        self.inv_man_frame.item_add_btn.config(command=self.add_item)
        self.inv_man_frame.mac_add_btn.config(command=self.add_mac)

        # Category view
        self.cat_treeview_frame = tk.Frame(self.inv_man_frame.cat_view_frame)
        self.cat_treeview_frame.pack()

        self.cat_treeview = TreeView(self.cat_treeview_frame, height=14)

        # Create columns
        self.cat_treeview["columns"] = ("Sl.no", "Categories")
        self.cat_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the cart_tree column
        self.cat_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.cat_treeview.column("Categories", width=250, anchor=tk.CENTER)

        # Create headings
        self.cat_treeview.heading("Sl.no", text="Sl.no")
        self.cat_treeview.heading("Categories", text="Categories", anchor=tk.CENTER)

        self.show_categories()

        # category remove button
        self.cat_remove_btn = tk.Button(self.inv_man_frame.cat_view_frame, text="Remove", command=self.remove_cat)
        self.cat_remove_btn.pack(pady=(10,0))

        # Item view
        # create dropdown menu to select category
        # Create a variable to store the selected option
        self.var1 = tk.StringVar(self.inv_man_frame.item_view_frame)
        self.var1.set(self.category_data[0])  # Set the default option

        # Create the dropdown menu
        self.cat_dropdown = ttk.Combobox(self.inv_man_frame.item_view_frame, textvariable=self.var1, values=self.category_data)
        self.cat_dropdown.pack(pady=(0, 5))

        self.cat_dropdown.bind("<<ComboboxSelected>>", self.show_items)

        self.item_treeview_frame = tk.Frame(self.inv_man_frame.item_view_frame)
        self.item_treeview_frame.pack(pady=(0, 5))

        self.item_treeview = TreeView(self.item_treeview_frame, height=12)

        # Create columns
        self.item_treeview["columns"] = ("id", "Sl.no", "Items")
        self.item_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the cart_tree column
        self.item_treeview.column("id", width=0, stretch=tk.NO)  
        self.item_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.item_treeview.column("Items", width=350, anchor=tk.CENTER)

        # Create headings
        self.item_treeview.heading("id", text="id")
        self.item_treeview.heading("Sl.no", text="Sl.no")
        self.item_treeview.heading("Items", text="Items", anchor=tk.CENTER)

        self.show_items()

        # category remove button
        self.item_remove_btn = tk.Button(self.inv_man_frame.item_view_frame, text="Remove", command=self.remove_item)
        self.item_remove_btn.pack(pady=(10,0))

        # Item stock view
        # create dropdown menu to select category
        # Create a variable to store the selected option
        self.var2 = tk.StringVar(self.inv_man_frame.stock_main_frame)
        self.var2.set(self.category_data[0])  # Set the default option

        # Create the dropdown menu
        self.stock_dropdown = ttk.Combobox(self.inv_man_frame.stock_main_frame, textvariable=self.var2, values=self.category_data)
        self.stock_dropdown.pack()

        self.stock_dropdown.bind("<<ComboboxSelected>>", self.show_stock)

        self.inv_man_frame.restock_btn.config(command=self.restock)

        self.stock_treeview_frame = tk.Frame(self.inv_man_frame.stock_main_frame)
        self.stock_treeview_frame.pack(pady=(5,0))

        self.stock_treeview = TreeView(self.stock_treeview_frame, height=13)

        # Create columns
        self.stock_treeview["columns"] = ("id", "Sl.no", "Items", "Quantity")
        self.stock_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the cart_tree column
        self.stock_treeview.column("id", width=0, stretch=tk.NO)  
        self.stock_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.stock_treeview.column("Items", width=400, anchor=tk.CENTER)
        self.stock_treeview.column("Quantity", width=100, anchor=tk.CENTER)

        # Create headings
        self.stock_treeview.heading("id", text="id")
        self.stock_treeview.heading("Sl.no", text="Sl.no")
        self.stock_treeview.heading("Items", text="Items", anchor=tk.CENTER)
        self.stock_treeview.heading("Quantity", text="Quantity", anchor=tk.CENTER)

        # Bind the select event to the on_select function
        self.stock_treeview.bind('<<TreeviewSelect>>', self.on_select)

        self.show_stock()

        self.ip_man_frame = ItemPlacementManagement(self.frame_container)
        self.ip_man_frame.rack_add_btn.config(command=self.add_rack)

        self.ip_item_treeview_frame = tk.Frame(self.ip_man_frame.ip_placement_label_frame)
        self.ip_item_treeview_frame.pack(pady=(5,0))

        self.ip_item_treeview = TreeView(self.ip_item_treeview_frame, height=4)

        # Create columns
        self.ip_item_treeview["columns"] = ("id", "Sl.no", "Category", "Items")
        self.ip_item_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the cart_tree column
        self.ip_item_treeview.column("id", width=0, stretch=tk.NO)  
        self.ip_item_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.ip_item_treeview.column("Category", width=200, anchor=tk.CENTER)
        self.ip_item_treeview.column("Items", width=400, anchor=tk.CENTER)

        # Create headings
        self.ip_item_treeview.heading("id", text="id")
        self.ip_item_treeview.heading("Sl.no", text="Sl.no")
        self.ip_item_treeview.heading("Category", text="Category")
        self.ip_item_treeview.heading("Items", text="Items", anchor=tk.CENTER)

        # Bind the select event to the on_select function
        self.ip_item_treeview.bind('<<TreeviewSelect>>', self.on_ip_select)

        self.show_ip_items()

        self.ip_widget_frame1 = tk.Frame(self.ip_man_frame.ip_placement_label_frame)
        self.ip_widget_frame1.pack(pady=(10,0))

        self.ip_widget_frame2 = tk.Frame(self.ip_man_frame.ip_placement_label_frame)
        self.ip_widget_frame2.pack(pady=(10,0))

        self.ip_widget_frame3 = tk.Frame(self.ip_man_frame.ip_placement_label_frame)
        self.ip_widget_frame3.pack(pady=(10,0))

        self.ip_item_label = tk.Label(self.ip_widget_frame1, text="Item Name:")
        self.ip_item_label.grid(row=0, column=0)

        self.ip_item_name = tk.Label(self.ip_widget_frame1, text="", width=30, anchor='w')
        self.ip_item_name.grid(row=0, column=1)

        # dropdown to select rack, row and column

        # create dropdown menu to select rack
        # Create a variable to store the selected option
        self.rack = tk.StringVar(self.ip_widget_frame2)
        self.rack.set(self.racks[0])  # Set the default option

        # Create the dropdown menu
        self.rack_label = tk.Label(self.ip_widget_frame2, text='Select Rack')
        self.rack_label.grid(row=1, column=0)

        self.rack_dropdown = ttk.Combobox(self.ip_widget_frame2, textvariable=self.rack, values=self.racks)
        self.rack_dropdown.grid(row=1, column=1, sticky='w')

        # create dropdown menu to select row
        # Create a variable to store the selected option
        self.row = tk.StringVar(self.ip_widget_frame3)
        self.row.set(self.rows[0])  # Set the default option

        # Create the dropdown menu
        self.row_label = tk.Label(self.ip_widget_frame3, text='Select Row: ')
        self.row_label.grid(row=2, column=0)

        self.row_dropdown = ttk.Combobox(self.ip_widget_frame3, textvariable=self.row, values=self.rows, width=5)
        self.row_dropdown.grid(row=2, column=1)

        self.emp_label = tk.Label(self.ip_widget_frame3, text='       ')
        self.emp_label.grid(row=2, column=2)

        # create dropdown menu to select column
        # Create a variable to store the selected option
        self.col = tk.StringVar(self.ip_widget_frame3)
        self.col.set(self.cols[0])  # Set the default option

        # Create the dropdown menu
        self.col_label = tk.Label(self.ip_widget_frame3, text='Select Column: ')
        self.col_label.grid(row=2, column=3)

        self.col_dropdown = ttk.Combobox(self.ip_widget_frame3, textvariable=self.col, values=self.cols, width=5)
        self.col_dropdown.grid(row=2, column=4)

        self.place_btn = tk.Button(self.ip_man_frame.ip_placement_label_frame, text="Place", command=self.place_item)
        self.place_btn.pack(pady=(10,0))

        # view racks
        self.rack_treeview_frame = tk.Frame(self.ip_man_frame.rack_view_frame)
        self.rack_treeview_frame.pack()

        self.rack_treeview = TreeView(self.rack_treeview_frame, height=15)

        # Create columns
        self.rack_treeview["columns"] = ("Sl.no", "id", "Rack")
        self.rack_treeview.column("#0", width=0, stretch=tk.NO) 
        self.rack_treeview.column("Sl.no", width=50, anchor=tk.CENTER)
        self.rack_treeview.column("id", width=0, stretch=tk.NO)
        self.rack_treeview.column("Rack", width=200, anchor=tk.CENTER)

        # Create headings
        self.rack_treeview.heading("Sl.no", text="Sl.no", anchor=tk.CENTER)
        self.rack_treeview.heading("Rack", text="Rack", anchor=tk.CENTER)

        self.show_all_racks()

        # category remove button
        self.rack_remove_btn = tk.Button(self.ip_man_frame.rack_view_frame, text="Remove", command=self.remove_rack)
        self.rack_remove_btn.pack(pady=(10,0))

        # item placement view
        # create dropdown menu to select rack
        # Create a variable to store the selected option
        self.var1 = tk.StringVar(self.ip_man_frame.rack_view_frame)
        self.var1.set(self.racks[0])  # Set the default option

        # Create the dropdown menu
        self.rack_dropdown = ttk.Combobox(self.ip_man_frame.placement_view_frame, textvariable=self.var1, values=self.racks)
        self.rack_dropdown.pack()

        self.rack_dropdown.bind("<<ComboboxSelected>>", self.show_item_placement_data)

        self.item_placement_treeview_frame = tk.Frame(self.ip_man_frame.placement_view_frame)
        self.item_placement_treeview_frame.pack()

        self.item_placement_treeview = TreeView(self.item_placement_treeview_frame, height=13)

        # Create columns
        self.item_placement_treeview["columns"] = ("Sl.no", "Category", "Item", "Quantity", "rp.id", "Position", "ip.id")
        self.item_placement_treeview.column("#0", width=0, stretch=tk.NO)   
        self.item_placement_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.item_placement_treeview.column("Category", width=150, anchor=tk.CENTER)
        self.item_placement_treeview.column("Item", width=350, anchor=tk.CENTER)
        self.item_placement_treeview.column("Quantity", width=70, anchor=tk.CENTER)
        self.item_placement_treeview.column("rp.id", width=0, stretch=tk.NO)  
        self.item_placement_treeview.column("Position", width=70, anchor=tk.CENTER)
        self.item_placement_treeview.column("ip.id", width=0, stretch=tk.NO) 

        # Create headings
        self.item_placement_treeview.heading("Sl.no", text="Sl.no")
        self.item_placement_treeview.heading("Category", text="Category", anchor=tk.CENTER)
        self.item_placement_treeview.heading("Item", text="Item", anchor=tk.CENTER)
        self.item_placement_treeview.heading("Quantity", text="Quantity", anchor=tk.CENTER)
        self.item_placement_treeview.heading("Position", text="Position", anchor=tk.CENTER)

        self.show_item_placement_data()

        # category remove button
        self.item_placement_remove_btn = tk.Button(self.ip_man_frame.placement_view_frame, text="Remove", command=self.remove_item_placement)
        self.item_placement_remove_btn.pack(pady=(10,0))

        self.ts_frame = TroubleShooting(self.frame_container)

        self.read_card_label = tk.Label(self.ts_frame.read_card, text="Place the card on the Reader")
        self.read_card_label.pack(pady=(10,10))

        self.read_card_btn = tk.Button(self.ts_frame.read_card, text="Read Card", command=self.read_card)
        self.read_card_btn.pack()

        self.widget_container = tk.Frame(self.ts_frame.read_card)
        self.widget_container.pack()

        self.read_id_label = tk.Label(self.widget_container, text="Card ID:")
        self.read_id_label.grid(row=0, column=0)

        self.card_id = tk.Label(self.widget_container, text="", width=20)
        self.card_id.grid(row=0, column=1)

        # Actaute page
        self.send_message_label = tk.Label(self.ts_frame.actuate, text="Send Message: ")
        self.send_message_label.pack(pady=(10,10))

        self.dropdown_contatiner = tk.Frame(self.ts_frame.actuate)
        self.dropdown_contatiner.pack()

        # dropdown to select rack, row and column
        # create dropdown menu to select rack
        # Create a variable to store the selected option
        self.rack2 = tk.StringVar(self.dropdown_contatiner)
        self.rack2.set(self.racks[0])  # Set the default option

        # Create the dropdown menu
        self.rack_label = tk.Label(self.dropdown_contatiner, text='Select Rack')
        self.rack_label.pack(side=tk.LEFT)

        self.rack_dropdown2 = ttk.Combobox(self.dropdown_contatiner, textvariable=self.rack2, values=self.racks)
        self.rack_dropdown2.pack(side=tk.LEFT, padx=(0, 15))

        # create dropdown menu to select row
        # Create a variable to store the selected option
        self.row2 = tk.StringVar(self.dropdown_contatiner)
        self.row2.set(self.rows[0])  # Set the default option

        # Create the dropdown menu
        self.row_label = tk.Label(self.dropdown_contatiner, text='Select Row: ')
        self.row_label.pack(side=tk.LEFT)

        self.row_dropdown2 = ttk.Combobox(self.dropdown_contatiner, textvariable=self.row2, values=self.rows, width=5)
        self.row_dropdown2.pack(side=tk.LEFT, padx=(0, 15))

        # create dropdown menu to select column
        # Create a variable to store the selected option
        self.col2 = tk.StringVar(self.dropdown_contatiner)
        self.col2.set(self.cols[0])  # Set the default option

        # Create the dropdown menu
        self.col_label = tk.Label(self.dropdown_contatiner, text='Select Column: ')
        self.col_label.pack(side=tk.LEFT)

        self.col_dropdown2 = ttk.Combobox(self.dropdown_contatiner, textvariable=self.col2, values=self.cols, width=5)
        self.col_dropdown2.pack(side=tk.LEFT, padx=(0, 15))

        # create dropdown menu to select action
        # Create a variable to store the selected option
        self.action = tk.StringVar(self.dropdown_contatiner)
        self.action.set('OPEN')  # Set the default option

        # Create the dropdown menu
        self.action_label = tk.Label(self.dropdown_contatiner, text='Action: ')
        self.action_label.pack(side=tk.LEFT)

        self.action_dropdown = ttk.Combobox(self.dropdown_contatiner, textvariable=self.action, values=['OPEN','CLOSE'], width=5)
        self.action_dropdown.pack(side=tk.LEFT, padx=(0, 15))

        self.send_message_btn = tk.Button(self.ts_frame.actuate, text="Send", command=self.send_msg)
        self.send_message_btn.pack(pady=(20,10))


    def switch_frame(self, frame):
        for widget in self.frame_container.winfo_children():
            widget.forget()
        frame.pack()

    def update_datetime(self):
        self.top_bar.update_datetime()

    def add_user(self):
        name = self.emp_man_frame.name_entry.get()
        uid = self.emp_man_frame.uid_entry.get()
        role = self.emp_man_frame.role_var.get()
        self.employee_details = [name, uid, role]
        # check for integrity and add the data to database
        success, message = database.add_user(self.employee_details[0], self.employee_details[1], self.employee_details[2])
        if success:
            msgbox.show_success_message_box(message)
        else:
            msgbox.show_error_message_box("Error", message)
        # show the updated list
        self.show_user_info()

    def delete_treeview_items(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)

    def show_user_info(self):
        self.delete_treeview_items(self.user_treeview)
        # get the user data from database
        user_data = database.get_user_details()
        # insert all user data in the user Treeview
        for i, item in enumerate(user_data, start=1):
            if i % 2 == 0:
                self.user_treeview.insert("", "end", values=(f"{item[0]}", f"{item[1]}", f"{item[2]}", f"{'Admin 'if item[3] == 1 else 'Employee'}"), tags=('evenrow',))
            else:
                self.user_treeview.insert("", "end", values=(f"{item[0]}", f"{item[1]}", f"{item[2]}", f"{'Admin 'if item[3] == 1 else 'Employee'}"), tags=('oddrow',))

    def remove_user(self):
        # remove the selected user and update the treeview
        selected_item = self.user_treeview.focus()
        if selected_item:
            item_values = self.user_treeview.item(selected_item, 'values')
            # get the id of the user
            user_id = item_values[0]
            if msgbox.confirm_remove_user():
                database.remove_user_by_id(user_id)
            else:
                pass
        # show the updated list
        self.show_user_info()

    def add_cat(self):
        name = self.inv_man_frame.cat_entry.get().upper()
        success, message = database.add_category(name)
        if success:
            msgbox.show_success_message_box(message)
            self.category_data = database.fetch_categories()
            self.cat_dropdown.config(textvariable=self.var1, values=self.category_data)
            self.stock_dropdown.config(textvariable=self.var2, values=self.category_data)
        else:
            msgbox.show_error_message_box("Error", message)
        self.show_categories()

    def add_item(self):
        cat_name = self.inv_man_frame.cat_item_entry.get().strip().upper()
        cat_id = database.get_category_id_by_name(cat_name)
        if cat_id is not None:
            item_name = self.inv_man_frame.item_entry.get()
            success, message = database.add_item(cat_id, item_name)
            if success:
                msgbox.show_success_message_box(message)
                self.item_data = database.fetch_all_items(self.category_data)
            else:
                msgbox.show_error_message_box("Error", message)
        self.show_items()
        self.show_stock()

    def add_mac(self):
        pass

    def show_categories(self):
        self.delete_treeview_items(self.cat_treeview)
        # get the user data from database
        cat_data = database.fetch_categories()
        # insert all user data in the user Treeview
        for i, item in enumerate(cat_data, start=1):
            if i % 2 == 0:
                self.cat_treeview.insert("", "end", values=(f"{i}", f"{item}"), tags=('evenrow',))
            else:
                self.cat_treeview.insert("", "end", values=(f"{i}", f"{item}"), tags=('oddrow',))

    def remove_cat(self):
        # remove the selected category and update the treeview
        selected_item = self.cat_treeview.focus()
        if selected_item:
            item_values = self.cat_treeview.item(selected_item, 'values')
            # get the id of the user
            cat_id = database.get_category_id_by_name(item_values[1])
            if msgbox.confirm_remove_category():
                database.delete_category_by_id(cat_id)
            else:
                pass
        # show the updated list
        self.show_categories()

    def show_items(self, event=None):
        self.delete_treeview_items(self.item_treeview)
        selected_cat = self.cat_dropdown.get()
        # grab all the items from the category
        item_data = self.item_data[selected_cat]
        # insert all items in the item Treeview
        for i, item in enumerate(item_data, start=1):
            if i % 2 == 0:
                self.item_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[2]}"), tags=('evenrow',))
            else:
                self.item_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[2]}"), tags=('oddrow',))

    def remove_item(self):
        # remove the selected item and update the treeview
        selected_item = self.item_treeview.focus()
        if selected_item:
            item_values = self.item_treeview.item(selected_item, 'values')
            # get the id of the item
            item_id = item_values[0]
            if msgbox.confirm_remove_item():
                database.delete_item_by_id(item_id)
                self.item_data = database.fetch_all_items(self.category_data)
            else:
                pass
        # show the updated list
        self.show_items()

    def show_stock(self, event=None):
        self.delete_treeview_items(self.stock_treeview)
        selected_cat = self.stock_dropdown.get()
        # grab all the items from the category
        item_data = self.item_data[selected_cat]
        # insert all items in the item Treeview
        for i, item in enumerate(item_data, start=1):
            if i % 2 == 0:
                self.stock_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[2]}", f"{item[-1]}"), tags=('evenrow',))
            else:
                self.stock_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[2]}", f"{item[-1]}"), tags=('oddrow',))

    def on_select(self, event=None):
        # Get the selected item's data
        item = self.stock_treeview.focus()
        if item != '':
            item_data = self.stock_treeview.item(item, 'values')

            # Clear the label widget
            self.inv_man_frame.restock_item_name.config(text=item_data[2])
            self.inv_man_frame.restock_quantity_entry.delete(0, tk.END)

    def restock(self):
        item = self.stock_treeview.focus()
        item_data = self.stock_treeview.item(item, 'values')
        item_id = item_data[0]
        quantity = self.inv_man_frame.restock_quantity_entry.get()

        if int(quantity) > 0:
            placement_info = database.get_rack_and_position((item_id, ))
            try:
                data = tuple(placement_info.values())[0]
                rack, pos_label = data
                self.open_item(client=self.mqtt_client, topic=rack, pos_label=pos_label)
            
                if msgbox.confirm_item_restock():
                    database.restock_item(item_id, int(quantity))
                    self.item_data = database.fetch_all_items(self.category_data)
                    self.close_item(client=self.mqtt_client, topic=rack, pos_label=pos_label)
                    self.show_stock()
                else:
                    pass
            
            except Exception as e:
                msgbox.show_error_message_box('Error', "Item not placed in the rack")

            finally:
                pass
        
    def add_rack(self):
        name = self.ip_man_frame.rack_entry.get()
        success, message = database.add_rack(name)
        if success:
            msgbox.show_success_message_box(message)
            self.rack_details = database.get_all_racks()
            self.racks = [name for id, name in database.get_all_racks()]
            self.rack_dropdown.config(textvariable=self.rack, values=self.racks)
            self.rack_details = database.get_all_racks()
            self.racks = [name for id, name in database.get_all_racks()]
            self.show_all_racks()
        else:
            msgbox.show_error_message_box("Error", message)

    def show_ip_items(self):
        self.delete_treeview_items(self.ip_item_treeview)
        # grab all the items that are not placed
        item_data = database.get_items_not_in_placement()
        # insert all items in the item Treeview
        for i, item in enumerate(item_data, start=1):
            if i % 2 == 0:
                self.ip_item_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[1]}", f"{item[2]}"), tags=('evenrow',))
            else:
                self.ip_item_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[1]}", f"{item[2]}"), tags=('oddrow',))

    def place_item(self):
        # check for integrity and place it (update in the database)
        rack = self.rack.get()
        label = self.row.get()+self.col.get()
        for id, name in self.rack_details:
            if name == rack:
                rack_id = id
        item = self.ip_item_treeview.focus()
        if item != '':
            item_data = self.ip_item_treeview.item(item, 'values')
            item_id = item_data[0]
            # write the placement data to the database
            success, message = database.add_rack_position_and_item_placement(rack_id, label.strip(), item_id)
            if success:
                msgbox.show_success_message_box(message)
            else:
                msgbox.show_error_message_box("Error", message)
            # show the updated list
        self.show_ip_items()
        
    def on_ip_select(self, event=None):
        # display the name of the item in the item label
        item = self.ip_item_treeview.focus()
        if item != '':
            item_data = self.ip_item_treeview.item(item, 'values')
            print(item_data)
            self.ip_item_name.config(text=item_data[-1].strip())

    def open_item(self, client, topic, pos_label):
        """
        Opens an item by sending an MQTT message.

        Args:
            client: The MQTT client used for publishing.
            topic: The topic to which the message will be published.
            pos_label: The position label of the item to be opened.
        """
        open_message = f"('{pos_label}', 1)"
        handle_publish(client=client, topic=f"smart_vault/{topic}", message=open_message)

    def close_item(self, client, topic, pos_label):
        """
        Closes an item by sending an MQTT message.

        Args:
            client: The MQTT client used for publishing.
            topic: The topic to which the message will be published.
            pos_label: The position label of the item to be closed.
        """
        close_message = f"('{pos_label}', 0)"
        handle_publish(client=client, topic=f"smart_vault/{topic}", message=close_message)

    def show_all_racks(self):
        self.delete_treeview_items(self.rack_treeview)
        # insert all rack data in the rack Treeview
        for i, item in enumerate(self.rack_details, start=1):
            if i % 2 == 0:
                self.rack_treeview.insert("", "end", values=(f"{i}", f"{item[0]}", f"{item[1]}"), tags=('evenrow',))
            else:
                self.rack_treeview.insert("", "end", values=(f"{i}", f"{item[0]}", f"{item[1]}"), tags=('oddrow',))

    def remove_rack(self):
        # remove the selected item and update the treeview
        selected_item = self.rack_treeview.focus()
        if selected_item:
            item_values = self.rack_treeview.item(selected_item, 'values')
            print(item_values)
            # get the id of the item
            rack_id = item_values[1]
            if msgbox.confirm_remove_rack():
                database.delete_rack_by_id(rack_id)
                self.rack_details = database.get_all_racks()
                self.racks = [name for id, name in database.get_all_racks()]
            else:
                pass
        # show the updated list
        self.show_all_racks()

    def show_item_placement_data(self, event=None):
        self.delete_treeview_items(self.item_placement_treeview)
        selected_rack = self.rack_dropdown.get()
        # grab all the items from the category
        for id, rack_name in self.rack_details:
            if rack_name == selected_rack:
                rack_id = id
                break 
        placement_data = database.get_items_in_rack(rack_id)
        # insert all items in the item Treeview
        for i, data in enumerate(placement_data, start=1):
            if i % 2 == 0:
                self.item_placement_treeview.insert("", "end", values=(f"{i}", f"{data[0]}", f"{data[1]}", f"{data[2]}", f"{data[3]}", f"{data[4]}", f"{data[5]}"), tags=('evenrow',))
            else:
                self.item_placement_treeview.insert("", "end", values=(f"{i}", f"{data[0]}", f"{data[1]}", f"{data[2]}", f"{data[3]}", f"{data[4]}", f"{data[5]}"), tags=('oddrow',))

    def remove_item_placement(self):
        # remove the selected item and update the treeview
        selected_item = self.item_placement_treeview.focus()
        if selected_item:
            item_values = self.item_placement_treeview.item(selected_item, 'values')
            print(item_values)
            # get the id of the item
            ip_id = item_values[-1]
            if msgbox.confirm_remove_ip():
                database.delete_item_placement_by_id(ip_id)
            else:
                pass
        # show the updated list
        self.show_item_placement_data()

    def read_card(self):
        # Creating and starting the RFID scanning thread
        scan_thread = threading.Thread(target=scan_rfid, args=(card_data,))
        scan_thread.start()
        try:
            result = card_data.get_nowait()
            if result[0] == 'Success':
                uid = result[1]
                self.card_id.config(text=uid)
            else: 
                pass
        except Exception as e:
            print(e)

    def send_msg(self):
        rack = self.rack_dropdown2.get()
        row = self.row_dropdown2.get()
        col = self.col_dropdown2.get()
        action = self.action_dropdown.get()

        if action == 'OPEN':
            self.open_item(client=self.mqtt_client, topic=rack, pos_label=row+col)
        elif action == 'CLOSE':
            self.close_item(client=self.mqtt_client, topic=rack, pos_label=row+col)


# If this file is run directly for testing purposes
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(SCREEN_SIZE)
    style = ttk.Style(root)

    # build the path to the theme file
    theme_path = os.path.join("/home/pi/Python/smart_tool_vault", "theme", "forest-light.tcl")

    root.tk.call("source", theme_path)
    style.theme_use("forest-light")
    
    # Create an instance of EmployeePanel and pack it into the root window
    main_frame = AdminPanel(root)
    main_frame.pack()

    main_frame.update_datetime()
    
    root.mainloop()