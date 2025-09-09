FROM ros:noetic-ros-core

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    curl \
    ros-noetic-rospy \
    ros-noetic-nav-msgs \
    bash-completion \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install \
    "numpy==1.24.0" \
    "pandas==1.5.3" \
    "protobuf==3.20.0" \
    nespy \
    holoviews \
    bokeh \
    requests \
    sseclient \
    paho-mqtt

RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc

RUN mkdir -p /bags /scripts

CMD ["/bin/bash"]
