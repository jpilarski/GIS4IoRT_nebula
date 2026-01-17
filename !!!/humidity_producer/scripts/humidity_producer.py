import sys
import time
import json
import random
import math
import paho.mqtt.client as mqtt
from shapely import wkb
from shapely.geometry import Point

class Profile:
    def get_value(self, x):
        raise NotImplementedError

class SineProfile(Profile):
    def get_value(self, x):
        return 15 + 14 * math.sin(x)

class CosineProfile(Profile):
    def get_value(self, x):
        return 15 + 14 * math.cos(x)

class SawtoothProfile(Profile):
    def get_value(self, x):
        cycle_progress = (x % (2 * math.pi)) / (2 * math.pi)
        return cycle_progress * 30

class RandomProfile(Profile):
    def get_value(self, x):
        return random.uniform(0, 30)

class TrapezoidProfile(Profile):
    def get_value(self, x):
        cycle = x % (2 * math.pi)
        quarter = (2 * math.pi) / 4
        if cycle < quarter:
            return (cycle / quarter) * 30
        elif cycle < 2 * quarter:
            return 30
        elif cycle < 3 * quarter:
            prog = (cycle - 2*quarter) / quarter
            return 30 * (1 - prog)
        else:
            return 0

class VirtualSensor:
    def __init__(self, sensor_id, polygon, profile_type):
        self.sensor_id = sensor_id
        self.x, self.y = self._generate_position(polygon)
        self.profile = profile_type
        self.tick_counter = 0
        self.phase_offset = random.uniform(0, 2 * math.pi)
        self.speed_factor = random.uniform(0.5, 2.0)
        self.next_emit_time = time.time() + random.uniform(0, 1.0)

    def _generate_position(self, polygon):
        minx, miny, maxx, maxy = polygon.bounds
        while True:
            p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
            if polygon.contains(p):
                return p.x, p.y

    def should_emit(self, current_time):
        return current_time >= self.next_emit_time

    def get_payload(self, current_time):
        base_resolution = 20.0
        step_size = (2 * math.pi) / base_resolution
        angle = (self.tick_counter * step_size * self.speed_factor) + self.phase_offset
        base_val = self.profile.get_value(angle)
        noise = random.uniform(-0.5, 0.5)
        raw_humidity = base_val + noise
        self.tick_counter += 1
        humidity = round(max(0.0, min(30.0, raw_humidity)), 1)
        
        return {
            "timestamp": int(current_time * 1000),
            "sensor_id": self.sensor_id,
            "position_x": self.x,
            "position_y": self.y,
            "humidity": humidity
        }

    def schedule_next(self, current_time, interval):
        jitter = random.uniform(-0.1 * interval, 0.1 * interval)
        self.next_emit_time = current_time + interval + jitter

def load_polygon(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            poly = wkb.loads(bytes.fromhex(content))
            return poly
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 6:
        print("Usage: python3 humidity_producer.py <IP> <PORT> <FIELD_FILE> <NUM_SENSORS> <FREQ_HZ>")
        return

    mqtt_ip = sys.argv[1]
    mqtt_port = int(sys.argv[2])
    field_file = sys.argv[3]
    num_sensors = int(sys.argv[4])
    freq_hz = float(sys.argv[5])
    interval = 1.0 / freq_hz
    mqtt_topic = "humidity_producer"
    polygon = load_polygon(field_file)
    sensors = []
    available_profiles = [SineProfile(), CosineProfile(), SawtoothProfile(), TrapezoidProfile(), RandomProfile()]
    for i in range(num_sensors):
        profile = random.choice(available_profiles)
        s = VirtualSensor(i, polygon, profile)
        sensors.append(s)
    client = mqtt.Client(
        client_id="humidity_farm_producer",
        transport="websockets",
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    try:
        client.connect(mqtt_ip, mqtt_port, 60)
        client.loop_start()
        while True:
            now = time.time()
            for sensor in sensors:
                if sensor.should_emit(now):
                    payload = sensor.get_payload(now)
                    try:
                        client.publish(mqtt_topic, json.dumps(payload))
                    except Exception as e:
                        print(f"Error: {e}")
                    sensor.schedule_next(now, interval)
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    main()
