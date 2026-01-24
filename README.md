# NebulaStream for GIS4IoRT Chist-Era Project

### Usage

1. **Clone the repository:**
    ```bash
    git clone https://github.com/jpilarski/GIS4IoRT_nebula
    cd GIS4IoRT_nebula
    ```

2. **On Machine 1 (Coordinator):**
    Navigate to the `/nes_coordinator` directory:
    * Set the `NES_COORDINATOR_IP` in the `.env` file to the IP address of Machine 1
    * Run `docker compose pull` and `docker compose up`

3. **On Machine 2 (ROS2 Bridge):**
    Navigate to the `/ros2_mqtt_bridge` directory:
    * _Optional: Set `MQTT_IP` in the `.env` file to the IP address of Machine 2, or leave it as `127.0.0.1`_
    * Configure `ROBOT_NAME`, `ROS2_TOPIC`, and `MQTT_TOPIC` in the `.env` file, select between `leader`, `follower` and `leader_inv`
    * Run `docker compose pull` and `docker compose build`
    * Run services: `docker compose up mosquitto -d` and `docker compose up ros2_mqtt -d`
    * Run `docker compose up ros2_play` (perform this after configuring the worker in Step 4, and preferably after submitting the queries in Step 8)

4. **On Machine 2 (Robot Worker):**
    Navigate to the `/nes_robot_worker` directory:
    * Open `config/nes_robot_worker_config.yml` and update the following:
        * Set `coordinatorHost` to match `NES_COORDINATOR_IP` (from Step 2)
        * Set `localWorkerHost` to the IP address of this Machine
        * Update `workerId`
        * Set `physicalSourceName` and `topic` to match `ROBOT_NAME` and `MQTT_TOPIC` (from Step 3)
        * Update `url` if `MQTT_IP` was changed in Step 3
    * Run `docker compose pull` and `docker compose up`

5. **Repeat steps 3–4** for each additional robot on a new machine

6. **On another Machine (Humidity Producer):**
    Navigate to the `/humidity_producer` directory:
    * _Optional: Set `MQTT_IP` in the `.env` file to the IP address of this Machine, or leave it as `127.0.0.1`_
    * Run `docker compose pull` and `docker compose build`
    * Run services: `docker compose up mosquitto -d` and `docker compose up humidity_producer`

7. **On the same Machine (Humidity Worker):**
    Navigate to the `/nes_humidity_worker` directory:
    * Open `config/nes_humidity_worker_config.yml` and update the following:
        * Set `coordinatorHost` to match `NES_COORDINATOR_IP` (from Step 2)
        * Set `localWorkerHost` to the IP address of this Machine
        * Update `workerId`
        * Update `url` if `MQTT_IP` was changed in Step 6
    * Run `docker compose pull` and `docker compose up`

8. **On Machine 1 (or a separate machine from the worker):**
    Navigate to the `/nes_query_results_ui` directory:
    * Set `NES_COORDINATOR_IP` in the `.env` file to match the IP from Step 2
    * Set `QUERY_HOST_IP` to the IP address of this Machine
    * Update `GEOFENCE_QUERY`, `FIELD_FILE`, `HUMIDITY_QUERY`, `HUMIDITY_THRESHOLD`, `BUFFER_RADIUS`, `COLLISION_QUERY`, `COLLISION_RADIUS` and `QUERY_NAMES`
    * Run `docker compose pull` and `docker compose build`
    * Run services: `docker compose up mosquitto -d`, `docker compose up nes_ui -d`
    * Run queries: `docker compose up geofence_query -d`, `docker compose up humidity_query -d` and `docker compose up collision_query -d`
    * Open the NES UI (current Machine IP, port `9000`) and enter `NES_COORDINATOR_IP:8081`
    * Run subscriber by running `docker compose up subscriber`

### One-machine Usage

You can also run all the components on one machine. to do so enter the /all_in_one_configuration directory. you can either type `docker compose up...` commands by urself, or type bash shell/run_all.sh. this will run all the robots and humidity producer, also the ui , all the queries and the subscriber. it will also run visualizer to see everythong in realtime on your browser. change MACHINE_IP!!