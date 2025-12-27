import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
import paho.mqtt.client as mqtt
import sys, json, time

class Ros2MqttBridge(Node):
    def __init__(self, mqtt_client, robot_name):
        super().__init__('ros2_mqtt_bridge')
        self.mqtt_client = mqtt_client
        self.robot_name = robot_name

        self.create_subscription(
            NavSatFix, 
            f'/{robot_name}/gps/fix', 
            self.callback, 
            10)
        self.get_logger().info(f"Bridge started for robot: {robot_name}")

    def callback(self, msg):
        payload = {
            # total_nsec = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
            # timestamp = total_nsec // 1_000_000 
            "timestamp": int(time.time() * 1000),
            "robot_name": self.robot_name,
            "position_x": msg.longitude,
            "position_y": msg.latitude
        }
        try:
            self.mqtt_client.publish(f"{self.robot_name}_gps_fix", json.dumps(payload))
        except Exception as e:
            self.get_logger().error(f"MQTT publish failed: {e}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 script.py <IP> <PORT> <ROBOT_NAME>")
        return

    m_ip, m_port, r_name = sys.argv[1], int(sys.argv[2]), sys.argv[3]

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        transport="websockets",
        protocol=mqtt.MQTTv5
    )

    try:
        client.connect(m_ip, m_port, 60)
        client.loop_start()

        rclpy.init()
        node = Ros2MqttBridge(client, r_name)
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    main()
