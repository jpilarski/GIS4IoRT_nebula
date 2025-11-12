import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix  # Import wiadomości NavSatFix
import paho.mqtt.client as mqtt
import sys
import json
import time

class Ros2MqttBridge(Node):
    def __init__(self, mqtt_client):
        super().__init__('ros2_mqtt_gps_bridge')
        self.mqtt_client = mqtt_client
        self.leader_sub = self.create_subscription(
            NavSatFix,
            '/leader/gps/fix',
            self.leader_callback,
            10)
        self.follower_sub = self.create_subscription(
            NavSatFix,
            '/follower/gps/fix',
            self.follower_callback,
            10)

    def leader_callback(self, msg):
        self.process_and_publish(msg, robot_id=0)

    def follower_callback(self, msg):
        self.process_and_publish(msg, robot_id=1)

    def process_and_publish(self, msg, robot_id):
        data = {
            "timestamp": time.time(),
            "robot_id": robot_id,
            "position_x": msg.latitude,
            "position_y": msg.longitude
        }
        try:
            payload = json.dumps(data)
            self.mqtt_client.publish("gps_fix", payload)
        
        except Exception as e:
            pass

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        pass
    else:
        print(f"Error MQTT: {rc}")

def main(args=None):
    mqtt_ip = sys.argv[1]
    mqtt_port = int(sys.argv[2])
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(mqtt_ip, mqtt_port, 60)
    mqtt_client.loop_start()
    rclpy.init(args=args)
    bridge_node = Ros2MqttBridge(mqtt_client)
    try:
        rclpy.spin(bridge_node)
    except KeyboardInterrupt:
        pass
    finally:
        bridge_node.destroy_node()
        rclpy.shutdown()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == '__main__':
    main()