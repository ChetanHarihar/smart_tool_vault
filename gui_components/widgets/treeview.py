import tkinter as tk
from tkinter import ttk
import os

class TreeView(ttk.Treeview):
    def __init__(self, parent, tags=('oddrow', 'evenrow'), *args, **kwargs):
        super().__init__(parent, selectmode='browse', *args, **kwargs)
        
        # Set tags and their configurations
        for tag in tags:
            self.tag_configure(tag, background='#ECECEC' if tag == 'oddrow' else '#CFCFCF', foreground='#000000')
        
        # Create and place the vertical scrollbar
        self.vertical_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        self.vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create and place the horizontal scrollbar
        self.horizontal_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.xview)
        self.horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure the Treeview's yscroll command to the vertical scrollbar
        self.configure(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)
        
        # Pack the Treeview widget last so it fills the remaining space after scrollbars have been placed
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Example usage:
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)

    # build the path to the theme file
    theme_path = os.path.join("/home/pi/Python/SMART_VAULT", "theme", "forest-light.tcl")

    root.tk.call("source", theme_path)
    style.theme_use("forest-light")
    
    # Create and configure the custom treeview
    custom_treeview = TreeView(root)

    # Create columns
    custom_treeview["columns"] = ("SL.no", "ID", "Category", "Size", "Quantity", "Quantity_selected")
    custom_treeview.column("#0", width=0, stretch=tk.NO)  # Hide the item_tree column
    custom_treeview.column("SL.no", width=40)
    custom_treeview.column("ID", width=0, stretch=tk.NO)
    custom_treeview.column("Category", width=180, anchor=tk.CENTER)
    custom_treeview.column("Size", width=250)
    custom_treeview.column("Quantity", width=0, stretch=tk.NO)
    custom_treeview.column("Quantity_selected", width=0, stretch=tk.NO)

    # Create headings
    custom_treeview.heading("SL.no", text="SL.no")
    custom_treeview.heading("Category", text="Category")
    custom_treeview.heading("Size", text="Size")
    
    # Inserting categories/items in the Treeview
    for i in range(1, 11):
        if i % 2 == 0:
            custom_treeview.insert('', tk.END, values=(f"Item {i}",), tags=('evenrow',))
        else:
            custom_treeview.insert('', tk.END, values=(f"Item {i}",), tags=('oddrow',))
    
    root.mainloop()