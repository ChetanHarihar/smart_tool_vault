from settings.config import *
from gui_components.widgets import msgbox
from gui_components.widgets.treeview import TreeView
from gui_components.widgets.topbar import TopBar
from gui_components.frames.admin_panel_frames import *
from services.mqtt_functions import connect_mqtt, handle_publish
from services import database


class AdminPanel(tk.Frame):
    def __init__(self, user_id, username, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(width=1024, height=576)
        self.root = master
        self.user_id = user_id
        self.user_name = username
        self.category_data = database.fetch_categories(db_path=DATABASE_PATH)
        self.item_data = database.fetch_all_items(self.category_data, db_path=DATABASE_PATH)
        self.machine_data = database.get_all_machines(db_path=DATABASE_PATH)
        self.rack_details = database.get_all_racks(db_path=DATABASE_PATH)
        self.racks = [name for id, name in database.get_all_racks(db_path=DATABASE_PATH)]
        self.rows = ['A', 'B', 'C', 'D', 'E']
        self.cols = ['1', '2', '3', '4', '5', '6']
        self.data_to_log = None
        # Connect ot MQTT Server
        self.mqtt_client = connect_mqtt(mqtt_server=MQTT_SERVER, mqtt_port=MQTT_PORT)
        self.init_ui()

    def init_ui(self):
        # ----- Create and pack topbar widget -----
        self.top_bar = TopBar(self)
        self.top_bar.pack(padx=(2.5, 2.5), pady=(5, 2.5))

        # Configure user info label 
        self.top_bar.user_info_label.config(text=f"User: {self.user_name}")

        # Configure machine info label
        self.top_bar.machine_info_label.config(text="")

        # ----- Create and pack main container frame -----
        main_container = tk.Frame(self, width=1024, height=526)
        main_container.pack_propagate(False)
        main_container.pack(padx=(2.5, 2.5), pady=(2.5,5))

        # ----- Create sidebar widget -----
        side_menu = tk.Frame(main_container, width=200, height=526, bg="#00563B")
        side_menu.pack_propagate(False)
        side_menu.grid(row=0, column=0)

        # Container to hold page buttons
        page_btns_container = tk.Frame(side_menu, bg="#00563B")
        page_btns_container.pack(pady=(180, 0))

        # ----- Create Page Buttons -----

        user_man_btn = tk.Button(page_btns_container, text="User Management", bg="#00563B", fg="white", relief='flat', highlightbackground="#00563B", width=200, command=lambda: self.switch_frame(self.user_man_frame))
        user_man_btn.pack()

        inv_man_btn = tk.Button(page_btns_container, text="Inventory Management", bg="#00563B", fg="white", relief='flat', highlightbackground="#00563B", width=200, command=lambda: self.switch_frame(self.inv_man_frame))
        inv_man_btn.pack()

        ip_man_btn = tk.Button(page_btns_container, text="Item Placement Management", bg="#00563B", fg="white", relief='flat', highlightbackground="#00563B", width=200, command=lambda: self.switch_frame(self.ip_man_frame))
        ip_man_btn.pack()

        ts_btn = tk.Button(page_btns_container, text="Trouble Shooting", bg="#00563B", fg="white", relief='flat', highlightbackground="#00563B", width=200, command=lambda: self.switch_frame(self.ts_frame))
        ts_btn.pack()

        # ----- Create frame to display page content -----
        self.page_container = tk.Frame(main_container, bg="#E8E9EB", width=824, height=526)
        self.page_container.pack_propagate(False)
        self.page_container.grid(row=0, column=1)

        # ----- User Management page -----
        self.user_man_frame = UserManagement(self.page_container)
        self.user_man_frame.add_btn.config(command=self.add_user)
        self.user_man_frame.pack()

        self.view_user_label_frame = tk.LabelFrame(self.user_man_frame, text="View Users")
        self.view_user_label_frame.pack(pady=(5, 0))

        # ----- Create tree view to display the list of users -----

        # Create a frame to pack the cart treeview
        user_treeview_frame = tk.Frame(self.view_user_label_frame, width=814, height=270)
        user_treeview_frame.pack_propagate(False)
        user_treeview_frame.pack()

        self.user_treeview = TreeView(user_treeview_frame, height=7)

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

        self.show_users()

        # Remove user button
        self.remove_btn = tk.Button(self.user_man_frame, text="Remove", command=self.remove_user)
        self.remove_btn.pack(pady=(10, 0))


        # ----- Inventory Management page -----
        self.inv_man_frame = InventoryManagement(self.page_container)

        # Configure button commands
        self.inv_man_frame.cat_add_btn.config(command=self.add_category)
        self.inv_man_frame.item_add_btn.config(command=self.add_item)
        self.inv_man_frame.mac_add_btn.config(command=self.add_machine)

        # ----- Category view -----
        category_treeview_frame = tk.Frame(self.inv_man_frame.cat_view_frame)
        category_treeview_frame.pack()

        # Category treeview
        self.category_treeview = TreeView(category_treeview_frame, height=14)

        # Create columns
        self.category_treeview["columns"] = ("Sl.no", "Categories")
        self.category_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the cart_tree column
        self.category_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.category_treeview.column("Categories", width=250, anchor=tk.CENTER)

        # Create headings
        self.category_treeview.heading("Sl.no", text="Sl.no")
        self.category_treeview.heading("Categories", text="Categories", anchor=tk.CENTER)

        self.show_categories()

        # Category remove button
        self.category_remove_btn = tk.Button(self.inv_man_frame.cat_view_frame, text="Remove", command=self.remove_category)
        self.category_remove_btn.pack(pady=(10,0))

        # ----- Item view -----
        # Create dropdown menu to select category
        self.item_view_var = tk.StringVar(self.inv_man_frame.item_view_frame)
        self.item_view_var.set(self.category_data[0])  # Set the default option

        self.item_view_category_dropdown = ttk.Combobox(self.inv_man_frame.item_view_frame, textvariable=self.item_view_var, values=self.category_data)
        self.item_view_category_dropdown.pack(pady=(0, 5))

        self.item_view_category_dropdown.bind("<<ComboboxSelected>>", self.show_items)

        item_treeview_frame = tk.Frame(self.inv_man_frame.item_view_frame)
        item_treeview_frame.pack(pady=(0, 5))

        # Item treeview
        self.item_treeview = TreeView(item_treeview_frame, height=12)

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

        # Item remove button
        self.item_remove_btn = tk.Button(self.inv_man_frame.item_view_frame, text="Remove", command=self.remove_item)
        self.item_remove_btn.pack(pady=(10,0))

        # ----- Machine view -----
        machine_treeview_frame = tk.Frame(self.inv_man_frame.mac_view_frame)
        machine_treeview_frame.pack(pady=(0, 5))

        # Machine treeview
        self.machine_treeview = TreeView(machine_treeview_frame, height=14)

        # Create columns
        self.machine_treeview["columns"] = ("id", "Sl.no", "Machine Name", "Machine Code")
        self.machine_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the cart_tree column
        self.machine_treeview.column("id", width=0, stretch=tk.NO)  
        self.machine_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.machine_treeview.column("Machine Name", width=200, anchor=tk.CENTER)
        self.machine_treeview.column("Machine Code", width=150, anchor=tk.CENTER)

        # Create headings
        self.machine_treeview.heading("id", text="id")
        self.machine_treeview.heading("Sl.no", text="Sl.no")
        self.machine_treeview.heading("Machine Name", text="Machine Name", anchor=tk.CENTER)
        self.machine_treeview.heading("Machine Code", text="Machine Code", anchor=tk.CENTER)

        self.show_machines()

        # Machine remove button
        self.machine_remove_btn = tk.Button(self.inv_man_frame.mac_view_frame, text="Remove", command=self.remove_machine)
        self.machine_remove_btn.pack(pady=(10,0))


        # ----- Stock view -----
        # Create dropdown menu to select category
        self.stock_view_var = tk.StringVar(self.inv_man_frame.stock_main_frame)
        self.stock_view_var.set(self.category_data[0])  # Set the default option

        self.stock_view_category_dropdown = ttk.Combobox(self.inv_man_frame.stock_main_frame, textvariable=self.stock_view_var, values=self.category_data)
        self.stock_view_category_dropdown.pack()

        self.stock_view_category_dropdown.bind("<<ComboboxSelected>>", self.show_stock)

        # Configure restock button
        self.inv_man_frame.restock_btn.config(command=self.restock_item)

        stock_treeview_frame = tk.Frame(self.inv_man_frame.stock_main_frame)
        stock_treeview_frame.pack(pady=(5,0))

        # Stock treeview
        self.stock_treeview = TreeView(stock_treeview_frame, height=13)

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
        self.stock_treeview.bind('<<TreeviewSelect>>', self.show_item_on_stock_select)

        self.show_stock()


        # ----- Create and pack item placement management page -----
        self.ip_man_frame = ItemPlacementManagement(self.page_container)

        # Configure add rack button
        self.ip_man_frame.rack_add_btn.config(command=self.add_rack)

        ip_treeview_frame = tk.Frame(self.ip_man_frame.ip_label_frame)
        ip_treeview_frame.pack(pady=(5,0))

        # Item placement treeview
        self.ip_treeview = TreeView(ip_treeview_frame, height=4)

        # Create columns
        self.ip_treeview["columns"] = ("id", "Sl.no", "Category", "Items")
        self.ip_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the cart_tree column
        self.ip_treeview.column("id", width=0, stretch=tk.NO)  
        self.ip_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.ip_treeview.column("Category", width=200, anchor=tk.CENTER)
        self.ip_treeview.column("Items", width=400, anchor=tk.CENTER)

        # Create headings
        self.ip_treeview.heading("id", text="id")
        self.ip_treeview.heading("Sl.no", text="Sl.no")
        self.ip_treeview.heading("Category", text="Category")
        self.ip_treeview.heading("Items", text="Items", anchor=tk.CENTER)

        # Bind the select event to the on_select function
        self.ip_treeview.bind('<<TreeviewSelect>>', self.on_ip_select)

        self.show_unplaced_items()

        # ----- Container to store widgets -----
        ip_widget_frame = tk.Frame(self.ip_man_frame.ip_label_frame)
        ip_widget_frame.pack(pady=(10,0))

        tk.Label(ip_widget_frame, text="Item Name:").pack(side=tk.LEFT, padx=(5))

        self.ip_item_name = tk.Label(ip_widget_frame, text="", width=30, anchor='w')
        self.ip_item_name.pack(side=tk.LEFT, padx=(5))

        # ----- Container to store dropdown widgets -----
        ip_dropdown_widget_frame = tk.Frame(self.ip_man_frame.ip_label_frame)
        ip_dropdown_widget_frame.pack(pady=(15))

        # Dropdown to select rack, row and column

        # Create dropdown menu to select rack
        self.ip_rack_var = tk.StringVar(ip_dropdown_widget_frame)
        self.ip_rack_var.set(self.racks[0])  # Set the default option

        tk.Label(ip_dropdown_widget_frame, text='Select Rack: ').pack(side=tk.LEFT, padx=(2))

        self.ip_rack_dropdown = ttk.Combobox(ip_dropdown_widget_frame, textvariable=self.ip_rack_var, values=self.racks)
        self.ip_rack_dropdown.pack(side=tk.LEFT, padx=(2))

        # Create dropdown menu to select row
        self.ip_row_var = tk.StringVar(ip_dropdown_widget_frame)
        self.ip_row_var.set(self.rows[0])  # Set the default option

        tk.Label(ip_dropdown_widget_frame, text='Select Row: ').pack(side=tk.LEFT, padx=(2))

        self.ip_row_dropdown = ttk.Combobox(ip_dropdown_widget_frame, textvariable=self.ip_row_var, values=self.rows, width=5)
        self.ip_row_dropdown.pack(side=tk.LEFT, padx=(2))

        # Create dropdown menu to select column
        self.ip_col_var = tk.StringVar(ip_dropdown_widget_frame)
        self.ip_col_var.set(self.cols[0])  # Set the default option

        tk.Label(ip_dropdown_widget_frame, text='Select Column: ').pack(side=tk.LEFT, padx=(2))

        self.ip_col_dropdown = ttk.Combobox(ip_dropdown_widget_frame, textvariable=self.ip_col_var, values=self.cols, width=5)
        self.ip_col_dropdown.pack(side=tk.LEFT, padx=(2))

        self.place_btn = tk.Button(self.ip_man_frame.ip_label_frame, text="Place", command=self.place_item)
        self.place_btn.pack(pady=(10,0))


        # ----- View racks frame -----
        rack_treeview_frame = tk.Frame(self.ip_man_frame.rack_view_frame)
        rack_treeview_frame.pack()

        self.rack_treeview = TreeView(rack_treeview_frame, height=15)

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

        # remove rack button
        self.rack_remove_btn = tk.Button(self.ip_man_frame.rack_view_frame, text="Remove", command=self.remove_rack)
        self.rack_remove_btn.pack(pady=(10,0))


        # ----- View item placement frame -----
        # create dropdown menu to select rack
        self.vp_rack_var = tk.StringVar(self.ip_man_frame.rack_view_frame)
        self.vp_rack_var.set(self.racks[0])  # Set the default option

        # Create the dropdown menu
        self.vp_rack_dropdown = ttk.Combobox(self.ip_man_frame.placement_view_frame, textvariable=self.vp_rack_var, values=self.racks)
        self.vp_rack_dropdown.pack()

        self.vp_rack_dropdown.bind("<<ComboboxSelected>>", self.show_item_placement_data)

        view_ip_treeview_frame = tk.Frame(self.ip_man_frame.placement_view_frame)
        view_ip_treeview_frame.pack()

        self.view_ip_treeview = TreeView(view_ip_treeview_frame, height=13)

        # Create columns
        self.view_ip_treeview["columns"] = ("Sl.no", "Category", "Item", "Quantity", "rp.id", "Position", "ip.id")
        self.view_ip_treeview.column("#0", width=0, stretch=tk.NO)   
        self.view_ip_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.view_ip_treeview.column("Category", width=150, anchor=tk.CENTER)
        self.view_ip_treeview.column("Item", width=350, anchor=tk.CENTER)
        self.view_ip_treeview.column("Quantity", width=70, anchor=tk.CENTER)
        self.view_ip_treeview.column("rp.id", width=0, stretch=tk.NO)  
        self.view_ip_treeview.column("Position", width=70, anchor=tk.CENTER)
        self.view_ip_treeview.column("ip.id", width=0, stretch=tk.NO) 

        # Create headings
        self.view_ip_treeview.heading("Sl.no", text="Sl.no")
        self.view_ip_treeview.heading("Category", text="Category", anchor=tk.CENTER)
        self.view_ip_treeview.heading("Item", text="Item", anchor=tk.CENTER)
        self.view_ip_treeview.heading("Quantity", text="Quantity", anchor=tk.CENTER)
        self.view_ip_treeview.heading("Position", text="Position", anchor=tk.CENTER)

        self.show_item_placement_data()

        # remove item placement button
        self.item_placement_remove_btn = tk.Button(self.ip_man_frame.placement_view_frame, text="Remove", command=self.remove_item_placement)
        self.item_placement_remove_btn.pack(pady=(10,0))


        # ----- Trouble Shooting page -----
        self.ts_frame = TroubleShooting(self.page_container)

        # ----- Read Card Page -----
        tk.Label(self.ts_frame.read_card, text="Place the card on the Reader").pack(pady=(30, 10))

        read_card_widget_container = tk.Frame(self.ts_frame.read_card)
        read_card_widget_container.pack()

        tk.Label(read_card_widget_container, text="Card ID:").grid(row=1, column=0, pady=(10))

        self.card_id = tk.Entry(read_card_widget_container, width=25)
        self.card_id.grid(row=1, column=1, pady=(10))
        self.card_id.focus()

        self.clear_id_btn = tk.Button(read_card_widget_container, text="Clear", command=self.clear_id_entry)
        self.clear_id_btn.grid(row=2, column=0, columnspan=2)

        # ----- Actaute Page -----
        tk.Label(self.ts_frame.actuate, text="Send Message: ").pack(pady=(30,10))

        actuate_widget_container = tk.Frame(self.ts_frame.actuate)
        actuate_widget_container.pack(pady=(10))

        # ----- Create dropdown to select rack, row and column -----
        
        # Create dropdown menu to select rack
        self.actuation_rack_var = tk.StringVar(actuate_widget_container)
        self.actuation_rack_var.set(self.racks[0])  # Set the default option

        tk.Label(actuate_widget_container, text='Select Rack: ').pack(side=tk.LEFT, padx=(2))

        self.actuation_rack_dropdown = ttk.Combobox(actuate_widget_container, textvariable=self.actuation_rack_var, values=self.racks)
        self.actuation_rack_dropdown.pack(side=tk.LEFT, padx=(2))

        # Create dropdown menu to select row
        self.actuation_row_var = tk.StringVar(actuate_widget_container)
        self.actuation_row_var.set(self.rows[0])  # Set the default option

        tk.Label(actuate_widget_container, text='Select Row: ').pack(side=tk.LEFT, padx=(2))

        self.actuation_row_dropdown = ttk.Combobox(actuate_widget_container, textvariable=self.actuation_row_var, values=self.rows, width=5)
        self.actuation_row_dropdown.pack(side=tk.LEFT, padx=(2))

        # Create dropdown menu to select column
        self.actuation_col_var = tk.StringVar(actuate_widget_container)
        self.actuation_col_var.set(self.cols[0])  # Set the default option

        tk.Label(actuate_widget_container, text='Select Column: ').pack(side=tk.LEFT, padx=(2))

        self.actuation_col_dropdown = ttk.Combobox(actuate_widget_container, textvariable=self.actuation_col_var, values=self.cols, width=5)
        self.actuation_col_dropdown.pack(side=tk.LEFT, padx=(2))

        # Create dropdown menu to select action
        self.actuation_action_var = tk.StringVar(actuate_widget_container)
        self.actuation_action_var.set('OPEN')  # Set the default option

        tk.Label(actuate_widget_container, text='Action: ').pack(side=tk.LEFT, padx=(2))

        self.actuation_action_dropdown = ttk.Combobox(actuate_widget_container, textvariable=self.actuation_action_var, values=['OPEN','CLOSE'], width=6)
        self.actuation_action_dropdown.pack(side=tk.LEFT, padx=(2))

        self.send_actuation_msg_btn = tk.Button(self.ts_frame.actuate, text="Send", command=self.send_actuation_msg)
        self.send_actuation_msg_btn.pack(pady=(10))

    def switch_frame(self, frame):
        for widget in self.page_container.winfo_children():
            widget.forget()
        frame.pack()

    def update_datetime(self):
        self.top_bar.update_datetime()

    def delete_treeview_items(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)

    def show_users(self):
        self.delete_treeview_items(self.user_treeview)
        # get the user data from database
        user_data = database.get_user_details(db_path=DATABASE_PATH)
        # insert all user data in the user Treeview
        for i, item in enumerate(user_data, start=1):
            if i % 2 == 0:
                self.user_treeview.insert("", "end", values=(f"{item[0]}", f"{item[1]}", f"{item[2]}", f"{'Admin 'if item[3] == 1 else 'Employee'}"), tags=('evenrow',))
            else:
                self.user_treeview.insert("", "end", values=(f"{item[0]}", f"{item[1]}", f"{item[2]}", f"{'Admin 'if item[3] == 1 else 'Employee'}"), tags=('oddrow',))

    def add_user(self):
        name = self.user_man_frame.name_entry.get().capitalize()
        uid = self.user_man_frame.uid_entry.get()
        role = self.user_man_frame.role_var.get()
        print("\nUser details:\n", f"Name: {name}, UID: {uid}, Role: {"Admin" if role == 1 else "Employee"}\n")
        self.user_details = [name, uid, role]
        # check for integrity and add the data to database
        success, message = database.add_user(self.user_details[0], self.user_details[1], self.user_details[2], db_path=DATABASE_PATH)
        if success:
            msgbox.show_success_message_box(message)
            # show the updated list
            self.show_users()
            self.user_man_frame.name_entry.delete(0, tk.END)
            self.user_man_frame.uid_entry.delete(0, tk.END)
        else:
            msgbox.show_error_message_box("Error", message)

    def remove_user(self):
        # remove the selected user and update the treeview
        selected_item = self.user_treeview.focus()
        if selected_item:
            item_values = self.user_treeview.item(selected_item, 'values')
            # get the id of the user
            user_id = item_values[0]
            if msgbox.confirm_remove_user():
                database.remove_user_by_id(user_id, db_path=DATABASE_PATH)
                # show the updated list
                self.show_users()
            else:
                pass

    def show_categories(self):
        self.delete_treeview_items(self.category_treeview)
        # insert all category data in the category Treeview
        for i, item in enumerate(self.category_data, start=1):
            if i % 2 == 0:
                self.category_treeview.insert("", "end", values=(f"{i}", f"{item}"), tags=('evenrow',))
            else:
                self.category_treeview.insert("", "end", values=(f"{i}", f"{item}"), tags=('oddrow',))

    def add_category(self):
        name = self.inv_man_frame.cat_entry.get().upper()
        min_stock = self.inv_man_frame.min_stock_entry.get()
        if name:
            if min_stock.isnumeric():
                success, message = database.add_category(name=name, min_stock=int(min_stock), db_path=DATABASE_PATH)
                if success:
                    msgbox.show_success_message_box(message)
                    self.category_data = database.fetch_categories(db_path=DATABASE_PATH)
                    self.item_view_category_dropdown.config(textvariable=self.item_view_var, values=self.category_data)
                    self.stock_view_category_dropdown.config(textvariable=self.stock_view_var, values=self.category_data)
                    # show the updated list
                    self.show_categories()
                    self.inv_man_frame.cat_entry.delete(0, tk.END)
                    self.inv_man_frame.min_stock_entry.delete(0, tk.END)
                else:
                    msgbox.show_error_message_box("Error", message)
            else:
                msgbox.show_error_message_box("Error", "Enter a valid number for Minimum stock.")
        else:
                msgbox.show_error_message_box("Error", "Enter a valid category name.")

    def remove_category(self):
        # remove the selected category and update the treeview
        selected_item = self.category_treeview.focus()
        if selected_item:
            item_values = self.category_treeview.item(selected_item, 'values')
            # get the category id
            cat_id = database.get_category_id_by_name(item_values[1], db_path=DATABASE_PATH)
            if msgbox.confirm_remove_category():
                result = database.delete_category_by_id(cat_id, db_path=DATABASE_PATH)
                # if Error the show error message
                if not result[0]:
                    msgbox.show_error_message_box(title="Error", message=result[1])
                    return
                self.category_data = database.fetch_categories(db_path=DATABASE_PATH)
                self.item_view_category_dropdown.config(textvariable=self.item_view_var, values=self.category_data)
                self.stock_view_category_dropdown.config(textvariable=self.stock_view_var, values=self.category_data)
                # show the updated list
                self.show_categories()
            else:
                pass

    def show_items(self, event=None):
        self.delete_treeview_items(self.item_treeview)
        selected_cat = self.item_view_category_dropdown.get()
        # grab all the items from the category
        item_data = self.item_data[selected_cat]
        # insert all items in the item Treeview
        for i, item in enumerate(item_data, start=1):
            if i % 2 == 0:
                self.item_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[2]}"), tags=('evenrow',))
            else:
                self.item_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[2]}"), tags=('oddrow',))

    def add_item(self):
        cat_name = self.inv_man_frame.cat_item_entry.get().strip().upper()
        cat_id = database.get_category_id_by_name(cat_name, db_path=DATABASE_PATH)
        print(cat_id)
        item_name = self.inv_man_frame.item_entry.get()
        if cat_id is not None:
            if item_name:
                success, message = database.add_item(cat_id, item_name, db_path=DATABASE_PATH)
                if success:
                    msgbox.show_success_message_box(message)
                    self.item_data = database.fetch_all_items(self.category_data, db_path=DATABASE_PATH)
                    # show the updated list
                    self.show_items()
                    self.show_stock()
                    self.show_unplaced_items()
                    self.inv_man_frame.cat_item_entry.delete(0, tk.END)
                    self.inv_man_frame.item_entry.delete(0, tk.END)
                else:
                    msgbox.show_error_message_box("Error", message)
            else:
                    msgbox.show_error_message_box("Error", "Invalid item name.\nEnter a valid item name.")
        else:
            msgbox.show_error_message_box("Error", "Invalid category name.\nSpecified category doesn't exists.")

    def remove_item(self):
        # remove the selected item and update the treeview
        selected_item = self.item_treeview.focus()
        if selected_item:
            item_values = self.item_treeview.item(selected_item, 'values')
            # get the id of the item
            item_id = item_values[0]
            if msgbox.confirm_remove_item():
                result = database.delete_item_by_id(item_id, db_path=DATABASE_PATH)
                # if Error the show error message
                if not result[0]:
                    msgbox.show_error_message_box(title="Error", message=result[1])
                    return
                self.item_data = database.fetch_all_items(self.category_data, db_path=DATABASE_PATH)
                # show the updated list
                self.show_items()
                self.show_stock()
                self.show_unplaced_items()
            else:
                pass

    def show_machines(self):
        self.delete_treeview_items(self.machine_treeview)
        # insert all machine data in the machine Treeview
        for i, item in enumerate(self.machine_data, start=1):
            if i % 2 == 0:
                self.machine_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[1]}", f"{item[2]}"), tags=('evenrow',))
            else:
                self.machine_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[1]}", f"{item[2]}"), tags=('oddrow',))

    def add_machine(self):
        mac_name = self.inv_man_frame.mac_name_entry.get().strip().upper()
        mac_code = self.inv_man_frame.mac_code_entry.get().strip().upper()
        if mac_name and mac_code:
            success, message = database.add_machine(mac_name, mac_code, db_path=DATABASE_PATH)
            if success:
                msgbox.show_success_message_box(message)
                self.machine_data = database.get_all_machines(db_path=DATABASE_PATH)
                # show the updated list
                self.show_machines()
                self.inv_man_frame.mac_name_entry.delete(0, tk.END)
                self.inv_man_frame.mac_code_entry.delete(0, tk.END)
            else:
                msgbox.show_error_message_box("Error", message)
        else:
                msgbox.show_error_message_box("Error", "Enter a valid Machine name and Machine code.")

    def remove_machine(self):
        # remove the selected machine and update the treeview
        selected_item = self.machine_treeview.focus()
        if selected_item:
            item_values = self.machine_treeview.item(selected_item, 'values')
            # get the id of the item
            machine_id = item_values[0]
            if msgbox.confirm_remove_item():
                database.delete_machine(machine_id, db_path=DATABASE_PATH)
                self.machine_data = database.get_all_machines(db_path=DATABASE_PATH)
                # show the updated list
                self.show_machines()
            else:
                pass

    def show_stock(self, event=None):
        self.delete_treeview_items(self.stock_treeview)
        selected_cat = self.stock_view_category_dropdown.get()
        # grab all the items from the category
        item_data = self.item_data[selected_cat]
        # insert all items in the item Treeview
        for i, item in enumerate(item_data, start=1):
            if i % 2 == 0:
                self.stock_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[2]}", f"{item[-1]}"), tags=('evenrow',))
            else:
                self.stock_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[2]}", f"{item[-1]}"), tags=('oddrow',))

    def show_item_on_stock_select(self, event=None):
        # Get the selected item's data
        item = self.stock_treeview.focus()
        if item != '':
            item_data = self.stock_treeview.item(item, 'values')

            # Clear the widgets and display the item data
            self.inv_man_frame.restock_item_name.config(text=item_data[2])
            self.inv_man_frame.restock_quantity_entry.delete(0, tk.END)

    def restock_item(self):
        selected_item = self.stock_treeview.focus()
        item_data = self.stock_treeview.item(selected_item, 'values')
        item_id = item_data[0]
        category = self.stock_view_category_dropdown.get()
        item = item_data[-2]
        quantity = self.inv_man_frame.restock_quantity_entry.get()

        if int(quantity) > 0:
            placement_info = database.get_rack_and_position(item_ids=(item_id, ), db_path=DATABASE_PATH)
            try:
                data = tuple(placement_info.values())[0]
                rack, pos_label = data
                print(f"Open msg: Topic={rack}, pos_label={pos_label}.")
                self.open_item(client=self.mqtt_client, sub_topic=rack, pos_label=pos_label)

                if msgbox.confirm_item_restock():
                    database.restock_item(item_id, int(quantity), db_path=DATABASE_PATH)
                    self.item_data = database.fetch_all_items(self.category_data, db_path=DATABASE_PATH)
                    self.data_to_log = [self.user_name, category, item, ' ', ' ', str(quantity)]
                    # log data
                    self.close_item(client=self.mqtt_client, sub_topic=rack, pos_label=pos_label)
                    print(f"Close msg: Topic={rack}, pos_label={pos_label}.")
                    self.show_stock()
            
            except Exception as e:
                print(e)
                msgbox.show_error_message_box('Error', "Item not placed in the rack")

            finally:
                print(f"Close msg: Topic={rack}, pos_label={pos_label}.")

    def show_all_racks(self):
        self.delete_treeview_items(self.rack_treeview)
        # insert all rack data in the rack Treeview
        for i, item in enumerate(self.rack_details, start=1):
            if i % 2 == 0:
                self.rack_treeview.insert("", "end", values=(f"{i}", f"{item[0]}", f"{item[1]}"), tags=('evenrow',))
            else:
                self.rack_treeview.insert("", "end", values=(f"{i}", f"{item[0]}", f"{item[1]}"), tags=('oddrow',))

    def add_rack(self):
        name = self.ip_man_frame.rack_entry.get()
        if name:
            success, message = database.add_rack(name, db_path=DATABASE_PATH)
            if success:
                msgbox.show_success_message_box(message)
                self.rack_details = database.get_all_racks(db_path=DATABASE_PATH)
                self.racks = [name for id, name in database.get_all_racks(db_path=DATABASE_PATH)]
                self.ip_rack_dropdown.config(textvariable=self.ip_rack_var, values=self.racks)
                self.vp_rack_dropdown.config(textvariable=self.vp_rack_var, values=self.racks)
                # show the updated list
                self.show_all_racks()
                self.ip_man_frame.rack_entry.delete(0, tk.END)
            else:
                msgbox.show_error_message_box("Error", message)
        else:
                msgbox.show_error_message_box("Error", "Enter a valid rack name.")

    def remove_rack(self):
        # remove the selected rack and update the treeview
        selected_item = self.rack_treeview.focus()
        if selected_item:
            item_values = self.rack_treeview.item(selected_item, 'values')
            # get the id of the rack
            rack_id = item_values[1]
            if msgbox.confirm_remove_rack():
                result = database.delete_rack_by_id(rack_id, db_path=DATABASE_PATH)
                # if Error the show error message
                if not result[0]:
                    msgbox.show_error_message_box(title="Error", message=result[1])
                    return
                self.rack_details = database.get_all_racks(db_path=DATABASE_PATH)
                self.racks = [name for id, name in database.get_all_racks(db_path=DATABASE_PATH)]
                self.ip_rack_dropdown.config(textvariable=self.ip_rack_var, values=self.racks)
                self.vp_rack_dropdown.config(textvariable=self.vp_rack_var, values=self.racks)
                # show the updated list
                self.show_all_racks()
            else:
                pass

    def show_unplaced_items(self):
        self.delete_treeview_items(self.ip_treeview)
        # grab all the items that are not placed
        item_data = database.get_items_not_in_placement(db_path=DATABASE_PATH)
        # insert all items in the item Treeview
        for i, item in enumerate(item_data, start=1):
            if i % 2 == 0:
                self.ip_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[1]}", f"{item[2]}"), tags=('evenrow',))
            else:
                self.ip_treeview.insert("", "end", values=(f"{item[0]}", f"{i}", f"{item[1]}", f"{item[2]}"), tags=('oddrow',))

    def on_ip_select(self, event=None):
        # display the name of the item in the item label
        item = self.ip_treeview.focus()
        if item != '':
            item_data = self.ip_treeview.item(item, 'values')
            print(item_data)
            self.ip_item_name.config(text=item_data[-1].strip())

    def place_item(self):
        # check for integrity and place it (update in the database)
        rack = self.ip_rack_dropdown.get()
        label = self.ip_row_dropdown.get() + self.ip_col_dropdown.get()
        for id, name in self.rack_details:
            if name == rack:
                rack_id = id
        item = self.ip_treeview.focus()
        if item != '':
            item_data = self.ip_treeview.item(item, 'values')
            item_id = item_data[0]
            # write the placement data to the database
            success, message = database.add_rack_position_and_item_placement(rack_id, label.strip(), item_id, db_path=DATABASE_PATH)
            if success:
                msgbox.show_success_message_box(message)
                # show the updated list
                self.show_unplaced_items()
                self.show_item_placement_data()
            else:
                msgbox.show_error_message_box("Error", message)

    def show_item_placement_data(self, event=None):
        self.delete_treeview_items(self.view_ip_treeview)
        selected_rack = self.vp_rack_dropdown.get()
        # grab all the items from the category
        for id, rack_name in self.rack_details:
            if rack_name == selected_rack:
                rack_id = id
                break 
        placement_data = database.get_items_in_rack(rack_id, db_path=DATABASE_PATH)
        # insert all items in the treeview
        for i, data in enumerate(placement_data, start=1):
            if i % 2 == 0:
                self.view_ip_treeview.insert("", "end", values=(f"{i}", f"{data[0]}", f"{data[1]}", f"{data[2]}", f"{data[3]}", f"{data[4]}", f"{data[5]}"), tags=('evenrow',))
            else:
                self.view_ip_treeview.insert("", "end", values=(f"{i}", f"{data[0]}", f"{data[1]}", f"{data[2]}", f"{data[3]}", f"{data[4]}", f"{data[5]}"), tags=('oddrow',))

    def remove_item_placement(self):
        # remove the selected item and update the treeview
        selected_item = self.view_ip_treeview.focus()
        if selected_item:
            item_values = self.view_ip_treeview.item(selected_item, 'values')
            print(item_values)
            # get the id of the item
            ip_id = item_values[-1]
            if msgbox.confirm_remove_ip():
                database.delete_item_placement_by_id(ip_id, db_path=DATABASE_PATH)
                # show the updated list
                self.show_item_placement_data()
                self.show_unplaced_items()
            else:
                pass

    def open_item(self, client, sub_topic, pos_label):
        """
        Opens an item by sending an MQTT message.

        Args:
            client: The MQTT client used for publishing.
            topic: The topic to which the message will be published.
            pos_label: The position label of the item to be opened.
        """
        open_message = f"('{pos_label}', 1)"
        handle_publish(client=client, topic=f"{BASE_TOPIC}/{sub_topic}", message=open_message)

    def close_item(self, client, sub_topic, pos_label):
        """
        Closes an item by sending an MQTT message.

        Args:
            client: The MQTT client used for publishing.
            topic: The topic to which the message will be published.
            pos_label: The position label of the item to be closed.
        """
        close_message = f"('{pos_label}', 0)"
        handle_publish(client=client, topic=f"{BASE_TOPIC}/{sub_topic}", message=close_message)

    def clear_id_entry(self):
        self.card_id.delete(0, tk.END)

    def send_actuation_msg(self):
        rack = self.actuation_rack_dropdown.get()
        row = self.actuation_row_dropdown.get()
        col = self.actuation_col_dropdown.get()
        action = self.actuation_action_dropdown.get()

        print("\nActuation message sent")
        print("topic: ", rack)
        print("message: ", f"('{row}{col}', {1 if action == 'OPEN' else 0})\n")

        if action == 'OPEN':
            pass
            self.open_item(client=self.mqtt_client, sub_topic=rack, pos_label=row+col)
        elif action == 'CLOSE':
            pass
            self.close_item(client=self.mqtt_client, sub_topic=rack, pos_label=row+col)


# If this file is run directly for testing purposes
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{SCREEN_SIZE[0]}x{SCREEN_SIZE[1]}")
    style = ttk.Style(root)

    # build the path to the theme file
    theme_path = os.path.join(BASE_DIR, "theme", "forest-light.tcl")

    root.tk.call("source", theme_path)
    style.theme_use("forest-light")
    
    # Create an instance of AdminPanel and pack it into the root window
    frame = AdminPanel(master=root, user_id="1234", username="Chetan")
    frame.pack()

    frame.update_datetime()
    
    root.mainloop()