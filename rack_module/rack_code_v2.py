import machine
import network
import time
from umqtt.simple import MQTTClient

# Network settings for WiFi and MQTT
SSID = 'Das 2G'       # WiFi SSID
PASSWORD = 'DasCnc.1.'      # WiFi Password
MQTT_SERVER = 'broker.hivemq.com'      # IP address of the MQTT server
MQTT_PORT = 1883
BASE_TOPIC = 'smartvault'   # MQTT BASE TOPIC
RACK_NAME = 'Rack #'       # DEVICE NAME
MQTT_TOPIC = BASE_TOPIC + '/' + RACK_NAME       # MQTT topic to subscribe to

# Define GPIO pins for the lock
LOCK_PINS = [13, 12, 14, 27, 26]
lock_objs = [machine.Pin(pin, machine.Pin.OUT) for pin in LOCK_PINS]  # Create pin objects

for lock in lock_objs:
    lock.value(0)  # Set the initial value to low

# Define control pins for the CD74HC4067 multiplexer
S0 = machine.Pin(2, machine.Pin.OUT)
S1 = machine.Pin(4, machine.Pin.OUT)
S2 = machine.Pin(5, machine.Pin.OUT)
S3 = machine.Pin(18, machine.Pin.OUT)

# SIG pins used to control LEDs
SIG1 = machine.Pin(19, machine.Pin.OUT)
SIG2 = machine.Pin(15, machine.Pin.OUT)

SIG1.value(0)  # Initially turn off SIG1
SIG2.value(0)  # Initially turn off SIG2

# Mapping of channels to servo control based on location identifiers
channel_select = {
    'A1': 0, 'A2': 1, 'A3': 2, 'A4': 3, 'A5': 4, 'A6': 5,
    'B1': 6, 'B2': 7, 'B3': 8, 'B4': 9, 'B5': 10, 'B6': 11,
    'C1': 12, 'C2': 13, 'C3': 14, 'C4': 15, 'C5': 16, 'C6': 17,
    'D1': 18, 'D2': 19, 'D3': 20, 'D4': 21, 'D5': 22, 'D6': 23,
    'E1': 24, 'E2': 25, 'E3': 26, 'E4': 27, 'E5': 28, 'E6': 29,
}

def connect_wifi():
    """Function to connect to the Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(SSID, PASSWORD)

        while not wlan.isconnected():
            pass

    print('WiFi connected successfully!')

def connect_mqtt():
    """Function to connect to the MQTT broker and subscribe to a topic."""
    client = MQTTClient(RACK_NAME, MQTT_SERVER, MQTT_PORT)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC.encode())

    print('Connected to MQTT Broker and subscribed to topic')

    return client

def control_door(row, action):
    """Control door based on the row ('A' to 'E') and action (True for OPEN, False for CLOSE)."""
    if row == 'A':
        lock = lock_objs[0]
    elif row == 'B':
        lock = lock_objs[1]
    elif row == 'C':
        lock = lock_objs[2]
    elif row == 'D':
        lock = lock_objs[3]
    elif row == 'E':
        lock = lock_objs[4]

    lock.value(1 if action else 0)  # Set lock value based on action

def mqtt_callback(topic, msg):
    """Callback function that processes messages received from MQTT."""

    print('Message on topic: %s: %s' % (topic, msg.decode()))

    try:
        # Strip the outer quotes from the string before evaluation
        message_str = msg.decode().strip('"')
        command = eval(message_str)  # convert the string to a tuple

        row = command[0][0]  # Get row (e.g., 'A', 'B', etc.)
        column = command[0]  # Get full column identifier (e.g., 'A1', 'B2')
        action = command[1]  # Get action (0 or 1)

        control_door(row, action)  # Control the door

        channel = channel_select[column]

        set_channel(channel)
        set_led(channel, action)

    except Exception as e:
        print(f"Error processing message: {e}")

def set_channel(channel):
    """Set the CD74HC4067 multiplexer channel for controlling different servos."""
    S0.value(channel & 0x01)
    S1.value((channel >> 1) & 0x01)
    S2.value((channel >> 2) & 0x01)
    S3.value((channel >> 3) & 0x01)

def set_led(channel, action):
    """Control LED status based on channel and action (True to turn ON, False to turn OFF)."""

    if channel < 16:
        SIG1.value(action)
    else:
        SIG2.value(action)

    print(f"Channel {channel} LED {'turned ON' if action else 'turned OFF'}")

def main():
    """Main function to initialize system and continuously check for MQTT messages."""
    
    connect_wifi()
    client = connect_mqtt()

    while True:

        try:
            client.check_msg()

        except Exception as e:
            print("Error:", e)
            print("Reconnecting...")
            time.sleep(2)
            connect_wifi()
            client = connect_mqtt()


if __name__ == "__main__":

    main()