#!/usr/bin/env python3
import rospy
import json
import paho.mqtt.client as mqtt
from nav_msgs.msg import Odometry
from threading import Lock
import time

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    transport="websockets",
    protocol=mqtt.MQTTv5
)

client.connect("mosquitto", 9001, 60)
client.loop_start()

sent_count = 0
sec_timer = 5
lock = Lock()

def callback(msg: Odometry):
    global sent_count
    timestamp = int(time.time() * 1000)
    # timestamp = msg.header.stamp.to_nsec() // 1_000_000

    data = {
        "timestamp": timestamp,
        "robot_id": msg.child_frame_id,
        "header_seq": msg.header.seq,
        "position_x": msg.pose.pose.position.x,
        "position_y": msg.pose.pose.position.y,
        "position_z": msg.pose.pose.position.z,
        "orientation_z": msg.pose.pose.orientation.z,
        "orientation_w": msg.pose.pose.orientation.w
    }

    with lock:
        client.publish("gps_odom", json.dumps(data))
        sent_count += 1

def report_counts(event):
    global sent_count, sec_timer
    with lock:
        print(f"{sec_timer}s - {sent_count}")
        sec_timer += 5

def listener():
    rospy.init_node('gps_odom_to_mqtt', anonymous=True)
    rospy.Subscriber("/gps_odom", Odometry, callback)
    
    rospy.Timer(rospy.Duration(5), report_counts)
    
    rospy.spin()

if __name__ == '__main__':
    listener()
