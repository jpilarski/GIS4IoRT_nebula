import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from kafka import KafkaProducer # Zmiana biblioteki
import sys
import json
import time

class Ros2KafkaBridge(Node):
    def __init__(self, kafka_producer, topic_name):
        super().__init__('ros2_kafka_gps_bridge')
        self.producer = kafka_producer
        self.topic_name = topic_name
        
        self.leader_sub = self.create_subscription(
            NavSatFix, '/leader/gps/fix', self.leader_callback, 10)
        self.follower_sub = self.create_subscription(
            NavSatFix, '/follower/gps/fix', self.follower_callback, 10)

    def leader_callback(self, msg):
        self.process_and_publish(msg, robot_id=0)

    def follower_callback(self, msg):
        self.process_and_publish(msg, robot_id=1)

    def process_and_publish(self, msg, robot_id):
        timestamp = int(time.time() * 1000)
        data = {
            "timestamp": timestamp,
            "robot_id": robot_id,
            "position_x": msg.longitude,
            "position_y": msg.latitude
        }
        try:
            # KafkaProducer sam ogarnia serializację dzięki value_serializer w main()
            future = self.producer.send(self.topic_name, data)
            # Opcjonalnie: future.get(timeout=10) # jeśli chcesz czekać na potwierdzenie (blokujące)
        except Exception as e:
            self.get_logger().error(f'Kafka send fail: {e}')

def main(args=None):
    if len(sys.argv) < 3:
        print("Usage: python3 ros2_kafka.py <KAFKA_IP> <KAFKA_PORT>")
        sys.exit(1)
        
    kafka_ip = sys.argv[1]
    kafka_port = sys.argv[2]
    bootstrap_servers = f"{kafka_ip}:{kafka_port}"
    topic_name = "gps_fix"

    print(f"Connecting to Kafka at {bootstrap_servers}...")

    # Czekamy na wstanie Kafki (prosty retry mechanism)
    producer = None
    for _ in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Kafka connected")
            break
        except Exception as e:
            print(f"Waiting for Kafka... {e}")
            time.sleep(2)
            
    if not producer:
        print("Failed to connect to Kafka")
        sys.exit(1)

    rclpy.init(args=args)
    bridge_node = Ros2KafkaBridge(producer, topic_name)

    try:
        rclpy.spin(bridge_node)
    except KeyboardInterrupt:
        bridge_node.get_logger().info('KeyboardInterrupt')
    finally:
        bridge_node.destroy_node()
        rclpy.shutdown()
        producer.close()

if __name__ == '__main__':
    main()