# FROM ros:noetic-ros-core

# RUN apt-get update && apt-get install -y \
#     python3-pip \
#     python3-dev \
#     build-essential \
#     curl \
#     ros-noetic-rospy \
#     ros-noetic-nav-msgs \
#     bash-completion \
#     && rm -rf /var/lib/apt/lists/*

# RUN pip install --upgrade pip

# RUN pip install \
#     "numpy==1.24.0" \
#     "pandas==1.5.3" \
#     "protobuf==3.20.0" \
#     nespy \
#     holoviews \
#     bokeh \
#     requests \
#     sseclient \
#     paho-mqtt \
#     keyboard \
#     rosbags

# RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc

# RUN mkdir -p /bags /scripts

# CMD ["/bin/bash"]

# Zmieniamy obraz bazowy na ROS 2 Humble (LTS)
FROM ros:humble-ros-core

# Humble używa Pythona 3 domyślnie, więc instalujemy tylko pakiety systemowe
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    curl \
    ros-humble-ros-base \
    # Jeśli potrzebujesz innych specyficznych pakietów ROS 2
    ros-humble-sensor-msgs \
    bash-completion \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# rosbag jest teraz wbudowany w ros2. Rosbags może się przydać do konwersji, ale nie do play
RUN pip install \
    "numpy==1.24.0" \
    "pandas==1.5.3" \
    "protobuf==3.20.0" \
    nespy \
    holoviews \
    bokeh \
    requests \
    sseclient \
    paho-mqtt \
    keyboard \
    rosbags # Zostawiamy rosbags do konwersji, jeśli to potrzebne

# Zmieniamy ścieżkę źródłową na ROS 2
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

RUN mkdir -p /bags /scripts

CMD ["/bin/bash"]