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
        self.get_logger().debug(f'Odebrano dane z /leader/gps/fix: {msg.latitude}, {msg.longitude}')
        self.process_and_publish(msg, robot_id=0)

    def follower_callback(self, msg):
        self.get_logger().debug(f'Odebrano dane z /follower/gps/fix: {msg.latitude}, {msg.longitude}')
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
            self.get_logger().debug(f'Opublikowano na MQTT (gps_fix): {payload}')
        
        except Exception as e:
            self.get_logger().error(f'MQTT fail: {e}')

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT connect")
    else:
        print(f"MQTT connection error: {rc}")

def main(args=None):
    if len(sys.argv) < 3:
        sys.exit(1)

    mqtt_ip = sys.argv[1]
    mqtt_port = int(sys.argv[2])

    print(f"Łączenie z brokerem MQTT pod adresem {mqtt_ip}:{mqtt_port}...")
    mqtt_client = mqtt.Client()
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
        bridge_node.get_logger().info('Otrzymano KeyboardInterrupt, zamykanie...')
    except Exception as e:
        bridge_node.get_logger().error(f'Napotkano nieoczekiwany błąd: {e}')
    finally:
        bridge_node.get_logger().info('Zamykanie węzła ROS i klienta MQTT.')
        bridge_node.destroy_node()
        rclpy.shutdown()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Zamknięto pomyślnie.")

if __name__ == '__main__':
    main()