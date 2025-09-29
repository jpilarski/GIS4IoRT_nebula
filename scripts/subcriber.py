import paho.mqtt.client as mqtt
import sys
import select
import tty
import termios

BROKER = "mosquitto"
PORT = 9001
TOPICS = ["window-demo", "simple-copy", "circle-filter"]

current_index = 0
current_topic = None

def on_connect(client, userdata, flags, reasonCode, properties):
    switch_topic(client)

def on_message(client, userdata, msg):
    print(msg.payload.decode())

def switch_topic(client):
    global current_topic
    if current_topic:
        client.unsubscribe(current_topic)
    current_topic = TOPICS[current_index]
    client.subscribe(current_topic)
    print(f"Listening for {current_topic}")

client = mqtt.Client(
    transport="websockets",
    protocol=mqtt.MQTTv5,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
tty.setcbreak(fd)

print("Press SPACE to switch topic, Ctrl+C to exit")

try:
    while True:
        if select.select([sys.stdin], [], [], 0.1)[0]:
            c = sys.stdin.read(1)
            if c == ' ':
                current_index = (current_index + 1) % len(TOPICS)
                switch_topic(client)
except KeyboardInterrupt:
    pass
finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    client.loop_stop()
    client.disconnect()
