import paho.mqtt.client as mqtt
from threading import Thread, Event

# Event to signal when the MQTT client has connected
mqtt_connected = Event()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:
        mqtt_connected.set()  # Set the event when connected
    else:
        print(f"Failed to connect, return code {rc}")
        mqtt_connected.clear()  # Clear the event on failure

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        mqtt_connected.clear()  # Clear the event on unexpected disconnect
        try:
            print("Attempting to reconnect...")
            client.reconnect()
        except Exception as e:
            print(f"Reconnection failed: {e}")

def on_publish(client, userdata, mid):
    print("Message Published...")

def publish_message(client, topic, message):
    mqtt_connected.wait()  # Wait for the connection to be established or reestablished
    client.publish(topic, message, qos=2)
    print(f"Sent '{message}' to topic '{topic}'")

def handle_publish(client, topic, message):
    # Run publishing in a separate thread
    Thread(target=publish_message, args=(client, topic, message)).start()

def connect_mqtt(mqtt_server, mqtt_port):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.connect(mqtt_server, mqtt_port, 60)
    client.loop_start()
    return client

if __name__ == "__main__":
    MQTT_SERVER = '192.168.144.10'
    MQTT_PORT = 1883

    # Example usage
    mqtt_client = connect_mqtt(MQTT_SERVER, MQTT_PORT)
    # Now you can use mqtt_client to publish messages or perform other MQTT operations

    # Publishing a sample message
    sample_topic = "mqtt/test"
    sample_message = "open"
    handle_publish(mqtt_client, sample_topic, sample_message)
    
    # Ensure all threads are joined before exiting
    mqtt_client.loop_stop()
    mqtt_client.disconnect()