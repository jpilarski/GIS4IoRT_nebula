import paho.mqtt.client as mqtt
import sys
import json

TOPIC = sys.argv[3]
BROKER_IP = sys.argv[1]
PORT = int(sys.argv[2])

def on_connect(client, userdata, flags, reasonCode, properties):
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    output_parts = [f'{key.split("$")[-1]}: {value}' for key, value in data.items()]
    output_string = ", ".join(output_parts)
    print(output_string, flush=True)

client = mqtt.Client(
    transport="websockets",
    protocol=mqtt.MQTTv5,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    pass
finally:
    client.disconnect()