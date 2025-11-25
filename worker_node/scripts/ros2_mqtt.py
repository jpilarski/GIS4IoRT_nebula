import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
import paho.mqtt.client as mqtt
import sys
import json
import heapq # Do kolejki priorytetowej

class Ros2MqttBridge(Node):
    def __init__(self, mqtt_client):
        super().__init__('ros2_mqtt_gps_bridge')
        self.mqtt_client = mqtt_client
        
        # Konfiguracja bufora
        # Ile czasu (w ns) "trzymamy" wiadomości w buforze, żeby dać szansę spóźnialskim.
        # Przy prędkości x10, 0.2s z baga przelatuje w 0.02s rzeczywistego czasu.
        # Wartość 200ms (0.2s) jest bezpieczna dla większości opóźnień sieciowych.
        self.buffer_delay_ns = 200 * 1_000_000 
        
        # Sterta (Priority Queue): przechowuje krotki (timestamp, robot_id, msg)
        self.msg_heap = []
        
        # Najnowszy timestamp jaki widzieliśmy (do obliczania progu uwolnienia bufora)
        self.max_seen_ts = 0
        
        # Ostatni WYSŁANY timestamp (do pilnowania ścisłej monotoniczności)
        self.last_sent_ts = 0

        # Subskrypcje
        self.leader_sub = self.create_subscription(
            NavSatFix, '/leader/gps/fix', lambda m: self.buffer_callback(m, 0), 10)
        self.follower_sub = self.create_subscription(
            NavSatFix, '/follower/gps/fix', lambda m: self.buffer_callback(m, 1), 10)

        # Timer procesujący bufor (np. co 0.01s - bardzo często, żeby nie dławić przepływu)
        self.timer = self.create_timer(0.01, self.process_buffer)

    def buffer_callback(self, msg, robot_id):
        # Oblicz czas w nanosekundach
        ts = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
        
        # Aktualizujemy najnowszy widziany czas
        if ts > self.max_seen_ts:
            self.max_seen_ts = ts
            
        # Wrzucamy na stertę. Heapq automatycznie trzyma najstarszy element (najmniejszy ts) na początku.
        # Format: (czas, id, wiadomość)
        heapq.heappush(self.msg_heap, (ts, robot_id, msg))

    def process_buffer(self):
        if not self.msg_heap:
            return

        # Próg uwalniania: Najnowszy_widziany_czas - Opóźnienie
        # Wszystko co jest STARSZE niż ten próg, uznajemy za "bezpieczne i ułożone"
        release_threshold = self.max_seen_ts - self.buffer_delay_ns

        # Pętla wyciągająca wiadomości gotowe do wysłania
        while self.msg_heap:
            # Podglądamy najstarszy element na stercie (bez usuwania)
            head_ts, head_id, head_msg = self.msg_heap[0]

            if head_ts <= release_threshold:
                # Jeśli jest wystarczająco stary -> wysyłamy
                heapq.heappop(self.msg_heap) # Usuwamy ze sterty
                self.publish_mqtt(head_ts, head_id, head_msg)
            else:
                # Jeśli najstarszy element jest wciąż zbyt "świeży" (blisko max_seen),
                # to znaczy że musimy poczekać, bo może przyjść coś starszego od niego.
                break

    def publish_mqtt(self, ts_ns, robot_id, msg):
        # OSTATECZNY STRAŻNIK MONOTONICZNOŚCI
        # Jeśli z jakiegoś powodu (restart baga, pętla) czas się cofnie -> ignorujemy
        if ts_ns < self.last_sent_ts:
            self.get_logger().warn(f"Odrzucono stary pakiet! ID: {robot_id}, TS: {ts_ns} < Ostatni: {self.last_sent_ts}")
            return

        self.last_sent_ts = ts_ns
        timestamp_ms = ts_ns // 1_000_000

        data = {
            "timestamp": timestamp_ms,
            "robot_id": robot_id,
            "position_x": msg.longitude,
            "position_y": msg.latitude
        }
        
        try:
            payload = json.dumps(data)
            self.mqtt_client.publish("gps_fix", payload)
        except Exception as e:
            self.get_logger().error(f'MQTT send fail: {e}')

# ... (Reszta kodu: on_connect, main - bez zmian) ...
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

# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import NavSatFix
# import paho.mqtt.client as mqtt
# import sys
# import json
# import time

# class Ros2MqttBridge(Node):
#     def __init__(self, mqtt_client):
#         super().__init__('ros2_mqtt_gps_bridge')
#         self.mqtt_client = mqtt_client
        
#         # Otwarcie pliku do logowania (tryb 'w' - nadpisuje przy starcie)
#         self.log_file = open('scripts/ros_received.txt', 'w')
#         self.log_file.write("ros_timestamp_ns,receive_timestamp_ns,robot_id\n")
        
#         self.leader_sub = self.create_subscription(
#             NavSatFix, '/leader/gps/fix', self.leader_callback, 10)
#         self.follower_sub = self.create_subscription(
#             NavSatFix, '/follower/gps/fix', self.follower_callback, 10)

#     def leader_callback(self, msg):
#         self.process_and_publish(msg, robot_id=0)

#     def follower_callback(self, msg):
#         self.process_and_publish(msg, robot_id=1)

#     def process_and_publish(self, msg, robot_id):
#         # Czas z wiadomości ROS
#         ros_total_nsec = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
#         timestamp_ms = ros_total_nsec // 1_000_000
        
