from settings.config import *
from gui_components.widgets.treeview import TreeView
from gui_components.widgets.topbar import TopBar
from services.mqtt_functions import connect_mqtt, handle_publish
from gui_components.widgets import msgbox
from services import database


class EmployeePanel(tk.Frame):
    def __init__(self, user_id, username, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(width=1024, height=576)
        self.root = master
        self.top_bar = TopBar(self)  # create topbar widget
        self.machine_data = database.get_all_machines(db_path=DATABASE_PATH)
        self.user_id = user_id
        self.user_name = username
        self.machine_code = None
        self.machine_name = None
        self.category_data = database.fetch_categories(db_path=DATABASE_PATH)
        self.item_data = database.fetch_all_items(categories=self.category_data, db_path=DATABASE_PATH)
        self.cart = []
        self.pickup_data = None
        self.placement_info = None
        self.session_generator = None
        self.checkboxes = []  # List to hold checkbox widgets
        self.checkbox_vars = []  # List to hold the variables associated with checkboxes
        self.current_index = 0
        self.current_command = None
        self.data_to_log = None
        self.update_item_data = None
        # Connect ot MQTT Server
        # self.mqtt_client = connect_mqtt(mqtt_server=MQTT_SERVER, mqtt_port=MQTT_PORT)   # Connect ot MQTT Server
        self.select_machine_frame()

    def select_machine_frame(self):
        # ----- Select Machine frame -----
        machine_treeview_frame = tk.Frame(self)
        machine_treeview_frame.pack(pady=(10,0))

        tk.Label(machine_treeview_frame, text="Select Machine", font=('times new roman', 12, 'bold')).pack(pady=(10,10))

        # Machine treeview
        self.machine_treeview = TreeView(machine_treeview_frame, height=14)

        # Create columns
        self.machine_treeview["columns"] = ("Sl.no", "id", "Machine Name", "Machine Code")
        self.machine_treeview.column("#0", width=0, stretch=tk.NO)
        self.machine_treeview.column("Sl.no", width=40, anchor=tk.CENTER)
        self.machine_treeview.column("id", width=0, stretch=tk.NO)
        self.machine_treeview.column("Machine Name", width=200, anchor=tk.CENTER)
        self.machine_treeview.column("Machine Code", width=200, anchor=tk.CENTER)

        # Create headings
        self.machine_treeview.heading("Sl.no", text="Sl.no")
        self.machine_treeview.heading("id", text="id", anchor=tk.CENTER)
        self.machine_treeview.heading("Machine Name", text="Machine Name", anchor=tk.CENTER)
        self.machine_treeview.heading("Machine Code", text="Machine Code", anchor=tk.CENTER)
    
        # Inserting machine data in the treeview
        for i, machine in enumerate(self.machine_data, start=1):
            if i % 2 == 0:
                self.machine_treeview.insert('', tk.END, values=(f'{i}', f'{machine[0]}', f'{machine[1]}', f'{machine[2]}'), tags=('evenrow',))
            else:
                self.machine_treeview.insert('', tk.END, values=(f'{i}', f'{machine[0]}', f'{machine[1]}', f'{machine[2]}'), tags=('oddrow',))

        # Machine select button
        self.machine_select_btn = tk.Button(self, text="Select", command=self.item_selection_ui, state='disabled')
        self.machine_select_btn.pack(pady=(20,0))

        self.machine_treeview.bind('<ButtonRelease-1>', self.on_machine_select)

    def item_selection_ui(self):
        # Clear the frame and display the item selection UI
        for widget in self.winfo_children():
            if widget != self.top_bar:  # if widget is topbar keep it
                widget.destroy()

        # Pack topbar frame
        self.top_bar.pack(padx=(2.5, 2.5), pady=(5,2.5))

        # Configure user info label
        self.top_bar.user_info_label.config(text=f"User: {self.user_name}")

        # Configure machine info label
        self.top_bar.machine_info_label.config(text=f"Machine: {self.machine_code}")

        # ----- Create and pack main frame (contains item selection frame and cart frame) -----
        self.main_frame = tk.Frame(self, width=1024, height=526)
        self.main_frame.pack_propagate(False)
        self.main_frame.pack(padx=(2.5, 2.5), pady=(2.5, 5))

        # Create a frame to display categories and items 
        container_frame = tk.Frame(self.main_frame, width=512, height=526, borderwidth=2, relief="groove", bg="white")
        container_frame.pack_propagate(False)
        container_frame.pack(side=tk.LEFT, padx=(0, 1.5))

        # Button frame
        selection_btn_frame = tk.Frame(container_frame)
        selection_btn_frame.pack()

        # Frame for housing labels and treeview frame
        self.selection_frame = tk.Frame(container_frame)
        self.selection_frame.pack()

        # ----- Category frame to display categories -----
        self.category_frame = tk.Frame(self.selection_frame)
        self.category_frame.pack()

        tk.Label(self.category_frame, text="Categories", font=("Arial", 12, 'bold')).pack(pady=(5, 5))

        # Create Category treeview
        self.category_treeview = TreeView(self.category_frame, show="tree", height=14)

        # Create columns
        self.category_treeview["columns"] = ("Category")
        self.category_treeview.column("#0", width=0, stretch=tk.NO)
        self.category_treeview.column("Category", width=440, anchor=tk.CENTER)
    
        # Inserting categories in the Treeview
        for i, category in enumerate(self.category_data, start=1):
            if i % 2 == 0:
                self.category_treeview.insert('', tk.END, values=(category, ), tags=('evenrow',))
            else:
                self.category_treeview.insert('', tk.END, values=(category, ), tags=('oddrow',))

        self.category_treeview.bind('<ButtonRelease>', self.category_selected)

        # ----- Item frame to display items -----
        self.item_frame = tk.Frame(self.selection_frame)

        tk.Label(self.item_frame, text="Items", font=("Arial", 12, 'bold')).pack(pady=(5, 5))

        # Create Item treeview
        self.item_treeview = TreeView(self.item_frame, height=13)

        # Create columns
        self.item_treeview["columns"] = ("SL.no", "ID", "Category", "Size", "Quantity", "Quantity_selected")
        self.item_treeview.column("#0", width=0, stretch=tk.NO)  
        self.item_treeview.column("SL.no", width=40, anchor=tk.CENTER)
        self.item_treeview.column("ID", width=0, stretch=tk.NO)
        self.item_treeview.column("Category", width=0, stretch=tk.NO)
        self.item_treeview.column("Size", width=400)
        self.item_treeview.column("Quantity", width=0, stretch=tk.NO)
        self.item_treeview.column("Quantity_selected", width=0, stretch=tk.NO)

        # Create headings
        self.item_treeview.heading("SL.no", text="SL.no")
        self.item_treeview.heading("Size", text="Size")

        self.item_treeview.bind('<ButtonRelease>', self.display_selected_item_data)

        # Buttons to switch between category treeview and item treeview 
        self.category_btn = tk.Button(selection_btn_frame, text="Select Category", width=32, command=lambda: self.switch_frame(self.category_frame))
        self.category_btn.pack(side="left")
        self.item_btn = tk.Button(selection_btn_frame, text="Select Item", width=32, command=lambda: self.switch_frame(self.item_frame))
        self.item_btn.pack(side="right")

        # ----- Frame to display data of the selected item ----- 
        selected_item_frame = tk.LabelFrame(container_frame, text="Item Details", width=512, height=100, borderwidth=2, relief="groove")
        selected_item_frame.pack_propagate(False)
        selected_item_frame.pack(pady=(5, 0), fill=tk.BOTH, expand=True)

        # Display Item data
        tk.Label(selected_item_frame, text="Item Name: ").grid(row=1, column=1, pady=(4,0))

        self.item_name_entry = tk.Entry(selected_item_frame, width=54, relief='groove')
        self.item_name_entry.grid(row=1, column=2, sticky='ew')

        tk.Label(selected_item_frame, text="Quantity in Stock: ").grid(row=2, column=1)

        self.quantity_stock_entry = tk.Entry(selected_item_frame, width=54, relief='groove')
        self.quantity_stock_entry.grid(row=2, column=2, sticky='ew')

        # Widget to enter item quantity
        self.enter_quantity_spinbox = ttk.Spinbox(selected_item_frame, from_=0, to=0, width=46, font=('Arial', 10), foreground='#333333')
        self.enter_quantity_spinbox.insert(0, "Enter Quantity")
        self.enter_quantity_spinbox.grid(row=3, columnspan=3, sticky='sw', padx=(2,0))

        # Add button to add selected item to cart
        self.add_btn = tk.Button(selected_item_frame, text="Add", width=12, relief="groove", command=self.add_to_cart)
        self.add_btn.grid(row=3, column=2, sticky='e')


        # ----- Cart frame -----
        cart_frame = tk.Frame(self.main_frame, width=512, height=526, borderwidth=2, relief="groove", bg="white")
        cart_frame.pack_propagate(False)
        cart_frame.pack(side=tk.RIGHT, padx=(1.5, 0))

        tk.Label(cart_frame, text="Cart", font=("Arial", 12, 'bold')).pack(pady=(5, 5))

        # Create a frame to pack the cart treeview
        self.cart_treeview_frame = tk.Frame(cart_frame)
        self.cart_treeview_frame.pack()

        # Cart treeview
        self.cart_treeview = TreeView(self.cart_treeview_frame, height=18)

        # Create columns
        self.cart_treeview["columns"] = ("SL.no", "ID", "Category", "Size", "Quantity", "Quantity Selected")
        self.cart_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the cart_tree column
        self.cart_treeview.column("SL.no", width=40, anchor=tk.CENTER)
        self.cart_treeview.column("ID", width=0, stretch=tk.NO)
        self.cart_treeview.column("Category", width=0, stretch=tk.NO)
        self.cart_treeview.column("Size", width=280, anchor=tk.CENTER)
        self.cart_treeview.column("Quantity", width=0, stretch=tk.NO)
        self.cart_treeview.column("Quantity Selected", width=120, anchor=tk.CENTER)

        # Create headings
        self.cart_treeview.heading("SL.no", text="SL.no")
        self.cart_treeview.heading("Size", text="Size", anchor=tk.CENTER)
        self.cart_treeview.heading("Quantity Selected", text="Quantity Selected", anchor=tk.CENTER)

        # Frame to hold cart section buttons
        cart_btn_frame = tk.Frame(cart_frame)
        cart_btn_frame.pack(pady=(1, 2.5), side=tk.BOTTOM)

        self.remove_btn = tk.Button(cart_btn_frame, text="Remove", width=30, command=self.remove_item)
        self.remove_btn.pack(side="left", padx=(0.5,0))
        self.pickup_btn = tk.Button(cart_btn_frame, text="Pickup", width=30, command=self.pickup)
        self.pickup_btn.pack(side="right", padx=(0,0.5))

    def load_pickup_frame(self):
        # Get data of Items and Placement
        self.pickup_data = {item[1]: (item[3], item[5], item[2]) for item in self.cart}
        self.placement_info = database.get_rack_and_position(tuple(self.pickup_data.keys()), db_path=DATABASE_PATH)
        self.session_generator = iter(self.placement_info.items())

        # ----- Pickup page -----
        tk.Label(self.main_frame, text="Pickup", font=("times new roman", 12, "bold")).pack(pady=(0, 10))

        # Frame to display items to be picked
        pickup_list_frame = tk.Frame(self.main_frame, width=512, height=526, borderwidth=2, relief='groove')
        pickup_list_frame.pack_propagate(False)
        pickup_list_frame.pack(side=tk.LEFT, padx=(0, 1.5))

        # Creating canvas
        self.pickup_list_canvas = tk.Canvas(pickup_list_frame)
        self.pickup_list_canvas.pack(side='left', fill='both', expand=True)

        # Add a Scrollbar to the pickup list
        self.pickup_list_scrollbar = tk.Scrollbar(pickup_list_frame, orient='vertical', command=self.pickup_list_canvas.yview)
        self.pickup_list_scrollbar.pack(side='right', fill='y')
        self.pickup_list_canvas.configure(yscrollcommand=self.pickup_list_scrollbar.set)

        grid_container = tk.Frame(self.pickup_list_canvas)
        self.pickup_list_canvas.create_window((0, 0), window=grid_container, anchor='nw')

        tk.Label(grid_container, text="Items", font=("times new roman", 12), bg="#BEBEBE", width=30).grid(row=0, column=0)

        tk.Label(grid_container, text="Quantity", font=("times new roman", 12), bg="#BEBEBE", width=19).grid(row=0, column=1)

        tk.Label(grid_container, text="  ", font=("Arial", 12), bg="#BEBEBE", width=4).grid(row=0, column=2)    # this is just place holder label

        grid_container.bind('<Configure>', self.update_pickup_scroll_region)

        # Add Item data labels and Checkboxes inside the frame (Pickup list)
        for i, k in enumerate(self.placement_info.keys(), 1):

            tk.Label(grid_container, text=self.pickup_data[str(k)][0], font=("Arial", 9), bg="white", width=38).grid(row=i, column=0, sticky="w")

            tk.Label(grid_container, text=self.pickup_data[str(k)][1], font=("Arial", 9), bg="white", width=24).grid(row=i, column=1, sticky="w")
            
            pickup_item_var = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(grid_container, text="", variable=pickup_item_var, state='disabled')  # Initially disabled
            checkbox.grid(row=i, column=2, sticky="w")
            
            self.checkboxes.append(checkbox)
            self.checkbox_vars.append(pickup_item_var)

        self.pickup_list_canvas.bind('<Configure>', lambda e: self.pickup_list_canvas.configure(scrollregion=self.pickup_list_canvas.bbox("all")))

        command_frame = tk.Frame(self.main_frame, width=512, height=526, borderwidth=2, relief='groove')
        command_frame.pack_propagate(False)
        command_frame.pack(side=tk.RIGHT, padx=(1.5, 0))

        self.pickup_data_label = tk.Label(command_frame, text="Press Start Session to\nstart collecting the items", font=("Arial", 11), highlightbackground="black", highlightthickness=2, width=45, height=5)
        self.pickup_data_label.pack(pady=(70, 0))

        self.session_button = tk.Button(command_frame, text="Start Session", width=15, command=lambda: self.session_control("start"))
        self.session_button.pack(side=tk.LEFT, padx=(30, 0))

        self.terminate_btn = tk.Button(command_frame, text="Terminate Session", width=15, command=lambda: self.session_control("terminate"))
        self.terminate_btn.pack(side=tk.RIGHT, padx=(0, 30))

        # disable exit
        self.disable_exit(message="Cannot exit the application while a process is running!\nTerminate Session to exit the application.")

    def switch_frame(self, frame):
        for widget in self.selection_frame.winfo_children():
            widget.forget()

        frame.pack(fill=tk.BOTH, expand=True)

    def delete_treeview_items(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)

    def category_selected(self, event):
        selected_item = self.category_treeview.focus()
        if selected_item:
            category = self.category_treeview.item(selected_item)['values'][0].strip()
        
        # Fetch all items of the category
        items = self.item_data[category]

        # Clear all item in the item Treeview
        self.delete_treeview_items(self.item_treeview)

        # Insert all item in the item Treeview
        for i, item in enumerate(items, start=1):
            if i % 2 == 0:
                self.item_treeview.insert("", "end", values=(f"{i}", f"{item[0]}", f"{item[1]}", f"{item[2]}", f"{item[3]}", '0'), tags=('evenrow',))
            else:
                self.item_treeview.insert("", "end", values=(f"{i}", f"{item[0]}", f"{item[1]}", f"{item[2]}", f"{item[3]}", '0'), tags=('oddrow',))
        
        # After the items are added to treeview switch the frame
        self.switch_frame(self.item_frame)

    def display_selected_item_data(self, event):
        selected_item = self.item_treeview.focus()
        if selected_item:
            item_data = self.item_treeview.item(selected_item)['values']
            item_index = next((i for i, item in enumerate(self.cart) if int(item[1]) == item_data[1]), None)
            if item_index is not None:
                self.clear_item_entry()
                self.item_name_entry.insert(0, f"{self.cart[item_index][3]}")
                self.quantity_stock_entry.insert(0, f"{self.cart[item_index][4]}")
                self.enter_quantity_spinbox.insert(0, f"{self.cart[item_index][5]}")
                self.enter_quantity_spinbox.config(from_=0, to=self.cart[item_index][4])
            else:
                self.clear_item_entry()
                self.item_name_entry.insert(0, f"{item_data[3]}")
                self.quantity_stock_entry.insert(0, f"{item_data[4]}")
                self.enter_quantity_spinbox.insert(0, "Enter Quantity")
                self.enter_quantity_spinbox.config(from_=item_data[5] + 1, to=item_data[4])
        else:
            pass

    def clear_item_entry(self):
        self.item_name_entry.delete(0, tk.END)
        self.quantity_stock_entry.delete(0, tk.END)
        self.enter_quantity_spinbox.delete(0, tk.END)

    def show_cart(self):
        self.delete_treeview_items(self.cart_treeview)
        # insert all item in the item Treeview
        for i, item in enumerate(self.cart, start=1):
            if i % 2 == 0:
                self.cart_treeview.insert("", "end", values=(f"{i}", f"{item[1]}", f"{item[2]}", f"{item[3]}", f"{item[4]}", f"{item[5]}"), tags=('evenrow',))
            else:
                self.cart_treeview.insert("", "end", values=(f"{i}", f"{item[1]}", f"{item[2]}", f"{item[3]}", f"{item[4]}", f"{item[5]}"), tags=('oddrow',))

    def add_to_cart(self):
        selected_item = self.item_treeview.focus()
        if selected_item:
            item_values = self.item_treeview.item(selected_item, 'values')
            new_quantity = int(self.enter_quantity_spinbox.get())
            quantity_instock = int(item_values[4])
            if 0 < new_quantity <= quantity_instock:  # Ensure the quantity is valid
                # Check if item already exists in cart
                existing_item_index = next((index for index, item in enumerate(self.cart) if item[1] == item_values[1]), None)
                if existing_item_index is not None:
                    # If item exists, update the quantity
                    existing_item = list(self.cart[existing_item_index])
                    existing_item[5] = str(new_quantity)  # Update quantity
                    self.cart[existing_item_index] = tuple(existing_item)
                else:
                    # If item does not exist, add as new entry
                    self.cart.append((item_values[0], item_values[1], item_values[2], item_values[3], item_values[4], str(new_quantity)))
            else:
                msgbox.invalid_quantity(max_quantity=quantity_instock)
        self.show_cart()

    def remove_item(self):
        if msgbox.confirm_remove_item_from_cart():
            selected_item = self.cart_treeview.focus()
            if selected_item:
                item_values = self.cart_treeview.item(selected_item, 'values')[1:]
                for item in self.cart:
                    if item[1:] == item_values:
                        self.cart.remove(item)
            self.show_cart()

    def pickup(self):
        if len(self.cart) > 0:
            # confirm pickup msgbox
            if msgbox.confirm_pickup():
                for widget in self.main_frame.winfo_children():
                    widget.destroy()
                self.load_pickup_frame()

    def update_pickup_scroll_region(self, event):
        # Update the scroll region to encompass the inner frame
        self.pickup_list_canvas.configure(scrollregion=self.pickup_list_canvas.bbox('all'))

    def session_control(self, action):
        if action == "start" or action == "next":
            if self.current_command:
                topic, message = self.current_command
                print(topic, message)
                # handle_publish(client=self.mqtt_client, topic=topic, message=message.replace(", 1)", ", 0)"))  # Send close command for current
                # change the status of the checkbox
                self.check_checkboxes()
                q = database.update_item_quantity(self.update_item_data[0], int(self.update_item_data[1]), db_path=DATABASE_PATH)
                # check for the min stock
            try:
                item_id, (rack, pos_label) = next(self.session_generator)
                self.pickup_data_label.config(text=f"Collect {self.pickup_data[str(item_id)][0]}\nQuantity = {self.pickup_data[str(item_id)][1]}\nat {rack}")
                self.data_to_log = [self.user_name, self.pickup_data[str(item_id)][2], self.pickup_data[str(item_id)][0], str(self.machine_name), self.pickup_data[str(item_id)][1], ' ']
                self.update_item_data = [str(item_id), self.pickup_data[str(item_id)][1]]
                topic = f"smart_vault/{rack}"
                open_message = f"('{pos_label}', 1)"
                self.current_command = (topic, open_message)
                # handle_publish(client=self.mqtt_client, topic=topic, message=open_message)  # Send open command for next
                self.session_button.config(text="Next")
            except StopIteration:
                self.session_button.config(text="Session Ended", state="disabled")
                self.terminate_btn.config(text="Session Terminated", state="disabled")
                self.terminate_btn.config(state="disabled")  # Disable terminate button at end
                self.session_button.config(state="disabled")  # Also disable start session button
                self.enable_exit()
        elif action == "terminate":
            if self.current_command:
                topic, message = self.current_command
                # handle_publish(client=self.mqtt_client, topic=topic, message=message.replace(", 1)", ", 0)"))  # Ensure current is closed
            self.terminate_btn.config(text="Session Terminated", state="disabled")
            self.terminate_btn.config(state="disabled")
            self.session_button.config(state="disabled")  # Disable start session button on terminate
            self.enable_exit()

    def check_checkboxes(self):
        if self.current_index < len(self.checkboxes):
            # Check and disable the current checkbox
            self.checkbox_vars[self.current_index].set(True)
            self.checkboxes[self.current_index].configure(state='disabled')
            self.current_index += 1  # Move to the next checkbox

    def update_datetime(self):
        self.top_bar.update_datetime()

    def on_machine_select(self, event):
        selected_mac = self.machine_treeview.focus()
        if selected_mac:
            machine = self.machine_treeview.item(selected_mac)['values']
            self.machine_name = machine[2]
            self.machine_code = machine[3]
            self.machine_select_btn.config(state='normal')

    def disable_exit(self, message):
        # Disable the close button by showing the error message
        self.root.protocol("WM_DELETE_WINDOW", lambda:msgbox.exit_error_msg(root=self.root, message=message))

    def enable_exit(self):
        # Re-enable the close button
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        

# If this file is run directly for testing purposes
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{SCREEN_SIZE[0]}x{SCREEN_SIZE[1]}")
    style = ttk.Style(root)

    # build the path to the theme file
    theme_path = os.path.join(BASE_DIR, "theme", "forest-light.tcl")

    root.tk.call("source", theme_path)
    style.theme_use("forest-light")
    
    # Create an instance of EmployeePanel and pack it into the root window
    frame = EmployeePanel(master=root, user_id=11, username="Prathap")
    frame.pack()

    frame.update_datetime()
    
    root.mainloop()