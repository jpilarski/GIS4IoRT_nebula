import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
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
        # total_nsec = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
        # timestamp = total_nsec // 1_000_000
        timestamp = int(time.time() * 1000)
        data = {
            "timestamp": timestamp,
            "robot_id": robot_id,
            "position_x": msg.longitude,
            "position_y": msg.latitude
        }
        try:
            payload = json.dumps(data)
            self.mqtt_client.publish("gps_fix", payload)
        except Exception as e:
            self.get_logger().error(f'MQTT send fail: {e}')

def on_connect(client, userdata, flags, reasonCode, properties):
    if reasonCode.is_failure:
        print(f"MQTT connection error: {reasonCode}")
    else:
        print("MQTT connect")

def main(args=None):
    if len(sys.argv) < 3:
        sys.exit(1)
    mqtt_ip = sys.argv[1]
    mqtt_port = int(sys.argv[2])
    mqtt_client = mqtt.Client(
        transport="websockets",
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
    mqtt_client.on_connect = on_connect

    try:
        mqtt_client.connect(mqtt_ip, mqtt_port, 60)
    except Exception as e:
        sys.exit(1)
    
    mqtt_client.loop_start()

    rclpy.init(args=args)
    bridge_node = Ros2MqttBridge(mqtt_client)

    try:
        rclpy.spin(bridge_node)
    except KeyboardInterrupt:
        bridge_node.get_logger().info('KeyboardInterrupt')
    except Exception as e:
        bridge_node.get_logger().error(f'Error: {e}')
    finally:
        bridge_node.destroy_node()
        rclpy.shutdown()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == '__main__':
    main()