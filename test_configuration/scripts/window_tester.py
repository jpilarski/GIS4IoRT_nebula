import paho.mqtt.client as mqtt
import json
import time

# Configuration
BROKER_IP = "127.0.0.1"
PORT_LEADER = 9001
PORT_FOLLOWER = 9002

TOPIC_LEADER = "leader_gps_fix"
TOPIC_FOLLOWER = "follower_gps_fix"

# Settings
PUBLISH_FREQUENCY_HZ = 0.25
REPEAT_BATCH = 3  # Ile razy powtórzyć wysłanie w jednym cyklu

# Position Data
POS_LEADER_X = 3.43355735
POS_LEADER_Y = 46.339390194

POS_FOLLOWER_X = 3.43355736
POS_FOLLOWER_Y = 46.33939019

def create_client(client_name, port):
    client = mqtt.Client(
        client_id=f"{client_name}_pub",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        transport="websockets",
        protocol=mqtt.MQTTv5
    )
    print(f"Connecting {client_name} to {BROKER_IP}:{port}...", flush=True)
    client.connect(BROKER_IP, port, 60)
    client.loop_start()
    return client

def main():
    sleep_duration = 1.0 / PUBLISH_FREQUENCY_HZ

    client_leader = create_client("leader", PORT_LEADER)
    client_follower = create_client("follower", PORT_FOLLOWER)

    print("------------------------------------------------")
    print(f"Broadcasting at {PUBLISH_FREQUENCY_HZ} Hz.")
    print(f"Batch size: {REPEAT_BATCH} messages per cycle.")
    print("------------------------------------------------")

    try:
        while True:
            # Loop for the batch repetition
            for i in range(REPEAT_BATCH):
                
                # --- 1. LEADER ---
                ts_leader = int(time.time() * 1000)
                payload_leader = {
                    "timestamp": ts_leader,
                    "robot_name": "leader",
                    "position_x": POS_LEADER_X,
                    "position_y": POS_LEADER_Y
                }
                client_leader.publish(TOPIC_LEADER, json.dumps(payload_leader))
                print(f"leader: {ts_leader/1000}")

                time.sleep(0.001)
                # --- 2. FOLLOWER ---
                # Fetch new timestamp immediately
                ts_follower = int(time.time() * 1000)
                payload_follower = {
                    "timestamp": ts_follower,
                    "robot_name": "follower",
                    "position_x": POS_FOLLOWER_X,
                    "position_y": POS_FOLLOWER_Y
                }
                client_follower.publish(TOPIC_FOLLOWER, json.dumps(payload_follower))
                print(f"follower: {ts_follower/1000}")

                # Tiny sleep to ensure timestamp (ms) changes between repetitions
                # if the CPU is too fast
                time.sleep(0.001)

                print()
            # Wait for the next major cycle (2 Hz)
            time.sleep(sleep_duration)
            print()

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        client_leader.loop_stop()
        client_leader.disconnect()
        client_follower.loop_stop()
        client_follower.disconnect()
        print("Disconnected both clients.")

if __name__ == '__main__':
    main()