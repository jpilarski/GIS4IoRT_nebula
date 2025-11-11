#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import json
import paho.mqtt.client as mqtt
from sensor_msgs.msg import NavSatFix
from threading import Lock
import time

WORKER_IP = "192.168.0.163"

# Konfiguracja klienta MQTT (pozostaje taka sama)
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    transport="websockets",
    protocol=mqtt.MQTTv5
)

client.connect(WORKER_IP, 9001, 60)
client.loop_start()

lock = Lock()

# Definicja węzła ROS 2
class MqttPublisherNode(Node):
    
    def __init__(self):
        # Inicjalizacja węzła ROS 2
        super().__init__('gps_fix_to_mqtt')
        self.sent_count = 0
        self.sec_timer = 5
        
        # 1. Tworzenie subskrypcji
        self.subscription = self.create_subscription(
            NavSatFix,                       # Typ wiadomości
            '/leader/gps/fix',               # Temat do nasłuchiwania
            self.gps_callback,               # Metoda zwrotna
            10                               # QoS: głębokość kolejki
        )
        self.get_logger().info('ROS 2 Node started and subscribed to /leader/gps/fix')
        
        # 2. Tworzenie timera do raportowania
        self.timer = self.create_timer(5.0, self.report_counts) # 5.0 sekund
    
    # Zmieniona funkcja zwrotna (bez argumentu 'event' z ROS 1)
    def gps_callback(self, msg: NavSatFix):
        global client, lock
        
        # Użycie bieżącego czasu systemowego
        timestamp = int(time.time() * 1000) 
        
        # Pobrane pola: latitude i longitude
        data = {
            "timestamp": timestamp,
            "robot_id": 1,
            "latitude": msg.latitude,
            "longitude": msg.longitude
        }

        with lock:
            client.publish("gps_fix", json.dumps(data))
            self.sent_count += 1

    # Funkcja wywoływana przez ROS 2 Timer
    def report_counts(self):
        with lock:
            self.get_logger().info(f"{self.sec_timer}s - {self.sent_count}")
            self.sec_timer += 5
            
def main(args=None):
    rclpy.init(args=args)      # Inicjalizacja środowiska ROS 2
    
    node = MqttPublisherNode()
    
    try:
        rclpy.spin(node)       # Utrzymywanie węzła aktywnego
    except KeyboardInterrupt:
        pass
    
    # Czyste zamknięcie
    node.destroy_node()
    rclpy.shutdown()
    client.loop_stop()

if __name__ == '__main__':
    main()