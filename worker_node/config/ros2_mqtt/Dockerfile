FROM ros:jazzy-ros-base

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-paho-mqtt \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*