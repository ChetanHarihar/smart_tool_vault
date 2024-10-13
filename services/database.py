import sqlite3
import re

def check_scan_result(uid, role, db_path):
    conn = None
    """
    Checks the RFID scan and returns the Result.

    Args:
    UID (str): The UID of the card.
    role (str): The role expected from the RFID scan.

    Returns:
    list: User Data if the scan result is successful and matches the role, None otherwise.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, role FROM user WHERE uid = ?", (uid,))
        fetched_result = cursor.fetchone()
        conn.close()

        if fetched_result is not None and fetched_result[-1] == role:
            print("Authentication Successful")
            return fetched_result
        else:
            print("Authentication Failed")
            
    except Exception as e:
        print(e)

    return None

def fetch_categories(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT name FROM category
        ''')
        
        categories = cursor.fetchall()
        category_names = [category[0] for category in categories]
        return category_names

    except sqlite3.Error as e:
        print("SQLite error:", e)
        return []

    finally:
        if conn:
            conn.close()

def get_category_id_by_name(category_name, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM category WHERE name = ?", (category_name,))
        result = cursor.fetchone()

        if result:
            category_id = result[0]
            print(f"Category ID for '{category_name}' is {category_id}.")
            return category_id
        else:
            print(f"No category found with the name '{category_name}'.")
            return None

    except sqlite3.Error as e:
        print("Error retrieving category ID:", e)
        return None

    finally:
        cursor.close()
        conn.close()

def fetch_all_items(categories, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        all_items = {}

        for category in categories:
            cursor.execute('''
                            SELECT Item.id AS ItemID, category.name AS CategoryName, item.item_size AS ItemSize, item.quantity AS Quantity
                            FROM item
                            INNER JOIN category ON item.category_id = category.id
                            WHERE category.name = ?
                ''', (category,))
            
            items = cursor.fetchall()
            all_items[category] = items

        return all_items

    except sqlite3.Error as e:
        print("SQLite error:", e)
        return {}

    finally:
        if conn:
            conn.close()

def get_rack_and_position(item_ids, db_path):
    conn = None
    results_dict = {}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = f"""
        SELECT
            ip.item_id,
            r.name AS RackName,
            rp.position_label AS PositionLabel
        FROM
            item_placement ip
        INNER JOIN
            rack_position rp ON ip.rack_position_id = rp.id
        INNER JOIN
            rack r ON rp.rack_id = r.id
        WHERE
            ip.item_id IN ({','.join('?'*len(item_ids))});
        """
        
        cursor.execute(query, item_ids)
        results = cursor.fetchall()
        
        for item_id, rack_name, position_label in results:
            results_dict[item_id] = (rack_name, position_label)
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        
    finally:
        if conn:
            conn.close()
    
    return {k: v for k, v in sorted(results_dict.items(), key=lambda item: (item[1][0], item[1][1]))}

import sqlite3

def update_item_quantity(item_id, subtract_amount, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch the current quantity of the item
        cursor.execute('SELECT quantity FROM item WHERE id = ?', (item_id,))
        result = cursor.fetchone()

        # Check if the item exists in the table
        if result is None:
            print(f"Item with id {item_id} does not exist.")
            return None

        current_quantity, = result

        # Calculate the new quantity and ensure it does not go below zero
        new_quantity = current_quantity - subtract_amount
        if new_quantity < 0:
            print(f"Error: Subtracting {subtract_amount} from item {item_id} would result in negative quantity.")
            return None

        # Update the quantity in the database
        cursor.execute('UPDATE item SET quantity = ? WHERE id = ?', (new_quantity, item_id))
        conn.commit()

        return new_quantity

    except sqlite3.Error as e:
        print("An error occurred:", e)
        if conn:
            conn.rollback()  # Roll back changes on error
        return None

    finally:
        # Close the connection if it was opened
        if conn:
            conn.close()

def get_user_details(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        return users

    except sqlite3.Error as e:
        print("Error fetching users details:", e)
        return []

    finally:
        if conn:
            conn.close()

def add_user(name, uid, role, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO user (name, uid, role) VALUES (?, ?, ?)", (name, uid, role))
        conn.commit()

        return True, "User added successfully."

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            error_message = "A user with the provided UID already exists."
        elif "NOT NULL constraint failed" in str(e):
            error_message = "Name, UID, or Role cannot be left empty."
        else:
            error_message = f"Integrity error: {e}"
        
        return False, f"Error adding user: {error_message}"

    except sqlite3.Error as e:
        return False, f"Error adding user: {e}"

    finally:
        if conn:
            conn.close()

def remove_user_by_id(user_id, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
        conn.commit()

        print(f"User with ID {user_id} removed successfully.")

    except sqlite3.Error as e:
        print("Error removing user:", e)

    finally:
        if conn:
            conn.close()

def add_category(name, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO category (name) VALUES (?)", (name,))
        conn.commit()

        print(f"Category '{name}' added successfully.")
        return True, f"Category '{name}' added successfully."

    except sqlite3.IntegrityError:
        error_message = f"Category '{name}' already exists."
        print(error_message)
        return False, error_message

    except sqlite3.Error as e:
        error_message = f"Error adding category: {e}"
        print(error_message)
        return False, error_message

    finally:
        cursor.close()
        conn.close()

def delete_category_by_id(category_id, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM category WHERE id = ?", (category_id,))
        conn.commit()

        print(f"Category with ID {category_id} deleted successfully.")
        return True, f"Category with ID {category_id} deleted successfully."

    except sqlite3.Error as e:
        error_message = f"Error deleting category: {e}"
        print(error_message)
        return False, error_message

    finally:
        cursor.close()
        conn.close()

def add_item(category_id, item, db_path, quantity=0):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO item (category_id, item_size, quantity) VALUES (?, ?, ?)", (category_id, item, quantity))
        conn.commit()

        print(f"Item '{item}' added successfully.")
        return True, f"Item '{item}' added successfully."

    except sqlite3.IntegrityError:
        error_message = f"Item '{item}' for category ID {category_id} already exists."
        print(error_message)
        return False, error_message

    except sqlite3.Error as e:
        error_message = f"Error adding item: {e}"
        print(error_message)
        return False, error_message

    finally:
        cursor.close()
        conn.close()

def delete_item_by_id(item_id, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM item WHERE id = ?", (item_id,))
        conn.commit()

        print(f"Item with ID {item_id} deleted successfully.")
        return True, f"Item with ID {item_id} deleted successfully."

    except sqlite3.Error as e:
        error_message = f"Error deleting item: {e}"
        print(error_message)
        return False, error_message

    finally:
        cursor.close()
        conn.close()

def restock_item(item_id, add_amount, db_path):
    if add_amount < 0:
        return
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT quantity FROM item WHERE id = ?', (item_id,))
        result = cursor.fetchone()
        
        current_quantity, = result
        
        new_quantity = current_quantity + add_amount 
        
        cursor.execute('UPDATE item SET quantity = ? WHERE id = ?', (new_quantity, item_id))
        conn.commit()
    
    except sqlite3.Error as e:
        print("An error occurred:", e)
        conn.rollback()
    
    finally:
        if conn:
            conn.close()

def add_rack(name, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO rack (name) VALUES (?)", (name,))
        conn.commit()

        print(f"Rack '{name}' added successfully.")
        return True, f"Rack '{name}' added successfully."

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: rack.name" in str(e):
            error_message = f"Rack '{name}' already exists."
        elif "NOT NULL constraint failed: rack.name" in str(e):
            error_message = "Rack name cannot be left blank."
        else:
            error_message = f"Integrity Error: {e}"
        print(error_message)
        return False, error_message

    except sqlite3.Error as e:
        error_message = f"Error adding rack: {e}"
        print(error_message)
        return False, error_message

    finally:
        cursor.close()
        conn.close()

def get_all_racks(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM rack")
        racks = cursor.fetchall()

        return racks

    except sqlite3.Error as e:
        print(f"Error getting racks: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

def get_items_not_in_rack_positions(db_path):
    conn = None
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the SQL query to find items not in rack positions
        cursor.execute('''
            SELECT item.id, category.name, item.item_size
            FROM item
            LEFT JOIN rack_position ON item.id = rack_position.id
            LEFT JOIN category ON item.category_id = category.id
            WHERE rack_position.id IS NULL
        ''')

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        return rows

    except sqlite3.Error as e:
        print("An error occurred:", e)
        return None

    finally:
        # Ensure the cursor and connection are closed, even if an error occurs
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_items_not_in_placement(db_path):
    conn = None
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute the SQL query
        cursor.execute('''
            SELECT item.id, category.name, item.item_size
            FROM item
            LEFT JOIN category ON item.category_id = category.id
            LEFT JOIN item_placement ON item.id = item_placement.item_id
            WHERE item_placement.item_id IS NULL
        ''')
        
        # Fetch all rows from the query result
        rows = cursor.fetchall()

        return rows
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        rows = []
    
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

def delete_rack_by_id(rack_id, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM rack WHERE id = ?", (rack_id,))
        conn.commit()

        print(f"Rack with ID {rack_id} deleted successfully.")
        return True, f"Rack with ID {rack_id} deleted successfully."

    except sqlite3.Error as e:
        error_message = f"Error deleting rack: {e}"
        print(error_message)
        return False, error_message

    finally:
        cursor.close()
        conn.close()

def get_items_in_rack(rack_id, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # SQL query to join the tables and retrieve the specified fields for a specific rack
        query = '''
        SELECT
            category.name AS category,
            item.item_size,
            item.quantity,
            rack_position.id AS rack_position_id,
            rack_position.position_label,
            item_placement.id AS item_placement_id
        FROM
            item_placement
        JOIN
            item ON item_placement.item_id = item.id
        JOIN
            category ON item.category_id = category.id
        JOIN
            rack_position ON item_placement.rack_position_id = rack_position.id
        JOIN
            rack ON rack_position.rack_id = rack.id
        WHERE
            rack.id = ?
        '''

        # Execute the query with the specified rack_id
        cursor.execute(query, (rack_id,))

        # Fetch all the results
        results = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []  # Return an empty list or handle the error as needed

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

    # Custom sort function for position labels
    def sort_key(label):
        match = re.match(r"([A-Z]+)(\d+)", label)
        if match:
            letter, number = match.groups()
            return (letter, int(number))
        return (label, 0)  # In case of unexpected label format, sort them to the end

    # Sort the results based on the rack_position.position_label
    sorted_results = sorted(results, key=lambda x: sort_key(x[4]))

    return sorted_results

def delete_item_placement_by_id(item_placement_id, db_path):
    conn = None
    try:
        # Connect to the SQLite database using the absolute path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL query to delete a row from item_placement based on the id
        cursor.execute("DELETE FROM item_placement WHERE id = ?", (item_placement_id,))
        conn.commit()
        
        print(f"Item placement with ID {item_placement_id} deleted successfully.")
        return True, f"Item placement with ID {item_placement_id} deleted successfully."
    
    except sqlite3.Error as e:
        error_message = f"Error deleting item placement: {e}"
        print(error_message)
        return False, error_message
    
    finally:
        cursor.close()
        conn.close()

def add_rack_position(rack_id, position_label, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO rack_position (rack_id, position_label) VALUES (?, ?)", (rack_id, position_label))
        conn.commit()

        new_id = cursor.lastrowid

        print(f"Position '{position_label}' added successfully to rack ID {rack_id} with position ID {new_id}.")
        return True, f"Position '{position_label}' added successfully to rack ID {rack_id} with position ID {new_id}.", new_id

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: rack_position.rack_id, rack_position.position_label" in str(e):
            error_message = f"Position '{position_label}' already exists in rack ID {rack_id}."
        elif "FOREIGN KEY constraint failed" in str(e):
            error_message = f"Rack ID {rack_id} does not exist."
        elif "NOT NULL constraint failed" in str(e):
            error_message = "Position label cannot be left blank."
        else:
            error_message = f"Integrity Error: {e}"
        print(error_message)
        return False, error_message, None

    except sqlite3.Error as e:
        error_message = f"Error adding rack position: {e}"
        print(error_message)
        return False, error_message, None

    finally:
        if conn:
            cursor.close()
            conn.close()

def add_item_placement(rack_position_id, item_id, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO item_placement (rack_position_id, item_id) VALUES (?, ?)", (rack_position_id, item_id))
        conn.commit()

        print(f"Item ID {item_id} placed successfully in rack position ID {rack_position_id}.")
        return True, f"Item ID {item_id} placed successfully in rack position ID {rack_position_id}."

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: item_placement.rack_position_id" in str(e):
            error_message = f"Rack position ID {rack_position_id} already has an item."
        elif "UNIQUE constraint failed: item_placement.item_id" in str(e):
            error_message = f"Item ID {item_id} is already placed in a rack position."
        elif "FOREIGN KEY constraint failed" in str(e):
            error_message = f"Invalid rack position ID {rack_position_id} or item ID {item_id}."
        elif "NOT NULL constraint failed" in str(e):
            error_message = "Rack position ID and item ID cannot be left blank."
        else:
            error_message = f"Integrity Error: {e}"
        print(error_message)
        return False, error_message

    except sqlite3.Error as e:
        error_message = f"Error adding item placement: {e}"
        print(error_message)
        return False, error_message

    finally:
        cursor.close()
        conn.close()

def add_rack_position_and_item_placement(rack_id, position_label, item_id, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Start a transaction
        cursor.execute("BEGIN TRANSACTION")

        # Insert into rack_position
        cursor.execute("INSERT INTO rack_position (rack_id, position_label) VALUES (?, ?)", (rack_id, position_label))
        new_rack_position_id = cursor.lastrowid

        # Insert into item_placement
        cursor.execute("INSERT INTO item_placement (rack_position_id, item_id) VALUES (?, ?)", (new_rack_position_id, item_id))
        
        # Commit the transaction
        conn.commit()

        success_message = f"Position '{position_label}' added successfully to rack ID {rack_id} and item ID {item_id} placed successfully in rack position ID {new_rack_position_id}."
        print(success_message)
        return True, success_message

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: rack_position.rack_id, rack_position.position_label" in str(e):
            error_message = f"Position '{position_label}' already exists in rack ID {rack_id}."
        elif "UNIQUE constraint failed: item_placement.rack_position_id" in str(e):
            error_message = f"Rack position ID {new_rack_position_id} already has an item."
        elif "UNIQUE constraint failed: item_placement.item_id" in str(e):
            error_message = f"Item ID {item_id} is already placed in a rack position."
        elif "FOREIGN KEY constraint failed" in str(e):
            error_message = f"Invalid rack ID {rack_id}, rack position ID {new_rack_position_id}, or item ID {item_id}."
        elif "NOT NULL constraint failed" in str(e):
            error_message = "Rack ID, position label, and item ID cannot be left blank."
        else:
            error_message = f"Integrity Error: {e}"
        print(error_message)
        
        # Rollback the transaction
        if conn:
            conn.rollback()
        
        return False, error_message

    except sqlite3.Error as e:
        error_message = f"Error adding rack position and item placement: {e}"
        print(error_message)

        # Rollback the transaction
        if conn:
            conn.rollback()
        
        return False, error_message

    finally:
        if conn:
            cursor.close()
            conn.close()

def add_machine(name, code, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO machine (name, code) VALUES (?, ?)''', (name, code))
        
        conn.commit()
        msg = "Machine added successfully."
        return True, msg
    
    except sqlite3.IntegrityError as e:
        print(f"Integrity error occurred: {e}")
        return False, f"Integrity error occurred: {e}"
    
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        return False, f"Database error occurred: {e}"
    
    finally:
        if conn:
            conn.close()

def get_all_machines(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, code FROM machine')
        machines = cursor.fetchall()
        
        return machines
    
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def delete_machine(machine_id, db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM machine WHERE id = ?', (machine_id,))
        
        if cursor.rowcount == 0:
            print(f"No machine found with id {machine_id}")
            return False, f"Machine with id {machine_id} not found."
        else:
            conn.commit()
            print("Machine deleted successfully.")
            return True, f"Machine with id {machine_id} deleted."
    
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        return False, f"Database error occurred: {e}"
    
    finally:
        if conn:
            conn.close()