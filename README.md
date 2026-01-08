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

3. **On Machine 2 (Bridge):**
    Navigate to the `/ros2_mqtt_bridge` directory:
    * _Optional: Update `MQTT_IP` to the IP address of Machine 2, or leave it as `127.0.0.1`_
    * Configure `ROBOT_NAME`, `ROS2_TOPIC`, and `MQTT_TOPIC`, select between `leader` and `follower`
    * Run `docker compose pull` and `docker compose build`
    * Run services: `docker compose up mosquitto -d` and `docker compose up ros2_mqtt -d`
    * Run `docker compose up ros2_play` (perform this after configuring the worker in Step 4, and preferably after submitting the query in Step 6)

4. **On Machine 2 (Worker):**
    Navigate to the `/nes_worker` directory:
    * Open `config/nes_worker_config.yml` and update the following:
        * Set `coordinatorHost` to match `NES_COORDINATOR_IP` (from Step 2)
        * Update `localWorkerHost` and `workerId`
        * Set `physicalSourceName` and `topic` to match `ROBOT_NAME` and `MQTT_TOPIC` (from Step 3)
        * Update `url` if `MQTT_IP` was changed in Step 3
    * Run `docker compose pull` and `docker compose up`

5. **Repeat steps 3–4** for each additional robot/worker on a new machine

6. **On Machine 1 (or a separate machine from the worker):**
    Navigate to the `/nes_query_results_ui` directory:
    * Set `NES_COORDINATOR_IP` in the `.env` file to match the IP from Step 2
    * Update `QUERY_HOST_IP` to the IP address of this Machine
    * Update `QUERY_NAME`
    * Run `docker compose pull` and `docker compose build`
    * Run services: `docker compose up mosquitto -d`, `docker compose up nes_ui -d`, and `docker compose up subscriber`
    * Open the NES UI (port 9000) and enter `NES_COORDINATOR_IP:8081`
    * Run Query...