#         # Logowanie do pliku (format: czas_z_baga, czas_odebrania_przez_skrypt, id)
#         try:
#             recv_time = time.time_ns()
#             self.log_file.write(f"{ros_total_nsec},{recv_time},{robot_id}\n")
#             # Flush wymusza zapis na dysk od razu (bezpieczniej przy crashu, wolniej w działaniu)
#             # Przy x10 prędkości można usunąć flush() jeśli będzie lagować
#             # self.log_file.flush() 
#         except Exception as e:
#             self.get_logger().error(f'Log file error: {e}')

#         data = {
#             "timestamp": timestamp_ms,
#             "robot_id": robot_id,
#             "position_x": msg.longitude,
#             "position_y": msg.latitude
#         }
        
#         try:
#             payload = json.dumps(data)
#             # QoS 0 w MQTT jest szybkie, ale nie gwarantuje dostarczenia. 
#             # QoS 1 lub 2 gwarantuje, ale spowalnia. Tu domyślnie jest zwykle 0.
#             self.mqtt_client.publish("gps_fix", payload)
#         except Exception as e:
#             self.get_logger().error(f'MQTT send fail: {e}')

#     def cleanup(self):
#         if self.log_file:
#             self.log_file.close()
#             print("Log file closed.")

# # ... (Funkcja on_connect bez zmian) ...
# def on_connect(client, userdata, flags, reasonCode, properties):
#     if reasonCode.is_failure:
#         print(f"MQTT connection error: {reasonCode}")
#     else:
#         print("MQTT connect")

# def main(args=None):
#     if len(sys.argv) < 3:
#         sys.exit(1)
#     mqtt_ip = sys.argv[1]
#     mqtt_port = int(sys.argv[2])
    
#     mqtt_client = mqtt.Client(
#         transport="websockets",
#         protocol=mqtt.MQTTv5,
#         callback_api_version=mqtt.CallbackAPIVersion.VERSION2
#     )
#     mqtt_client.on_connect = on_connect

#     try:
#         mqtt_client.connect(mqtt_ip, mqtt_port, 60)
#     except Exception as e:
#         sys.exit(1)
    
#     mqtt_client.loop_start()
#     rclpy.init(args=args)
    
#     bridge_node = Ros2MqttBridge(mqtt_client)

#     try:
#         rclpy.spin(bridge_node)
#     except KeyboardInterrupt:
#         bridge_node.get_logger().info('KeyboardInterrupt')
#     except Exception as e:
#         bridge_node.get_logger().error(f'Error: {e}')
#     finally:
#         bridge_node.cleanup() # Zamykamy plik
#         bridge_node.destroy_node()
#         rclpy.shutdown()
#         mqtt_client.loop_stop()
#         mqtt_client.disconnect()

# if __name__ == '__main__':
#     main()

# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import NavSatFix
# import paho.mqtt.client as mqtt
# import sys
# import json
# import time

# class Ros2MqttBridge(Node):
#     def __init__(self, mqtt_client):
#         super().__init__('ros2_mqtt_gps_bridge')
#         self.mqtt_client = mqtt_client
#         self.leader_sub = self.create_subscription(
#             NavSatFix,
#             '/leader/gps/fix',
#             self.leader_callback,
#             10)
#         self.follower_sub = self.create_subscription(
#             NavSatFix,
#             '/follower/gps/fix',
#             self.follower_callback,
#             10)

#     def leader_callback(self, msg):
#         self.process_and_publish(msg, robot_id=0)

#     def follower_callback(self, msg):
#         self.process_and_publish(msg, robot_id=1)

#     def process_and_publish(self, msg, robot_id):
#         total_nsec = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
#         timestamp = total_nsec // 1_000_000
#         data = {
#             "timestamp": timestamp,
#             "robot_id": robot_id,
#             "position_x": msg.longitude,
#             "position_y": msg.latitude
#         }
#         try:
#             payload = json.dumps(data)
#             self.mqtt_client.publish("gps_fix", payload)
#         except Exception as e:
#             self.get_logger().error(f'MQTT send fail: {e}')

# def on_connect(client, userdata, flags, reasonCode, properties):
#     if reasonCode.is_failure:
#         print(f"MQTT connection error: {reasonCode}")
#     else:
#         print("MQTT connect")

# def main(args=None):
#     if len(sys.argv) < 3:
#         sys.exit(1)
#     mqtt_ip = sys.argv[1]
#     mqtt_port = int(sys.argv[2])
#     mqtt_client = mqtt.Client(
#         transport="websockets",
#         protocol=mqtt.MQTTv5,
#         callback_api_version=mqtt.CallbackAPIVersion.VERSION2
#         )
#     mqtt_client.on_connect = on_connect

#     try:
#         mqtt_client.connect(mqtt_ip, mqtt_port, 60)
#     except Exception as e:
#         sys.exit(1)
    
#     mqtt_client.loop_start()

#     rclpy.init(args=args)
#     bridge_node = Ros2MqttBridge(mqtt_client)

#     try:
#         rclpy.spin(bridge_node)
#     except KeyboardInterrupt:
#         bridge_node.get_logger().info('KeyboardInterrupt')
#     except Exception as e:
#         bridge_node.get_logger().error(f'Error: {e}')
#     finally:
#         bridge_node.destroy_node()
#         rclpy.shutdown()
#         mqtt_client.loop_stop()
#         mqtt_client.disconnect()

# if __name__ == '__main__':
#     main()