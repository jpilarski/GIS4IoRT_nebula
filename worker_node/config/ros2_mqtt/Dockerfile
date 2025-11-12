FROM ros:jazzy-ros-base

RUN apt-get update && apt-get install -y \
    python3-pip \
 && pip3 install paho-mqtt \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*