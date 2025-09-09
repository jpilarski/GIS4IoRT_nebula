import paho.mqtt.client as mqtt

BROKER = "mosquitto"
PORT = 9001
TOPIC = "window-results"

def on_connect(client, userdata, flags, reasonCode, properties):
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(msg.payload.decode())

client = mqtt.Client(
    transport="websockets",
    protocol=mqtt.MQTTv5,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
