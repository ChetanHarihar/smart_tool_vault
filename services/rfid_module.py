import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import sqlite3
import threading
import queue

# Setup GPIO warnings
GPIO.setwarnings(False)

def scan_rfid(q):
    """
    Scans an RFID tag using the RFID reader, putting the result into the queue.

    Args:
    q (queue.Queue): The queue to put the scan result.
    """
    try:
        while not q.empty():
            q.get_nowait()  # Clear the queue
    except queue.Empty:
        pass
    
    reader = SimpleMFRC522()
    try:
        uid, text = reader.read()
        print(f"UID: {uid}")
        print(f"TEXT: {text}")
        q.put(('Success', uid, text))
    except Exception as e:
        q.put(('Failed',))
    finally:
        GPIO.cleanup()

def check_scan_result(q, role):
    """
    Checks the RFID scan result and returns True or False accordingly.

    Args:
    q (queue.Queue): The queue from which to get the scan result.
    role (str): The role expected from the RFID scan.

    Returns:
    bool: True if the scan result is successful and matches the role, False otherwise.
    """
    try:
        result = q.get_nowait()
        if result[0] == 'Success':
            uid = result[1]
            conn = sqlite3.connect('/home/pi/Python/smart_tool_vault/smartvault.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, role FROM user WHERE uid = ?", (uid,))
            fetched_result = cursor.fetchone()
            conn.close()

            if fetched_result is not None and fetched_result[-1] == role:
                print("Access Granted")
                return fetched_result
            else:
                print("Authentication Failed")
                return None
        else:
            return False
    except queue.Empty:
        return False

if __name__ == "__main__":
    test_queue = queue.Queue()

    # Creating and starting the RFID scanning thread
    scan_thread = threading.Thread(target=scan_rfid, args=(test_queue,))
    scan_thread.start()

    # Waiting for the scanning thread to complete
    scan_thread.join()

    # Checking the scan result
    user_data = check_scan_result(q=test_queue, role=2)
    print(user_data)