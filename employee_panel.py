import tkinter as tk
from tkinter import ttk
from tkinter import Toplevel
import os
from gui_components.widgets.treeview import TreeView
from gui_components.widgets.topbar import TopBar
from gui_components.widgets import msgbox
from services import database
from services.mqtt_functions import connect_mqtt, handle_publish
from services.data_logger import log_data
from services.email_sender import restock_email
from settings.config import *

class EmployeePanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(width=1024, height=576)
        self.root = master
        self.category_data = database.fetch_categories()
        self.item_data = database.fetch_all_items(self.category_data)
        self.user_name = None
        self.user_id = None
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
        self.min_stock_details = []
        self.init_ui()

    def init_ui(self):
        # create and pack nav_bar frame
        self.top_bar = TopBar(self)
        self.top_bar.pack(padx=(2.5, 2.5), pady=(5,2.5))

        # user info label
        self.user_label = tk.Label(self.top_bar, text=f"Logged in as: ", font=('times new roman', 12, 'bold'), bg="white")
        self.user_label.pack(side=tk.LEFT, padx=(20, 0))

        # Create and pack frame container
        self.frame_container = tk.Frame(self, width=1024, height=526)
        self.frame_container.pack_propagate(False)
        self.frame_container.pack(padx=(2.5, 2.5), pady=(2.5,5))

        # Create a frame to display categories and items
        self.selection_frame = tk.Frame(self.frame_container, width=512, height=526, borderwidth=2, relief="groove", bg="white")
        self.selection_frame.pack_propagate(False)
        self.selection_frame.pack(side=tk.LEFT, padx=(0, 1.5))

        # Button frame
        self.selection_btn_frame = tk.Frame(self.selection_frame)
        self.selection_btn_frame.pack()

        # Parent frame housing category frame and item frame
        self.container_frame = tk.Frame(self.selection_frame)
        self.container_frame.pack()

        # Category frame to display categories
        self.category_frame = tk.Frame(self.container_frame)
        self.category_frame.pack()

        # Create and pack category Treeview
        self.category_label = tk.Label(self.category_frame, text="Categories", font=("Arial", 12, 'bold'))
        self.category_label.pack(pady=(5, 5))

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

        # on click event --> category Treeview 
        self.category_treeview.bind('<ButtonRelease>', self.category_selected)

        # Item frame to display items
        self.item_frame = tk.Frame(self.container_frame)

        # Create and pack item Treeview
        self.item_label = tk.Label(self.item_frame, text="Items", font=("Arial", 12, 'bold'))
        self.item_label.pack(pady=(5, 5))

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

        # on click event --> item Treeview 
        self.item_treeview.bind('<ButtonRelease>', self.display_data)

        # add buttons to switch between category page and item page 
        self.category_btn = tk.Button(self.selection_btn_frame, text="Select Category", width=28, command=lambda: self.switch_frame(self.category_frame))
        self.category_btn.pack(side="left", padx=(0, 0.25))
        self.item_btn = tk.Button(self.selection_btn_frame, text="Select Item", width=28, command=lambda: self.switch_frame(self.item_frame))
        self.item_btn.pack(side="right", padx=(0.25, 0))

        # Frame to display data of the selected item 
        self.selected_item_frame = tk.LabelFrame(self.selection_frame, text="Item Details", width=512, height=100, borderwidth=2, relief="groove")
        self.selected_item_frame.pack_propagate(False)
        self.selected_item_frame.pack(pady=(10, 0), fill=tk.BOTH, expand=True)

        # Widget to display item name
        self.item_name_label = tk.Label(self.selected_item_frame, text="Item Name: ")
        self.item_name_label.grid(row=1, column=1)

        self.item_name_entry = tk.Entry(self.selected_item_frame, width=46, relief='groove')
        self.item_name_entry.grid(row=1, column=2, sticky='ew')

        # Widget to display item quantity
        self.quantity_label = tk.Label(self.selected_item_frame, text="Quantity in Stock: ")
        self.quantity_label.grid(row=2, column=1)

        self.quantity_stock_entry = tk.Entry(self.selected_item_frame, width=46, relief='groove')
        self.quantity_stock_entry.grid(row=2, column=2, sticky='ew')

        # Widget to enter item quantity
        self.enter_quantity_spinbox = ttk.Spinbox(self.selected_item_frame, from_=0, to=0, width=46, font=('Arial', 10), foreground='#333333')
        self.enter_quantity_spinbox.insert(0, "Enter Quantity")
        self.enter_quantity_spinbox.grid(row=3, columnspan=3, sticky='sw')

        # Add button to add selected item to cart
        self.add_btn = tk.Button(self.selected_item_frame, text="Add", width=10, relief="groove", command=self.add_to_cart)
        self.add_btn.grid(row=3, column=2, sticky='se')

        # Create a frame to display the items in cart
        self.cart_frame = tk.Frame(self.frame_container, width=512, height=526, borderwidth=2, relief="groove", bg="white")
        self.cart_frame.pack_propagate(False)
        self.cart_frame.pack(side=tk.RIGHT, padx=(1.5, 0))

        # Create and pack cart Treeview
        self.cart_label = tk.Label(self.cart_frame, text="Cart", font=("Arial", 12, 'bold'))
        self.cart_label.pack(pady=(5, 5))

        # Create a frame to pack the cart treeview
        self.cart_treeview_frame = tk.Frame(self.cart_frame)
        self.cart_treeview_frame.pack()

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
        self.cart_btn_frame = tk.Frame(self.cart_frame)
        self.cart_btn_frame.pack(pady=(2.5, 2.5), side=tk.BOTTOM)

        self.remove_btn = tk.Button(self.cart_btn_frame, text="Remove", width=28, command=self.remove_item)
        self.remove_btn.pack(side="left", padx=(2.5, 1))
        self.pickup_btn = tk.Button(self.cart_btn_frame, text="Pickup", width=28, command=self.pickup)
        self.pickup_btn.pack(side="right", padx=(1, 2.5))

    def load_pickup_frame(self):
        # get data of items and placement
        self.pickup_data = {item[1]: (item[3], item[5], item[2]) for item in self.cart}
        self.placement_info = database.get_rack_and_position(tuple(self.pickup_data.keys()))
        self.session_generator = iter(self.placement_info.items())

        # Connect ot MQTT Server
        self.mqtt_client = connect_mqtt(mqtt_server=MQTT_SERVER, mqtt_port=MQTT_PORT)

        # Pickup page setup
        self.checkout_label = tk.Label(self.frame_container, text="Pickup", font=("times new roman", 12, "bold"))
        self.checkout_label.pack(pady=(0, 10))

        self.pickup_list_frame = tk.Frame(self.frame_container, width=512, height=526, borderwidth=2, relief='groove')
        self.pickup_list_frame.pack_propagate(False)
        self.pickup_list_frame.pack(side=tk.LEFT, padx=(0, 1.5))

        # creating canvas
        self.canvas = tk.Canvas(self.pickup_list_frame)
        self.canvas.pack(side='left', fill='both', expand=True)

        # Add a Scrollbar to the pickup_list_frame, linking it to the canvas
        self.scrollbar = tk.Scrollbar(self.pickup_list_frame, orient='vertical', command=self.canvas.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.grid_container = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.grid_container, anchor='nw')

        self.items_label = tk.Label(self.grid_container, text="Items", font=("times new roman", 12), bg="#BEBEBE", width=45)
        self.items_label.grid(row=0, column=0)

        self.quantities_label = tk.Label(self.grid_container, text="Quantity", font=("times new roman", 12), bg="#BEBEBE", width=12)
        self.quantities_label.grid(row=0, column=1)

        self.check_label = tk.Label(self.grid_container, text="  ", font=("Arial", 12), bg="#BEBEBE", width=6)
        self.check_label.grid(row=0, column=2)

        self.grid_container.bind('<Configure>', self.update_scroll_region)

        # Add item labels and checkboxes inside the frame
        for i , k in enumerate(self.placement_info.keys(), 1):
            item_label = tk.Label(self.grid_container, text=self.pickup_data[str(k)][0], font=("Arial", 9), bg="white", width=51)
            item_label.grid(row=i, column=0, sticky="w")

            quantity_label = tk.Label(self.grid_container, text=self.pickup_data[str(k)][1], font=("Arial", 9), bg="white", width=13)
            quantity_label.grid(row=i, column=1, sticky="w")
            
            var = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(self.grid_container, text="", variable=var, state='disabled')  # Initially disabled
            checkbox.grid(row=i, column=2, sticky="w")
            
            self.checkboxes.append(checkbox)
            self.checkbox_vars.append(var)

        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.send_cmd_frame = tk.Frame(self.frame_container, width=512, height=526, borderwidth=2, relief='groove')
        self.send_cmd_frame.pack_propagate(False)
        self.send_cmd_frame.pack(side=tk.RIGHT, padx=(1.5, 0))

        self.pickup_data_label = tk.Label(self.send_cmd_frame, text="Press Start Session to\nstart collecting the items", font=("Arial", 11), highlightbackground="black", highlightthickness=2, width=45, height=5)
        self.pickup_data_label.pack(pady=(70, 0))

        self.session_button = tk.Button(self.send_cmd_frame, text="Start Session", width=15, command=lambda: self.session_control("start"))
        self.session_button.pack(side=tk.LEFT, padx=(30, 0))

        self.terminate_btn = tk.Button(self.send_cmd_frame, text="Terminate Session", width=15, command=lambda: self.session_control("terminate"))
        self.terminate_btn.pack(side=tk.RIGHT, padx=(0, 30))

    def switch_frame(self, frame):
        for widget in self.container_frame.winfo_children():
            widget.forget()

        frame.pack(fill=tk.BOTH, expand=True)

    def category_selected(self, event):
        selected_item = self.category_treeview.focus()
        if selected_item:
            category = self.category_treeview.item(selected_item)['values'][0].strip()
        
        # fetch all items of the category
        items = self.item_data[category]

        # clear all item in the item Treeview
        self.delete_treeview_items(self.item_treeview)

        # insert all item in the item Treeview
        for i, item in enumerate(items, start=1):
            if i % 2 == 0:
                self.item_treeview.insert("", "end", values=(f"{i}", f"{item[0]}", f"{item[1]}", f"{item[2]}", f"{item[3]}", '0'), tags=('evenrow',))
            else:
                self.item_treeview.insert("", "end", values=(f"{i}", f"{item[0]}", f"{item[1]}", f"{item[2]}", f"{item[3]}", '0'), tags=('oddrow',))
        
        # after the changes are done switch page
        self.switch_frame(self.item_frame)

    def delete_treeview_items(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)

    def display_data(self, event):
        selected_item = self.item_treeview.focus()
        if selected_item:
            item_data = self.item_treeview.item(selected_item)['values']
            item_index = next((i for i, item in enumerate(self.cart) if int(item[1]) == item_data[1]), None)
            if item_index is not None:
                self.clear_entry()
                self.item_name_entry.insert(0, f"{self.cart[item_index][3]}")
                self.quantity_stock_entry.insert(0, f"{self.cart[item_index][4]}")
                self.enter_quantity_spinbox.insert(0, f"{self.cart[item_index][5]}")
                self.enter_quantity_spinbox.config(from_=0, to=self.cart[item_index][4])
            else:
                self.clear_entry()
                self.item_name_entry.insert(0, f"{item_data[3]}")
                self.quantity_stock_entry.insert(0, f"{item_data[4]}")
                self.enter_quantity_spinbox.insert(0, "Enter Quantity")
                self.enter_quantity_spinbox.config(from_=item_data[5] + 1, to=item_data[4])
        else:
            pass

    def clear_entry(self):
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
            if new_quantity > 0:  # Ensure the quantity is positive
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
        self.show_cart()

    def remove_item(self):
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
            for widget in self.frame_container.winfo_children():
                widget.destroy()
            self.load_pickup_frame()

    def update_scroll_region(self, event):
        # Update the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def session_control(self, action):
        if action == "start" or action == "next":
            if self.current_command:
                topic, message = self.current_command
                handle_publish(client=self.mqtt_client, topic=topic, message=message.replace(", 1)", ", 0)"))  # Send close command for current
                # change the status of the checkbox
                self.check_checkboxes()
                q = database.update_item_quantity(self.update_item_data[0], int(self.update_item_data[1]))
                # check for the min stock
                print(MIN_STOCK[self.data_to_log[1]])
                if q < MIN_STOCK[self.data_to_log[1]]:
                    self.min_stock_details.append((self.data_to_log[2], q))
                    print(self.min_stock_details)
            try:
                item_id, (rack, pos_label) = next(self.session_generator)
                self.pickup_data_label.config(text=f"Collect {self.pickup_data[str(item_id)][0]}\nat {rack} \nQuantity = {self.pickup_data[str(item_id)][1]}")
                self.data_to_log = [self.user_name, self.pickup_data[str(item_id)][2], self.pickup_data[str(item_id)][0], self.pickup_data[str(item_id)][1]]
                self.update_item_data = [str(item_id), self.pickup_data[str(item_id)][1]]
                topic = f"smart_vault/{rack}"
                open_message = f"('{pos_label}', 1)"
                self.current_command = (topic, open_message)
                handle_publish(client=self.mqtt_client, topic=topic, message=open_message)  # Send open command for next
                self.session_button.config(text="Next")
            except StopIteration:
                self.session_button.config(text="Session Ended", state="disabled")
                self.terminate_btn.config(text="Session Terminated", state="disabled")
                self.terminate_btn.config(state="disabled")  # Disable terminate button at end
                self.session_button.config(state="disabled")  # Also disable start session button
                subject = 'Rectock Alert'
                message = ''
                for item in self.min_stock_details:
                    message += f'Restock {item[0]} only {item[1]} left\n'
                print(message)
                restock_email(EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, subject, message)
                self.show_countdown(10)
        elif action == "terminate":
            if self.current_command:
                topic, message = self.current_command
                handle_publish(client=self.mqtt_client, topic=topic, message=message.replace(", 1)", ", 0)"))  # Ensure current is closed
            self.terminate_btn.config(text="Session Terminated", state="disabled")
            self.terminate_btn.config(state="disabled")
            self.session_button.config(state="disabled")  # Disable start session button on terminate

    def check_checkboxes(self):
        if self.current_index < len(self.checkboxes):
            # Check and disable the current checkbox
            self.checkbox_vars[self.current_index].set(True)
            self.checkboxes[self.current_index].configure(state='disabled')
            self.current_index += 1  # Move to the next checkbox

    def update_datetime(self):
        self.top_bar.update_datetime()

    def countdown(self, top, label, count):
        # Change the text in the label
        label['text'] = f"Please wait {count} seconds before closing the application"

        if count > 0:
            # Call countdown again after 1000ms (1s)
            top.after(1000, self.countdown, top, label, count - 1)
        else:
            # When the countdown reaches zero, close the window
            top.destroy()

    def show_countdown(self, count):
        # Create a custom top-level window
        top = Toplevel()
        top.title("Wait")
        top.geometry("500x100")

        # Create a label to display the countdown
        label = tk.Label(top, font=('Helvetica', 14))
        label.pack(pady=20)

        # Start the countdown
        self.countdown(top, label, count)


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
    main_frame = EmployeePanel(root)
    main_frame.pack()

    main_frame.update_datetime()
    
    root.mainloop()