import sqlite3

def check_scan_result(uid, role, db_path):
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
