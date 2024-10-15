from config import *

# Connect to the SQLite database. If it doesn't exist, it will be created.
conn = sqlite3.connect(os.path.join(BASE_DIR, "smartvault.db"))

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Creating the Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    uid TEXT NOT NULL UNIQUE,
    role INTEGER NOT NULL
);
''')

# Creating the Machines table
cursor.execute('''
CREATE TABLE IF NOT EXISTS machine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE
);
''')

# Creating the Categories table
cursor.execute('''
CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
''')

# Creating the Items table
cursor.execute('''
CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    item_size TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE RESTRICT,
    UNIQUE(category_id, item_size)
);
''')

# Creating the Racks table
cursor.execute('''
CREATE TABLE IF NOT EXISTS rack (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
''')

# Creating the RackPositions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS rack_position (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rack_id INTEGER,
    position_label TEXT NOT NULL,
    FOREIGN KEY (rack_id) REFERENCES rack(id) ON DELETE RESTRICT,
    UNIQUE(rack_id, position_label)
);
''')

# Creating the ItemPlacement table
cursor.execute('''
CREATE TABLE IF NOT EXISTS item_placement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rack_position_id INTEGER,
    item_id INTEGER,
    FOREIGN KEY (rack_position_id) REFERENCES rack_position(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE
);
''')


# Creating trigger to prevent deletion of categories with existing items
cursor.execute('''
CREATE TRIGGER prevent_category_delete
BEFORE DELETE ON category
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (SELECT COUNT(*) FROM item WHERE category_id = OLD.id) > 0 THEN
            RAISE(ABORT, 'Cannot delete category with existing items.')
    END;
END;
''')

# Creating trigger to delete associated rack positions if no items exist in them
cursor.execute('''
CREATE TRIGGER delete_rack_position_if_empty
AFTER DELETE ON item_placement
FOR EACH ROW
BEGIN
    DELETE FROM rack_position
    WHERE id = OLD.rack_position_id
    AND NOT EXISTS (SELECT 1 FROM item_placement WHERE rack_position_id = OLD.rack_position_id);
END;
''')

# Creating the trigger to prevent deletion of racks with items placed in them
cursor.execute('''
CREATE TRIGGER IF NOT EXISTS prevent_rack_delete
BEFORE DELETE ON rack
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (SELECT COUNT(*) FROM item_placement WHERE rack_position_id IN (SELECT id FROM rack_position WHERE rack_id = OLD.id)) > 0 THEN
            RAISE(ABORT, 'Cannot delete rack with items placed in it.')
    END;
END;
''')

# Creating the trigger to prevent deletion of items that are placed in rack positions
cursor.execute('''
CREATE TRIGGER prevent_item_delete
BEFORE DELETE ON item
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (SELECT COUNT(*) FROM item_placement WHERE item_id = OLD.id) > 0 THEN
            RAISE(ABORT, 'Cannot delete item as it is placed in a rack.')
    END;
END;
''')


# Commit the transaction
conn.commit()

# Close the connection when done
conn.close()